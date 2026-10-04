"""QuanTik demo API. Run: python -m uvicorn server:app --port 8000 (in backend/)."""
from __future__ import annotations
import copy, datetime as dt, hashlib, json, threading, time, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import adapters

OUT = Path(__file__).parent / 'out'
OUT.mkdir(exist_ok=True)
app = FastAPI(title='QuanTik API')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_methods=['GET','POST'], allow_headers=['Content-Type'])
JOBS: dict[str,dict] = {}
POOL = ThreadPoolExecutor(max_workers=2)
LOCK = threading.Lock()
CACHE_LOCKS: dict[str,threading.Lock] = {}
NAMES = {m['id']:m for m in adapters.MODULES}

class JobRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=5)
    modules: list[str] | None = None

@app.get('/api/board')
def board(group: str = 'ALL', exchange: str | None = None, sector: str | None = None):
    return adapters.load_board(group,exchange,sector)

@app.get('/api/instruments')
def instruments():
    return {'mode':adapters.MODE,'classification':adapters.SAMPLE['classification'],'instruments':adapters.SAMPLE['instruments']}

@app.get('/api/sectors')
def sectors():
    return {'mode':adapters.MODE,'classification':adapters.SAMPLE['classification'],'sectors':adapters.SAMPLE['sectors']}

@app.get('/api/sectors/summary')
def sector_summary(exchange: str | None = None, sector: str | None = None):
    return {'asOf':adapters.SAMPLE['asOf'],'mode':adapters.MODE,'method':'equal-weight-return','sectors':adapters.sector_summary(exchange,sector)}

@app.get('/api/quant/modules')
def modules():
    return adapters.MODULES

@app.post('/api/quant/jobs')
def create_job(req: JobRequest):
    sym=req.symbol.strip().upper()
    if sym not in {i['symbol'] for i in adapters.SAMPLE['instruments']}:
        raise HTTPException(400,'Mã chưa có trong danh mục dữ liệu')
    if req.modules == []:
        raise HTTPException(400,'Chọn ít nhất một module')
    unknown=set(req.modules or [])-NAMES.keys()
    if unknown:
        raise HTTPException(400,f'Module không tồn tại: {sorted(unknown)}')
    ids=[m['id'] for m in adapters.MODULES if req.modules is None or m['id'] in req.modules]
    key=hashlib.sha256(json.dumps([sym,ids,adapters.DATA_VERSION,adapters.MODEL_VERSION,'D']).encode()).hexdigest()
    job_id=uuid.uuid4().hex
    job={'id':job_id,'symbol':sym,'status':'queued','error':None,'summary':None,'metrics':[],
         'mode':adapters.MODE,'asOf':adapters.SAMPLE['asOf'],'dataVersion':adapters.DATA_VERSION,
         'modelVersion':adapters.MODEL_VERSION,'timeframe':'D','units':{'price':'thousand-VND'},
         'modules':[{'id':i,'name':NAMES[i]['name'],'state':'wait','sec':None} for i in ids]}
    with LOCK:
        JOBS[job_id]=job
        cache_lock=CACHE_LOCKS.setdefault(key,threading.Lock())
    POOL.submit(run_job,job_id,key,cache_lock)
    return {'id':job_id}

def run_job(job_id: str, key: str, cache_lock):
    job=JOBS[job_id]
    png=OUT/f'{key}.png'
    cache=OUT/f'{key}.json'
    try:
        with cache_lock:
            job['status']='running'
            cached=None
            if cache.exists() and png.exists():
                try:
                    cached=json.loads(cache.read_text())
                    if not {'summary','metrics'} <= cached.keys(): cached=None
                except (ValueError,OSError): cached=None
            if cached is None:
                ctx=adapters.load_context(job['symbol'])
                for m in job['modules']:
                    m['state']='running';t=time.perf_counter()
                    ctx=adapters.run_module(m['id'],ctx)
                    m['sec']=round(time.perf_counter()-t,1);m['state']='done'
                adapters.render_image(ctx,png)
                payload={'summary':adapters.summarize(ctx),'metrics':adapters.metric_results(ctx)}
                tmp=cache.with_suffix('.tmp')
                tmp.write_text(json.dumps(payload,ensure_ascii=False));tmp.replace(cache)
            else:
                payload=cached
                for m in job['modules']:m.update(state='done',sec=0)
            with LOCK:
                job.update(summary=payload['summary'],metrics=payload['metrics'],png=str(png),cached=cached is not None,status='done')
    except Exception as e:
        with LOCK:job.update(status='error',error=f'{type(e).__name__}: {e}')

@app.get('/api/quant/jobs/{job_id}')
def get_job(job_id: str):
    with LOCK:
        job=JOBS.get(job_id)
        if not job:raise HTTPException(404,'Không thấy job')
        return copy.deepcopy({k:v for k,v in job.items() if k!='png'})

@app.get('/api/quant/jobs/{job_id}/image')
def job_image(job_id: str):
    with LOCK:job=JOBS.get(job_id)
    if not job or job['status']!='done' or not job.get('png'):
        raise HTTPException(404,'Chưa có ảnh')
    return FileResponse(job['png'],media_type='image/png')
