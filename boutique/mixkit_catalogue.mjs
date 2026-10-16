import { chromium } from 'playwright-core';
import fs from 'fs';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox','--disable-blink-features=AutomationControlled'] });
const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' });
const pg = await ctx.newPage();
const out = {};
for (const u of process.argv.slice(3)) {
  try {
    await pg.goto(u, { waitUntil: 'domcontentloaded', timeout: 45000 });
    for (let i = 0; i < 12; i++) { if (!(await pg.title()).includes('moment')) break; await pg.waitForTimeout(2500); }
    await pg.waitForTimeout(1200);
    out[u] = await pg.evaluate(() => {
      const r = [];
      document.querySelectorAll('[data-audio-player-preview-url-value], [data-audio-player-url-value]').forEach(e => {
        const url = e.getAttribute('data-audio-player-preview-url-value') || e.getAttribute('data-audio-player-url-value');
        const card = e.closest('.item-grid-card, [class*=item-grid], article, li, div');
        let titre = '';
        let c = e; for (let k = 0; k < 6 && c; k++) { const h = c.querySelector && c.querySelector('h2, h3, .item-grid-card__title'); if (h) { titre = h.innerText; break; } c = c.parentElement; }
        let dur = ''; c = e; for (let k = 0; k < 6 && c; k++) { const m = (c.innerText || '').match(/\d+:\d\d/); if (m) { dur = m[0]; break; } c = c.parentElement; }
        r.push({ titre, url, dur });
      });
      return r;
    });
    console.log(u, out[u].length);
  } catch (e) { console.log('ERR', u, e.message.slice(0, 100)); }
}
fs.writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
await b.close();
