// filmer.mjs <dist web> <sortie> [prises...] : filme les vrais écrans de l'appli KamForms (export web Expo,
// données de démo de mobile/screenshots/fixtures.mjs) par screencast CDP, image + horodatage.
import { chromium } from '/home/user/Montage-vid-o-/node_modules/playwright-core/index.mjs'
import { createServer } from 'node:http'
import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { extname, join } from 'node:path'
const KF = '/home/user/kamforms/mobile'
const data = await import(KF + '/screenshots/fixtures.mjs')
const [dist, out, ...seules] = process.argv.slice(2)
const types = { '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.ttf': 'font/ttf', '.html': 'text/html', '.json': 'application/json' }
const server = createServer(async (req, res) => {
  const path = decodeURIComponent(new URL(req.url, 'http://x').pathname)
  if (path.startsWith('/__fonts/')) return res.writeHead(200, { 'content-type': 'font/ttf' }).end(await readFile(join(KF, 'assets/fonts', path.slice(9))))
  try { const b = await readFile(join(dist, path)); res.writeHead(200, { 'content-type': types[extname(path)] ?? 'application/octet-stream' }).end(b) }
  catch { res.writeHead(200, { 'content-type': 'text/html' }).end(await readFile(join(dist, 'index.html'))) }
}).listen(0)
const base = `http://localhost:${server.address().port}`
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' })
const IA = Number(process.env.IA ?? 2600)
function api(route) {
  const url = new URL(route.request().url()), p = url.pathname, method = route.request().method()
  const cors = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*' }
  if (method === 'OPTIONS') return route.fulfill({ status: 204, headers: cors })
  const json = body => route.fulfill({ status: 200, headers: cors, contentType: 'application/json', body: JSON.stringify(body) })
  if (p.startsWith('/api/uploads/')) return route.fulfill({ status: 200, headers: cors, contentType: 'image/jpeg', body: data.bannerJpeg() })
  if (p === '/api/forms' && method === 'GET') return json(data.forms)
  if (p === '/api/forms' && method === 'POST') return json({ id: 'f9', slug: 'commande-boutique' })
  if (p === '/api/generate') return new Promise(r => setTimeout(r, IA)).then(() => json(data.generated))
  if (/^\/api\/forms\/[^/]+\/analytics$/.test(p)) return json(data.analytics)
  if (/^\/api\/forms\/[^/]+\/submissions$/.test(p)) return json({ submissions: data.submissions, total: 48, page: 1, limit: 20 })
  if (/^\/api\/forms\/[^/]+$/.test(p)) return json(data.formDetail)
  if (p === '/api/submissions') return json({ submissions: data.inbox, nextCursor: null })
  if (/^\/api\/submissions\/[^/]+$/.test(p)) return json({ ...data.submissions[0], form: { title: data.formDetail.title, schema: data.formDetail.schema } })
  if (p === '/api/templates') return json({ templates: data.templates })
  if (p === '/api/dashboard') return json(data.homeStats)
  if (p === '/api/user') return json(data.user)
  if (p === '/api/billing/usage') return json(data.billing)
  return json({})
}
const tap = (p, t) => p.getByText(t, { exact: true }).first().click()
const glisse = async (p, dy, n = 14) => { await p.mouse.move(195, 500); for (let k = 0; k < n; k++) { await p.mouse.wheel(0, dy / n); await p.waitForTimeout(60) } }

async function prise(nom, { path = '/', signedIn = true, intro = true, act }) {
  if (seules.length && !seules.includes(nom)) return
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, locale: 'fr-FR' })
  await ctx.addInitScript(({ signedIn, intro }) => {
    globalThis.__KF_SIGNED_IN = signedIn
    if (intro) localStorage.setItem('kamforms:intro-seen', '1')
    localStorage.setItem('kamforms:onboarding-done', '1')
    const css = [...[[500, 'Medium'], [600, 'SemiBold'], [700, 'Bold']].map(([w, n]) => ['Newsreader', w, `Newsreader-${n}`]),
      ...[[400, 'Regular'], [500, 'Medium'], [600, 'SemiBold'], [700, 'Bold']].map(([w, n]) => ['HankenGrotesk', w, `HankenGrotesk-${n}`])]
      .map(([f, w, file]) => `@font-face{font-family:${f};font-weight:${w};src:url(/__fonts/${file}.ttf)}`).join('')
    document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s) })
  }, { signedIn, intro })
  await ctx.route('https://kamforms.com/api/**', api)
  const page = await ctx.newPage()
  await page.goto(base + path); await page.waitForTimeout(2200)
  const dir = join(out, nom); await mkdir(dir, { recursive: true })
  const cdp = await ctx.newCDPSession(page)
  const imgs = []; const t0 = Date.now(); let filme = true
  const boucle = (async () => {
    while (filme) {
      const { data: d } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 90, optimizeForSpeed: true, clip: { x: 0, y: 0, width: 390, height: 844, scale: 2 } })
      const fichier = `${String(imgs.length).padStart(4, '0')}.jpg`
      imgs.push({ t: (Date.now() - t0) / 1000, f: fichier })
      await writeFile(join(dir, fichier), Buffer.from(d, 'base64'))
    }
  })()
  await page.waitForTimeout(600)
  await act(page).catch(e => console.warn(nom, e.message.split('\n')[0]))
  await page.waitForTimeout(800)
  filme = false; await boucle
  await writeFile(join(dir, 'images.json'), JSON.stringify(imgs))
  console.log('✓', nom, imgs.length, 'images', imgs.at(-1)?.t, 's')
  await ctx.close()
}

await prise('creer', { path: '/create', act: async p => {
  await p.waitForTimeout(700); await tap(p, 'Le décrire'); await p.waitForTimeout(900)
  const box = p.getByRole('textbox').last(); await box.click()
  await p.keyboard.type('Prise de commande : nom, téléphone, produit, quantité, quartier de livraison', { delay: 38 })
  await p.waitForTimeout(400); await p.getByLabel('Envoyer').last().click()
  await p.waitForTimeout(1500)
  if (await p.getByText('Une seule page', { exact: true }).count()) { await tap(p, 'Une seule page') }
  await p.waitForTimeout(IA + 1800); await glisse(p, 700); await p.waitForTimeout(1500)
} })
await prise('apercu', { path: '/', signedIn: false, intro: false, act: async p => {
  const steps = [() => tap(p, 'Commencer'), async () => { await tap(p, 'Des commandes'); await tap(p, 'Continuer') },
    async () => { await tap(p, 'Il manque toujours une info'); await tap(p, 'Continuer') }, () => tap(p, 'Continuer'),
    () => tap(p, 'Préparer mon formulaire'), async () => { await tap(p, 'Mode'); await tap(p, 'Continuer'); await p.waitForTimeout(1300) }]
  // on avance sans filmer l'utile : seule la dernière étape compte
  for (const s of steps) { await s(); await p.waitForTimeout(450) }
  await p.waitForTimeout(800); await tap(p, 'Voir ce que je vais recevoir'); await p.waitForTimeout(2500)
} })
await prise('reponses', { path: '/inbox', act: async p => { await p.waitForTimeout(900); await tap(p, 'Toutes'); await p.waitForTimeout(1600); await glisse(p, 500); await p.waitForTimeout(1200) } })
await prise('detail', { path: '/submission/s1', act: async p => { await p.waitForTimeout(2500) } })
await prise('formulaire', { path: '/form/f1', act: async p => { await p.waitForTimeout(1600); await glisse(p, 300); await p.waitForTimeout(1500) } })
await prise('accueil', { path: '/', act: async p => { await p.waitForTimeout(2000); await glisse(p, 500); await p.waitForTimeout(1500) } })
await prise('voir', { path: '/form/f1', act: async p => { await p.waitForTimeout(1200); await tap(p, 'Voir'); await p.waitForTimeout(3000); await glisse(p, 400); await p.waitForTimeout(1500) } })
await prise('perso', { path: '/customize/f1', act: async p => { await p.waitForTimeout(2500) } })
await browser.close(); server.close()
