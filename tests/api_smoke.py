"""HTTP smoke test of the shipped API; loopback only, no live provider needed."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
with socket.socket() as listener:
    listener.bind(('127.0.0.1',0));port=listener.getsockname()[1]
cache=tempfile.TemporaryDirectory()
launcher="import sys; from pathlib import Path; import server,uvicorn; server.OUT=Path(sys.argv[1]); uvicorn.run(server.app,host='127.0.0.1',port=int(sys.argv[2]))"
process=subprocess.Popen([sys.executable,'-c',launcher,cache.name,str(port)],cwd=ROOT/'backend',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
base=f'http://127.0.0.1:{port}'
def request(path,payload=None):
    req=Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
    with urlopen(req,timeout=10) as response:return json.load(response),response.headers
try:
    for _ in range(100):
        try:board,_=request('/api/board');break
        except OSError:
            if process.poll() is not None:raise RuntimeError('API did not start')
            time.sleep(.05)
    else:raise RuntimeError('API startup timeout')
    highlights,headers=request('/api/scan/latest/highlights')
    assert headers['Cache-Control']=='no-store'
    assert len(highlights['rows'])<=10
    assert len(highlights['highlights']['opportunities'])<=5 and len(highlights['highlights']['cautions'])<=5
    assert len(set(r['symbol'] for r in highlights['rows']))==len(highlights['rows'])
    catalog,_=request('/api/instruments');assert len(catalog['instruments'])==len(board['instruments'])
    a,_=request('/api/quant/jobs',{'symbol':'FPT','modules':['trend','mc']})
    b,_=request('/api/quant/jobs',{'symbol':'FPT'});assert a['id']==b['id']
    for _ in range(200):
        job,_=request(f"/api/quant/jobs/{a['id']}")
        if job['status'] in {'done','error'}:break
        time.sleep(.05)
    assert job['status']=='done',job.get('error')
    assert job['research']['mode']=='demo' and job['research']['symbol']=='FPT'
    assert job['research']['cone'][0]['p50']==job['summary']['entry']*1000
    print('HTTP smoke passed: full catalog, read-only 5/5, duplicate POST reuse, completed structured report.')
finally:
    process.terminate()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:process.kill();process.wait()
    cache.cleanup()
