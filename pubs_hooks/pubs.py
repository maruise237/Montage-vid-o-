"""10 pubs KamForms, une par type de hook vu chez @theo.vizuals (ses 10 reels les plus vus).

Les hooks sont repris comme MÉCANIQUES (anticipation, visuel, stitch, danger, stress, illusion,
avant/après, question, valeur, coulisses), pas les extraits des autres créateurs.
Seule capture produit utilisée : la vraie démo du téléphone de kamforms.com (kamforms2/tel).
Faits KamForms utilisés (site) : l'IA crée les questions à partir d'une description, partage dans les
groupes WhatsApp, réponses en privé, 10 formulaires gratuits, réponses illimitées.

Usage : python pubs.py SORTIE_DIR [nom ...]
"""
import json
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1]
QUOI = sys.argv[2:]
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
W, H, FPS, SR = 1080, 1920, 30, 44100

NOIR, GRIS, CREME = (17, 17, 20), (112, 112, 120), (247, 244, 236)
VERT = (15, 111, 60)            # vert du site kamforms.com (« façon simple », badge GRATUIT)
ROUGE = (214, 40, 52)
WA_FOND, WA_VERT, WA_BULLE = (239, 231, 222), (37, 211, 102), (217, 253, 211)


def F(nom, t):
    return _f(nom, int(t))


@lru_cache(None)
def _f(nom, t):
    return ImageFont.truetype(f"{RACINE}/fonts/{nom}", t)


SANS, SERIF, SERIF_R = "InterTight-ExtraBold.ttf", "InstrumentSerif-Italic.ttf", "InstrumentSerif-Regular.ttf"
LOGO = Image.open(f"{RACINE}/assets/logos/kamforms.png").convert("RGBA")


def clamp(x):
    return max(0.0, min(1.0, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def pop(t, t0, d=0.2):
    """0 → 1 avec léger dépassement (apparition)."""
    if t < t0:
        return 0.0
    p = clamp((t - t0) / d)
    return ease(p) + 0.12 * np.sin(p * np.pi)


# ------------------------------------------------------------ démo réelle (téléphone de kamforms.com)

TEL_T = json.load(open(f"{RACINE}/kamforms2/tel/t.json"))


@lru_cache(None)
def _tel(i):
    im = Image.open(f"{RACINE}/kamforms2/tel/{i:04d}.jpg").convert("RGB").crop((80, 430, 1000, 1560))
    return im


def tel(r):
    """Image du téléphone au temps réel r de la capture (cycle propre : 7,6 → 17,0 s)."""
    i = max(0, min(len(TEL_T) - 1, int(np.searchsorted(TEL_T, r, side="right") - 1)))
    return _tel(i)


def demo_r(s, debut=7.6, fin=17.0, vitesse=1.0):
    return min(fin, debut + s * vitesse)


def arrondi(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    im = im.convert("RGBA")
    im.putalpha(m)
    return im


def ombre_portee(img, im, x, y, flou=40, force=90, dy=30):
    sh = Image.new("RGBA", (im.width + 4 * flou, im.height + 4 * flou), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * force // 255)
    sh.paste((0, 0, 0, 255), (2 * flou, 2 * flou), a)
    sh = sh.filter(ImageFilter.GaussianBlur(flou))
    img.alpha_composite(sh, (int(x - 2 * flou), int(y - 2 * flou + dy)))


def coller(img, im, cx, cy, s=1.0, alpha=1.0):
    if s <= 0.01 or alpha <= 0.01:
        return
    im = im.convert("RGBA")
    if s != 1:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    if alpha < 1:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im.putalpha(a)
    img.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def demo_carte(r, largeur=860, rayon=56):
    im = tel(r)
    im = im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)
    return arrondi(im, rayon)


# ------------------------------------------------------------ texte

def lignes(texte, f, largeur):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    out, cur = [], ""
    for m in texte.split():
        essai = (cur + " " + m).strip()
        if d.textlength(essai, font=f) <= largeur or not cur:
            cur = essai
        else:
            out.append(cur)
            cur = m
    return out + [cur]


def bloc(d, texte, x, y, f, fill, largeur=W - 160, centre=False, interligne=1.12):
    for l in lignes(texte, f, largeur):
        tw = d.textlength(l, font=f)
        d.text((x - tw / 2 if centre else x, y), l, font=f, fill=fill)
        y += round(f.size * interligne)
    return y


def calque():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def texte_pop(img, texte, cx, cy, f, fill, t, t0, largeur=W - 160, fond=None, pad=28):
    """Bloc de texte centré qui apparaît en pop (échelle) ; fond = pastille arrondie optionnelle."""
    s = pop(t, t0)
    if s <= 0:
        return
    ls = lignes(texte, f, largeur)
    lh = round(f.size * 1.12)
    tw = max(ImageDraw.Draw(img).textlength(l, font=f) for l in ls)
    c = Image.new("RGBA", (int(tw + 2 * pad), lh * len(ls) + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    if fond:
        d.rounded_rectangle((0, 0, c.width - 1, c.height - 1), 30, fill=fond)
    y = pad - f.size * 0.08
    for l in ls:
        lw = d.textlength(l, font=f)
        d.text(((c.width - lw) / 2, y), l, font=f, fill=fill)
        y += lh
    coller(img, c, cx, cy, s)


def bulle(texte, sortant=False, largeur=560, taille=40, nom=None):
    f = F("InterTight-ExtraBold.ttf", taille) if False else _f_reg(taille)
    ls = lignes(texte, f, largeur - 60)
    lh = round(taille * 1.25)
    tw = max(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=f) for l in ls)
    hn = round(taille * 1.2) if nom else 0
    w, h = int(tw + 56), lh * len(ls) + 36 + hn
    c = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((4, 6, w + 4, h + 6), 26, fill=(0, 0, 0, 30))
    d.rounded_rectangle((0, 0, w, h), 26, fill=WA_BULLE if sortant else (255, 255, 255))
    y = 18
    if nom:
        d.text((28, y), nom, font=_f_reg(round(taille * 0.85)), fill=(30, 150, 90))
        y += hn
    for l in ls:
        d.text((28, y), l, font=f, fill=(30, 30, 34))
        y += lh
    return c


@lru_cache(None)
def _f_reg(t):
    # police lisible pour les bulles de discussion (DejaVu, présente sur le système)
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, t)
    return _f(SANS, t)


# ------------------------------------------------------------ fond & carte de fin

def fond_creme():
    return Image.new("RGBA", (W, H), CREME + (255,))


@lru_cache(None)
def _ciel():
    a = np.zeros((H, W, 3), np.float32)
    haut, bas = np.array([129, 189, 217]), np.array([236, 244, 240])
    k = np.linspace(0, 1, H)[:, None]
    a[:] = (haut * (1 - k) + bas * k)[:, None, :]
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def fond_ciel():
    return _ciel().copy()


def carte_fin(t):
    """Signature de fin commune (t = temps local) : logo, promesse du site, URL, offre gratuite."""
    img = fond_creme()
    coller(img, LOGO.resize((230, 230), Image.LANCZOS), W / 2, 600, pop(t, 0.0, 0.25))
    c = calque()
    d = ImageDraw.Draw(c)
    a = int(255 * ease(t / 0.3))
    f1, f2 = F(SERIF_R, 104), F(SERIF, 104)
    x = W / 2 - (d.textlength("La ", font=f1) + d.textlength("façon simple", font=f2)) / 2
    d.text((x, 790), "La ", font=f1, fill=NOIR + (a,))
    d.text((x + d.textlength("La ", font=f1), 790), "façon simple", font=f2, fill=VERT + (a,))
    tw = d.textlength("de créer des formulaires.", font=f1)
    d.text((W / 2 - tw / 2, 900), "de créer des formulaires.", font=f1, fill=NOIR + (a,))
    img.alpha_composite(c)
    s = pop(t, 0.35)
    if s > 0:
        p = Image.new("RGBA", (560, 120), (0, 0, 0, 0))
        dp = ImageDraw.Draw(p)
        dp.rounded_rectangle((0, 0, 559, 119), 60, fill=NOIR)
        f = F(SANS, 56)
        dp.text((280 - dp.textlength("kamforms.com", font=f) / 2, 26), "kamforms.com", font=f, fill="white")
        coller(img, p, W / 2, 1120, s)
    if t > 0.6:
        d = ImageDraw.Draw(img)
        f = F(SANS, 40)
        txt = "10 formulaires gratuits · Réponses illimitées"
        d.text((W / 2 - d.textlength(txt, font=f) / 2, 1230), txt, font=f, fill=GRIS)
    return img


FIN = 2.2  # durée de la carte de fin


# ------------------------------------------------------------ les 10 pubs
# Chaque pub renvoie (rendu(t) -> Image RGBA, durée, événements son [(t, type)], réglage musique)

def pub_anticipation():
    phrase = "Prise de commande : nom, téléphone WhatsApp, produit, quantité, quartier de livraison"
    T_TAPE, T_FIN_TAPE, T_COMPTE, T_ENTREE, T_DEMO = 0.35, 2.5, 2.6, 4.4, 4.5
    D_DEMO = 4.6
    duree = T_DEMO + D_DEMO + FIN
    ev = [(0.0, "pop")]
    n = len(phrase)
    for k in range(0, n, 3):
        ev.append((T_TAPE + (T_FIN_TAPE - T_TAPE) * k / n, "touche"))
    ev += [(T_COMPTE, "tic"), (T_COMPTE + 0.6, "tic"), (T_COMPTE + 1.2, "tic"), (T_COMPTE + 0.2, "riser16"),
           (T_ENTREE, "impact"), (T_DEMO + D_DEMO, "whoosh")]

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        if t < T_DEMO:
            img = fond_creme()
            d = ImageDraw.Draw(img)
            a = ease(t / 0.25)
            d.text((80, 300), "Regarde ce qui se passe", font=F(SANS, 70), fill=NOIR + (int(255 * a),))
            d.text((80, 385), "quand j'appuie sur Entrée…", font=F(SERIF, 92), fill=VERT + (int(255 * a),))
            # champ de saisie
            c = Image.new("RGBA", (920, 470), (0, 0, 0, 0))
            dc = ImageDraw.Draw(c)
            dc.rounded_rectangle((0, 0, 919, 469), 44, fill=(255, 255, 255), outline=(225, 222, 214), width=3)
            dc.text((48, 36), "Décris ton formulaire", font=F(SANS, 34), fill=GRIS)
            k = int(n * clamp((t - T_TAPE) / (T_FIN_TAPE - T_TAPE)))
            y = 100
            ls = lignes(phrase[:k], _f_reg(44), 820)
            for l in ls:
                dc.text((48, y), l, font=_f_reg(44), fill=NOIR)
                y += 58
            if int(t * 3) % 2 == 0 or t < T_FIN_TAPE:
                xc = 48 + dc.textlength(ls[-1], font=_f_reg(44)) if ls[-1] else 48
                dc.rectangle((xc + 4, y - 56, xc + 8, y - 8), fill=VERT)
            ombre_portee(img, c, 80, 640, 30, 50, 20)
            img.alpha_composite(c, (80, 640))
            # touche Entrée + compte à rebours
            presse = T_ENTREE <= t
            s = 0.92 if presse else 1 + 0.03 * np.sin(t * 9) * (t > T_COMPTE)
            key = Image.new("RGBA", (440, 170), (0, 0, 0, 0))
            dk = ImageDraw.Draw(key)
            dk.rounded_rectangle((0, 0, 439, 169), 40, fill=VERT if presse else NOIR)
            fk = F(SANS, 64)
            dk.text((220 - dk.textlength("Entrée ↵", font=fk) / 2, 44), "Entrée ↵", font=fk, fill="white")
            coller(img, key, W / 2, 1300, s)
            if T_COMPTE <= t < T_ENTREE:
                i = int((t - T_COMPTE) / 0.6)
                chiffre = "321"[min(i, 2)]
                u = ((t - T_COMPTE) % 0.6) / 0.6
                f = F(SANS, round(300 * (1.25 - 0.25 * ease(u * 3))))
                d = ImageDraw.Draw(img)
                d.text((W / 2 - d.textlength(chiffre, font=f) / 2, 1460), chiffre, font=f,
                       fill=VERT + (int(255 * (1 - u * 0.6)),))
            return img
        u = t - T_DEMO
        img = fond_ciel()
        r = demo_r(u, debut=11.0, vitesse=(17.0 - 11.0) / (D_DEMO - 0.4))
        coller(img, demo_carte(r, 900), W / 2, 1120, 0.9 + 0.1 * ease(u / 0.35))
        d = ImageDraw.Draw(img)
        msg = "Une phrase." if u < 2.4 else "Un formulaire prêt."
        f = F(SERIF, 120)
        d.text((W / 2 - d.textlength(msg, font=f) / 2, 250), msg, font=f, fill=NOIR)
        return img
    return rendu, duree, ev, 0


MESSAGES = [
    "slt", "c'est combien ?", "je veux 2", "vous livrez à Odza ?", "le noir est encore là ?",
    "mon quartier c'est Bastos", "j'avais commandé hier ??", "taille M stp", "allô ?", "le même que ma sœur",
    "je passe à quelle heure ?", "c'est pour samedi", "vous avez le rouge ?", "j'envoie le numéro",
    "et la livraison ?", "3 pièces", "vous êtes où ?", "réponds stp", "le prix final ?", "Biyem-Assi",
    "j'ai payé", "c'est bon ?", "je veux changer", "Mvan", "1 de chaque", "encore dispo ?",
]


def mur_de_bulles(t, t0, t_aspire=None, seed=3, n=34):
    """Bulles qui pop partout (t0 → t0+2,4 s), puis aspirées vers le centre à t_aspire."""
    rng = np.random.default_rng(seed)
    c = calque()
    for i in range(n):
        ti = t0 + 2.4 * (i / n) ** 1.3
        if t < ti:
            continue
        x, y = rng.uniform(80, W - 80), rng.uniform(560, H - 220)
        rot = rng.uniform(-8, 8)
        b = bulle(MESSAGES[i % len(MESSAGES)], sortant=bool(i % 3 == 0), taille=40)
        b = b.rotate(rot, expand=True, resample=Image.BICUBIC)
        s = pop(t, ti, 0.15)
        if t_aspire is not None and t > t_aspire:
            k = ease((t - t_aspire) / 0.55)
            x, y = x + (W / 2 - x) * k, y + (1150 - y) * k
            s *= 1 - k
        coller(c, b, x, y, s)
    return c


def carte_formulaire(t, t0, champs=("Nom", "Téléphone WhatsApp", "Produit", "Quantité", "Quartier de livraison")):
    c = Image.new("RGBA", (860, 780), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, 859, 779), 48, fill=(255, 255, 255))
    d.text((56, 50), "Prise de commande", font=F(SANS, 58), fill=NOIR)
    for i, ch in enumerate(champs):
        y = 170 + i * 118
        a = clamp((t - t0 - 0.25 - 0.18 * i) / 0.2)
        if a <= 0:
            continue
        d.rounded_rectangle((56, y, 804, y + 92), 22, fill=(246, 245, 241, int(255 * a)))
        d.text((92, y + 24), ch, font=_f_reg(40), fill=(40, 40, 44, int(255 * a)))
        d.ellipse((730, y + 26, 770, y + 66), fill=VERT + (int(255 * a),))
        d.line((740, y + 47, 748, y + 55, 762, y + 38), fill=(255, 255, 255, int(255 * a)), width=5)
    return c


def pub_visuel():
    T_ASP, T_CARTE, T_DEMO, D_DEMO = 2.9, 3.35, 5.4, 3.4
    duree = T_DEMO + D_DEMO + FIN
    ev = [(0.0, "pop")] + [(2.4 * (i / 34) ** 1.3, "pop_l") for i in range(0, 34, 2)]
    ev += [(T_ASP - 0.1, "whoosh"), (T_CARTE, "impact")] + [(T_CARTE + 0.25 + 0.18 * i, "pop") for i in range(5)]
    ev += [(T_DEMO, "whoosh"), (T_DEMO + D_DEMO, "whoosh")]

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        if t < T_DEMO:
            img = Image.new("RGBA", (W, H), WA_FOND + (255,))
            img.alpha_composite(mur_de_bulles(t, 0.15, T_ASP))
            d = ImageDraw.Draw(img)
            if t < T_ASP:
                texte_pop(img, "Tes commandes sur WhatsApp :", W / 2, 330, F(SANS, 64), NOIR, t, 0.0, fond=(255, 255, 255))
                if t > 1.7:
                    texte_pop(img, "le chaos.", W / 2, 455, F(SERIF, 130), ROUGE, t, 1.7)
            else:
                texte_pop(img, "Avec KamForms :", W / 2, 330, F(SANS, 64), NOIR, t, T_ASP + 0.2, fond=(255, 255, 255))
                texte_pop(img, "un seul formulaire.", W / 2, 455, F(SERIF, 112), VERT, t, T_ASP + 0.35)
                if t >= T_CARTE:
                    carte = carte_formulaire(t, T_CARTE)
                    ombre_portee(img, carte, W / 2 - 430, 760, 40, 60)
                    coller(img, carte, W / 2, 1150, pop(t, T_CARTE, 0.25))
            return img
        u = t - T_DEMO
        img = fond_ciel()
        coller(img, demo_carte(demo_r(u, 7.6, vitesse=9.4 / (D_DEMO - 0.3)), 900), W / 2, 1130)
        d = ImageDraw.Draw(img)
        bloc(d, "Tu le décris, l'IA crée les questions.", W / 2, 230, F(SERIF, 96), NOIR, centre=True)
        return img
    return rendu, duree, ev, 1


def pub_stitch():
    T_SPLIT, D_DEMO = 1.9, 7.0
    duree = T_SPLIT + D_DEMO + FIN
    etapes = [(0.0, "1. Je décris mon formulaire"), (2.4, "2. L'IA crée les questions"),
              (4.6, "3. Je partage le lien dans mes groupes WhatsApp")]
    ev = [(0.0, "pop"), (0.5, "ding"), (T_SPLIT, "whoosh")] + [(T_SPLIT + a, "pop") for a, _ in etapes]
    ev += [(T_SPLIT + D_DEMO, "whoosh")]
    question = "Comment vous faites pour prendre les commandes sans tout mélanger ?"

    def haut(t, h):
        """La « vidéo d'origine » : la question dans un groupe WhatsApp."""
        c = Image.new("RGBA", (W, h), WA_FOND + (255,))
        d = ImageDraw.Draw(c)
        d.rectangle((0, 0, W, 150), fill=(0, 128, 105))
        d.text((60, 52), "Groupe · Les vendeuses de Yaoundé", font=_f_reg(40), fill="white")
        b = bulle(question, taille=48, largeur=880, nom="Une cliente")
        coller(c, b, W / 2 - 10, 150 + (h - 150) / 2, pop(t, 0.5, 0.2))
        return c

    def rendu(t):
        if t >= T_SPLIT + D_DEMO:
            return carte_fin(t - T_SPLIT - D_DEMO)
        img = fond_creme()
        if t < T_SPLIT:
            img.alpha_composite(haut(t, H))
            d = ImageDraw.Draw(img)
            texte_pop(img, "La question que tout vendeur sur WhatsApp se pose :", W / 2, 330, F(SANS, 60), NOIR, t, 0.0,
                      largeur=900, fond=(255, 255, 255))
            return img
        u = t - T_SPLIT
        k = ease(u / 0.35)
        hh = round(H - (H - 760) * k)
        img.alpha_composite(haut(t, hh))
        d = ImageDraw.Draw(img)
        d.rectangle((0, hh, W, hh + 6), fill=NOIR)
        if k >= 1:
            dem = demo_carte(demo_r(u, 7.6, vitesse=9.4 / (D_DEMO - 0.4)), 640, 44)
            coller(img, dem.crop((0, 0, dem.width, min(dem.height, 1000))), W / 2, 760 + 6 + 520)
            for a, txt in reversed(etapes):
                if u >= a:
                    texte_pop(img, txt, W / 2, 1720, F(SANS, 56), "white", t, T_SPLIT + a, largeur=900, fond=NOIR)
                    break
        return img
    return rendu, duree, ev, 2


def pub_danger():
    T_TWIST, T_CALME, D_DEMO = 2.3, 3.7, 4.3
    duree = T_CALME + D_DEMO + FIN
    ev = [(0.0, "sirene"), (0.0, "impact"), (T_TWIST, "impact"), (T_TWIST, "glitch"), (T_CALME, "carillon"),
          (T_CALME + D_DEMO, "whoosh")]

    def triangle(c, cx, cy, s):
        if s < 0.02:
            return
        d = ImageDraw.Draw(c)
        p = [(cx, cy - 170 * s), (cx + 190 * s, cy + 150 * s), (cx - 190 * s, cy + 150 * s)]
        d.polygon(p, fill=(255, 200, 0))
        f = F(SANS, round(230 * s))
        d.text((cx - d.textlength("!", font=f) / 2, cy - 120 * s), "!", font=f, fill=NOIR)

    def rendu(t):
        if t >= T_CALME + D_DEMO:
            return carte_fin(t - T_CALME - D_DEMO)
        if t < T_CALME:
            rouge = int(t * 4) % 2 == 0
            img = Image.new("RGBA", (W, H), ((150, 0, 12) if rouge else (20, 0, 4)) + (255,))
            dx = dy = 0
            if t >= T_TWIST:
                img.alpha_composite(mur_de_bulles(t, T_TWIST - 0.6, None, seed=9, n=26))
                img.alpha_composite(Image.new("RGBA", (W, H), (150, 0, 12, 110)))
                dx, dy = np.random.default_rng(int(t * 30)).integers(-18, 18, 2)
            c = calque()
            triangle(c, W / 2, 470, pop(t, 0.0, 0.18))
            d = ImageDraw.Draw(c)
            f = F(SANS, 150)
            d.text((W / 2 - d.textlength("ATTENTION", font=f) / 2, 700), "ATTENTION", font=f, fill="white")
            if t < T_TWIST:
                bloc(d, "Si tu prends encore tes commandes dans tes messages WhatsApp…", W / 2, 950, F(SANS, 64),
                     "white", largeur=900, centre=True)
            else:
                texte_pop(c, "…un jour, tu vas en oublier une.", W / 2, 1050, F(SERIF, 110), "white", t, T_TWIST,
                          largeur=940, fond=(150, 0, 12))
            img.alpha_composite(c, (int(dx), int(dy)))
            return img
        u = t - T_CALME
        img = fond_ciel()
        d = ImageDraw.Draw(img)
        f = F(SERIF, 120)
        d.text((W / 2 - d.textlength("Fais plutôt ça :", font=f) / 2, 230), "Fais plutôt ça :", font=f, fill=NOIR)
        coller(img, demo_carte(demo_r(u, 7.6, vitesse=9.4 / (D_DEMO - 0.3)), 880), W / 2, 1150, 0.94 + 0.06 * ease(u / 0.3))
        return img
    return rendu, duree, ev, 3


BANNIERES = ["Nouvelle commande ?", "Vous livrez à Mvan ?", "C'est combien le sac ?", "Allô ??",
             "J'ai envoyé mon adresse", "Encore dispo ?", "Réponds stp", "Je veux 3", "Odza c'est loin ?",
             "Tu as vu mon message ?"]


def pub_stress():
    T_STOP, T_DEMO, D_DEMO = 3.3, 4.4, 4.2
    duree = T_DEMO + D_DEMO + FIN
    dings = [3.2 * (1 - (1 - k / 22) ** 0.6) for k in range(22)]
    ev = [(x, "ding") for x in dings] + [(T_STOP, "coupure"), (T_DEMO, "pop"), (T_DEMO + D_DEMO, "whoosh")]

    def telephone(t):
        c = Image.new("RGBA", (680, 1340), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, 679, 1339), 90, fill=(25, 25, 28))
        d.rounded_rectangle((24, 24, 655, 1315), 70, fill=(255, 255, 255))
        d.rectangle((24, 120, 655, 250), fill=(0, 128, 105))
        d.text((70, 160), "WhatsApp", font=_f_reg(50), fill="white")
        n = sum(1 for x in dings if t >= x)
        for i in range(7):
            y = 290 + i * 140
            d.ellipse((60, y, 160, y + 100), fill=(205, 210, 214))
            d.text((190, y + 6), ["Cliente", "Maman Brenda", "Paul", "Inconnu", "Groupe Boutique", "Sandrine", "Client"][i],
                   font=_f_reg(38), fill=NOIR)
            d.text((190, y + 56), BANNIERES[(i + n) % len(BANNIERES)], font=_f_reg(32), fill=GRIS)
            if n > i:
                v = min(99, n * (i + 2) // 2)
                d.ellipse((560, y + 30, 620, y + 90), fill=WA_VERT)
                txt = str(v)
                d.text((590 - d.textlength(txt, font=_f_reg(28)) / 2, y + 44), txt, font=_f_reg(28), fill="white")
        return c

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        if t < T_STOP:
            g = clamp(t / T_STOP)
            img = Image.new("RGBA", (W, H), (int(247 - 40 * g), int(244 - 170 * g), int(236 - 170 * g), 255))
            d = ImageDraw.Draw(img)
            d.text((70, 230), "Samedi soir.", font=F(SERIF, 110), fill=NOIR)
            d.text((70, 360), "Ta boutique sur WhatsApp :", font=F(SANS, 62), fill=NOIR)
            amp = 4 + 26 * g
            rng = np.random.default_rng(int(t * 30))
            coller(img, telephone(t), W / 2 + rng.uniform(-amp, amp), 1330 + rng.uniform(-amp, amp),
                   0.8, 1.0)
            # bannières de notification qui tombent du haut
            k = sum(1 for x in dings if t >= x)
            for j in range(max(0, k - 3), k):
                tj = dings[j]
                y = 520 + (j - max(0, k - 3)) * 120 - 60 * (1 - ease((t - tj) / 0.15))
                b = bulle(BANNIERES[j % len(BANNIERES)], taille=38, largeur=860)
                coller(img, b, W / 2, y)
            badge = "99+" if k > 16 else str(k * 6)
            texte_pop(img, badge, W - 170, 520, F(SANS, 70), "white", t, 0.2, fond=ROUGE, pad=22)
            return img
        if t < T_DEMO:
            img = fond_creme()
            texte_pop(img, "Respire.", W / 2, H / 2 - 60, F(SERIF, 220), NOIR, t, T_STOP + 0.15)
            return img
        u = t - T_DEMO
        img = fond_ciel()
        d = ImageDraw.Draw(img)
        bloc(d, "Un seul lien. Les réponses arrivent en privé.", W / 2, 210, F(SERIF, 96), NOIR, centre=True, largeur=900)
        coller(img, demo_carte(demo_r(u, 9.0, vitesse=8.0 / (D_DEMO - 0.3)), 860), W / 2, 1180)
        return img
    return rendu, duree, ev, 4


def pub_illusion():
    T_REVELE, D_TOTAL = 3.0, 7.6
    duree = D_TOTAL + FIN
    ev = [(0.0, "pop"), (T_REVELE - 0.2, "whoosh"), (T_REVELE + 0.3, "impact"), (D_TOTAL, "whoosh")]
    ev += [(x, "pop_l") for x in (0.9, 1.6, 2.4)]

    def rendu(t):
        if t >= D_TOTAL:
            return carte_fin(t - D_TOTAL)
        img = fond_ciel()
        r = demo_r(t, 7.6, vitesse=9.4 / (D_TOTAL - 0.4))
        dem = demo_carte(r, 900)
        k = ease_io((t - T_REVELE) / 0.7)
        z = 2.0 + (1.0 - 2.0) * k                 # gros plan sur la discussion, puis dézoom
        cy = 1150 + (60 * (1 - k))
        cible = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        coller(cible, dem, W / 2 + 60 * (1 - k), cy, z)
        img.alpha_composite(cible)
        if t < T_REVELE:
            img.alpha_composite(Image.new("RGBA", (W, 745), CREME + (255,)), (0, 0))
            d = ImageDraw.Draw(img)
            bloc(d, "Tu crois que je discute avec un client ?", W / 2, 250, F(SANS, 76), NOIR, centre=True, largeur=900)
        else:
            d = ImageDraw.Draw(img)
            texte_pop(img, "Non.", W / 2, 230, F(SERIF, 140), ROUGE, t, T_REVELE + 0.3)
            if t > T_REVELE + 0.8:
                texte_pop(img, "C'est l'IA de KamForms qui crée mon formulaire.", W / 2, 400, F(SANS, 58), NOIR, t,
                          T_REVELE + 0.8, largeur=900, fond=(255, 255, 255))
        return img
    return rendu, duree, ev, 5


def pub_avant_apres():
    T_APRES, T_DEMO, D_DEMO = 3.0, 6.3, 3.2
    duree = T_DEMO + D_DEMO + FIN
    ev = [(0.0, "pop")] + [(0.3 + 0.35 * i, "pop_l") for i in range(7)] + [(T_APRES - 0.15, "whoosh"),
                                                                        (T_APRES + 0.3, "carillon"),
                                                                        (T_DEMO, "whoosh"), (T_DEMO + D_DEMO, "whoosh")]
    avant = ["slt", "je veux le sac noir", "c combien ?", "vous livrez à Odza ?", "mon nom c'est Brenda",
             "ah non 2 sacs", "j'ai envoyé l'adresse hier"]

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        if t < T_DEMO:
            img = Image.new("RGBA", (W, H), WA_FOND + (255,))
            d = ImageDraw.Draw(img)
            # AVANT
            y = 560
            for i, m in enumerate(avant):
                if t >= 0.3 + 0.35 * i:
                    b = bulle(m, taille=44, largeur=700)
                    coller(img, b, 90 + b.width / 2, y + b.height / 2, pop(t, 0.3 + 0.35 * i, 0.15))
                    y += b.height + 18
            texte_pop(img, "AVANT", W / 2, 400, F(SANS, 90), "white", t, 0.0, fond=ROUGE)
            d.text((W / 2 - d.textlength("Même boutique.", font=F(SERIF, 100)) / 2, 190), "Même boutique.",
                   font=F(SERIF, 100), fill=NOIR)
            if t >= T_APRES - 0.15:
                k = ease((t - (T_APRES - 0.15)) / 0.35)
                volet = Image.new("RGBA", (W, H - 310), CREME + (255,))
                dv = ImageDraw.Draw(volet)
                texte_pop(volet, "AVEC KAMFORMS", W / 2, 70, F(SANS, 84), "white", t, T_APRES, fond=VERT)
                b = carte_reponse()
                coller(volet, b, W / 2, 620, pop(t, T_APRES + 0.3, 0.25))
                if t > T_APRES + 0.8:
                    bloc(dv, "Chaque commande arrive complète, en privé.", W / 2, 1180, F(SERIF, 84), NOIR,
                         centre=True, largeur=880)
                hv = max(1, int((H - 310) * k))
                img.alpha_composite(volet.crop((0, 0, W, hv)), (0, 310))
            return img
        u = t - T_DEMO
        img = fond_ciel()
        d = ImageDraw.Draw(img)
        bloc(d, "Tu décris. L'IA crée les questions.", W / 2, 230, F(SERIF, 100), NOIR, centre=True)
        coller(img, demo_carte(demo_r(u, 11.0, vitesse=6.0 / (D_DEMO - 0.3)), 880), W / 2, 1150)
        return img
    return rendu, duree, ev, 6


def carte_reponse():
    c = Image.new("RGBA", (840, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, 839, 559), 40, fill=(255, 255, 255))
    d.text((50, 40), "Nouvelle réponse · Prise de commande", font=_f_reg(36), fill=VERT)
    for i, (k, v) in enumerate((("Nom", "Brenda"), ("Produit", "Sac noir"), ("Quantité", "2"),
                                ("Quartier", "Odza"))):
        y = 130 + i * 100
        d.text((50, y), k, font=_f_reg(42), fill=GRIS)
        d.text((360, y), v, font=F(SANS, 46), fill=NOIR)
        d.line((50, y + 78, 790, y + 78), fill=(235, 235, 235), width=2)
    return c


def pub_question():
    T_REP, T_DEMO, D_DEMO = 2.5, 3.5, 4.4
    duree = T_DEMO + D_DEMO + FIN
    ev = [(0.0, "pop"), (1.3, "pop"), (1.9, "tic"), (T_REP, "impact"), (T_DEMO, "whoosh"), (T_DEMO + D_DEMO, "whoosh")]

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        if t < T_DEMO:
            img = Image.new("RGBA", (W, H), VERT + (255,))
            d = ImageDraw.Draw(img)
            a = ease(t / 0.25)
            y = bloc(d, "Qui d'autre relit 50 messages", W / 2, 470, F(SANS, 84), (255, 255, 255, int(255 * a)),
                     centre=True, largeur=940)
            y = bloc(d, "pour retrouver UNE adresse de livraison ?", W / 2, y + 10, F(SERIF, 110),
                     (255, 255, 255, int(255 * a)), centre=True, largeur=940)
            for i, lab in enumerate(("Moi", "Moi aussi")):
                s = pop(t, 1.3 + 0.12 * i)
                b = Image.new("RGBA", (380, 130), (0, 0, 0, 0))
                db = ImageDraw.Draw(b)
                choisi = t >= 1.9 and i == 0
                db.rounded_rectangle((0, 0, 379, 129), 65, fill=(255, 255, 255) if not choisi else NOIR)
                f = F(SANS, 56)
                db.text((190 - db.textlength(lab, font=f) / 2, 32), lab, font=f, fill=NOIR if not choisi else "white")
                coller(img, b, W / 2 - 210 + 420 * i, y + 200, s * (0.94 if choisi and t < 2.0 else 1))
            if t >= T_REP:
                texte_pop(img, "Plus besoin.", W / 2, y + 470, F(SERIF, 150), (255, 220, 120), t, T_REP)
            return img
        u = t - T_DEMO
        img = fond_ciel()
        d = ImageDraw.Draw(img)
        bloc(d, "Chaque client remplit son formulaire. Tout est noté.", W / 2, 210, F(SERIF, 92), NOIR, centre=True,
             largeur=920)
        coller(img, demo_carte(demo_r(u, 7.6, vitesse=9.4 / (D_DEMO - 0.3)), 860), W / 2, 1190)
        return img
    return rendu, duree, ev, 7


def pub_valeur():
    champs = ["Nom", "Téléphone WhatsApp", "Produit", "Quantité", "Quartier de livraison"]
    T0, PAS, T_OU, T_DEMO, D_DEMO = 0.6, 0.62, 4.0, 4.9, 4.2
    duree = T_DEMO + D_DEMO + FIN
    ev = [(0.0, "impact")] + [(T0 + PAS * i, "pop") for i in range(5)] + [(T_OU, "whoosh"), (T_DEMO, "pop"),
                                                                        (T_DEMO + D_DEMO, "whoosh")]

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        if t < T_DEMO:
            img = fond_creme()
            d = ImageDraw.Draw(img)
            s = pop(t, 0.0, 0.18)
            c = calque()
            dc = ImageDraw.Draw(c)
            dc.text((70, 230), "5", font=F(SANS, 300), fill=VERT)
            dc.text((290, 270), "questions à mettre", font=F(SANS, 64), fill=NOIR)
            dc.text((290, 350), "dans ton formulaire", font=F(SANS, 64), fill=NOIR)
            dc.text((290, 420), "de commande", font=F(SERIF, 96), fill=VERT)
            coller(img, c, W / 2, H / 2, s)
            for i, ch in enumerate(champs):
                ti = T0 + PAS * i
                if t < ti:
                    continue
                y = 690 + i * 175
                a = ease((t - ti) / 0.2)
                x = 70 + 60 * (1 - a)
                d.text((x, y), f"{i + 1}", font=F(SERIF, 130), fill=VERT + (int(255 * a),))
                d.text((x + 120, y + 40), ch, font=F(SANS, 70), fill=NOIR + (int(255 * a),))
            if t >= T_OU:
                img.alpha_composite(Image.new("RGBA", (W, H), CREME + (int(255 * ease((t - T_OU) / 0.25)),)))
                texte_pop(img, "Ou écris-les en une phrase.", W / 2, 860, F(SERIF, 120), NOIR, t, T_OU, largeur=900)
                texte_pop(img, "KamForms crée le formulaire.", W / 2, 1100, F(SANS, 66), "white", t, T_OU + 0.3,
                          fond=VERT, largeur=900)
            return img
        u = t - T_DEMO
        img = fond_ciel()
        coller(img, demo_carte(demo_r(u, 9.0, vitesse=8.0 / (D_DEMO - 0.3)), 900), W / 2, 1050)
        return img
    return rendu, duree, ev, 8


def pub_coulisses():
    D_DEMO = 8.4
    T_DEMO = 1.6
    duree = T_DEMO + D_DEMO + FIN
    vit = 9.4 / (D_DEMO - 0.4)
    etapes = [(7.6, "Étape 1 · Tu choisis de le décrire"), (10.3, "Étape 2 · Tu écris ce dont tu as besoin"),
              (12.9, "Étape 3 · L'IA te pose une question"), (15.5, "Étape 4 · Elle prépare tes questions"),
              (16.6, "Prêt : 5 questions, en ligne")]
    ev = [(0.0, "clap"), (T_DEMO, "whoosh")] + [(T_DEMO + (r - 7.6) / vit, "pop") for r, _ in etapes]
    ev += [(T_DEMO + D_DEMO, "carillon")]

    def rendu(t):
        if t >= T_DEMO + D_DEMO:
            return carte_fin(t - T_DEMO - D_DEMO)
        img = Image.new("RGBA", (W, H), (22, 22, 24, 255))
        d = ImageDraw.Draw(img)
        if t < T_DEMO:
            # clap de cinéma
            ang = 0 if t > 0.12 else 18 * (1 - t / 0.12)
            c = Image.new("RGBA", (760, 520), (0, 0, 0, 0))
            dc = ImageDraw.Draw(c)
            dc.rectangle((0, 140, 759, 519), fill=(240, 240, 240))
            dc.text((40, 200), "COULISSES", font=F(SANS, 110), fill=NOIR)
            dc.text((40, 340), "Prise : un formulaire KamForms", font=_f_reg(40), fill=NOIR)
            barre = Image.new("RGBA", (760, 120), (0, 0, 0, 0))
            db = ImageDraw.Draw(barre)
            db.rectangle((0, 0, 759, 119), fill=NOIR)
            for i in range(6):
                db.polygon([(i * 140 + 20, 0), (i * 140 + 90, 0), (i * 140 + 40, 119), (i * 140 - 30, 119)],
                           fill=(240, 240, 240))
            barre = barre.rotate(ang, expand=True, center=(0, 119), resample=Image.BICUBIC)
            c.alpha_composite(barre.crop((0, 0, 760, min(140, barre.height))), (0, 0))
            coller(img, c, W / 2, 820)
            bloc(d, "Comment un formulaire KamForms est créé", W / 2, 1180, F(SERIF, 96), "white", centre=True,
                 largeur=900)
        else:
            u = t - T_DEMO
            r = demo_r(u, 7.6, vitesse=vit)
            coller(img, demo_carte(r, 900), W / 2, 1080)
            for rr, txt in reversed(etapes):
                if r >= rr:
                    texte_pop(img, txt, W / 2, 1760, F(SANS, 54), NOIR, t, T_DEMO + (rr - 7.6) / vit,
                              largeur=960, fond=(255, 255, 255))
                    break
        # REC + chrono façon caméra
        if int(t * 2) % 2 == 0:
            d.ellipse((70, 110, 110, 150), fill=ROUGE)
        d.text((130, 106), "REC", font=F(SANS, 44), fill="white")
        tc = f"00:00:{int(t):02d}:{int((t % 1) * 25):02d}"
        d.text((W - 70 - d.textlength(tc, font=_f_reg(40)), 110), tc, font=_f_reg(40), fill="white")
        return img
    return rendu, duree, ev, 9


PUBS = {"01_anticipation": pub_anticipation, "02_visuel": pub_visuel, "03_stitch": pub_stitch,
        "04_danger": pub_danger, "05_stress": pub_stress, "06_illusion": pub_illusion,
        "07_avant_apres": pub_avant_apres, "08_question": pub_question, "09_valeur": pub_valeur,
        "10_coulisses": pub_coulisses}


# ------------------------------------------------------------ son (synthèse maison)

def t_(d):
    return np.arange(int(d * SR)) / SR


def lp(x, a=0.15):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def bruit(d, rng):
    return rng.standard_normal(int(d * SR))


def sfx(nom, rng):
    if nom == "pop":
        x = t_(0.14); return np.sin(2 * np.pi * (500 + 1100 * x) * x) * np.exp(-30 * x) * 0.55
    if nom == "pop_l":
        x = t_(0.1); return np.sin(2 * np.pi * (700 + 900 * x) * x) * np.exp(-40 * x) * 0.25
    if nom == "tic":
        x = t_(0.05); return np.sin(2 * np.pi * 1800 * x) * np.exp(-90 * x) * 0.5
    if nom == "touche":
        x = t_(0.03); return bruit(0.03, rng) * np.exp(-150 * x) * 0.18
    if nom == "ding":
        x = t_(0.35); return (np.sin(2 * np.pi * 1318 * x) + 0.5 * np.sin(2 * np.pi * 1976 * x)) * np.exp(-11 * x) * 0.22
    if nom == "impact":
        x = t_(0.7)
        return (np.sin(2 * np.pi * (45 + 110 * np.exp(-12 * x)) * x) * np.exp(-5 * x) * 0.9
                + bruit(0.7, rng) * np.exp(-25 * x) * 0.25)
    if nom == "whoosh":
        x = t_(0.45); env = np.sin(np.pi * x / 0.45) ** 2
        return lp(bruit(0.45, rng), 0.08) * env * 1.2
    if nom.startswith("riser"):
        d = float(nom[5:]) / 10; x = t_(d)
        return (lp(bruit(d, rng), 0.05) * 1.2 + np.sin(2 * np.pi * (200 + 600 * x / d) * x) * 0.15) * (x / d) ** 2
    if nom == "glitch":
        x = t_(0.3); return np.sign(np.sin(2 * np.pi * 90 * x)) * (rng.random(len(x)) > 0.5) * 0.25 * np.exp(-6 * x)
    if nom == "sirene":
        x = t_(2.3); f = 700 + 250 * np.sign(np.sin(2 * np.pi * 2 * x))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.22 * np.minimum(1, (2.3 - x) * 6)
    if nom == "carillon":
        x = t_(1.4)
        return sum(np.sin(2 * np.pi * f * x) * np.exp(-3 * x) for f in (880, 1320, 1760)) * 0.15
    if nom == "clap":
        x = t_(0.12); return bruit(0.12, rng) * np.exp(-60 * x) * 0.8
    return np.zeros(1)


def musique(duree, reglage, coupures):
    """Boucle lo-fi (basse, accords, charley), tonalité/tempo variés selon la pub, coupée sur `coupures`."""
    rng = np.random.default_rng(reglage)
    n = int(duree * SR)
    s = np.zeros(n)
    bpm = [98, 104, 92, 110, 120, 96, 100, 94, 102, 88][reglage]
    temps = 60 / bpm
    grilles = [[220, 277.2, 329.6], [196, 246.9, 293.7], [174.6, 220, 261.6], [196, 246.9, 293.7]]
    dec = reglage % 4
    k = 0
    while k * temps < duree:
        tt = k * temps
        i = int(tt * SR)
        acc = grilles[((k // 4) + dec) % 4]
        if k % 4 == 0:
            x = t_(temps * 4)
            seg = sum(np.sin(2 * np.pi * f * x) for f in acc) * np.exp(-1.0 * x) * 0.07
            seg += np.sin(2 * np.pi * acc[0] / 2 * x) * np.exp(-1.6 * x) * 0.3
            j = min(n, i + len(seg)); s[i:j] += seg[:j - i]
        if k % 2 == 0:
            x = t_(0.25)
            seg = np.sin(2 * np.pi * (50 + 90 * np.exp(-30 * x)) * x) * np.exp(-14 * x) * 0.5
            j = min(n, i + len(seg)); s[i:j] += seg[:j - i]
        x = t_(0.05)
        seg = rng.standard_normal(len(x)) * np.exp(-90 * x) * 0.05
        i2 = int((tt + temps / 2) * SR); j = min(n, i2 + len(seg))
        if i2 < n:
            s[i2:j] += seg[:j - i2]
        k += 1
    for a, b in coupures:
        ia, ib = int(a * SR), min(n, int(b * SR))
        s[ia:ib] *= 0.0
    return s


def bande_son(duree, ev, reglage, chemin):
    rng = np.random.default_rng(100 + reglage)
    n = int(duree * SR)
    coupures = []
    if reglage == 3:   # danger : la sirène seule, la musique arrive au calme
        coupures = [(0, 3.7)]
    if reglage == 4:   # stress : silence sur « Respire. »
        coupures = [(3.3, 4.4)]
    s = musique(duree, reglage, coupures) * 0.55
    for t0, nom in ev:
        x = sfx(nom, rng)
        i = int(t0 * SR)
        j = min(n, i + len(x))
        if i < n:
            s[i:j] += x[:j - i]
        if nom == "coupure":
            s[i:] *= 1.0
    fondu = np.minimum(1, np.minimum(np.arange(n) / (0.02 * SR), (n - np.arange(n)) / (0.35 * SR)))
    s = s * fondu
    s = (s / (np.abs(s).max() + 1e-9) * 0.85 * 32767).astype(np.int16)
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    for nom, fab in PUBS.items():
        if QUOI and nom not in QUOI:
            continue
        rendu, duree, ev, reglage = fab()
        muet, wav = f"{OUT}/{nom}_muet.mp4", f"{OUT}/{nom}.wav"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                                "-pix_fmt", "yuv420p", muet], stdin=subprocess.PIPE)
        for k in range(int(round(duree * FPS))):
            enc.stdin.write(np.asarray(rendu(k / FPS).convert("RGB")).tobytes())
        enc.stdin.close()
        enc.wait()
        bande_son(duree, ev, reglage, wav)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", muet, "-i", wav, "-af",
                        "loudnorm=I=-13:TP=-1.5:LRA=11,volume=1.5dB,alimiter=limit=0.89", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", f"{OUT}/pub_kamforms_{nom}.mp4"],
                       check=True)
        os.remove(muet)
        os.remove(wav)
        print("ok", nom, round(duree, 1), flush=True)


if __name__ == "__main__":
    main()
