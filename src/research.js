import fixture from '../shared/research-demo.json';

// Only the explicitly requested demo uses fixture data. Live missing panels stay missing.
export function demoResearch(symbol,priceVnd){
 const research=structuredClone(fixture);research.symbol=symbol;
 if(!Number.isFinite(priceVnd)||priceVnd<=0){research.cone=[];research.regime=[];return research;}
 research.cone=research.cone.map(p=>({...p,...Object.fromEntries(['p05','p25','p50','p75','p95'].map(k=>[k,p[k]*priceVnd]))}));
 research.regime=research.regime.map(p=>({...p,price:p.price*priceVnd}));
 return research;
}
export function normalizeResearch(value,symbol){
 if(!value||value.schemaVersion!==1||value.symbol!==symbol||value.units?.price!=='VND'||value.units?.return!=='pct')return null;
 const finite=Number.isFinite,points=(key,valid)=>Array.isArray(value[key])&&value[key].length<=2000?value[key].filter(valid):[];
 const cone=points('cone',p=>p&&finite(p.session)&&p.session>=0&&['p05','p25','p50','p75','p95'].every(k=>finite(p[k])&&p[k]>0)&&p.p05<=p.p25&&p.p25<=p.p50&&p.p50<=p.p75&&p.p75<=p.p95).sort((a,b)=>a.session-b.session);
 return {...value,cone,
  distribution:points('distribution',p=>p&&finite(p.returnPct)&&finite(p.probabilityPct)&&p.probabilityPct>=0&&p.probabilityPct<=100),
  regime:points('regime',p=>p&&typeof p.date==='string'&&finite(p.price)&&p.price>0&&['bull','bear','sideways'].every(k=>finite(p.probabilities?.[k])&&p.probabilities[k]>=0&&p.probabilities[k]<=1)&&Math.abs(Object.values(p.probabilities).reduce((a,b)=>a+b,0)-1)<.001),
  drawdown:points('drawdown',p=>p&&typeof p.date==='string'&&finite(p.valuePct)&&p.valuePct<=0&&p.valuePct>=-100),
  factors:points('factors',p=>p&&typeof p.id==='string'&&typeof p.label==='string'&&finite(p.value)&&finite(p.min)&&finite(p.max)&&p.max>p.min&&p.value>=p.min&&p.value<=p.max),
  riskMetrics:points('riskMetrics',p=>p&&typeof p.id==='string'&&typeof p.label==='string'&&finite(p.value)&&typeof p.unit==='string')};
}
export function payoff(entry,stop,target){
 if(![entry,stop,target].every(Number.isFinite)||stop<=0||!(stop<entry&&entry<target))return null;
 return {upsidePct:100*(target/entry-1),downsidePct:100*(stop/entry-1),rr:(target-entry)/(entry-stop)};
}
