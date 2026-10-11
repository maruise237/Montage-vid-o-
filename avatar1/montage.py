"""Vidéo avatar n°1 « Cette vidéo est entièrement montée avec du code » (voix de Mariuse, ~77 s).

Type : démonstration / vulgarisation, DA « 2D sticker » (compétence video-avatar) : fond crème quadrillé,
sous-titres en haut, avatar détouré avec contour blanc, une pose par phrase, cartes néo-brutalistes,
vrais logos. Les demandes de Mariuse dans la voix (« mets ton logo », « change l'arrière-plan », « une ville »,
« une salle où on voit KAMTECH », « un avatar de toi sur la plage », « mon avatar derrière toi ») sont
exécutées à l'écran au mot prononcé.
Usage : python3 avatar1/montage.py → avatar1/muet.mp4 + avatar1/evenements.json
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(ICI)
AV = f'{RACINE}/assets/avatar'; LOGOS = f'{RACINE}/assets/logos'
W, H, FPS = 1080, 1920, 30
CREME, ENCRE, ROUGE, BLANC = (241, 235, 224), (18, 18, 18), (217, 68, 43), (255, 255, 255)
F = lambda n, s: ImageFont.truetype(f'{RACINE}/fonts/{n}', s)
SANS, SERIF_I, MONO = 'InterTight-ExtraBold.ttf', 'InstrumentSerif-Italic.ttf', 'JetBrainsMono-Medium.ttf'

# ---------- voix : mots (temps de la voix montée) ----------
FIN_VOIX = 74.6
DUREE = FIN_VOIX + 3.2
CORR = {'suivez': 'sentez', 'voice': 'vocal', 'même': 'mets', "qu'il": 'que je', 'vient': 'viens',
        'avatar': 'avatar', 'Veo': 'Veo 3'}


def charger_mots():
    brut = [m for m in json.load(open(f'{ICI}/mots_montes.json')) if m['s'] < FIN_VOIX]
    out = []
    for m in brut:
        w = m['w']
        if out and (w.startswith("'") or w.startswith('-') or w == '%'):
            out[-1]['w'] += ('' if w != '%' else ' ') + w; out[-1]['e'] = m['e']; continue
        if w == '3' and out and out[-1]['w'] == 'Veo':
            out[-1]['e'] = m['e']; continue
        out.append(dict(m))
    for m in out:
        nu = m['w'].strip('.,')
        if nu in CORR: m['w'] = m['w'].replace(nu, CORR[nu])
    return out


MOTS = charger_mots()


def q(mot, n=0):
    l = [m['s'] for m in MOTS if m['w'].strip('.,').lower() == mot.strip('.,').lower()]
    return l[n]


ACCENT = {'code', 'cap', 'avatar', 'gratuite', 'claude', 'animer', 'seedance', 'logo', "l'arrière-plan", 'ville',
          'kamtech', 'puissance', 'plage', 'derrière', 'merci', 'hésitations', 'surpris', 'vocal', 'illustrée',
          'lunettes', 'intelligence', 'personnage'}


def blocs():
    res, cur = [], []
    for k, m in enumerate(MOTS):
        cur.append(k); w = m['w']
        nxt = MOTS[k + 1]['s'] if k + 1 < len(MOTS) else 99
        if len(cur) == 3 or w[-1] in '.,' or nxt - m['e'] > .35 or (len(cur) == 2 and len(MOTS[cur[0]]['w'] + w) > 13):
            res.append(cur); cur = []
    if cur: res.append(cur)
    out = []
    for i, b in enumerate(res):
        fin = min(MOTS[res[i + 1][0]]['s'] if i + 1 < len(res) else FIN_VOIX, MOTS[b[-1]]['e'] + .6)
        out.append((MOTS[b[0]]['s'] - .04, fin, b))
    return out


BLOCS = blocs()

# ---------- temps clés (mots prononcés) ----------
T = dict(code=q('code.'), nous=q('nous'), cap=q('cap'), ia=q("l'intelligence"), maintenant=q('maintenant'),
         illustrees=q('illustrées'), avatar=q('avatar'), pour=q('pour', 1), gratuite=q('gratuite.'),
         mon=q('mon'), claude1=q('claude'), montage=q('montage.'), animer=q('animer'), ce=q('ce'),
         veo=q('veo 3'), kling=q('kling'), seedance=q('seedance.'), cette2=q('cette', 2), illustree=q('illustrée'),
         claude_ill=q('claude', 1), comme=q('comme', 1), logo=q('logo.'), change=q('change'),
         arriere=q("l'arrière-plan"), mets1=q('mets'), ville=q('ville.'), mets2=q('mets', 1), kamtech=q('kamtech.'),
         tous=q('tous'), puissance=q('puissance'), claude_gen=q('claude', 5), marcher=q('marcher'),
         lunettes=q('lunettes'), plage=q('plage.'), ok1=q('ok,'), avatar2=q('avatar', 2),
         ok2=q('ok', 1), merci=q('merci.'), et=q('et', 0), travail=q('travail'), cest=q("c'est", 1),
         surpris=q('surpris.'), claude_fin=q('claude', 9))

# les débuts de phrase de whisper sont souvent 0,2–0,4 s trop tôt : on cale les changements de scène sur le
# vrai départ de la phrase (mesuré sur l'énergie dans coupe.py → plan.json)
DEBUTS = [x['debut'] for x in json.load(open(f'{ICI}/plan.json'))]
for _k in ['nous', 'maintenant', 'pour', 'mon', 'ce', 'cette2', 'comme', 'change', 'mets1', 'mets2', 'tous',
           'claude_gen', 'et', 'cest']:
    _d = min(DEBUTS, key=lambda d: abs(d - T[_k]))
    if abs(_d - T[_k]) < .7: T[_k] = _d + .05

# scènes : (début, fond, pose, x centre, y pieds, hauteur, extra)
SC = [
    (0.0, 'creme', 'pointe', 790, 1840, 1080, 'code'),
    (T['nous'] - .05, 'creme', 'victoire', 300, 1850, 1060, 'cap'),
    (T['maintenant'] - .05, 'creme', 'face', 560, 2550, 1900, 'poses'),
    (T['pour'] - .05, 'creme', 'pouce', 810, 1850, 1000, 'facture'),
    (T['mon'] - .05, 'creme', 'explique', 640, 1850, 1060, 'claude'),
    (T['ce'] - .05, 'creme', 'haussement', 540, 1900, 760, 'pas'),
    (T['cette2'] - .05, 'creme', 'reflechit', 290, 1850, 1060, 'illustree'),
    (T['comme'] - .05, 'creme', 'pointe', 800, 1850, 1060, 'logo'),
    (T['change'] - .05, 'ciel', 'face', 540, 1800, 1000, 'ciel'),
    (T['mets1'] - .05, 'ville', 'pouce', 640, 1830, 980, 'ville'),
    (T['mets2'] - .05, 'bureau', 'bras_croises', 560, 1880, 940, 'bureau'),
    (T['tous'] - .05, 'creme', 'ordinateur', 780, 1850, 940, 'recap'),
    (T['claude_gen'] - .05, 'creme', 'explique', 300, 1850, 1000, 'prompt'),
    (T['marcher'] - .05, 'plage', None, 0, 0, 0, 'plage'),
    (T['et'] - .05, 'creme', 'bras_croises', 790, 1880, 940, 'vocal_brut'),
    (T['cest'] - .05, 'creme', 'telephone', 720, 1880, 960, 'vocal'),
    (FIN_VOIX + .05, 'rouge', 'pouce', 540, 2000, 900, 'fin'),
]


def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def pop(x, d=.2):
    x = max(0, x / d)
    return 0 if x <= 0 else (1.12 * (1 - (1 - x) ** 3) if x < 1 else 1 + .12 * math.exp(-(x - 1) * 4) * math.cos((x - 1) * 6))


# ---------- ressources ----------
def fond_creme():
    im = Image.new('RGB', (W, H), CREME); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line((x, 0, x, H), fill=(228, 221, 208), width=2)
    for y in range(0, H, 60): d.line((0, y, W, y), fill=(228, 221, 208), width=2)
    return im


def couvrir(chemin):
    im = Image.open(chemin).convert('RGB'); s = max(W / im.width, H / im.height)
    im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    return im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))


def sticker(chemin, h=1300, bord=11):
    im = Image.open(chemin).convert('RGBA'); s = h / im.height
    im = im.resize((int(im.width * s), h), Image.LANCZOS)
    p = bord * 3; c = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); c.alpha_composite(im, (p, p))
    # pas de contour blanc (demande de Mariuse) : juste une ombre douce sous le personnage
    ombre = c.getchannel('A').filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .22))
    out = Image.new('RGBA', c.size, (0, 0, 0, 0))
    o = Image.new('RGBA', c.size, (0, 0, 0, 0)); o.putalpha(ombre); out.alpha_composite(o, (8, 14))
    out.alpha_composite(c)
    return out, p


def logo(nom, taille):
    lg = Image.open(f'{LOGOS}/{nom}.png').convert('RGBA'); lg = lg.crop(lg.getbbox())
    s = taille / max(lg.size); return lg.resize((max(1, int(lg.width * s)), max(1, int(lg.height * s))), Image.LANCZOS)


def carte(w, h, fond=BLANC, etiquette=None, ombre=12, bord=5):
    c = Image.new('RGBA', (w + ombre + 4, h + ombre + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    y0 = 36 if etiquette else 0
    d.rectangle((ombre, y0 + ombre, w - 1 + ombre, y0 + h - 1 + ombre), fill=ENCRE)
    d.rectangle((0, y0, w - 1, y0 + h - 1), fill=fond, outline=ENCRE, width=bord)
    if etiquette:
        f = F(SANS, 30); tw = f.getlength(etiquette)
        d.rectangle((18, 0, 18 + tw + 32, 52), fill=ROUGE, outline=ENCRE, width=4)
        d.text((34, 27), etiquette, font=f, fill=BLANC, anchor='lm')
    return c, y0


R = {}


def init():
    if R: return
    R['creme'] = fond_creme()
    R['ciel'] = couvrir(f'{AV}/brut/fond_ciel.png'); R['ville'] = couvrir(f'{AV}/brut/fond_ville.png')
    R['plage'] = couvrir(f'{AV}/brut/fond_plage.png')
    b = Image.open(f'{AV}/brut/fond_bureau.png').convert('RGB')
    # vrai logo KAMTECH posé sur le panneau noir du mur (repéré : x 314–704, y 254–583 sur 768x1344)
    lg = Image.open(f'{LOGOS}/kamtech.png').convert('RGBA'); s = (704 - 314) * .82 / lg.width
    lg = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    b2 = b.copy().convert('RGBA'); b2.alpha_composite(lg, (int(509 - lg.width / 2), int(418 - lg.height / 2)))
    b2.convert('RGB').save(f'{ICI}/fond_bureau_kamtech.png')
    R['bureau'] = couvrir(f'{AV}/brut/fond_bureau.png'); R['bureau_k'] = couvrir(f'{ICI}/fond_bureau_kamtech.png')
    R['rouge'] = Image.new('RGB', (W, H), ROUGE)
    for n in ['pointe', 'victoire', 'face', 'pouce', 'explique', 'haussement', 'reflechit', 'bras_croises',
              'ordinateur', 'telephone', 'choque', 'marche', 'claude_mascotte']:
        R['p_' + n] = sticker(f'{AV}/poses/{n}.png')
    for n in ['choque', 'pouce', 'reflechit', 'victoire']:
        R['mini_' + n] = sticker(f'{AV}/poses/{n}.png', 540, 9)
    R['env'] = enveloppe()


def enveloppe():
    sr = 16000
    a = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', f'{ICI}/voix_montee.wav', '-ar', str(sr), '-ac', '1',
                                               '-f', 's16le', '-']), np.int16).astype(np.float32) / 32768
    h = sr // FPS; n = len(a) // h
    e = np.sqrt((a[:n * h].reshape(n, h) ** 2).mean(1)); e = np.clip(e / (np.percentile(e, 95) + 1e-9), 0, 1)
    sm = np.zeros(n); p = 0
    for i, v in enumerate(e): p = v if v > p else p * .7 + v * .3; sm[i] = p
    return sm


def env(t):
    i = int(t * FPS); return float(R['env'][i]) if i < len(R['env']) else 0.0


# ---------- dessin ----------
def poser(img, nom, cx, pied, haut, t, te, extra_y=0, flip=False, rot=0, ombre_sol=False):
    st, p = R['p_' + nom]
    s_in = pop(te, .22) if te < 1 else 1
    e = env(t); respire = 1 + .008 * math.sin(2 * math.pi * t / 2.6)
    hh = haut / (st.height - 2 * p) * s_in
    sx, sy = hh * (1 + .006 * e), hh * respire * (1 + .018 * e)
    if sx <= .01: return
    im = st.resize((max(2, int(st.width * sx)), max(2, int(st.height * sy))), Image.BILINEAR)
    if flip: im = ImageOps.mirror(im)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    y = pied - (st.height - p) * sy - 16 * e + extra_y
    if ombre_sol:
        o = Image.new('RGBA', (int(haut * .5), 60), (0, 0, 0, 0))
        ImageDraw.Draw(o).ellipse((0, 0, o.width - 1, 59), fill=(0, 0, 0, 70)); o = o.filter(ImageFilter.GaussianBlur(10))
        img.alpha_composite(o, (int(cx - o.width / 2), int(pied - 30)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def texte(d, xy, s, f, fill, anchor='mm', contour=0, cfill=BLANC):
    if contour: d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=contour, stroke_fill=cfill)
    else: d.text(xy, s, font=f, fill=fill, anchor=anchor)


def coller(img, el, cx, cy, s=1.0, rot=0):
    if s <= .02: return
    if s != 1: el = el.resize((max(2, int(el.width * s)), max(2, int(el.height * s))), Image.BILINEAR)
    if rot: el = el.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(el, (int(cx - el.width / 2), int(cy - el.height / 2)))


def geant(mot, taille, couleur=ENCRE, contour=0, police=SANS):
    contour = 0  # pas de bordure (demande de Mariuse)
    f = F(police, taille); bb = f.getbbox(mot)
    im = Image.new('RGBA', (bb[2] - bb[0] + 2 * contour + 40, bb[3] - bb[1] + 2 * contour + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((im.width / 2, im.height / 2), mot, font=f, fill=couleur, anchor='mm',
                            stroke_width=contour, stroke_fill=BLANC)
    return im


def tampon(txt, taille=64, rot=-8):
    f = F(SANS, taille); w = int(f.getlength(txt)) + 60; h = taille + 50
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w - 4, h - 4), 14, outline=ROUGE, width=8); d.text((w / 2, h / 2 + 2), txt, font=f, fill=ROUGE, anchor='mm')
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)


def croix(taille):
    im = Image.new('RGBA', (taille, taille), (0, 0, 0, 0)); d = ImageDraw.Draw(im); m = taille * .12
    for a, b in (((m, m), (taille - m, taille - m)), ((taille - m, m), (m, taille - m))):
        d.line((a, b), fill=ROUGE, width=int(taille * .13))
    return im


def sous_titre(img, t, photo=False):
    b = next((b for b in BLOCS if b[0] <= t < b[1]), None)
    if not b: return
    d = ImageDraw.Draw(img); f = F(SANS, 82); parts = []
    acc = next((k for k in b[2] if MOTS[k]['w'].strip('.,').lower() in ACCENT), None)
    for k in b[2]:
        parts.append((MOTS[k]['w'].strip('.,').upper(), MOTS[k]['s'], k == acc))
    total = sum(f.getlength(w) for w, _, _ in parts) + 26 * (len(parts) - 1)
    s = min(1, (W - 90) / total); f = F(SANS, int(82 * s)); total = sum(f.getlength(w) for w, _, _ in parts) + 26 * (len(parts) - 1)
    x = (W - total) / 2; y = 470
    for w, a, ac in parts:
        if t >= a - .05:
            sc = 1 + .12 * max(0, 1 - (t - a + .05) / .12)
            ff = f if sc == 1 else F(SANS, int(f.size * sc))
            if photo:  # sur un décor : texte blanc + ombre portée douce, sans contour
                d.text((x + f.getlength(w) / 2 + 4, y + 5), w, font=ff, fill=(0, 0, 0, 120), anchor='ms')
                d.text((x + f.getlength(w) / 2, y), w, font=ff, fill=(255, 214, 102) if ac else BLANC, anchor='ms')
            else:
                d.text((x + f.getlength(w) / 2, y), w, font=ff, fill=ROUGE if ac else ENCRE, anchor='ms')
        x += f.getlength(w) + 26


def fenetre_code(t, te):
    c, y0 = carte(620, 430, (28, 28, 32), 'montage.py')
    d = ImageDraw.Draw(c); fm = F(MONO, 30)
    for i, col in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((22 + i * 36, y0 + 20, 44 + i * 36, y0 + 42), fill=col)
    lignes = [('pose', '= "pointe"'), ('fond', '= "crème"'), ('logo', '= "claude.png"'), ('voix', '= "vocal.m4a"'),
              ('rendu', '(30 ips)')]
    n_car = int(te * 34)
    for i, (a, b) in enumerate(lignes):
        s = (a + ' ' + b)[:max(0, n_car - i * 14)]
        if not s: break
        d.text((34, y0 + 90 + i * 62), s[:len(a)], font=fm, fill=(255, 140, 110))
        if len(s) > len(a): d.text((34 + fm.getlength(a + ' '), y0 + 90 + i * 62), s[len(a) + 1:], font=fm, fill=(160, 220, 170))
    return c


def facture(t, te):
    c, y0 = carte(560, 560, BLANC, 'FACTURE')
    d = ImageDraw.Draw(c); f = F(SANS, 36); fi = F(SERIF_I, 40)
    lignes = [('Images (Cloudflare)', '0 €'), ('Transcription', '0 €'), ('Montage (code)', '0 €')]
    for i, (a, b) in enumerate(lignes):
        p = ease((te - .25 - i * .35) / .2)
        if p <= 0: continue
        d.text((36, y0 + 90 + i * 90), a, font=fi, fill=ENCRE + (int(255 * p),), anchor='lm')
        d.text((520, y0 + 90 + i * 90), b, font=f, fill=ENCRE + (int(255 * p),), anchor='rm')
    if te > 1.4:
        d.line((36, y0 + 380, 520, y0 + 380), fill=ENCRE, width=4)
        d.text((36, y0 + 450), 'TOTAL', font=F(SANS, 54), fill=ENCRE, anchor='lm')
        d.text((520, y0 + 450), '0 €', font=F(SANS, 72), fill=ROUGE, anchor='rm')
    return c


def bulle_prompt(te, n_car):
    txt = 'Génère un avatar de toi qui marche avec des lunettes sur la plage'
    c, y0 = carte(860, 250, BLANC, 'PROMPT À CLAUDE')
    d = ImageDraw.Draw(c); f = F(SERIF_I, 50); s = txt[:n_car]
    mots, lignes, cur = s.split(' '), [], ''
    for m in mots:
        if f.getlength(cur + ' ' + m) > 780 and cur: lignes.append(cur); cur = m
        else: cur = (cur + ' ' + m).strip()
    lignes.append(cur)
    for i, l in enumerate(lignes[:3]): d.text((40, y0 + 70 + i * 60), l, font=f, fill=ENCRE, anchor='lm')
    if n_car < len(txt) and int(te * 3) % 2 == 0:
        x = 40 + f.getlength(lignes[min(2, len(lignes) - 1)]); yl = y0 + 70 + (min(2, len(lignes) - 1)) * 60
        d.rectangle((x + 6, yl - 26, x + 12, yl + 26), fill=ROUGE)
    return c


def onde(te, brut=True):
    c, y0 = carte(900, 330, BLANC, 'TON VOCAL BRUT  2 min 16' if brut else 'VOIX MONTÉE  1 min 16')
    d = ImageDraw.Draw(c); rng = np.random.default_rng(3); n = 70
    hs = np.abs(rng.normal(0, 1, n)) * 38 + 14; trous = {5, 6, 13, 14, 15, 22, 30, 31, 38, 47, 48, 49, 57, 63}
    p = ease((te - .6) / 1.0)
    for i in range(n):
        x = 50 + i * 11.6; hh = hs[i]
        if i in trous:
            col = (217, 68, 43, int(255 * (1 - p))); hh *= .55
        else: col = ENCRE + (255,)
        d.rounded_rectangle((x, y0 + 165 - hh, x + 6, y0 + 165 + hh), 3, fill=col)
    if p > .2:
        texte(d, (450, y0 + 300), 'hésitations coupées : « euh », reprises, blancs', F(SERIF_I, 38), ROUGE + (int(255 * p),))
    return c


def message_vocal(te):
    c, y0 = carte(700, 190, (220, 248, 198), 'ENVOYÉ À CLAUDE')
    d = ImageDraw.Draw(c)
    d.ellipse((30, y0 + 50, 120, y0 + 140), fill=(37, 211, 102)); d.polygon([(64, y0 + 72), (64, y0 + 118), (102, y0 + 95)], fill=BLANC)
    rng = np.random.default_rng(9); pr = min(1, te / 3)
    for i in range(34):
        hh = abs(rng.normal(0, 1)) * 22 + 6; x = 150 + i * 13
        d.rounded_rectangle((x, y0 + 95 - hh, x + 6, y0 + 95 + hh), 3, fill=(37, 150, 90) if i / 34 < pr else (140, 160, 140))
    d.text((640, y0 + 160), '2:16', font=F(SANS, 30), fill=(90, 110, 90), anchor='rm')
    return c


def polaroid(fond, pose, rot):
    c = Image.new('RGBA', (300, 380), BLANC + (255,)); d = ImageDraw.Draw(c); d.rectangle((0, 0, 299, 379), outline=ENCRE, width=4)
    im = R[fond].resize((260, 462)).crop((0, 70, 260, 330)); c.paste(im, (20, 20))
    st, p = R['mini_' + pose] if 'mini_' + pose in R else R['mini_pouce']
    m = st.resize((int(st.width * .38), int(st.height * .38))); c.alpha_composite(m, (150 - m.width // 2, 290 - m.height))
    return c.rotate(rot, resample=Image.BICUBIC, expand=True)


def frame(i):
    init()
    t = i / FPS
    k = max(j for j, s in enumerate(SC) if t >= s[0]); t0, fond, pose, cx, pied, haut, ex = SC[k]
    te = t - t0
    if fond == 'bureau' and t >= T['kamtech'] - .1: fond = 'bureau_k'
    img = R[fond].copy().convert('RGBA')
    if ex == 'ciel':                                           # « change l'arrière-plan » : le crème s'ouvre en cercle
        p = ease((t - T['arriere'] + .05) / .45)
        if p < 1:
            m = Image.new('L', (W, H), 255); r = int(p * 1300)
            ImageDraw.Draw(m).ellipse((540 - r, 1200 - r, 540 + r, 1200 + r), fill=0)
            img.paste(R['creme'], (0, 0), m)
    d = ImageDraw.Draw(img)

    if ex == 'code':
        coller(img, fenetre_code(t, te), 360, 860, pop(te + .1, .25), -2)
        if t >= T['code'] - .05:
            coller(img, geant('100 % CODE', 140, ROUGE), 470, 1260, pop(t - T['code'] + .05), -4)
    elif ex == 'cap':
        coller(img, geant('nouveau', 110, ENCRE, 8, SERIF_I), 720, 700, pop(te, .25))
        if t >= T['cap'] - .05: coller(img, geant('CAP', 330, ROUGE, 12), 740, 900, pop(t - T['cap'] + .05))
        if t >= T['ia'] - .05:
            c, y0 = carte(330, 130, ENCRE); ImageDraw.Draw(c).text((165, 65), 'IA  VIDÉO', font=F(SANS, 54), fill=BLANC, anchor='mm')
            coller(img, c, 760, 1150, pop(t - T['ia'] + .05), 4)
    elif ex == 'poses':
        pass
    elif ex == 'facture':
        coller(img, facture(t, te), 330, 940, pop(te, .25), -2)
    elif ex == 'claude':
        if t >= T['claude1'] - .05:
            c, y0 = carte(380, 330, BLANC, 'LE MONTEUR'); dc = ImageDraw.Draw(c)
            lg = logo('claude', 170); c.alpha_composite(lg, (190 - lg.width // 2, y0 + 30))
            dc.text((190, y0 + 270), 'Claude', font=F(SANS, 58), fill=ENCRE, anchor='mm')
            coller(img, c, 290, 800, pop(t - T['claude1'] + .05), -4)
        if t >= T['animer'] - .05:
            coller(img, geant('animer', 150, ROUGE, 10, SERIF_I), 740, 700, pop(t - T['animer'] + .05))
    elif ex == 'pas':
        coller(img, geant('ce n\'est PAS un modèle vidéo IA', 54, ENCRE, 6), 540, 590, pop(te, .2))
        for j, (nom, cle, lab) in enumerate([('veo', 'veo', 'Veo 3'), ('kling', 'kling', 'Kling AI'), ('seedance', 'seedance', 'Seedance')]):
            if t < T[cle] - .05: continue
            c, y0 = carte(290, 300, BLANC); dc = ImageDraw.Draw(c); lg = logo(nom, 150)
            c.alpha_composite(lg, (145 - lg.width // 2, 40 + 75 - lg.height // 2))
            dc.text((145, 245), lab, font=F(SANS, 44), fill=ENCRE, anchor='mm')
            x = 190 + j * 350; y = 860
            coller(img, c, x, y, pop(t - T[cle] + .05), (-3, 2, -2)[j])
            if t >= T[cle] + .7: coller(img, croix(150), x + 105, y - 110, pop(t - T[cle] - .7, .15))
    elif ex == 'illustree':
        coller(img, geant('illustrée', 170, ENCRE, 10, SERIF_I), 700, 760, pop(te - .3, .25))
        if t >= T['claude_ill'] - .05:
            coller(img, logo('claude', 230), 720, 1060, pop(t - T['claude_ill'] + .05), 0)
            coller(img, geant('par Claude', 90, ROUGE, 8), 720, 1260, pop(t - T['claude_ill'] + .05))
    elif ex == 'logo':
        if t >= T['logo'] - .1:
            p = t - T['logo'] + .1
            c = Image.new('RGBA', (430, 430), (0, 0, 0, 0)); dc = ImageDraw.Draw(c)
            dc.ellipse((14, 14, 429, 429), fill=ENCRE); dc.ellipse((0, 0, 415, 415), fill=BLANC, outline=ENCRE, width=6)
            lg = logo('claude', 280); c.alpha_composite(lg, (208 - lg.width // 2, 208 - lg.height // 2))
            coller(img, c, 330, 860, pop(p, .22), -6 + 6 * ease(p / .3))
            if p > .5: coller(img, tampon('C\'EST FAIT', 58, 8), 380, 1150, pop(p - .5, .15))
        else:
            coller(img, geant('ton logo ?', 120, ENCRE, 10, SERIF_I), 380, 860, pop(te - .2, .25))
    elif ex == 'ville':
        c, _ = carte(330, 100, ENCRE); ImageDraw.Draw(c).text((165, 50), 'YAOUNDÉ', font=F(SANS, 52), fill=BLANC, anchor='mm')
        coller(img, c, 300, 720, pop(t - T['ville'] + .2), -3)
    elif ex == 'bureau':
        if t >= T['kamtech'] - .1:
            p = t - T['kamtech'] + .1; halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(halo).ellipse((240, 260, 860, 900), fill=(255, 255, 255, int(110 * max(0, 1 - p / .6))))
            img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60)))
    elif ex == 'recap':
        if t < T['puissance'] - .1:
            for j, (f_, po) in enumerate((('ciel', 'pouce'), ('ville', 'pouce'), ('bureau_k', 'victoire'))):
                coller(img, polaroid(f_, po, (-7, 2, 8)[j]), 210 + j * 330, 880 + (0, -30, 10)[j], pop(te - j * .25, .2))
        else:
            p = t - T['puissance'] + .1
            coller(img, geant('PUISSANCE', 150, ROUGE, 10), 520, 760, pop(p))
            coller(img, logo('claude', 200), 330, 1050, pop(p - .25), 0)
    elif ex == 'prompt':
        n_car = int(max(0, te - .1) * 26)
        coller(img, bulle_prompt(te, n_car), 560, 830, pop(te, .22), 0)
    elif ex == 'fin':
        coller(img, geant('ABONNE-TOI', 150, BLANC, 0), 540, 700, pop(te, .2))
        if te > .5:
            coller(img, geant('commente', 90, (255, 225, 215), 0, SERIF_I), 540, 900, pop(te - .5))
            c, _ = carte(560, 150, BLANC); ImageDraw.Draw(c).text((280, 75), 'AVATAR', font=F(SANS, 96), fill=ROUGE, anchor='mm')
            coller(img, c, 540, 1060, pop(te - .7), -3)

    # personnages
    if ex == 'plage':                                         # la mascotte Claude marche ; Mariuse arrive derrière
        def marche(nom, x, pied, haut, phase):
            bob = -abs(math.sin(2 * math.pi * (t * 1.7 + phase))) * 22
            poser(img, nom, x, pied, haut, t, 5, bob, rot=2.5 * math.sin(2 * math.pi * (t * 1.7 + phase)), ombre_sol=True)
        x_c = -300 + min(1, ease(te / 1.6)) * 920 + 30 * (te - 1.6 if te > 1.6 else 0)
        x_c = min(x_c, 760)
        if t >= T['avatar2'] - .1:
            pa = ease((t - T['avatar2'] + .1) / 1.0); marche('marche', -250 + pa * 560, 1720, 760, .5)
        if t >= T['merci'] - .05:
            poser(img, 'claude_mascotte', x_c, 1830, 640, t, 5, -abs(math.sin((t - T['merci']) * 9)) * 60 * max(0, 1 - (t - T['merci']) / 1.2))
        else:
            marche('claude_mascotte', x_c, 1830, 640, 0)
        if te < 3.2 and T['claude_gen'] < t:
            if te < 2.6: coller(img, bulle_prompt(9, 99), 560, 830)
        if t >= T['merci'] - .05:
            c, _ = carte(330, 110, BLANC); ImageDraw.Draw(c).text((165, 55), 'merci Claude', font=F(SERIF_I, 56), fill=ENCRE, anchor='mm')
            coller(img, c, 540, 760, pop(t - T['merci'] + .05), 3)
    elif pose and not (ex == 'poses' and t >= T['illustrees'] - .1):
        nom = pose; y_extra = 0
        if ex == 'claude' and T['animer'] - .1 <= t < T['animer'] + .55:
            y_extra = -230 * math.sin(math.pi * (t - T['animer'] + .1) / .65)
        if ex == 'vocal' and t >= T['claude_fin'] - .05: nom = 'choque'
        te_p = te if nom == pose else t - T['claude_fin'] + .05
        poser(img, nom, cx, pied, haut, t, te_p, y_extra, ombre_sol=fond in ('ville', 'bureau', 'bureau_k', 'ciel'))
        if ex == 'claude' and T['animer'] - .1 <= t < T['animer'] + .7:
            dd = ImageDraw.Draw(img)
            for j in range(3):
                x = cx - 160 + j * 160; dd.line((x, 1880, x, 1880 - 120 * ease((t - T['animer'] + .1) / .25)), fill=ENCRE, width=8)

    # cartes au-dessus de l'avatar
    if ex == 'poses' and t >= T['illustrees'] - .1:
        for j, n in enumerate(['choque', 'pouce', 'reflechit', 'victoire']):
            st, _ = R['mini_' + n]
            coller(img, st, (300, 780)[j % 2], (1030, 1640)[j // 2], pop(t - T['illustrees'] + .1 - j * .14), (-4, 3, -3, 4)[j])
        if t >= T['avatar'] - .05:
            coller(img, tampon('BANQUE DE POSES', 56, -4), 540, 1360, pop(t - T['avatar'] + .05))
    elif ex == 'facture' and t >= T['gratuite'] - .05:
        coller(img, tampon('100 % GRATUIT', 74, -10), 400, 1420, pop(t - T['gratuite'] + .05, .16))
    if ex == 'vocal_brut':
        coller(img, onde(te), 540, 760, pop(te, .22), -2)
        if t >= T['travail'] - .05: coller(img, tampon('BIEN FAIT', 70, -8), 300, 1150, pop(t - T['travail'] + .05, .15))
    elif ex == 'vocal':
        if t < T['claude_fin'] - .05: coller(img, message_vocal(te), 450, 700, pop(te, .22), -2)
        else:
            p = t - T['claude_fin'] + .05
            coller(img, geant('SURPRIS', 190, ROUGE, 12), 540, 820, pop(p, .16), -5)

    if t < FIN_VOIX + .05: sous_titre(img, t, fond not in ('creme', 'rouge') and not (ex == 'ciel' and t < T['arriere'] + .2))
    return img.convert('RGB').tobytes()


def evenements():
    """Moments pour la bande son (pops, whoosh, impacts)."""
    ev = []
    for t0, fond, pose, *_r, ex in SC: ev.append((t0, 'scene', fond))
    for k in ['code', 'cap', 'gratuite', 'puissance', 'surpris']: ev.append((T[k if k != 'surpris' else 'claude_fin'], 'impact', k))
    for k in ['ia', 'illustrees', 'avatar', 'claude1', 'animer', 'veo', 'kling', 'seedance', 'claude_ill', 'logo', 'ville',
              'kamtech', 'merci', 'travail', 'avatar2']:
        ev.append((T[k], 'pop', k))
    for k in ['veo', 'kling', 'seedance']: ev.append((T[k] + .7, 'croix', k))
    for k in ['arriere']: ev.append((T[k], 'whoosh', k))
    ev.append((T['claude_gen'], 'frappe', 2.6)); ev.append((0.0, 'frappe', 2.0))
    return sorted(ev)


def rendre(a_b):
    a, b, n = a_b; init()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                            f'{ICI}/part_{n}.mp4'], stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(frame(i))
        if n == 0 and i % 60 == 0: print(f'{i / FPS:.1f}s', flush=True)
    enc.stdin.close(); enc.wait()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'planche':
        ts = [float(x) for x in sys.argv[2:]] or list(np.arange(.5, DUREE, 2.0))
        init(); ims = [Image.frombytes('RGB', (W, H), frame(int(t * FPS))).resize((216, 384)) for t in ts]
        c = Image.new('RGB', (216 * 8, 404 * math.ceil(len(ims) / 8)), BLANC); dd = ImageDraw.Draw(c)
        for j, (im, tt) in enumerate(zip(ims, ts)):
            c.paste(im, ((j % 8) * 216, (j // 8) * 404)); dd.text(((j % 8) * 216 + 4, (j // 8) * 404 + 386), f'{tt:.1f}s', fill=ENCRE)
        c.save(f'{ICI}/planche.jpg'); print('planche ok')
        sys.exit()
    N = int(DUREE * FPS); P = 4; pas = math.ceil(N / P)
    with Pool(P) as pool: pool.map(rendre, [(j * pas, min(N, (j + 1) * pas), j) for j in range(P)])
    open(f'{ICI}/parts.txt', 'w').write(''.join(f"file 'part_{j}.mp4'\n" for j in range(P)))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{ICI}/parts.txt', '-c', 'copy', f'{ICI}/muet.mp4'], check=True)
    json.dump(dict(duree=DUREE, fin_voix=FIN_VOIX, ev=evenements()), open(f'{ICI}/evenements.json', 'w'), indent=1)
    print('ok', DUREE)
