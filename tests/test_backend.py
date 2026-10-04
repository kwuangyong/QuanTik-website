import copy, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import adapters, server
from fastapi import HTTPException

class BackendContract(unittest.TestCase):
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
