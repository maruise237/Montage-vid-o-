"""Vidéo « ne t'énerve jamais » (20,9 s, ambiance calme et sombre : or + bleu-vert). Images : assets/banque/calme/.
Sous-titres en bas calés sur Whisper (temps.json), mot fort en or ; coupes sur les kicks de la piste de Mariuse,
ragots qui flottent autour de lui, « moi… moi… » qui se perdent dans la salle vide, « personne. » géant,
puis drop final : sourire, bandes cinéma, à-coups sur les kicks, KAMTECH, fondu au noir.
Usage : python3 calme1/montage.py [planche] → calme1/muet.mp4"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ICI = os.path.dirname(os.path.abspath(__file__)); RAC = os.path.dirname(ICI)
BQ = f'{RAC}/assets/banque/calme'; FONTS = f'{RAC}/fonts'
W, H, FPS = 1080, 1920, 30
OR = (246, 184, 60)

_j = json.load(open(f'{ICI}/temps.json'))   # Whisper + kicks de la piste
SOUS, BEATS, DUREE, T_DROP = [tuple(x) for x in _j['sous']], _j['beats'], _j['duree'], _j['drop']
T_PERS = next(x[0] for x in SOUS if 'PERSONNE' in x[2])
T_EUX = next(x[0] for x in SOUS if 'MÊMES' in x[2])
# scènes : (début, image) — coupes sur les kicks
SC = [(0.0, 'mariuse_calme_yeux_fermes'), (3.39, 'poster_sali_boue'), (5.0, 'mariuse_entoure_bavards'),
      (8.27, 'scene_vide_micro'), (T_PERS - .1, 'scene_vide_micro'), (T_DROP, 'mariuse_sourire_assure'),
      (17.22, 'mariuse_entoure_bavards'), (18.03, 'mariuse_sourire_assure')]

police = lambda nom, t: ImageFont.truetype(f'{FONTS}/{nom}.ttf', t)
F_SOUS = police('InterTight-ExtraBold', 88)
F_MURM = police('InstrumentSerif-Italic', 72)
F_GEANT = police('InstrumentSerif-Italic', 300)
F_KAM = police('InterTight-ExtraBold', 44)

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lisse(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

_cache = {}
def source(nom):
    if nom not in _cache:  # base 2x (1536x2688) pour zoomer sans flou
        _cache[nom] = Image.open(f'{BQ}/{nom}.png').convert('RGB').resize((1536, 2688), Image.LANCZOS)
    return _cache[nom]

def cadre(nom, zoom, cx, cy):
    """zoom 1 = image entière ; (cx, cy) centre en fraction de l'image."""
    im = source(nom); w, h = im.size
    cw, ch = w / zoom, h / zoom
    x0 = min(max(cx * w - cw / 2, 0), w - cw); y0 = min(max(cy * h - ch / 2, 0), h - ch)
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)

rng = np.random.default_rng(3)
GRAIN = [Image.fromarray((rng.normal(0, 14, (H // 2, W // 2))).clip(-40, 40).astype(np.int16).astype(np.uint8) + 0, 'L')
         for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
VIGN = Image.fromarray((255 * (1 - .55 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2).clip(0, 1))).astype(np.uint8), 'L')

def grain_vignette(im, t):
    g = GRAIN[int(t * FPS) % 6].resize((W, H), Image.NEAREST)
    a = np.asarray(im, np.int16) + (np.asarray(g, np.int16).astype(np.int8)[..., None] * .6).astype(np.int16)
    a = a * (np.asarray(VIGN, np.float32)[..., None] / 255)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def decale_rgb(im, d):
    if d < 1: return im
    r, g, b = im.split(); d = int(d)
    return Image.merge('RGB', (ImageChops.offset(r, d, 0), g, ImageChops.offset(b, -d, 0)))

def glitch(im, force, t):
    """bandes horizontales décalées + séparation RGB."""
    if force <= 0: return im
    im = decale_rgb(im, 26 * force)
    a = np.asarray(im).copy(); r = np.random.default_rng(int(t * 1000))
    for _ in range(int(9 * force)):
        y = r.integers(0, H - 120); hh = r.integers(12, 110); dx = int(r.integers(-160, 160) * force)
        a[y:y + hh] = np.roll(a[y:y + hh], dx, axis=1)
    return Image.fromarray(a)

def texte(draw_im, txt, police_, xy, couleur, alpha, ombre=True, ancre='mm'):
    calque = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(calque)
    if ombre:
        o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).text((xy[0], xy[1] + 6), txt, font=police_, fill=(0, 0, 0, int(200 * alpha)), anchor=ancre)
        calque = Image.alpha_composite(calque, o.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(calque)
    d.text(xy, txt, font=police_, fill=couleur + (int(255 * alpha),), anchor=ancre)
    draw_im.alpha_composite(calque)

def sous_titre(im, t):
    for t0, t1, txt, fort in SOUS:
        if not (t0 <= t < t1): continue
        k = ease((t - t0) / .14); alpha = k * (1 - lisse((t - (t1 - .08)) / .08))
        mots = txt.split(' '); f = F_SOUS.font_variant(size=int(88 * (.86 + .14 * k)))
        larg = [f.getlength(m) for m in mots]; esp = f.getlength(' ')
        x = W / 2 - (sum(larg) + esp * (len(mots) - 1)) / 2; y = 1560 + 18 * (1 - k)
        for m, l in zip(mots, larg):
            texte(im, m, f, (x, y), OR if fort and m == fort else (255, 255, 255), alpha, ancre='lm'); x += l + esp

RAGOTS = [('il se prend pour qui ?', .26, .22, 0), ('tu as vu ?', .74, .30, .4), ('lui là…', .20, .42, .8),
          ("il paraît que…", .76, .52, 1.2), ('franchement…', .30, .62, 1.6), ('on dit que…', .68, .70, 2.0)]
MOI = [('moi…', .30, .30, 0), ('moi, je…', .72, .36, .35), ('écoutez-moi…', .40, .46, .7), ('moi !', .66, .25, 1.0)]

def flottants(im, t, t0, liste, couleur, vie=1.9):
    for txt, fx, fy, dt in liste:
        u = t - t0 - dt
        if u < 0 or u > vie: continue
        a = lisse(u / .35) * (1 - lisse((u - (vie - .5)) / .5)) * .75
        texte(im, txt, F_MURM, (fx * W + 30 * u, fy * H - 40 * u), couleur, a)

def coup(t):   # à-coup qui retombe après chaque kick
    return sum(math.exp(-(t - b) * 6) for b in BEATS if 0 <= t - b < 1.2)

def scene(t):
    i = max(k for k, (t0, _) in enumerate(SC) if t >= t0); t0, nom = SC[i]
    t1 = SC[i + 1][0] if i + 1 < len(SC) else DUREE; u = (t - t0) / (t1 - t0)
    if i == 0:      # yeux fermés, poussée très lente, la lumière respire
        im = cadre(nom, 1.05 + .18 * lisse(u), .5, .40)
        fl = 1 + .04 * math.sin(t * 2.2)
        im = Image.fromarray((np.asarray(im, np.float32) * fl).clip(0, 255).astype(np.uint8))
    elif i == 1:    # l'affiche salie : on descend le long des coulures
        im = cadre(nom, 1.35 + .1 * u, .52, .36 + .14 * lisse(u))
    elif i == 2:    # lui au centre, on recule pour montrer tous ceux qui le pointent
        im = cadre(nom, 1.9 - .75 * lisse(u), .5, .42)
    elif i == 3:    # salle vide : on avance lentement vers celui qui parle seul
        im = cadre(nom, 1.1 + .7 * lisse(u), .5, .62 + .1 * lisse(u))
    elif i == 4:    # « personne » : on recule d'un coup, la salle vide s'assombrit
        r = ease((t - t0) / .7)
        im = cadre(nom, 1.8 - .8 * r, .5, .72 - .22 * r)
        nuit = 1 - .75 * lisse((t - (SOUS[-1][1] - .2)) / (T_DROP - SOUS[-1][1]))
        im = Image.fromarray((np.asarray(im, np.float32) * nuit).astype(np.uint8))
    elif i == 6:    # rappel : il reste debout au milieu des bavards
        im = cadre(nom, 1.6 + .08 * coup(t), .5, .40)
    else:           # drop : sourire, poussée + à-coups sur les kicks
        z = 1.15 if i == 5 else 1.75
        im = cadre(nom, z + .2 * u + .06 * coup(t), .5, .36 if i == 5 else .30)
    return i, t0, im

def image(n):
    t = n / FPS
    i, t0, im = scene(t)
    pres = min(abs(t - s[0]) for s in SC[1:5])
    if pres < .12:                        # glitch doux aux coupes parlées
        im = glitch(im, .7 * (1 - pres / .12), t)
    if i >= 5 and t - t0 < .22:           # flash doré sur les coupes du drop
        f = (1 if i == 5 else .5) * (1 - (t - t0) / .22)
        im = Image.blend(im, Image.new('RGB', (W, H), (255, 236, 190)), f)
    if i >= 5:                            # bandes cinéma
        im = im.copy(); bh = int(170 * ease((t - T_DROP) / .6))
        ImageDraw.Draw(im).rectangle((0, 0, W, bh), fill=0); ImageDraw.Draw(im).rectangle((0, H - bh, W, H), fill=0)
        im = decale_rgb(im, 10 * max(0, 1 - min(abs(t - b) for b in BEATS) / .1))
    im = grain_vignette(im, t).convert('RGBA')
    if i == 0 and .9 < t < 2.3:           # « jamais. » fantôme derrière
        a = lisse((t - .9) / .25) * (1 - lisse((t - 1.9) / .4)) * .5
        texte(im, 'jamais.', F_GEANT, (W / 2, 260 - 30 * (t - .9)), OR, a, ombre=False)
    if i == 2: flottants(im, t, t0, RAGOTS, (235, 230, 220))
    if i == 3 and t > T_EUX - .3: flottants(im, t, T_EUX - .3, MOI, (170, 205, 210), vie=1.6)
    if i == 4:
        a = lisse((t - t0) / .3) * (1 - lisse((t - (T_DROP - .5)) / .4)) * .9
        texte(im, 'personne.', F_GEANT.font_variant(size=230), (W / 2, 330 - 12 * (t - t0)), (255, 255, 255), a)
    if i >= 5:
        a = lisse((t - T_DROP - .5) / .6) * (1 - lisse((t - (DUREE - .9)) / .5))
        texte(im, 'K A M T E C H', F_KAM, (W / 2, H - 85), (210, 200, 180), a * .8, ombre=False)
    sous_titre(im, t)
    out = im.convert('RGB')
    if t > DUREE - .6: out = Image.blend(out, Image.new('RGB', (W, H)), lisse((t - (DUREE - .6)) / .6))
    if t < .2: out = Image.blend(Image.new('RGB', (W, H)), out, t / .2)
    return out.tobytes()

if __name__ == '__main__':
    os.chdir(ICI)
    if sys.argv[1:] == ['planche']:
        ts = [.5, 1.3, 3.8, 4.6, 5.6, 7.4, 9.0, 11.2, 12.4, 14.0, 15.3, 17.5]
        ims = [Image.frombytes('RGB', (W, H), image(int(x * FPS))).resize((270, 480)) for x in ts]
        p = Image.new('RGB', (270 * 6, 480 * 2))
        for k, m in enumerate(ims): p.paste(m, (270 * (k % 6), 480 * (k // 6)))
        p.save('planche.jpg', quality=85); print('planche.jpg'); sys.exit()
    n = int(DUREE * FPS)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', 'muet.mp4'], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for k, b in enumerate(p.imap(image, range(n), chunksize=4)):
            ff.stdin.write(b)
            if k % 90 == 0: print(f'{k}/{n}', flush=True)
    ff.stdin.close(); ff.wait(); print('muet.mp4')
    json.dump({'SC': SC, 'T_DROP': T_DROP, 'T_EUX': T_EUX, 'T_PERS': T_PERS, 'DUREE': DUREE, 'BEATS': BEATS}, open('reperes.json', 'w'))
