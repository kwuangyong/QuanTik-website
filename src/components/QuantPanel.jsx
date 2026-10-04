import {useCallback,useEffect,useRef,useState} from 'react';
import {getJob,jobImageUrl,listModules,startQuant} from '../api.js';
import MetricLibrary from './MetricLibrary.jsx';
import TermHint from './TermHint.jsx';
import {demoSnapshot,fmt} from '../market.js';
function useQuantJob(){
 const [job,setJob]=useState(null),[error,setError]=useState('');const timer=useRef(null),generation=useRef(0);
 useEffect(()=>()=>{clearTimeout(timer.current);generation.current++;},[]);
 const run=useCallback(async(symbol,modules)=>{clearTimeout(timer.current);const token=++generation.current;setError('');setJob({status:'queued',modules:[]});
 try{const {id}=await startQuant(symbol,modules);if(token!==generation.current)return;
 const tick=async()=>{if(token!==generation.current)return;try{const next=await getJob(id);if(token!==generation.current)return;setJob(next);if(next.status==='error'){setError(next.error||'Pipeline báo lỗi.');return;}if(next.status!=='done')timer.current=setTimeout(tick,700);}catch{if(token===generation.current){setError('Mất kết nối khi chạy phân tích. Vui lòng thử lại.');setJob({status:'error',modules:[]});}}};await tick();
 }catch{if(token===generation.current){setError('Không kết nối được dịch vụ phân tích. Kiểm tra Python API rồi thử lại.');setJob({status:'error',modules:[]});}}},[]);
 const preview=useCallback(symbol=>{clearTimeout(timer.current);generation.current++;setError('');const r=demoSnapshot.quotes.find(x=>x.symbol===symbol);setJob({status:'done',mode:'demo',local:true,asOf:demoSnapshot.asOf,modules:[],summary:r?{score:r.score,action:'Kết quả mẫu giao diện',entry:r.price/1000,stop:r.price*.95/1000,tp1:r.price*1.1/1000,tp2:r.price*1.15/1000,net_r:2,atr_pct:null}:null,metrics:[]});},[]);
 return {job,error,run,preview};
}
export default function QuantPanel({sym,autoRun=false}){
 const [mods,setMods]=useState([]),[failed,setFailed]=useState(false),[selected,setSelected]=useState([]),[imageError,setImageError]=useState(false);
 const {job,error,run,preview}=useQuantJob();
 useEffect(()=>{let alive=true;listModules().then(m=>{if(alive){setMods(m);setSelected(m.map(x=>x.id));}}).catch(()=>{if(alive)setFailed(true);});return()=>{alive=false;};},[]);
 useEffect(()=>{if(autoRun)run(sym,null);},[sym,autoRun,run]);
 useEffect(()=>setImageError(false),[job?.id]);
 const running=job?.status==='queued'||job?.status==='running',s=job?.summary;
 return <><section className="card quant-controls"><h3>Chọn module cần chạy cho {sym}</h3><p className="dim">Theo ngày · Rê vào tên chỉ số để xem công thức.</p>{failed&&<p role="status" className="err">Chưa kết nối được dịch vụ phân tích. Bạn có thể xem bản mẫu giao diện.</p>}<details className="module-picker" open={!job}><summary>{selected.length}/{mods.length} module được chọn</summary><div className="mods">{mods.map(m=><label className="mod" key={m.id}><input type="checkbox" disabled={running} checked={selected.includes(m.id)} onChange={e=>setSelected(a=>e.target.checked?[...a,m.id]:a.filter(id=>id!==m.id))}/><span><b>{m.name}</b><small>{m.desc}</small></span></label>)}</div></details><div className="quant-actions"><button className="btn" disabled={running||!selected.length} onClick={()=>run(sym,selected)}>{running?'Đang phân tích…':`Chạy phân tích ${sym}`}</button><button className="btn ghost" disabled={running} onClick={()=>preview(sym)}>Xem kết quả mẫu</button></div></section>
 {running&&<section className="card" role="status"><h3>Đang chạy {sym}</h3>{(job.modules||[]).map(m=><div className={`mod ${m.state}`} key={m.id}><b>{m.name}</b><span className="st">{m.state==='done'?`✓ ${m.sec}s`:m.state==='running'?'Đang chạy':'Chờ'}</span></div>)}</section>}
 {job?.status==='error'&&<section className="card"><p role="alert" className="err">{error}</p><button className="btn ghost" onClick={()=>run(sym,selected.length?selected:null)}>Thử lại</button></section>}
 {job?.status==='done'&&<><div className="info-banner">{job.mode==='demo'?'Kết quả mô phỏng':job.mode==='live'||job.mode==='eod'?'Kết quả từ API':'Nguồn mô hình chưa xác nhận'} · {job.asOf?new Date(job.asOf).toLocaleString('vi-VN'):'Chưa có thời điểm dữ liệu'}{job.local&&' · Mẫu tĩnh, không chạy mô hình'}</div>{s&&<div className="keyrow">{[['quant_score','Điểm Quant',s.score,' / 100'],[null,'Kết luận',s.action,''],['entry','Điểm vào',fmt(s.entry),' nghìn ₫'],['stop_loss','Cắt lỗ',fmt(s.stop),' nghìn ₫'],['take_profit','Mục tiêu 1',fmt(s.tp1),' nghìn ₫'],['take_profit','Mục tiêu 2',fmt(s.tp2),' nghìn ₫'],['risk_reward','Lợi nhuận/rủi ro',fmt(s.net_r),'x'],['atr','ATR / Giá',fmt(s.atr_pct),'%']].map(([id,label,value,unit])=><div key={label}><small>{id?<TermHint id={id}>{label}</TermHint>:label}</small><b>{value==null?'—':`${value}${unit}`}</b></div>)}</div>}{!job.local&&job.id&&!imageError&&<img className="qimg" src={jobImageUrl(job.id)} onError={()=>setImageError(true)} alt={`Ảnh tổng quan phân tích ${sym}`}/>} {imageError&&<p className="err">Ảnh tổng quan chưa tải được; kết quả dạng bảng vẫn có thể xem.</p>}</>}
 <MetricLibrary metrics={job?.metrics||[]}/></>;
}
