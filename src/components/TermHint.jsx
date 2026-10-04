import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { getTerm } from '../content/glossary.js';

export function Formula({ latex }) {
  const html=useMemo(()=>katex.renderToString(latex || String.raw`\text{Chưa xác định}`,{throwOnError:false,trust:false,displayMode:true,output:'htmlAndMathml'}),[latex]);
  return <div className="formula" dangerouslySetInnerHTML={{__html:html}}/>;
}
export default function TermHint({ id, children, parameters, methodId }) {
  const term=getTerm(id);
  const anchor=useRef(null), popup=useRef(null), timer=useRef(null);
  const [mode,setMode]=useState(null),[position,setPosition]=useState({left:12,top:12});
  const uid=useId();
  const hide=()=>{clearTimeout(timer.current);timer.current=setTimeout(()=>setMode(m=>m==='detail'?m:null),180);};
  const show=()=>{clearTimeout(timer.current);timer.current=setTimeout(()=>setMode(m=>m==='detail'?m:'hover'),250);};
  const close=()=>{clearTimeout(timer.current);setMode(null);};
  useEffect(()=>()=>clearTimeout(timer.current),[]);
  useEffect(()=>{
    if(!mode)return;
    const place=()=>{
      const r=anchor.current?.getBoundingClientRect();if(!r)return;
      const w=Math.min(mode==='detail'?480:390,window.innerWidth-24);
      const h=popup.current?.offsetHeight || 220;
      setPosition({left:Math.max(12,Math.min(r.left,window.innerWidth-w-12)),top:Math.max(12,Math.min(r.bottom+8,window.innerHeight-h-12)),width:w,maxHeight:window.innerHeight-24});
    };
    place();window.addEventListener('resize',place);document.addEventListener('scroll',place,true);
    const dismiss=e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();close();if(mode==='detail')anchor.current?.focus();}};
    const outside=e=>{if(!popup.current?.contains(e.target)&&!anchor.current?.contains(e.target))close();};
    document.addEventListener('keydown',dismiss,true);document.addEventListener('pointerdown',outside);
    if(mode==='detail')popup.current?.querySelector('button')?.focus();
    return()=>{window.removeEventListener('resize',place);document.removeEventListener('scroll',place,true);document.removeEventListener('keydown',dismiss,true);document.removeEventListener('pointerdown',outside);};
  },[mode]);
  if(!term)return <span>{children||id}</span>;
  return <><button ref={anchor} type="button" className="term-trigger" aria-describedby={mode==='hover'?uid:undefined} aria-expanded={mode==='detail'} aria-haspopup="dialog" onPointerEnter={show} onPointerLeave={hide} onFocus={show} onBlur={hide} onClick={e=>{e.stopPropagation();clearTimeout(timer.current);setMode(m=>m==='detail'?null:'detail');}}>{children||term.en}<span aria-hidden="true" className="term-mark">i</span></button>
  {mode&&createPortal(<div ref={popup} id={uid} className={`term-popover ${mode==='detail'?'term-detail':''}`} data-detail={mode==='detail'||undefined} style={position} role={mode==='detail'?'dialog':'tooltip'} aria-label={mode==='detail'?term.en:undefined} onPointerEnter={()=>clearTimeout(timer.current)} onPointerLeave={hide} onKeyDown={e=>{if(mode==='detail'&&e.key==='Tab'){const nodes=[...popup.current.querySelectorAll('button,summary,a[href]')];const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}}}>
    <div className="term-title"><strong>{term.en}</strong>{mode==='detail'&&<button className="iconbtn" aria-label="Đóng giải thích" onClick={()=>{close();anchor.current?.focus();}}>×</button>}</div><small>{term.vi}</small><p>{term.short}</p><Formula latex={term.formulaLatex}/>
    {mode==='detail'?<><dl><div><dt>Phương pháp</dt><dd>{term.methodId}</dd></div><div><dt>Tham số</dt><dd>{parameters?Object.entries(parameters).map(([k,v])=>`${k}: ${v}`).join(' · '):term.parameters}</dd></div></dl>{methodId&&methodId!==term.methodId&&<p className="term-note">Kết quả dùng {methodId}; công thức này là tài liệu {term.methodId}, cần đối chiếu phương pháp.</p>}<h4>Dữ liệu đầu vào</h4><p className="preserve-lines">{term.variables}</p><h4>Cách sử dụng</h4><p>{term.usage}</p>{term.interpretation&&<details className="reference-thresholds"><summary>Ngưỡng phân loại trong Excel (tham khảo)</summary><p className="preserve-lines">{term.interpretation}</p></details>}<h4>Ví dụ</h4><p>{term.example}</p><h4>Giới hạn</h4><p>{term.limitations}</p>{term.references?.map(r=><p key={r.url}><a href={r.url} target="_blank" rel="noopener noreferrer">{r.title} ↗</a></p>)}{term.source&&<small>Nguồn: {term.source.file} · {term.source.sheet} · dòng {term.source.row}. Ngưỡng Excel là tham khảo, cần đối chiếu mô hình.</small>}</>:<><p className="term-note">{term.limitations}</p><small>Bấm để xem cách dùng, tham số và ví dụ.</small></>}
  </div>,document.body)}</>;
}
