"""Vidéo « mon ennemi / mon fan » (15 s, ambiance sombre). Images : assets/banque/mystere/.
Sous-titres propres en bas (2–3 mots, mot fort en rouge), transitions glitch / flash, chuchotements qui flottent,
révélation de la foule sur « FAN », puis 4 s de musique seule.
Les temps viennent du transcript de Mariuse ; quand la voix off arrive (mystere1/voix.wav), recaler SOUS avec Whisper Cloudflare (temps.json).
Usage : python3 mystere1/montage.py [planche] → mystere1/muet.mp4"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ICI = os.path.dirname(os.path.abspath(__file__)); RAC = os.path.dirname(ICI)
BQ = f'{RAC}/assets/banque/mystere'; FONTS = f'{RAC}/fonts'
W, H, FPS, DUREE = 1080, 1920, 30, 15.0
ROUGE = (226, 38, 43)

# (début, fin, texte, mot en rouge) — recalés par temps.json s'il existe
SOUS = [(0.15, 1.25, 'JE TE CONSIDÉRERAI', None), (1.25, 2.35, 'COMME MON ENNEMI', 'ENNEMI'),
        (2.35, 3.05, 'LE JOUR OÙ', None), (3.05, 3.85, 'TU ASSUMERAS', None), (3.85, 4.6, 'EN FACE', 'FACE'),
        (4.9, 5.75, 'CE QUE TU', None), (5.75, 6.6, 'MURMURES', 'MURMURES'), (6.6, 7.6, 'EN MON ABSENCE.', None),
        (8.0, 9.0, 'EN ATTENDANT,', None), (9.0, 10.1, "TU N'ES QUE", None), (10.1, 11.1, 'MON FAN.', 'FAN.')]
COUPES, BEATS = [4.6, 7.5, 10.68], [10.7, 13.48]
if os.path.exists(f'{ICI}/temps.json'):   # calé sur la vraie voix (Whisper) et les coups de basse de la piste
    _j = json.load(open(f'{ICI}/temps.json'))
    SOUS, COUPES, BEATS, DUREE = [tuple(s) for s in _j['sous']], _j['coupes'], _j['beats'], _j['duree']
T_FAN = next(s[0] for s in SOUS if 'FAN' in s[2])
# scènes : (début, image) ; la dernière revient sur le regard au 2e coup de basse
SC = [(0.0, 'mariuse_capuche_regard_ombre'), (COUPES[0], 'silhouettes_chuchotent_dans_le_dos'),
      (COUPES[1], 'mariuse_projecteur_foule_fans'), (COUPES[2], 'mariuse_part_de_dos_brouillard')]
T_MUS = SC[3][0]                       # la musique seule démarre ici
T_REGARD = next((b for b in BEATS if b > T_MUS + 1.5), DUREE)
SC.append((T_REGARD, 'mariuse_capuche_regard_ombre'))

police = lambda nom, t: ImageFont.truetype(f'{FONTS}/{nom}.ttf', t)
F_SOUS = police('InterTight-ExtraBold', 88)
F_MURM = police('InstrumentSerif-Italic', 72)
F_GEANT = police('InstrumentSerif-Italic', 300)

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
        k = ease((t - t0) / .14); sortie = lisse((t - (t1 - .08)) / .08)
        alpha = k * (1 - sortie)
        mots = txt.split(' '); taille = int(88 * (.86 + .14 * k))
        f = F_SOUS.font_variant(size=taille)
        larg = [f.getlength(m) for m in mots]; esp = f.getlength(' ')
        x = W / 2 - (sum(larg) + esp * (len(mots) - 1)) / 2; y = 1560 + 18 * (1 - k)
        for m, l in zip(mots, larg):
            c = ROUGE if fort and m == fort else (255, 255, 255)
            texte(im, m, f, (x, y), c, alpha, ancre='lm'); x += l + esp

MURMURES = [('il paraît que…', .22, .30, 0), ('tu as vu ?', .70, .24, .35), ('chut…', .78, .44, .7),
            ('lui là…', .20, .50, 1.0), ("on m'a dit que…", .58, .62, 1.35), ('tu savais ?', .30, .70, 1.7)]

def chuchotements(im, t, t0):
    for txt, fx, fy, dt in MURMURES:
        u = t - t0 - dt
        if u < 0 or u > 1.9: continue
        a = lisse(u / .35) * (1 - lisse((u - 1.4) / .5)) * .75
        texte(im, txt, F_MURM, (fx * W + 30 * u, fy * H - 40 * u), (235, 225, 225), a)

def scene(t):
    i = max(k for k, (t0, _) in enumerate(SC) if t >= t0); t0, nom = SC[i]
    t1 = SC[i + 1][0] if i + 1 < len(SC) else DUREE; u = (t - t0) / (t1 - t0)
    if i == 0:      # gros plan qui avance, lumière rouge qui vacille
        im = cadre(nom, 1.12 + .22 * lisse(u), .5, .36)
        fl = 1 + .06 * math.sin(t * 23) * math.sin(t * 7.3)
        im = Image.fromarray((np.asarray(im, np.float32) * fl).clip(0, 255).astype(np.uint8))
    elif i == 1:    # travelling latéral dans la ruelle
        im = cadre(nom, 1.30, .38 + .22 * lisse(u), .50)
    elif i == 2:    # serré sur le visage → on recule et la foule apparaît sur « FAN »
        r = lisse((t - (T_FAN - .35)) / .55)
        im = cadre(nom, 2.6 - 1.55 * r + .05 * u, .5, .43 + .12 * r)
    elif i == 3:    # musique seule : poussée lente + à-coup sur chaque coup de basse
        coup = sum(math.exp(-(t - b) * 5) for b in BEATS if 0 <= t - b < 1.5)
        im = cadre(nom, 1.05 + .18 * u + .05 * coup, .5, .55)
    else:           # retour brutal sur le regard, très serré, qui avance
        im = cadre(nom, 2.3 + .35 * lisse(u), .5, .40)
    return i, t0, im

def image(n):
    t = n / FPS
    i, t0, im = scene(t)
    # transitions : glitch (0→1, 2→3), flash blanc (1→2)
    pres = [abs(t - s[0]) for s in SC[1:]]
    if i == 2 and t - t0 < .25:
        im = Image.blend(im, Image.new('RGB', (W, H), (255, 255, 255)), 1 - (t - t0) / .25)
    elif min(pres) < .14 and i != 4:
        im = glitch(im, 1 - min(pres) / .14, t)
    if i == 4 and t - t0 < .2:  # flash rouge sur le retour du regard
        im = Image.blend(im, Image.new('RGB', (W, H), ROUGE), .7 * (1 - (t - t0) / .2))
    if abs(t - T_FAN) < .5:  # petit choc sur « FAN »
        im = decale_rgb(im, 14 * max(0, 1 - abs(t - T_FAN) / .2))
    if i >= 3:               # bandes cinéma qui entrent + fondu au noir final
        im = im.copy(); bh = int(170 * ease((t - T_MUS) / .6))
        ImageDraw.Draw(im).rectangle((0, 0, W, bh), fill=0); ImageDraw.Draw(im).rectangle((0, H - bh, W, H), fill=0)
    im = grain_vignette(im, t).convert('RGBA')
    if i == 0 and 1.3 < t < 2.6:   # « ENNEMI » géant fantôme derrière, en haut
        a = lisse((t - 1.3) / .25) * (1 - lisse((t - 2.2) / .4)) * .55
        texte(im, 'ennemi', F_GEANT, (W / 2, 250 - 30 * (t - 1.3)), ROUGE, a, ombre=False)
    if i == 1: chuchotements(im, t, t0)
    if i == 2 and t > T_FAN:
        a = lisse((t - T_FAN) / .2) * (1 - lisse((t - (SC[3][0] - .2)) / .2)) * .9
        texte(im, 'fan.', F_GEANT.font_variant(size=360), (W / 2, 330), (255, 255, 255), a)
    if i >= 3:
        a = lisse((t - T_MUS - .5) / .6) * (1 - lisse((t - (DUREE - .9)) / .5))
        texte(im, 'K A M T E C H', police('InterTight-ExtraBold', 44), (W / 2, H - 85), (200, 200, 200), a * .8, ombre=False)
    sous_titre(im, t)
    out = im.convert('RGB')
    if t > DUREE - .5: out = Image.blend(out, Image.new('RGB', (W, H)), lisse((t - (DUREE - .5)) / .5))
    if t < .2: out = Image.blend(Image.new('RGB', (W, H)), out, t / .2)
    return out.tobytes()

if __name__ == '__main__':
    os.chdir(ICI)
    if sys.argv[1:] == ['planche']:
        ts = [.6, 1.8, 3.4, 4.3, 5.0, 6.4, 8.2, 9.5, T_FAN + .4, 12, 13.7, 15.1]
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
    json.dump({'SC': SC, 'T_FAN': T_FAN, 'T_MUS': T_MUS, 'DUREE': DUREE, 'BEATS': BEATS}, open('reperes.json', 'w'))
