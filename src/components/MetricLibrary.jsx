import { useState } from 'react';
import { glossary, metricDefinitions } from '../content/glossary.js';
import TermHint from './TermHint.jsx';
export default function MetricLibrary({ all=false, metrics=[] }) {
 const [q,setQ]=useState('');
 const terms=(all?glossary:metricDefinitions).filter(t=>`${t.en} ${t.vi}`.toLocaleLowerCase('vi').includes(q.toLocaleLowerCase('vi')));
 const groups=[...new Set(terms.map(t=>t.group))];
 return <section className="metric-library"><div className="library-heading"><h3>{all?'Tra cứu chỉ báo & thuật ngữ':'21 chỉ số định lượng'}</h3><input aria-label="Tìm chỉ số" placeholder="Sharpe, RSI, VaR…" value={q} onChange={e=>setQ(e.target.value)}/></div><p className="dim library-note">Rê chuột xem ý nghĩa và công thức · Bấm để đọc chi tiết. Công thức tham khảo từ tài liệu; số thực chỉ xuất hiện khi pipeline cung cấp.</p>{groups.map(group=><div className="metric-group" key={group}><h4>{group}</h4><div className="metric-list">{terms.filter(t=>t.group===group).map(t=>{const m=metrics.find(x=>x.id===t.id);return <div key={t.id} className="metric-item"><TermHint id={t.id} parameters={m?.parameters} methodId={m?.methodId}/><span>{m?.value==null?'—':`${Number(m.value).toLocaleString('vi-VN',{maximumFractionDigits:3})}${m.unit||''}`}</span></div>;})}</div></div>)}{!terms.length&&<p className="empty">Không tìm thấy chỉ số.</p>}</section>;
}
