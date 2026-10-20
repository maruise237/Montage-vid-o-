"""Remplace les textes anglais de la vidéo par du français (titres, cartes, étiquettes, sous-titres).
usage : python3 doubler.py analyse | rendu [n_proc] | test t1 t2 ..."""
import sys, json, subprocess, re, unicodedata, os
import numpy as np, cv2
sys.path.insert(0, 'outils_d'); sys.path.insert(0, '.')
from effacer import effacer, analyser
from texte import calque, coller, police, largeur, ARC
from elements import E
W, H, FPS = 1080, 1920, 60
SRC = 'src/source.mp4'; DUREE = 50.0
BANDE = (0, 1420, 1080, 1590)          # sous-titres anglais d'origine
def lecteur(t0=0.0, dur=None, fps=FPS):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{t0:.4f}', '-i', SRC]
    if dur: cmd += ['-t', f'{dur:.4f}']
    cmd += ['-vf', f'fps={fps}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W*H*3)
        if len(b) < W*H*3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
def actif(e, t): return e['t'][0] <= t < e['t'][1]
def ink(cal):
    a = cal[..., 3] > 0.3; ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max()+1, ys.max()+1
# ---------- analyse : référence (taille, position, couleur) de chaque élément ----------
def analyse():
    rec = {i: [] for i in range(len(E))}
    for n, img in enumerate(lecteur(fps=20)):
        t = n/20
        for i, e in enumerate(E):
            if 'rangee' in e or 'puces' in e or not actif(e, t): continue
            inf = effacer(img, e['box'], k=e.get('k', 61), juste_info=True)
            if inf: rec[i].append(dict(t=t, n=inf['n'], bbox=inf['bbox'], c=inf['contraste'], col=[float(v) for v in inf['couleur']]))
    ref = {}
    for i, r in rec.items():
        if not r: continue
        cmax = np.percentile([x['c'] for x in r], 90)
        bons = [x for x in r if x['c'] >= .85*cmax] or r
        # largeur de référence = la plus fréquente parmi les grandes (texte entièrement écrit, posé)
        best = max(bons, key=lambda x: x['bbox'][2]-x['bbox'][0])
        if not E[i].get('frappe'):
            # position posée (après l'animation d'entrée) = médiane des boîtes
            bb = np.median(np.array([x['bbox'] for x in bons]), 0).astype(int).tolist()
            best = dict(min(bons, key=lambda x: np.abs(np.array(x['bbox']) - bb).sum())); best['bbox'] = bb
        if 'tref' in E[i]: best = min(r, key=lambda x: abs(x['t'] - E[i]['tref']))
        ref[i] = dict(c=float(cmax), bbox=best['bbox'], col=best['col'], t=best['t'])
        print(i, E[i]['fr'][0][0] if 'fr' in E[i] else E[i]['rangee'][0], ref[i]['bbox'], round(cmax), 'à', best['t'])
    json.dump(ref, open('ref.json', 'w'))
# ---------- préparation des calques français ----------
def preparer(ref):
    P = {}
    for i, e in enumerate(E):
        if 'rangee' in e or 'puces' in e:
            P[i] = dict(rangee=True); continue
        r = ref.get(str(i))
        if not r: continue
        x0, y0, x1, y1 = r['bbox']
        en, _ = calque([(t, f, (0, 0, 0)) for t, f in e['en']], 100, (0, 0, 0), e.get('esp', 0))
        ex0, ey0, ex1, ey1 = ink(en)
        taille = e.get('taille') or 100*(x1-x0)/(ex1-ex0)
        # hauteur : la police anglaise doit aussi coller verticalement (contrôle)
        en2, _ = calque([(t, f, (0, 0, 0)) for t, f in e['en']], taille, (0, 0, 0), e.get('esp', 0))
        asc_en = max(police(f, taille).getmetrics()[0] for _, f in e['en'])
        P[i] = dict(taille=taille, ref=r, base=y0 - ink(en2)[1] + 2 + asc_en)
    return P
def dessiner_el(img, e, p, inf):
    r = p['ref']; x0, y0, x1, y1 = r['bbox']
    coul = inf['couleur'] if e.get('couleur') == 'live' else r['col']
    alpha = 1.0 if e.get('couleur') == 'live' else float(np.clip(inf['contraste']/r['c'], 0, 1))**1.2
    taille = p['taille']
    cal, _ = calque(e['fr'], taille, coul, e.get('esp', 0))
    fx0, fy0, fx1, fy1 = ink(cal); fw = fx1-fx0
    maxw = e.get('maxw', 1000 if e.get('align') == 'c' else W-60-x0)
    if fw > maxw:
        taille *= maxw/fw; cal, _ = calque(e['fr'], taille, coul, e.get('esp', 0)); fx0, fy0, fx1, fy1 = ink(cal); fw = fx1-fx0
    # vertical : centre des capitales/x-height -> on aligne le haut de l'encre (ascendantes) sur l'original
    asc = max(police(f, taille).getmetrics()[0] for _, f, _ in e['fr'])
    ytop = p['base'] - (2 + asc) if 'base' in p else y0 - fy0
    if e.get('align') == 'c': x = (x0+x1)/2 - (fx0+fx1)/2
    elif e.get('align') == 'r': x = x1 - fx1
    else: x = x0 - fx0
    revele = 1.0
    if e.get('frappe'):
        bx0, _, bx1, _ = inf['bbox']; revele = np.clip((bx1-x0)/max(1, x1-x0), 0, 1)
        revele = (fx0 + revele*fw)/cal.shape[1]
    coller(img, cal, x, ytop, alpha, revele)
def rangee(img, e):
    k = e.get('k', 41); big, bg, d, sl, (X0, Y0) = analyser(img, e['box'], k)
    m = np.zeros(d.shape, np.uint8); m[sl] = d[sl] > e.get('seuil', 150)
    if m.sum() < 40: return
    g = e.get('gap', 40)
    md = cv2.dilate(m, np.ones((9, g), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(md)
    blocs = sorted([st[j] for j in range(1, n) if st[j][4] > 1200], key=lambda s: s[0])
    for j, (bx, by, bw, bh, _) in enumerate(blocs[:len(e['rangee'])]):
        box = (X0+bx, max(e['box'][1], Y0+by), X0+bx+bw, min(e['box'][3], Y0+by+bh))
        inf = effacer(img, box, k=k)
        if not inf: continue
        ix0, iy0, ix1, iy1 = inf['bbox']
        cal, _ = calque([(e['rangee'][j], e['police'], None)], e.get('taille', 33), inf['couleur'])
        fx0, fy0, fx1, fy1 = ink(cal)
        alpha = float(np.clip(inf['contraste']/e.get('cref', 500), 0, 1))
        coller(img, cal, (ix0+ix1)/2-(fx0+fx1)/2, iy0-fy0, 1.0 if alpha > .6 else alpha/.6)
def remplir(img, box, ep=3):
    x0, y0, x1, y1 = box
    def ligne(a): return cv2.GaussianBlur(a.mean(0, keepdims=True).astype(np.float32), (0, 0), 5)[0] if True else None
    sg = 6 if x1 - x0 < 600 else 30
    hau = cv2.GaussianBlur(img[y0-ep:y0, x0:x1].astype(np.float32).mean(0)[None], (0, 0), sigmaX=sg, sigmaY=0.1)[0]
    bas = cv2.GaussianBlur(img[y1:y1+ep, x0:x1].astype(np.float32).mean(0)[None], (0, 0), sigmaX=sg, sigmaY=0.1)[0]
    f = np.linspace(0, 1, y1-y0)[:, None, None]
    img[y0:y1, x0:x1] = (hau[None]*(1-f) + bas[None]*f).astype(np.uint8)
def pastille(w, h, coul, bord=None):
    from PIL import Image, ImageDraw
    s = 3; im = Image.new('RGBA', (w*s, h*s)); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w*s-1, h*s-1], radius=h*s//2, fill=tuple(int(c) for c in coul)+(255,),
                         outline=(tuple(int(c) for c in bord)+(255,)) if bord is not None else None, width=s*2 if bord is not None else 0)
    a = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32); a[..., 3] /= 255
    return a
def puces(img, e):
    for rects, labels in zip(e['puces'], e['labels']):
        echant = []
        for (x0, y0, x1, y1) in rects:
            ym = (y0+y1)//2
            bgc = np.median(img[ym-4:ym+4, x0+9:x0+15].reshape(-1, 3), 0)
            inf = effacer(img, (x0+12, y0+10, x1-12, y1-10), k=31, juste_info=True)
            echant.append((bgc, inf))
        for (x0, y0, x1, y1) in rects: remplir(img, (x0-6, y0-6, x1+6, y1+6))
        T = e['taille']; pad, gap = 24, 16
        ws = [largeur([(l, e['police'], None)], T) for l in labels]
        span = rects[-1][2] - rects[0][0] + 40
        tot = sum(ws) + 2*pad*len(ws) + gap*(len(ws)-1)
        if tot > span: T *= (span - 2*pad*len(ws) - gap*(len(ws)-1)) / sum(ws); ws = [largeur([(l, e['police'], None)], T) for l in labels]; tot = span
        x = (rects[0][0] + rects[-1][2])/2 - tot/2
        for (r, l, w, (bgc, inf)) in zip(rects, labels, ws, echant):
            y0, y1 = r[1], r[3]; cw = int(w + 2*pad)
            fond = img[(y0+y1)//2, int(min(max(x, 0), W-1))].astype(float)
            clair = bgc.mean() > 200
            pt = pastille(cw, y1-y0, bgc, (bgc*0.94) if clair else None)
            coller(img, pt, x, y0)
            if inf:
                cal, _ = calque([(l, e['police'], None)], T, inf['couleur'])
                fx0, fy0, fx1, fy1 = ink(cal); cy = (y0+y1)/2
                hx = ink(calque([("Hx", e['police'], None)], T, (0, 0, 0))[0])
                coller(img, cal, x + cw/2 - (fx0+fx1)/2, cy - (hx[1] + hx[3])/2 + 1, float(np.clip(inf['contraste']/300, 0, 1)))
            x += cw + gap
# ---------- sous-titres français ----------
BLEU = (40, 100, 235); ORANGE = (232, 86, 42)
ACCENT = {'toujours': 'arc', 'actif': 'arc', 'chatgpt': 'arc', 'objectif': 'arc', 'applis': 'arc',
          'reservations': BLEU, 'achats': BLEU, 'formulaires': BLEU, 'rappels': BLEU, 'quotidien': BLEU,
          'collegues': 'arc', 'ia': None, 'continu': 'arc', 'alternatives': ORANGE, 'comparatif': ORANGE,
          'complet': ORANGE, 'agent': 'arc', 'differents': None}
def norm(w):
    w = unicodedata.normalize('NFD', w.lower()); w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9]", '', w)
def morceaux():
    mots = json.load(open('voix/mots_fr.json')); M = []; cur = []
    for j, (w, s, e, ph, k) in enumerate(mots):
        if cur and (ph != cur[-1][3] or k != cur[-1][4] or re.search(r'[,.:;!?]$', cur[-1][0]) or len(cur) >= 3
                    or len(' '.join(x[0] for x in cur) + ' ' + w) > 22 or s - cur[-1][2] > .35):
            M.append(cur); cur = []
        cur.append([w, s, e, ph, k])
    if cur: M.append(cur)
    for j, m in enumerate(M):
        fin = m[-1][2] + .35
        if j+1 < len(M) and M[j+1][0][1] - m[-1][2] < .6: fin = M[j+1][0][1]
        m.append(fin)
    return M
MORC = None
def sous_titres(img, t, sombre):
    global MORC
    if MORC is None: MORC = morceaux()
    for m in MORC:
        mots, fin = m[:-1], m[-1]
        if not (mots[0][1] - .03 <= t < fin): continue
        base = (245, 245, 245) if sombre else (18, 17, 16)
        txt = ' '.join(x[0] for x in mots).replace(' :', ':')
        mots_aff = txt.split(' ')
        segs = []
        for k, w in enumerate(mots_aff):
            c = ACCENT.get(norm(w), None)
            segs.append((w + (' ' if k < len(mots_aff)-1 else ''), 'sans', c))
        taille = 58
        if largeur(segs, taille) > 980: taille *= 980/largeur(segs, taille)
        x = 540 - largeur(segs, taille)/2; y = 1476
        asc = police('sans', taille).getmetrics()[0]
        for k, (w, f, c) in enumerate(segs):
            a = np.clip((t - (mots[k][1] - .04)) / .12, 0, 1) if k < len(mots) else 1
            if a > 0:
                cal, _ = calque([(w, f, c)], taille, base)
                cx0, cy0, _, _ = ink(calque([("Hx", f, None)], taille, base)[0])
                coller(img, cal, x - 2, y - cy0, a)
            x += police(f, taille).getlength(w)
        return
def traiter(img, t, P):
    for i, e in enumerate(E):
        if not actif(e, t) or i not in P: continue
        if 'rangee' in e: rangee(img, e); continue
        if 'puces' in e: puces(img, e); continue
        if e.get('aplat'):
            inf = effacer(img, e['box'], k=e.get('k', 61), juste_info=True)
            if inf:
                x0, y0, x1, y1 = e['aplat']; img[y0:y1, x0:x1] = np.median(img[y0-4:y0-1, x0+20:x1-20].reshape(-1, 3), 0)
        else: inf = effacer(img, e['box'], k=e.get('k', 61))
        if inf: dessiner_el(img, e, P[i], inf)
    remplir(img, (0, 1422 if 8.5 < t < 10.5 else 1402, 1080, 1640), ep=6)
    lum = img[1400:1600:8, ::8].mean()
    sous_titres(img, t, lum < 110)
    return img
def charger():
    return preparer(json.load(open('ref.json')))
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'analyse': analyse()
    elif cmd == 'test':
        P = charger(); os.makedirs('test', exist_ok=True)
        for ts in sys.argv[2:]:
            t = float(ts); img = next(lecteur(t, 0.05))
            cv2.imwrite(f'test/a{ts}.jpg', cv2.cvtColor(np.concatenate([img.copy(), traiter(img, t, P)], 1), cv2.COLOR_RGB2BGR))
    elif cmd == 'segment':      # segment t0 dur sortie
        P = charger(); t0, dur, out = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for n, img in enumerate(lecteur(t0, dur)):
            enc.stdin.write(traiter(img, t0 + n/FPS, P).tobytes())
        enc.stdin.close(); enc.wait()
