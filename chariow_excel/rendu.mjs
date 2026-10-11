// rendu.mjs planche t1 t2 …  |  rendu.mjs seg <i0> <i1> <sortie.mp4>   (60 i/s, images envoyées à ffmpeg)
import { chromium } from 'playwright-core';
import fs from 'fs'; import path from 'path'; import { spawn } from 'child_process';
const FPS=60, ICI=path.dirname(new URL(import.meta.url).pathname);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--force-color-profile=srgb','--font-render-hinting=none','--allow-file-access-from-files']});
const pg=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
pg.on('pageerror',e=>console.error('ERREUR PAGE',e.message)); pg.on('console',m=>{if(m.type()==='error')console.error('console',m.text())});
await pg.goto('file://'+path.join(ICI,'animation.html'));
await pg.waitForFunction(()=>window.PRET===true,null,{timeout:30000});
await pg.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
const mode=process.argv[2];
if(mode==='sons'){fs.writeFileSync(path.join(ICI,'sons.json'),JSON.stringify(await pg.evaluate(()=>({sons:SONS,duree:DUREE}))));console.log('sons ok')}
else if(mode==='planche'){
  const ts=process.argv.slice(3).map(Number); fs.mkdirSync(path.join(ICI,'planche'),{recursive:true});
  for(let i=0;i<ts.length;i++){await pg.evaluate(t=>render(t),ts[i]);
    await pg.screenshot({path:path.join(ICI,'planche',`p${String(i).padStart(2,'0')}.jpg`),type:'jpeg',quality:80});}
  console.log('planche',ts.length);
}else{
  const i0=+process.argv[3], i1=+process.argv[4], out=process.argv[5];
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',String(FPS),out],{stdio:['pipe','inherit','inherit']});
  for(let f=i0;f<i1;f++){await pg.evaluate(t=>render(t),f/FPS);
    const buf=await pg.screenshot({type:'jpeg',quality:94});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if((f-i0)%300===0)process.stdout.write(`[${i0}:${f}] `);}
  ff.stdin.end(); await new Promise(r=>ff.on('close',r));
}
await b.close();
