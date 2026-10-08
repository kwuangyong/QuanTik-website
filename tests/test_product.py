import copy, json, os, sys, tempfile, threading, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import adapters, server, scan_snapshot
from scan_highlights import select_highlights
from market_snapshot import load_snapshot
from fastapi import HTTPException, Response

def row(i, **kw):
    return {'symbol':f'S{i:02}','name':'Company','exchange':'HOSE','score':i,**kw}

class ProductContract(unittest.TestCase):
    def test_highlights_publish_one_run_with_50_fields_and_no_engine(self):
        data = json.loads(scan_snapshot.DEMO_PATH.read_text())
        data.update(mode='published',runId='immutable-run',rows=[row(i) for i in range(20)],universeCount=20)
        data['rows'][0].update(action='AVOID',score=82,entry_vnd=16700,net_forecast_pct=0,up_day_ratio_pct=61.2)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'latest.json';path.write_text(json.dumps(data))
            with patch.dict(os.environ,{'QUANTIK_SCAN_SNAPSHOT':str(path)}),patch.object(server.POOL,'submit',side_effect=AssertionError('must not run')):
                result=server.scan_highlights(Response())
            self.assertEqual(result['runId'],'immutable-run');self.assertEqual(result['analyzedCount'],20)
            self.assertEqual(len(result['rows']),10)
            self.assertIn('S00',result['highlights']['cautions'])
            selected=next(r for r in result['rows'] if r['symbol']=='S00')
            self.assertEqual(selected['entry_vnd'],16700);self.assertEqual(selected['net_forecast_pct'],0)
            self.assertEqual(selected['up_day_ratio_pct'],61.2);self.assertEqual(result['buyNowCount'],0)

    def test_selection_handles_ties_failed_rows_and_all_avoid(self):
        data={'runId':'one','rows':[row(i,score=80) for i in range(15)]}
        a=select_highlights(data);b=select_highlights({**data,'rows':list(reversed(data['rows']))})
        self.assertEqual(a,b);self.assertEqual(len(set(r['symbol'] for r in a['rows'])),10)
        for r in data['rows']:r['action']='TRÁNH'
        a=select_highlights(data);self.assertFalse(a['highlights']['opportunities']);self.assertEqual(len(a['rows']),5)
        data['rows'][0]['data_quality_status']='FAIL';data['rows'][1]['score']=None
        data['rows'][2]['analysis_status']='error'
        self.assertEqual(select_highlights(data)['excludedCount'],3)

    def test_scan_numeric_fields_are_not_strings_and_gates_not_scores(self):
        data=json.loads(scan_snapshot.DEMO_PATH.read_text())
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'latest.json'
            for extra in [{'net_forecast_pct':'5%'},{'entry_vnd':0},{'gate_pass':'yes'},{'sharpe':True},{'model_coverage_pct':float('inf')}]:
                payload=copy.deepcopy(data);payload['rows'][0].update(extra);path.write_text(json.dumps(payload))
                with patch.dict(os.environ,{'QUANTIK_SCAN_SNAPSHOT':str(path)}),self.assertRaises(RuntimeError):scan_snapshot.load_published_scan()

    def test_all_listing_rows_survive_without_quotes_and_no_truncation(self):
        data={'mode':'live','source':'Test provider','asOf':'2026-10-08T08:00:00Z','units':{'price':'VND'},
              'instruments':[{'symbol':f'X{i}','name':f'Company {i}','exchange':'HNX'} for i in range(1700)],
              'quotes':[{'symbol':'X2','price':0,'ref':None,'vol':0}]}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'board.json';path.write_text(json.dumps(data))
            with patch.dict(os.environ,{'QUANTIK_MARKET_SNAPSHOT':str(path)}),patch.object(scan_snapshot,'load_published_scan',side_effect=AssertionError('independent')):
                board=server.board();catalog=server.instruments()
            self.assertEqual(len(board['instruments']),1700);self.assertEqual(len(catalog['instruments']),1700)
            self.assertIsNone(board['quotes'][0]['price']);self.assertEqual(board['quotes'][0]['vol'],0)
            self.assertEqual(board['mode'],'unknown')

    def test_market_bad_config_does_not_fall_back_or_leak_path(self):
        with patch.dict(os.environ,{'QUANTIK_MARKET_SNAPSHOT':'/private/provider/missing.json'}):
            with self.assertRaises(HTTPException) as caught:server.board()
            self.assertEqual(caught.exception.status_code,503);self.assertNotIn('/private',caught.exception.detail)

    def test_duplicate_job_requests_from_both_buttons_reuse_active_job(self):
        # Keep the worker queued to make the two requests deterministic.
        with patch.object(server.POOL,'submit') as submit:
            a=server.create_job(server.JobRequest(symbol='HPG',modules=['trend']))
            b=server.create_job(server.JobRequest(symbol='HPG',modules=None))
            self.assertEqual(a['id'],b['id']);self.assertTrue(b['reused']);self.assertEqual(submit.call_count,1)
            with server.LOCK:server.JOBS[a['id']]['status']='error'

    def test_research_fixture_is_demo_and_live_missing_payload_stays_missing(self):
        ctx=adapters.load_context('FPT');r=adapters.research_payload(ctx)
        self.assertEqual(r['mode'],'demo');self.assertEqual(r['units']['price'],'VND')
        self.assertEqual(r['cone'][0]['p50'],ctx['quote']['price']);self.assertEqual(len(r['factors']),5)
        self.assertAlmostEqual(sum(b['probabilityPct'] for b in r['distribution']),100)
        for p in r['regime']:self.assertAlmostEqual(sum(p['probabilities'].values()),1)
        with patch.object(adapters,'MODE','published'):self.assertIsNone(adapters.research_payload(ctx))

if __name__=='__main__':unittest.main()
