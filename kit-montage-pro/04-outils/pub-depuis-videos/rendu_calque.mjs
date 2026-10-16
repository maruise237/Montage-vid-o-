// rendu_calque.mjs <dossier> [instants...]
// sans instants : toutes les images du calque (PNG transparents) dans <dossier>/images, 4 pages en parallèle
// avec instants : <dossier>/planche/cNN.png pour la planche contact
import { chromium } from 'playwright-core';
import fs from 'fs'; import path from 'path';
const FPS = 30, dir = process.argv[2];
const url = 'file://' + path.resolve(dir, 'calque.html');
const instants = process.argv.slice(3).map(Number);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none'] });
async function page() {
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await pg.goto(url);
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForFunction(() => window.PRET === true);
  return pg;
}
const shot = (pg, t, f) => pg.evaluate(t => render(t), t).then(() => pg.screenshot({ path: f, omitBackground: true }));
if (instants.length) {
  const out = path.join(dir, 'planche'); fs.mkdirSync(out, { recursive: true });
  const pg = await page();
  for (let i = 0; i < instants.length; i++) await shot(pg, instants[i], path.join(out, `c${String(i).padStart(2, '0')}.png`));
} else {
  const out = path.join(dir, 'images'); fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
  const pg0 = await page(); const DUREE = await pg0.evaluate(() => window.DUREE);
  const n = Math.round(FPS * DUREE), K = 4;
  const pages = [pg0, ...(await Promise.all([...Array(K - 1)].map(page)))];
  let fait = 0;
  await Promise.all(pages.map(async (pg, k) => {
    for (let f = k; f < n; f += K) {
      await shot(pg, f / FPS, `${out}/f${String(f).padStart(5, '0')}.png`);
      if (++fait % 300 === 0) process.stdout.write(fait + ' ');
    }
  }));
  console.log('\n' + n + ' images');
}
await b.close();
