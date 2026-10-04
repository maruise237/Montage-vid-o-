"""Reel « 3 outils IA » (vidéo, photo, formulaire) : met KamForms en avant SANS faire pub.

Type (skill §0) : tuto outil / liste. Preuve sociale par association : KamForms est traité exactement
comme KlingAI et Nano Banana (Google) : même format d'écran, même durée, vraie capture du site, vrai logo.
Pas de « mon outil », pas de chiffres inventés.

Structure (sortie, silences coupés : 16,5 s → 11,5 s) :
  hook « VIDÉOS » derrière la tête → écran partagé KlingAI → « PHOTOS » → Nano Banana → « FORMULAIRES »
  → KamForms → récap des 3 liens → CTA champ commentaire.
Usage : python3 kamforms/montage.py  → kamforms/muet.mp4 + evenements.json (pour son.py)
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(ICI)
sys.path.insert(0, f'{RACINE}/outils')
from detourage import alphas

W, H, FPS = 1080, 1920, 30
SW, SH = 1296, 2304                       # source réduite (1728x3072 → ×0,75)
F = lambda n, s: ImageFont.truetype(f'{RACINE}/fonts/{n}', s)
SANS, SERIF_I, SERIF = 'InterTight-ExtraBold.ttf', 'InstrumentSerif-Italic.ttf', 'InstrumentSerif-Regular.ttf'
CREME, ENCRE, GRIS = (243, 238, 228), (20, 20, 20), (110, 104, 96)

# morceaux gardés de la source (début, fin) : silences retirés
SEGS = [(0.33, 2.80), (3.42, 6.02), (7.02, 9.52), (10.92, 14.85)]
OFF = []; o = 0
for a, b in SEGS: OFF.append((o, o + b - a, a - o)); o += b - a
DUREE = o
def src(t):
    for o0, o1, d in OFF:
        if t < o1: return t + d
    return OFF[-1][2] + t
def sortie(ts):
    for (a, b), (o0, o1, d) in zip(SEGS, OFF):
        if a - .05 <= ts <= b: return ts - d
MOTS = [dict(m, o=sortie(m['a']), f=sortie(m['b'])) for m in json.load(open(f'{ICI}/mots.json'))]
MOTS = [m for m in MOTS if m['o'] is not None]
def quand(mot, n=0): return [m['o'] for m in MOTS if m['w'].lower().strip(".,'").startswith(mot)][n]

T_UT = [quand('utilise', k) for k in range(3)]               # « utilise ça » → l'outil apparaît
T_GEN = [quand('génération', k) for k in range(3)]
T_MOT = [quand('vidéos'), quand('photos'), quand('formulaires')]
T_LIENS, T_COMM, T_OUTIL = quand('liens'), quand('commente'), quand('outil')
# écrans : (début, type, données)
ECRANS = [(0, 'hook', 0), (T_UT[0], 'outil', 0), (T_GEN[1] - .35, 'mot', 1), (T_UT[1], 'outil', 1),
          (T_GEN[2] - .35, 'mot', 2), (T_UT[2], 'outil', 2), (T_LIENS - .1, 'recap', 0), (T_COMM - .12, 'cta', 0)]
# caméras virtuelles (zoom, centre x, centre y relatifs à la source)
CAMS = {'hook': (1.00, .52, .42), 'mot1': (1.42, .53, .40), 'mot2': (1.22, .50, .42), 'cta': (1.12, .52, .43)}

OUTILS = [
    dict(nom='KlingAI', sous='génération de vidéos', capture='cap_kling.png', logo='kling.png', fond_carte=(0, 0, 0)),
    dict(nom='Nano Banana', sous='génération de photos', capture='cap_gemini.png', logo='geminisparkle.png',
         fond_carte=(255, 255, 255)),
    dict(nom='KamForms', sous='génération de formulaires', capture='cap_kamforms.png', logo='kamforms.png',
         fond_carte=(255, 255, 255)),
]
GEANTS = ['VIDÉOS', 'photos', 'FORMULAIRES']


def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def pop(x): x = min(1, max(0, x / .18)); return 1.1 * (1 - (1 - x) ** 3) if x < 1 else 1.0


def arrondi(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    im = im.convert('RGBA'); im.putalpha(Image.fromarray(np.minimum(np.asarray(im)[..., 3], np.asarray(m)))); return im


def ombre(im, r=30, a=90):
    pad = r * 2; o = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, a)); sh.putalpha(Image.fromarray((np.asarray(im)[..., 3] * a / 255).astype(np.uint8)))
    o.paste(sh, (pad, pad + 14), sh); o = o.filter(ImageFilter.GaussianBlur(r)); o.alpha_composite(im, (pad, pad)); return o, pad


def icone(o, taille):
    lg = Image.open(f'{RACINE}/assets/logos/{o["logo"]}').convert('RGBA')
    if o['logo'] == 'kling.png':
        lg = arrondi(lg.resize((taille, taille), Image.LANCZOS), int(taille * .23))
    else:
        lg.thumbnail((taille, taille), Image.LANCZOS)
    return lg


def carte_capture(o):
    """Vraie capture du site, en carte arrondie avec ombre (largeur 600 px)."""
    cap = Image.open(f'{ICI}/{o["capture"]}').convert('RGB')
    if o['nom'] == 'KlingAI':           # page sombre : on garde l'en-tête réel et on l'agrandit
        tete = cap.crop((140, 25, 480, 120)); fond = Image.new('RGB', (1075, 1750), (0, 0, 0))
        tete = tete.resize((int(tete.width * 2.6), int(tete.height * 2.6)), Image.LANCZOS)
        fond.paste(tete, ((1075 - tete.width) // 2, 430)); cap = fond
    else:
        cap = cap.crop((0, 0, 1075, 1750))
    cap = cap.resize((600, int(600 * cap.height / cap.width)), Image.LANCZOS)
    return ombre(arrondi(cap, 34))


def en_tete(o, k, t):
    """Bandeau du haut : « 1. » + logo officiel + nom + rôle."""
    im = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((64, 150), f'{k + 1}.', font=F(SERIF_I, 150), fill=GRIS, anchor='ls')
    s = pop(t - .05)
    if s > 0:
        lg = icone(o, max(2, int(104 * s))); im.alpha_composite(lg, (int(196 + 52 - lg.width / 2), int(96 - lg.height / 2)))
    p = ease((t - .08) / .25)
    d.text((326, 134 + 16 * (1 - p)), o['nom'], font=F(SANS, 86), fill=ENCRE + (int(255 * p),), anchor='ls')
    d.text((330, 206), o['sous'], font=F(SERIF_I, 58), fill=GRIS + (int(255 * ease((t - .2) / .25)),), anchor='ls')
    return im


def titre_geant(petit, geant, police, largeur=.94, couleur=(250, 248, 242)):
    tg = 420
    while F(police, tg).getlength(geant) > W * largeur: tg -= 6
    fg = F(police, tg); bb = fg.getbbox(geant); fp = F(SERIF_I, max(58, int(tg * .32))); bp = fp.getbbox(petit)
    hg, hp = bb[3] - bb[1], bp[3] - bp[1]
    im = Image.new('RGBA', (W, hg + hp + 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text(((W - bp[2] + bp[0]) / 2 - bp[0], 16 - bp[1]), petit, font=fp, fill=couleur + (235,))
    y = 16 + hp + 14; d.text(((W - bb[2] + bb[0]) / 2 - bb[0], y - bb[1]), geant, font=fg, fill=couleur + (255,))
    l = im.filter(ImageFilter.GaussianBlur(16)); out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(Image.eval(l, lambda v: v // 3)); out.alpha_composite(im); return out, y, y + hg


def etiquette(petit, geant, police, angle):
    """Mot de l'étape sur une étiquette crème inclinée : lisible sur le pagne sans assombrir l'image."""
    tg = 200 if police == SERIF_I else 150
    while F(police, tg).getlength(geant) > 860: tg -= 4
    fg, fp = F(police, tg), F(SERIF_I, 60); bb = fg.getbbox(geant)
    w = int(fg.getlength(geant)) + 110; h = (bb[3] - bb[1]) + 170
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=CREME + (255,))
    d.text((w / 2, 78), petit, font=fp, fill=GRIS, anchor='ms')
    d.text(((w - fg.getlength(geant)) / 2, 100 - bb[1]), geant, font=fg, fill=ENCRE)
    o, _ = ombre(im, 26, 110)
    return o.rotate(angle, resample=Image.BICUBIC, expand=True)


# ---------- sous-titres : 1 à 3 mots, blancs, sous le menton
def blocs():
    res, cur = [], []
    for m in MOTS:
        cur.append(m)
        if len(cur) == 3 or m['w'][-1] in '.,' or (len(cur) == 2 and len(cur[0]['w'] + m['w']) > 11):
            res.append(cur); cur = []
    if cur: res.append(cur)
    return [(b[0]['o'], (res[i + 1][0]['o'] if i + 1 < len(res) else DUREE), b) for i, b in enumerate(res)]
BLOCS = blocs()
ACCENT = {'vidéos', 'photos', 'formulaires', 'outil', 'description'}
def texte_mot(w): return {'l': "l'", "'outil": 'outil', 't': "t'", "'envoie": 'envoie'}.get(w, w).strip('.,')


def sous_titre(img, t, y, cache_mot=None):
    b = next((b for b in BLOCS if b[0] <= t < b[1]), None)
    if not b: return
    d = ImageDraw.Draw(img); parts = []
    for m in b[2]:
        w = texte_mot(m['w'])
        if cache_mot and w.lower() == cache_mot: continue
        acc = w.lower() in ACCENT
        parts.append((w, F(SERIF_I, 96) if acc else F(SANS, 64), m['o'], m['w'] in ('l', 't')))
    x = (W - sum(f.getlength(w) + (0 if c else 20) for w, f, _, c in parts) + 20) / 2
    for w, f, a, colle in parts:
        if t >= a - .04:
            for dy in (5, 3): d.text((x, y + dy), w, font=f, fill=(0, 0, 0, 150), anchor='ls')
            d.text((x, y), w, font=f, fill=(255, 255, 255), anchor='ls')
        x += f.getlength(w) + (0 if colle else 20)


# ---------- lecture de la source (flux en ordre croissant)
class Source:
    def __init__(s):
        s.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', f'{ICI}/source.mp4', '-vf', f'fps={FPS},scale={SW}:{SH}',
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        s.i = -1; s.img = None
    def get(s, ts):
        n = int(round(ts * FPS))
        while s.i < n:
            b = s.p.stdout.read(SW * SH * 3)
            if len(b) < SW * SH * 3: break
            s.img = b; s.i += 1
        return np.frombuffer(s.img, np.uint8).reshape(SH, SW, 3)


def cadre(img, z, xc, yc, w, h):
    cw = SW / z; ch = cw * h / w
    cx = min(max(SW * xc, cw / 2), SW - cw / 2); y0 = min(max(0, SH * yc - ch * .45), SH - ch)
    return (cx - cw / 2, y0, cx + cw / 2, y0 + ch)


def main():
    src_v = Source()
    # détourage pour le titre derrière la tête : hook seulement
    hook_fin = ECRANS[1][0]
    AL = [a for a in alphas(f'{ICI}/src_hook.mp4', 0, src(hook_fin) + .1, FPS)]
    titre_hook = titre_geant('génération de', 'VIDÉOS', SANS)
    titres = {1: titre_geant('génération de', 'photos', SERIF_I, .9), 2: titre_geant('génération de', 'FORMULAIRES', SANS, .92)}
    cartes = [carte_capture(o) for o in OUTILS]
    recap_logos = [icone(o, 120) for o in OUTILS]
    yy, xx = np.mgrid[0:H, 0:W]
    vign = (1 - .5 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .42) / (H * .65)) ** 2)).clip(.3, 1)[..., None]
    ev = []; vu = {}
    etiquettes = {1: etiquette('génération de', 'photos', SERIF_I, -3), 2: etiquette('génération de', 'FORMULAIRES', SANS, 2)}
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                            '-pix_fmt', 'yuv420p', f'{ICI}/muet.mp4'], stdin=subprocess.PIPE)
    tete_hook = None; n_img = int(DUREE * FPS)
    for i in range(n_img):
        t = i / FPS; ts = src(t); fr = src_v.get(ts)
        k = max(j for j, e in enumerate(ECRANS) if t >= e[0]); e0, typ, x = ECRANS[k]
        e1 = ECRANS[k + 1][0] if k + 1 < len(ECRANS) else DUREE; te = t - e0; pr = (t - e0) / (e1 - e0)
        if typ in ('hook', 'mot', 'cta'):
            z, xc, yc = CAMS['hook' if typ == 'hook' else 'cta' if typ == 'cta' else f'mot{x}']
            z *= 1 + .02 * pr
            box = cadre(fr, z, xc, yc, W, H)
            img = np.asarray(Image.fromarray(fr).resize((W, H), Image.LANCZOS, box=box), np.float32)
            if typ == 'hook':
                a = AL[min(len(AL) - 1, int(round(ts * FPS)))]
                ab = tuple(v * a.shape[1] / SW for v in box)
                al = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR, box=ab), np.float32)[..., None] / 255
                if tete_hook is None:
                    l = np.where(al[:, W // 3:2 * W // 3, 0].max(1) > .6)[0]; tete_hook = int(l[0]) if len(l) else 620
                ti, haut, bas = titre_hook; p = ease(te / .22); s = (1.12 - .12 * p) * (1 + .025 * pr)
                tw, th = int(ti.width * s), int(ti.height * s); tr = np.asarray(ti.resize((tw, th), Image.LANCZOS), np.float32)
                ty = int(tete_hook + .45 * (bas - haut) * s - bas * s); tx = (W - tw) // 2
                c = np.zeros((H, W, 4), np.float32); y0, y1 = max(0, ty), min(H, ty + th)
                c[y0:y1, max(0, tx):max(0, tx) + min(W, tw)] = tr[y0 - ty:y1 - ty, max(0, -tx):max(0, -tx) + min(W, tw)]
                ta = c[..., 3:4] / 255 * p
                fond = np.asarray(Image.fromarray(img.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) * .45 * vign
                fond = fond * (1 - ta) + c[..., :3] * ta
                img = fond * (1 - al) + img * al
                if i == 0: ev.append((0.0, 'titre', 0))
            out = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert('RGBA')
            if typ == 'mot' and t >= T_MOT[x] - .05:      # mot géant devant, au-dessus de la tête
                et = etiquettes[x]; p = pop(t - T_MOT[x] + .05)
                tt = et.resize((max(2, int(et.width * p)), max(2, int(et.height * p))), Image.LANCZOS)
                out.alpha_composite(tt, (int((W - tt.width) / 2), int(330 - tt.height / 2)))
                if not vu.get(('mot', x)): vu[('mot', x)] = 1; ev.append((t, 'mot', x))
            if typ in ('hook', 'mot'):
                ImageDraw.Draw(out).text((64, 210), f'{(0 if typ == "hook" else x) + 1}.', font=F(SERIF_I, 130),
                                         fill=(255, 255, 255, 220), anchor='ls')
            if typ == 'cta':
                cta(out, t, te, ev)
                sous_titre(out, t, 1250, cache_mot=None)
            else:
                sous_titre(out, t, 1330, cache_mot=GEANTS[x].lower() if typ == 'mot' and t >= T_MOT[x] - .05 else None)
        elif typ == 'outil':
            o = OUTILS[x]; out = Image.new('RGBA', (W, H), CREME + (255,))
            # moitié basse : la personne (continue de parler)
            hb = 900; box = cadre(fr, 1.32, .52, .47, W, hb)
            bas = Image.fromarray(fr).resize((W, hb), Image.LANCZOS, box=box)
            out.paste(bas, (0, H - hb))
            # moitié haute : bandeau + vraie capture qui monte
            (carte, pad) = cartes[x]; p = ease(te / .32); dy = int(260 * (1 - p)) - int(70 * pr)
            haut = Image.new('RGBA', (W, H - hb), CREME + (255,))
            rot = carte.rotate((-2.2, 2, -1.6)[x] * (1 - .3 * p), resample=Image.BICUBIC, expand=False)
            haut.alpha_composite(rot, ((W - rot.width) // 2, 280 - pad + dy))
            haut.alpha_composite(en_tete(o, x, te), (0, 0))
            out.paste(haut, (0, 0))
            ImageDraw.Draw(out).line((0, H - hb, W, H - hb), fill=(30, 30, 30), width=4)
            sous_titre(out, t, H - 170)
            if not vu.get(('outil', x)): vu[('outil', x)] = 1; ev += [(e0, 'whoosh', x), (e0 + .05, 'logo', x)]
        elif typ == 'recap':
            out = recap(t, te, recap_logos, ev, e0)
        enc.stdin.write(out.convert('RGB').tobytes())
        if i % 60 == 0: print(f'{t:.1f}/{DUREE:.1f}', flush=True)
    enc.stdin.close(); enc.wait()
    json.dump(dict(duree=DUREE, segs=SEGS, offs=OFF, ecrans=ECRANS, ev=ev), open(f'{ICI}/evenements.json', 'w'), indent=1)


def recap(t, te, logos, ev, e0):
    """Les 3 outils à égalité, liens en description."""
    out = Image.new('RGBA', (W, H), CREME + (255,)); d = ImageDraw.Draw(out)
    p = ease(te / .25)
    d.text((W / 2, 430 - 20 * (1 - p)), 'les liens sont en', font=F(SERIF_I, 82), fill=GRIS + (int(255 * p),), anchor='ms')
    d.text((W / 2, 560 - 20 * (1 - p)), 'DESCRIPTION', font=F(SANS, 128), fill=ENCRE + (int(255 * p),), anchor='ms')
    for j, (o, lg) in enumerate(zip(OUTILS, logos)):
        tj = te - .12 - .14 * j; s = pop(tj)
        if s <= 0: continue
        if 0 <= tj < 1 / FPS: ev.append((e0 + .12 + .14 * j, 'pop', j))
        y = 760 + j * 230
        carte = Image.new('RGBA', (860, 190), (0, 0, 0, 0))
        ImageDraw.Draw(carte).rounded_rectangle((0, 0, 859, 189), 40, fill=(255, 255, 255, 255))
        carte.alpha_composite(lg, (40 + (120 - lg.width) // 2, 35 + (120 - lg.height) // 2))
        dc = ImageDraw.Draw(carte)
        dc.text((200, 92), o['nom'], font=F(SANS, 66), fill=ENCRE, anchor='ls')
        dc.text((202, 150), o['sous'].replace('génération de ', ''), font=F(SERIF_I, 52), fill=GRIS, anchor='ls')
        dc.text((800, 112), '↓', font=F(SANS, 70), fill=ENCRE, anchor='rm')
        cs, pad = ombre(carte, 22, 50)
        cs = cs.resize((int(cs.width * s), int(cs.height * s)), Image.LANCZOS)
        out.alpha_composite(cs, (int(W / 2 - cs.width / 2), int(y + 95 - cs.height / 2)))
    return out


def cta(out, t, te, ev):
    """Champ commentaire où le nom de l'outil se tape (CTA « commente l'outil »)."""
    p = ease(te / .25); y = int(1420 + 120 * (1 - p))
    champ = Image.new('RGBA', (900, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(champ)
    d.rounded_rectangle((0, 0, 899, 149), 75, fill=(255, 255, 255, int(245 * p)))
    mot = 'KamForms'; t0 = T_OUTIL + .05; n = int(max(0, (t - t0) / .07))
    if 0 <= t - t0 < 1 / FPS: ev.append((t0, 'frappe', len(mot) * .07))
    txt = mot[:n]
    if txt:
        d.text((60, 98), txt, font=F(SANS, 60), fill=ENCRE, anchor='ls')
        if int(t * 2.5) % 2 == 0 and n < len(mot): d.line((64 + F(SANS, 60).getlength(txt), 40, 64 + F(SANS, 60).getlength(txt), 110), fill=ENCRE, width=4)
    else:
        d.text((60, 96), 'Ajouter un commentaire…', font=F(SERIF_I, 56), fill=(140, 140, 140, int(255 * p)), anchor='ls')
    envoi = n >= len(mot) and t > t0 + len(mot) * .07 + .25
    d.ellipse((770, 20, 879, 129), fill=(20, 20, 20, int(255 * p)) if envoi else (225, 225, 225, int(255 * p)))
    d.text((824, 78), '↑', font=F(SANS, 64), fill=(255, 255, 255, int(255 * p)), anchor='mm')
    if envoi and t - (t0 + len(mot) * .07 + .25) < 1 / FPS: ev.append((t, 'envoi', 0))
    out.alpha_composite(champ, (90, y))


if __name__ == '__main__':
    main()
