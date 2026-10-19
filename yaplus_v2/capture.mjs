import { chromium } from '/home/user/Montage-vid-o-/node_modules/playwright-core/index.mjs';
const out = process.argv[2], scheme = process.argv[3] || 'dark';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, colorScheme: scheme, isMobile: true, hasTouch: true, locale: 'fr-FR' });
await ctx.addInitScript(() => { const s = document.createElement('style'); s.textContent = 'nextjs-portal{display:none!important}'; document.addEventListener('DOMContentLoaded', () => document.head.appendChild(s)); });
const p = await ctx.newPage();
const base = 'http://localhost:3100';
const shot = async (n, w = 900) => { await p.waitForTimeout(w); await p.screenshot({ path: `${out}/${scheme}-${n}.png` }); };
await p.goto(base + '/?demo=1', { waitUntil: 'networkidle', timeout: 180000 }); await p.waitForTimeout(5000);
await p.goto(base + '/', { waitUntil: 'networkidle' }); await shot('accueil', 2000);
await p.click('a:has-text("Plomberie")'); await p.waitForURL(/categorie/); await shot('cat-avant', 5000);
const bx = async () => { const e = await p.$('button:has-text("Tuyau PVC 40")'); return e ? await e.boundingBox() : null; };
console.log('tuyau', JSON.stringify(await bx()));
await p.click('button:has-text("Tuyau PVC 40")'); await shot('cat-apres', 700);
await shot('cat-apres-fin', 3500);
await p.goto(base + '/a-racheter', { waitUntil: 'networkidle' }); await shot('racheter', 3000);
const cb = await p.$$eval('[role=checkbox], button[aria-pressed], input[type=checkbox]', es => es.map(e => { const r = e.getBoundingClientRect(); return [e.tagName, e.getAttribute('aria-label'), r.x, r.y, r.width]; }));
console.log(JSON.stringify(cb));
await p.locator('button:visible', { hasText: 'Envoyer' }).first().click(); await shot('envoyer', 1500);
await p.keyboard.press('Escape'); await p.goto(base + '/a-racheter', { waitUntil: 'networkidle' }); await p.waitForTimeout(2000);
const first = p.locator('[role=checkbox]:visible, input[type=checkbox]:visible').first();
if (await first.count()) { await first.click(); await shot('coche1', 900); }
const second = p.locator('[role=checkbox]:visible, input[type=checkbox]:visible').nth(1);
if (await second.count()) { await second.click(); await shot('coche2', 900); }
const third = p.locator('[role=checkbox]:visible, input[type=checkbox]:visible').nth(2);
if (await third.count()) { await third.click(); await shot('coche3', 900); }
await p.goto(base + '/historique', { waitUntil: 'networkidle' }); await shot('historique', 2000);
await b.close();
