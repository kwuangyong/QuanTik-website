import {test,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createServer} from 'vite';
import katex from 'katex';
const server=await createServer({server:{middlewareMode:true},appType:'custom'});
const {glossary}=await server.ssrLoadModule('/src/content/glossary.js');
const {normalizeSnapshot,sectorSummary,fmt,priceClass,change}=await server.ssrLoadModule('/src/market.js');
after(()=>server.close());
test('missing values and true zero stay distinct; price colors include limits',()=>{
 assert.equal(fmt(null),'—');assert.equal(fmt(0),'0.00');assert.equal(change({price:null,ref:1}),null);
 const r={ref:100,ceil:107,floor:93};assert.equal(priceClass(107,r),'ceil');assert.equal(priceClass(93,r),'floor');assert.equal(priceClass(100,r),'ref');
});
test('legacy adapter converts thousand VND and does not infer live status',()=>{
 const s=normalizeSnapshot([{sym:'FPT',price:100,ref:99,spark:[99,100]}]);
 assert.equal(s.quotes[0].price,100000);assert.equal(s.mode,'unknown');assert.equal(s.quotes[0].value,undefined);
 assert.throws(()=>normalizeSnapshot({quotes:[],units:{price:'USD'}}));
});
test('sector averages use valid subset and disclose liquidity coverage',()=>{
 const [g]=sectorSummary([{sectorId:'banks',ref:100,price:110,value:0,score:80},{sectorId:'banks',ref:100,price:90,value:200,score:60},{sectorId:'banks',ref:0,price:120,value:null}]);
 assert.equal(g.count,3);assert.equal(g.valid,2);assert(Math.abs(g.mean)<1e-12);assert.equal(g.value,200);assert.equal(g.valueCoverage,2);assert.equal(g.score,70);
 assert.equal(sectorSummary([{price:100,ref:100}])[0].id,'unknown');
});
test('all 21 spreadsheet metrics retain provenance and valid LaTeX',async()=>{
 const terms=JSON.parse(await readFile('src/content/metrics.json','utf8'));assert.equal(terms.length,21);assert.equal(new Set(terms.map(x=>x.id)).size,21);
 for(const t of glossary)assert.doesNotThrow(()=>katex.renderToString(t.formulaLatex,{throwOnError:true,trust:false}));
 for(const t of terms){assert(t.source.row>0);assert.doesNotThrow(()=>katex.renderToString(t.formulaLatex,{throwOnError:true,trust:false}));}
});

const {tokenizeTerms}=await server.ssrLoadModule('/src/content/term-aliases.js');
const {normalizeScan,demoScan,filterScan}=await server.ssrLoadModule('/src/scan.js');
test('scan contract rejects malformed or duplicate results, preserves nulls and timestamps',()=>{
 const sample=demoScan();assert.equal(sample.mode,'demo');assert.equal(sample.rows.length,21);
 const time=sample.publishedAt;const empty={...sample,rows:[],universeCount:0};assert.equal(normalizeScan(empty).rows.length,0);
 for(const bad of [{...sample,universeCount:0},{...sample,publishedAt:'not a date'},{...sample,rows:[sample.rows[0],sample.rows[0]]},{...sample,rows:[{...sample.rows[0],passed:'false'}]},{...sample,rows:[{...sample.rows[0],score:101}]}])assert.throws(()=>normalizeScan(bad));
 assert.equal(normalizeScan(sample).publishedAt,time);assert.equal(sample.rows[0].passed,null);
});
test('scan filters distinguish failed from unknown and retain zero in both score orders',()=>{
 const rows=[{symbol:'HPG',name:'Hòa Phát',exchange:'HOSE',recommendation:'Theo dõi',passed:false,score:0},{symbol:'FPT',name:'FPT',exchange:'HOSE',recommendation:'Đạt',passed:true,score:70},{symbol:'SHS',name:'SHS',exchange:'HNX',passed:null,score:null}];
 assert.deepEqual(filterScan(rows,{query:'hoa phat'}).map(r=>r.symbol),['HPG']);
 assert.deepEqual(filterScan(rows,{passed:'no'}).map(r=>r.symbol),['HPG']);
 assert.deepEqual(filterScan(rows,{passed:'unknown'}).map(r=>r.symbol),['SHS']);
 assert.deepEqual(filterScan(rows,{direction:'asc'}).map(r=>r.symbol),['HPG','FPT','SHS']);
 assert.deepEqual(filterScan(rows,{direction:'desc'}).map(r=>r.symbol),['FPT','HPG','SHS']);
 assert.equal(filterScan(rows,{exchange:'HNX',recommendation:'Theo dõi'}).length,0);
});
test('inline annotations preserve report text and match complete terms',()=>{
 const text='HMM BULL 100% · Sharpe 1.33 · CVaR 3% · Quant Factors · SHARPEX · AnnRet 21.9%';
 const parts=tokenizeTerms(text);
 assert.equal(parts.map(p=>p.text).join(''),text);
 assert.deepEqual(parts.filter(p=>p.id).map(p=>p.id),['hmm','sharpe','cvar','quant_factor','annual_return']);
 assert.equal(tokenizeTerms('Probability Loss >3%')[0].id,'probability_loss');
 assert.equal(tokenizeTerms('hmm')[0].id,'hmm');
});
