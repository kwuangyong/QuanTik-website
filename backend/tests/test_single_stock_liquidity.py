"""Liquidity filters scans, but does not abort a requested single-stock report."""
from contextlib import ExitStack, contextmanager
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

import engine
import quant_service
import store
import worker
from quant_engine.crawl_data import DataProvider
from quant_engine.quant import (ARIMAEngine, GARCHEngine, HMMEngine,
                                LiquidityEngine, QuantPipeline, ScreenerBridge,
                                SectorEngine, SingleSymbolQuantPipeline)


def prices(volume=100):
    dates = pd.bdate_range(end=pd.Timestamp.now().normalize() - pd.offsets.BDay(), periods=180)
    close = 20000 * np.exp(np.cumsum(np.random.RandomState(7).normal(.0004, .007, len(dates))))
    return pd.DataFrame({'open': close * .999, 'high': close * 1.01,
                         'low': close * .99, 'close': close, 'volume': volume}, index=dates)


@contextmanager
def model_run():
    """Stub expensive fits and external sector lookup; run the remaining core."""
    with ExitStack() as stack:
        fits = [stack.enter_context(patch.object(ARIMAEngine, 'fit', return_value={'order': [1, 0, 0]})),
                stack.enter_context(patch.object(GARCHEngine, 'fit', return_value={'garch': {'forecast_vol': [.7] * 10}})),
                stack.enter_context(patch.object(HMMEngine, 'fit',
                    side_effect=lambda frame, symbol=None: HMMEngine._fallback(frame)))]
        stack.enter_context(patch.object(SectorEngine, '_load_icb_map', return_value={}))
        yield fits


class SingleStockLiquidityTest(unittest.TestCase):
    def assert_full_report(self, report):
        self.assertNotIn('error', report)
        self.assertIs(report['liquidity']['pass'], False)
        for key in ('dist', 'stats', 'vol', 'ac', 'arima', 'garch', 'hmm',
                    'alpha', 'trend', 'flow', 'momentum_alpha', 'hurst',
                    'conditional_mr', 'fcast', 'costs', 'sl', 'rec', 'action'):
            self.assertIn(key, report)
        self.assertTrue(report['stats'])
        self.assertGreater(report['fcast']['_mc_paths'].size, 0)
        self.assertIn('LIQUIDITY_FAIL', report['action']['reason_codes'])

    def test_single_stock_models_run_for_low_sparse_and_zero_volume(self):
        for volume in (np.full(180, 100), np.tile([0, 100], 90), np.zeros(180)):
            with self.subTest(zero_volume=int((volume == 0).sum())), model_run() as fits:
                frame = prices(volume)
                report = SingleSymbolQuantPipeline().batch({'ABW': frame}, idx_df=prices(1000000),
                                                           exchange_map={'ABW': 'UPCOM'})[0]
                self.assert_full_report(report)
                self.assertEqual(report['liquidity'], LiquidityEngine.analyze(frame, 'UPCOM'))
                for fit in fits:
                    fit.assert_called_once()
                presentation = quant_service.present_report(report, frame)
                self.assertEqual(presentation['analysis_status'], 'completed')
                self.assertIs(presentation['liquidity']['pass'], False)
                self.assertTrue(presentation['research']['cone'])
                modules = {module['id']: module for module in presentation['module_reports']}
                self.assertEqual(modules['stats']['status'], 'computed')
                self.assertEqual(modules['liquidity']['result'], presentation['liquidity'])

    def test_scan_with_just_one_stock_still_excludes_low_liquidity(self):
        with model_run() as fits:
            report = QuantPipeline().batch({'ABW': prices()}, exchange_map={'ABW': 'UPCOM'})[0]
        self.assertEqual(report['error'], 'Liquidity gate failed')
        self.assertIs(report['liquidity']['pass'], False)
        self.assertNotIn('stats', report)
        for fit in fits:
            fit.assert_not_called()

    def test_scan_still_analyzes_liquid_stocks(self):
        with model_run() as fits:
            report = QuantPipeline().batch({'FPT': prices(1000000)}, idx_df=prices(1000000),
                                           exchange_map={'FPT': 'HOSE'})[0]
        self.assertNotIn('error', report)
        self.assertIs(report['liquidity']['pass'], True)
        self.assertTrue(report['stats'])
        for fit in fits:
            fit.assert_called_once()

    def test_disabling_liquidity_exclusion_keeps_data_validation(self):
        frame = prices()
        frame.iloc[-1, frame.columns.get_loc('high')] = 1
        with model_run() as fits:
            report = SingleSymbolQuantPipeline().analyze('ABW', frame, exchange='UPCOM')
        self.assertTrue(report['error'].startswith('Data quality failed:'))
        for fit in fits:
            fit.assert_not_called()

    def test_cached_single_symbol_adapter_runs_models_below_scan_threshold(self):
        frame = prices()
        bridge = Mock()
        bridge.fetch_ohlcv.return_value = {'ABW': frame}
        bridge.fetch_index.return_value = prices(1000000)
        bridge.fetch_exchange_map.return_value = {'ABW': 'UPCOM'}
        quant_service.analyze_symbol.cache_clear()
        self.addCleanup(quant_service.analyze_symbol.cache_clear)
        with model_run(), patch.object(ScreenerBridge, '__new__', return_value=bridge):
            report = quant_service.analyze_symbol('ABW')
        self.assertEqual(report['analysis_status'], 'completed')
        self.assertIs(report['liquidity']['pass'], False)
        self.assertTrue(report['stats'])

    def test_legacy_single_symbol_snapshot_also_runs_models(self):
        with model_run(), patch.dict('os.environ', {'QUANTIK_GENERATE_IMAGES': 'false'}):
            report, _, bars = engine.quant_from_snapshot(
                'ABW', engine.bars_from_frame(prices()), engine.bars_from_frame(prices(1000000)),
                'UPCOM', lambda *args: None, Path('/tmp'), include_backtest=True)
        self.assertEqual(report['analysis_status'], 'completed')
        self.assertIs(report['liquidity']['pass'], False)
        self.assertTrue(report['stats'])
        self.assertTrue(report['include_backtest'])
        self.assertEqual(len(bars), 180)

    def test_live_worker_succeeds_and_keeps_requested_backtest(self):
        raw = prices().rename_axis('time').reset_index()
        raw[['open', 'high', 'low', 'close']] /= 1000  # Provider quotes use thousand VND.
        provider = Mock()
        provider.get_ohlcv.return_value = raw
        provider.get_index_data.return_value = raw
        provider.get_stock_list.side_effect = lambda exchange: ['ABW'] if exchange == 'UPCOM' else []
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            stack.enter_context(patch.object(store, 'DB_PATH', Path(directory) / 'test.sqlite'))
            stack.enter_context(patch.object(worker, 'ARTIFACT_ROOT', Path(directory) / 'artifacts'))
            stack.enter_context(patch.dict('os.environ', {'QUANTIK_GENERATE_IMAGES': 'false'}))
            stack.enter_context(patch.object(DataProvider, '__new__', return_value=provider))
            stack.enter_context(model_run())
            backtest = stack.enter_context(patch.object(worker, 'recommendation_backtest',
                return_value={'status': 'insufficient_history', 'reason': 'Chưa đủ lịch sử tín hiệu.'}))
            store.init_db()
            job = store.new_job('quant', None, 'ABW', {'data_source_mode': 'crawl_data_live',
                                                      'include_backtest': True})
            self.assertTrue(worker.process_one())
            with store.connect() as db:
                saved = db.execute('SELECT status, report_json, error FROM jobs WHERE id=?',
                                   (job['id'],)).fetchone()
            self.assertEqual(saved['status'], 'succeeded', saved['error'])
            self.assertIsNone(saved['error'])
            report = store.loads(saved['report_json'], {})
            self.assertEqual(report['analysis_status'], 'completed')
            self.assertIs(report['liquidity']['pass'], False)
            self.assertTrue(report['stats'])
            backtest.assert_called_once()
            self.assertEqual(backtest.call_args.args[0], 'ABW')
            self.assertEqual(len(backtest.call_args.args[1]), 180)


if __name__ == '__main__':
    unittest.main()
