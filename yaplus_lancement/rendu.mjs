// rendu.mjs <sortie> [instants...] : sans instants, toutes les images (30 i/s) ; avec, des captures isolées
import { chromium } from '/home/user/Montage-vid-o-/node_modules/playwright-core/index.mjs';
import fs from 'fs'; import path from 'path';
const [out, ...inst] = process.argv.slice(2);
const FPS = 30, DUREE = 57.9, N = 6;
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
const url = 'file://' + path.resolve('lancement.html');
const temps = inst.length ? inst.map(Number) : [...Array(Math.round((process.env.FIN || DUREE) * FPS)).keys()].map(i => i / FPS);
async function travail(k) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto(url); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => {}))));
  for (let i = k; i < temps.length; i += N) {
    await p.evaluate(t => window.render(t), temps[i]);
    const nom = inst.length ? `c${String(i).padStart(2, '0')}.jpg` : `${String(i).padStart(5, '0')}.jpg`;
    await p.screenshot({ path: `${out}/${nom}`, type: 'jpeg', quality: 92 });
  }
}
await Promise.all([...Array(N).keys()].map(travail));
await b.close();
