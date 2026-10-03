// node podcast/rendu.mjs [instants...]   sans instants : rendu complet, 4 navigateurs en parallèle
import { chromium } from 'playwright-core'; import fs from 'fs'; import path from 'path';
const dir=path.dirname(new URL(import.meta.url).pathname), FPS=30;
const V=process.env.V||'';
const instants=process.argv.slice(2).map(Number);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--force-color-profile=srgb','--font-render-hinting=none','--allow-file-access-from-files']});
const erreurs=[];
async function page(){const pg=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
 pg.on('console',m=>{if(m.type()!=='log')erreurs.push(m.text())}); pg.on('pageerror',e=>erreurs.push(String(e)));
 await pg.goto('file://'+path.join(dir,`page${V}.html`)); await pg.waitForFunction(()=>window.PRET===true); return pg}
async function image(pg,t,fichier,q=92){
 await pg.evaluate(t=>render(t),t);
 await pg.waitForFunction(()=>{const c=document.getElementById('cam');return c.style.display==='none'||(c.complete&&c.naturalWidth>0)});
 await pg.screenshot({path:fichier,type:'jpeg',quality:q});
}
if(instants.length){
 const pg=await page(); fs.mkdirSync(path.join(dir,'planche'),{recursive:true});
 for(let i=0;i<instants.length;i++)await image(pg,instants[i],path.join(dir,'planche',`p${String(i).padStart(2,'0')}.jpg`),88);
}else{
 const out=path.join(dir,'images'+V); fs.rmSync(out,{recursive:true,force:true}); fs.mkdirSync(out);
 const pg0=await page(); const n=Math.round(FPS*await pg0.evaluate(()=>window.DUREE)); await pg0.close();
 const W=4; let fait=0;
 await Promise.all([...Array(W)].map(async(_,w)=>{const pg=await page();
  for(let f=w;f<n;f+=W){await image(pg,f/FPS,`${out}/f${String(f).padStart(5,'0')}.jpg`);if(++fait%300===0)console.log(fait,'/',n)}}));
 console.log(n,'images');
}
if(erreurs.length)console.log('AVERTISSEMENTS:',[...new Set(erreurs)].join('\n'));
await b.close();
