// Rend index.html image par image (1080x1920, 30 fps) puis assemble avec l'audio
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const FPS = 30, DUR = 36;
(async () => {
  const only = process.argv[2] ? process.argv.slice(2).map(Number) : null; // temps en s pour test
  const out = path.join(__dirname, 'build/frames'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.join(__dirname, 'index.html'));
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForFunction(() => [...document.images].every(i => i.complete));
  if (only) { for (const t of only) { await pg.evaluate(t => render(t), t); await pg.screenshot({ path: `build/test_${t}.png` }); } }
  else for (let f = 0; f < FPS * DUR; f++) {
    await pg.evaluate(t => render(t), f / FPS);
    await pg.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
    if (f % 90 === 0) console.log('frame', f);
  }
  await b.close();
})();
