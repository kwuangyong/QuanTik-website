import copy, sys, tempfile, time, unittest, json, os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import adapters, server
from fastapi import HTTPException
from fastapi import Response
import scan_snapshot

class BackendContract(unittest.TestCase):
    def test_scan_reads_existing_file_without_starting_engine(self):
        data=json.loads(scan_snapshot.DEMO_PATH.read_text())
        data.update(mode='published',runId='scheduled-run-1')
        data['rows'][0].update(score=0,passed=False)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'latest.json';path.write_text(json.dumps(data))
            with patch.dict(os.environ,{'QUANTIK_SCAN_SNAPSHOT':str(path)}),patch.object(adapters,'run_module',side_effect=AssertionError('engine must not run')),patch.object(server.POOL,'submit',side_effect=AssertionError('job must not start')):
                response=Response();first=server.latest_scan(response)
                self.assertEqual(first['runId'],'scheduled-run-1');self.assertTrue(first['isStale'])
                self.assertEqual(first['publishedAt'],data['publishedAt'])
                self.assertEqual(first['rows'][0]['score'],0);self.assertIs(first['rows'][0]['passed'],False)
                self.assertEqual(response.headers['cache-control'],'no-store')
                data['runId']='scheduled-run-2'
                temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data));temporary.replace(path)
                self.assertEqual(server.latest_scan(Response())['runId'],'scheduled-run-2')
    def test_scan_failure_does_not_fall_back_to_demo_or_leak_path(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'missing-private-file.json'
            with patch.dict(os.environ,{'QUANTIK_SCAN_SNAPSHOT':str(path)}):
                for text in [None,'broken JSON',json.dumps({'rows':[]})]:
                    if text is not None:path.write_text(text)
                    with self.assertRaises(HTTPException) as caught:server.latest_scan(Response())
                    self.assertEqual(caught.exception.status_code,503)
                    self.assertNotIn(str(path),caught.exception.detail)
    def test_scan_validation_and_empty_publication(self):
        data=json.loads(scan_snapshot.DEMO_PATH.read_text())
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'latest.json'
            with patch.dict(os.environ,{'QUANTIK_SCAN_SNAPSHOT':str(path)}):
                bads=[{**data,'universeCount':0},{**data,'rows':[data['rows'][0],data['rows'][0]]},{**data,'rows':[{**data['rows'][0],'passed':'false'}]},{**data,'publishedAt':'2026-10-05T00:00:00'},{**data,'rows':[{**data['rows'][0],'score':True}]}]
                for bad in bads:
                    path.write_text(json.dumps(bad))
                    with self.assertRaises(HTTPException):server.latest_scan(Response())
                path.write_text(json.dumps({**data,'universeCount':0,'rows':[]}))
                self.assertEqual(server.latest_scan(Response())['rows'],[])
    def test_board_units_and_exchange(self):
        data=server.board(exchange='HNX')
        self.assertEqual(data['mode'],'demo')
        self.assertEqual(data['units']['price'],'VND')
        self.assertTrue(all(i['exchange']=='HNX' for i in data['instruments']))
        self.assertEqual({i['symbol'] for i in data['instruments']},{q['symbol'] for q in data['quotes']})
        self.assertTrue(all(q['bids'][0]['price']>=q['bids'][2]['price'] for q in data['quotes']))
        data['quotes'][0]['price']=0
        self.assertNotEqual(server.board(exchange='HNX')['quotes'][0]['price'],0)
    def test_validation(self):
        for req in [server.JobRequest(symbol='XXXXX'),server.JobRequest(symbol='FPT',modules=[]),server.JobRequest(symbol='FPT',modules=['missing'])]:
            with self.assertRaises(HTTPException):server.create_job(req)
    def test_cache_preserves_summary_and_metrics_and_versions(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(server,'OUT',Path(temp)):
            def run():
                jid=server.create_job(server.JobRequest(symbol='FPT',modules=['trend']))['id']
                deadline=time.monotonic()+15
                while time.monotonic()<deadline:
                    job=server.get_job(jid)
                    if job['status'] in {'done','error'}:break
                    time.sleep(.02)
                self.assertEqual(job['status'],'done',job.get('error'))
                return job
            a=run();b=run()
            self.assertFalse(a['cached']);self.assertTrue(b['cached'])
            self.assertEqual(a['summary'],b['summary']);self.assertEqual(a['metrics'],b['metrics']);self.assertEqual(len(b['metrics']),21)
            self.assertEqual(b['mode'],'demo');self.assertEqual(b['units']['price'],'thousand-VND')
            self.assertTrue(Path(server.job_image(b['id']).path).is_file())
            with patch.object(adapters,'MODEL_VERSION','new-version'):
                c=run();self.assertFalse(c['cached'])
    def test_sector_scope(self):
        all_groups=server.sector_summary()['sectors'];hnx=server.sector_summary(exchange='HNX')['sectors']
        self.assertGreater(sum(g['count'] for g in all_groups),sum(g['count'] for g in hnx))
        self.assertTrue(all(g['mode']=='demo' for g in hnx))

if __name__=='__main__':unittest.main()
