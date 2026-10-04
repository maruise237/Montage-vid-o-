"""Reel « ChatGPT / KamForms » (7,5 s de prise) rallongé à ~10 s par une VRAIE démo de KamForms.

Comment on fait durer sans remplissage :
- les silences sont coupés (la parole reste nerveuse) ;
- après la phrase KamForms, 4,7 s de démo réelle : l'animation du téléphone de kamforms.com, capturée image
  par image (Playwright), accélérée sur les temps morts, avec des étapes écrites à lire (lecture = rétention)
  et la musique qui monte (ponctuation musicale, skill §2bis) ;
- fin sur l'URL, sans écran de fin générique.
Usage : python3 kamforms2/montage.py → kamforms2/muet.mp4 + evenements.json
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(ICI)
sys.path.insert(0, f'{RACINE}/outils')
from detourage import alphas

W, H, FPS = 1080, 1920, 30
SW, SH = 1296, 2304
F = lambda n, s: ImageFont.truetype(f'{RACINE}/fonts/{n}', s)
SANS, SERIF_I = 'InterTight-ExtraBold.ttf', 'InstrumentSerif-Italic.ttf'
CREME, ENCRE, GRIS = (243, 238, 228), (20, 20, 20), (110, 104, 96)

SEGS = [(0.70, 2.85), (3.88, 6.90)]
OFF = []; o = 0
for a, b in SEGS: OFF.append((o, o + b - a, a - o)); o += b - a
FIN_VOIX = o
# démo : (temps réel de la capture début, fin, vitesse)
DEMO = [(6.60, 6.90, 1.0), (6.90, 8.95, 4.0), (8.95, 12.85, 2.0), (12.85, 13.60, 1.0)]
D_DEMO = sum((b - a) / v for a, b, v in DEMO); TENUE = 1.2
DUREE = FIN_VOIX + D_DEMO + TENUE
def reel(u):
    for a, b, v in DEMO:
        d = (b - a) / v
        if u < d: return a + u * v
        u -= d
    return DEMO[-1][1]
def d_de(r):  # instant de démo (sortie) d'un temps réel de capture
    u = 0
    for a, b, v in DEMO:
        if r <= b: return u + max(0, r - a) / v
        u += (b - a) / v
    return u

# mots (Scribe pour le texte, horodatage vérifié)
MOTS = [('ChatGPT', .74, 1.14), ('génère', 1.18, 1.46), ('des', 1.5, 1.6), ('photos', 1.64, 1.9),
        ('personnalisées.', 1.96, 2.68), ('KamForms', 3.98, 4.40), ('génère', 4.42, 4.68), ('des', 4.72, 4.82),
        ('formulaires', 4.86, 5.26), ('interactifs', 5.32, 5.82), ('directement', 5.86, 6.30), ('sur', 6.34, 6.44),
        ('WhatsApp.', 6.48, 6.76)]
def sortie(ts):
    for (a, b), (o0, o1, d) in zip(SEGS, OFF):
        if a - .05 <= ts <= b: return ts - d
MOTS = [(w, sortie(a), sortie(b)) for w, a, b in MOTS]
T = {w.strip('.'): a for w, a, b in MOTS}
T_SPLIT = OFF[1][0]
BLOCS = [(0, 2), (2, 4), (4, 5), (5, 7), (7, 9), (9, 10), (10, 13)]   # 1 à 3 mots
ACCENT = {'photos', 'personnalisées.', 'formulaires', 'interactifs'}

# téléphone capturé sur kamforms.com
TEL_T = json.load(open(f'{ICI}/tel/t.json'))
def image_tel(r):
    i = max(0, min(len(TEL_T) - 1, int(np.searchsorted(TEL_T, r) - 1)))
    return Image.open(f'{ICI}/tel/{i:04d}.jpg').crop((80, 440, 1000, 1290))
EV_TEL = [9.2, 9.44, 10.5, 12.9, 13.12]                  # bulles qui apparaissent (diff d'images)


def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def pop(x): x = min(1, max(0, x / .18)); return 1.1 * (1 - (1 - x) ** 3) if x < 1 else 1.0
def arrondi(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    im = im.convert('RGBA'); im.putalpha(Image.fromarray(np.minimum(np.asarray(im)[..., 3], np.asarray(m)))); return im
def ombre(im, r=30, a=90):
    pad = r * 2; o = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, a)); sh.putalpha(Image.fromarray((np.asarray(im)[..., 3] * a / 255).astype(np.uint8)))
    o.paste(sh, (pad, pad + 14), sh); o = o.filter(ImageFilter.GaussianBlur(r)); o.alpha_composite(im, (pad, pad)); return o, pad
def logo(nom, taille):
    lg = Image.open(f'{RACINE}/assets/logos/{nom}.png').convert('RGBA'); lg.thumbnail((taille, taille), Image.LANCZOS); return lg
def pastille(nom, taille, s):
    """Logo officiel sur pastille blanche, échelle s (pop)."""
    if s <= 0: return None
    lg = logo(nom, max(2, int(taille * s))); m = int(lg.width * .2)
    f = Image.new('RGBA', (lg.width + 2 * m, lg.height + 2 * m), (0, 0, 0, 0))
    ImageDraw.Draw(f).rounded_rectangle((0, 0, f.width - 1, f.height - 1), m * 2, fill=(255, 255, 255, 245))
    f.alpha_composite(lg, (m, m)); return f


def titre_geant(petit, geant):
    tg = 420
    while F(SANS, tg).getlength(geant) > W * .92: tg -= 6
    fg = F(SANS, tg); bb = fg.getbbox(geant); fp = F(SERIF_I, int(tg * .34)); bp = fp.getbbox(petit)
    hg, hp = bb[3] - bb[1], bp[3] - bp[1]
    im = Image.new('RGBA', (W, hg + hp + 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text(((W - bp[2] + bp[0]) / 2 - bp[0], 16 - bp[1]), petit, font=fp, fill=(255, 255, 255, 235))
    y = 16 + hp + 14; d.text(((W - bb[2] + bb[0]) / 2 - bb[0], y - bb[1]), geant, font=fg, fill=(250, 248, 242, 255))
    l = im.filter(ImageFilter.GaussianBlur(16)); out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(Image.eval(l, lambda v: v // 3)); out.alpha_composite(im); return out, y, y + hg


def sous_titre(img, t, y):
    bloc = next(((a, b) for a, b in BLOCS if MOTS[a][1] - .02 <= t < (MOTS[b][1] if b < len(MOTS) else FIN_VOIX)), None)
    if not bloc: return None
    d = ImageDraw.Draw(img); parts = [(w.strip('.,'), F(SERIF_I, 96) if w in ACCENT else F(SANS, 64), a) for w, a, _ in MOTS[bloc[0]:bloc[1]]]
    x = (W - sum(f.getlength(w) + 20 for w, f, _ in parts) + 20) / 2; x0 = x
    for w, f, a in parts:
        if t >= a - .04:
            for dy in (5, 3): d.text((x, y + dy), w, font=f, fill=(0, 0, 0, 150), anchor='ls')
            d.text((x, y), w, font=f, fill=(255, 255, 255), anchor='ls')
        x += f.getlength(w) + 20
    return x0, x - 20


class Source:
    def __init__(s, chemin):
        s.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', chemin, '-vf', f'fps={FPS},scale={SW}:{SH}',
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE); s.i = -1; s.img = None
    def get(s, ts):
        n = int(round(ts * FPS))
        while s.i < n:
            b = s.p.stdout.read(SW * SH * 3)
            if len(b) < SW * SH * 3: break
            s.img = b; s.i += 1
        return np.frombuffer(s.img, np.uint8).reshape(SH, SW, 3)
def cadre(z, xc, yc, w, h):
    cw = SW / z; ch = cw * h / w; cx = min(max(SW * xc, cw / 2), SW - cw / 2); y0 = min(max(0, SH * yc - ch * .45), SH - ch)
    return (cx - cw / 2, y0, cx + cw / 2, y0 + ch)


def main():
    src = Source(f'{ICI}/source.mp4')
    AL = list(alphas(f'{ICI}/src_hook.mp4', 0, SEGS[0][1] + .1, FPS))
    ti, haut_t, bas_t = titre_geant('génère des', 'PHOTOS')
    cap = Image.open(f'{RACINE}/kamforms/cap_kamforms.png').convert('RGB').crop((0, 0, 1075, 1750))
    cap = ombre(arrondi(cap.resize((600, int(600 * cap.height / cap.width)), Image.LANCZOS), 34))
    yy, xx = np.mgrid[0:H, 0:W]
    vign = (1 - .5 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .42) / (H * .65)) ** 2)).clip(.3, 1)[..., None]
    ev = [(T['ChatGPT'], 'logo', 0), (T['photos'], 'titre', 0), (T_SPLIT, 'whoosh', 0), (T_SPLIT + .05, 'logo', 1),
          (T['WhatsApp'], 'logo', 2), (FIN_VOIX, 'whoosh', 1)] + \
         [(FIN_VOIX + d_de(r), 'bulle', k) for k, r in enumerate(EV_TEL)] + [(FIN_VOIX + D_DEMO, 'fin', 0)]
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', f'{ICI}/muet.mp4'], stdin=subprocess.PIPE)
    tete = None
    for i in range(int(DUREE * FPS)):
        t = i / FPS
        if t < T_SPLIT:                                            # ---- 1. ChatGPT, titre derrière la tête
            ts = t + OFF[0][2]; fr = src.get(ts)
            z = 1.0 if t < T['photos'] else 1.14
            z *= 1 + .02 * (t / T_SPLIT)
            box = cadre(z, .5, .42, W, H)
            img = np.asarray(Image.fromarray(fr).resize((W, H), Image.LANCZOS, box=box), np.float32)
            if t >= T['photos'] - .03:
                a = AL[min(len(AL) - 1, int(round(ts * FPS)))]; ab = tuple(v * a.shape[1] / SW for v in box)
                al = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR, box=ab), np.float32)[..., None] / 255
                if tete is None:
                    l = np.where(al[:, W // 3:2 * W // 3, 0].max(1) > .6)[0]; tete = int(l[0]) if len(l) else 600
                te = t - T['photos'] + .03; p = ease(te / .22); s = 1.12 - .12 * p + .02 * te
                tw, th = int(ti.width * s), int(ti.height * s); tr = np.asarray(ti.resize((tw, th), Image.LANCZOS), np.float32)
                ty = int(tete + .45 * (bas_t - haut_t) * s - bas_t * s); tx = (W - tw) // 2
                c = np.zeros((H, W, 4), np.float32); y0, y1 = max(0, ty), min(H, ty + th)
                c[y0:y1, max(0, tx):max(0, tx) + min(W, tw)] = tr[y0 - ty:y1 - ty, max(0, -tx):max(0, -tx) + min(W, tw)]
                ta = c[..., 3:4] / 255 * p
                k = 1 - (1 - .45) * p                               # assombrissement léger, progressif
                fond = np.asarray(Image.fromarray(img.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * p)), np.float32) * (k * (1 - p + p * vign))
                fond = fond * (1 - ta) + c[..., :3] * ta
                img = fond * (1 - al) + img * al
            out = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert('RGBA')
            xs = sous_titre(out, t, 1320)
            if T['ChatGPT'] - .02 <= t < T['photos']:               # mention rapide : logo qui pop sous le sous-titre
                pa = pastille('chatgpt', 120, pop(t - T['ChatGPT'] + .02))
                if pa: out.alpha_composite(pa, (int(W / 2 - pa.width / 2), int(1400)))
        elif t < FIN_VOIX:                                         # ---- 2. KamForms : écran partagé
            te = t - T_SPLIT; pr = te / (FIN_VOIX - T_SPLIT); fr = src.get(t + OFF[1][2])
            out = Image.new('RGBA', (W, H), CREME + (255,)); hb = 900
            out.paste(Image.fromarray(fr).resize((W, hb), Image.LANCZOS, box=cadre(1.32, .5, .47, W, hb)), (0, H - hb))
            haut = Image.new('RGBA', (W, H - hb), CREME + (255,)); (carte, pad) = cap; p = ease(te / .32)
            rot = carte.rotate(-1.8 * (1 - .3 * p), resample=Image.BICUBIC)
            haut.alpha_composite(rot, ((W - rot.width) // 2, 280 - pad + int(260 * (1 - p)) - int(80 * pr)))
            d = ImageDraw.Draw(haut); s = pop(te - .05)
            if s > 0:
                lg = logo('kamforms', max(2, int(104 * s))); haut.alpha_composite(lg, (int(120 - lg.width / 2), int(110 - lg.height / 2)))
            q = ease((te - .08) / .25)
            d.text((200, 146 + 16 * (1 - q)), 'KamForms', font=F(SANS, 88), fill=ENCRE + (int(255 * q),), anchor='ls')
            d.text((204, 218), 'formulaires sur WhatsApp', font=F(SERIF_I, 58), fill=GRIS + (int(255 * ease((te - .2) / .25)),), anchor='ls')
            out.paste(haut, (0, 0)); ImageDraw.Draw(out).line((0, H - hb, W, H - hb), fill=(30, 30, 30), width=4)
            sous_titre(out, t, H - 190)
            if t >= T['WhatsApp'] - .02:
                pa = pastille('whatsapp', 96, pop(t - T['WhatsApp'] + .02))
                if pa: out.alpha_composite(pa, (int(W - 60 - pa.width), int(H - hb + 60)))
        else:                                                      # ---- 3. démo réelle
            u = t - FIN_VOIX; r = reel(min(u, D_DEMO)); out = Image.new('RGBA', (W, H), CREME + (255,))
            tel = image_tel(r); z = 1.12 + .06 * min(1, u / (D_DEMO + TENUE))
            tel = arrondi(tel.resize((int(tel.width * z), int(tel.height * z)), Image.LANCZOS), 44)
            sh, pad = ombre(tel, 30, 70); p = ease(u / .3)
            out.alpha_composite(sh, (int(W / 2 - sh.width / 2), int(450 - pad + 220 * (1 - p))))
            d = ImageDraw.Draw(out)
            etape = ('1.', 'tu décris', 'ton formulaire en une phrase') if r < 12.85 else ('2.', "l'IA crée", 'les questions pour toi')
            if u >= D_DEMO: etape = ('3.', 'tu partages', 'le lien dans tes groupes WhatsApp')
            ke = 0 if r < 12.85 else 1 if u < D_DEMO else 2
            t_e = [0, d_de(12.9), D_DEMO][ke]; q = ease((u - t_e) / .22)
            d.text((80, 250 + 18 * (1 - q)), etape[0], font=F(SERIF_I, 150), fill=GRIS + (int(255 * q),), anchor='ls')
            d.text((210, 230 + 18 * (1 - q)), etape[1], font=F(SANS, 104), fill=ENCRE + (int(255 * q),), anchor='ls')
            d.text((214, 310 + 18 * (1 - q)), etape[2], font=F(SERIF_I, 62), fill=GRIS + (int(255 * q),), anchor='ls')
            if u >= D_DEMO:                                        # fin : l'URL, sobre
                s = pop(u - D_DEMO)
                pil = Image.new('RGBA', (560, 130), (0, 0, 0, 0)); dp = ImageDraw.Draw(pil)
                dp.rounded_rectangle((0, 0, 559, 129), 65, fill=ENCRE + (255,))
                dp.text((280, 66), 'kamforms.com', font=F(SANS, 64), fill=(255, 255, 255), anchor='mm')
                pil = pil.resize((max(2, int(560 * s)), max(2, int(130 * s))), Image.LANCZOS)
                out.alpha_composite(pil, (int(W / 2 - pil.width / 2), int(1600 - pil.height / 2)))
                if s > 0 and i % 1 == 0: pass
        enc.stdin.write(out.convert('RGB').tobytes())
        if i % 60 == 0: print(f'{t:.1f}/{DUREE:.1f}', flush=True)
    enc.stdin.close(); enc.wait()
    json.dump(dict(duree=DUREE, segs=SEGS, offs=OFF, fin_voix=FIN_VOIX, ev=ev), open(f'{ICI}/evenements.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
