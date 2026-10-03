// exporte les instants visuels (temps forts, mots-clés, frappe du code) pour caler les bruitages
import { chromium } from 'playwright-core'; import fs from 'fs'; import path from 'path';
const V=process.env.V||'';
const dir=path.dirname(new URL(import.meta.url).pathname);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--allow-file-access-from-files']});
const pg=await b.newPage(); await pg.goto('file://'+path.join(dir,`page${V}.html`)); await pg.waitForFunction(()=>window.PRET);
const ev=await pg.evaluate(()=>SEGS.map(s=>({type:s.type,t0:s.t0,t1:s.t1,tv:s.tv,accroche:!!s.accroche,q:s.q,
  beats:(s.beats||[]).map(b=>({t:b.t,n:b.co?b.co.length:0,vit:b.co?Math.max(b.co.length/.7,45):0})),
  pops:(s.pops||[]).map(p=>({t:p.t,cl:p.cl,ic:p.ic})),
  clips:(s.clips||[]).map(c=>c.t0)})));
fs.writeFileSync(path.join(dir,`evenements${V}.json`),JSON.stringify(ev)); console.log(ev.length,'segments'); await b.close();
