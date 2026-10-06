"""Mème « Jerry a choisi son parfum » → KamForms vs Google Forms.

Plan fixe : on efface les deux flacons (fond reconstruit), on pose les logos officiels
avec leur nom dessous, et on remet Jerry par-dessus (détourage par couleur : orange + contour noir).
Jerry finit collé au flacon de GAUCHE → KamForms à gauche.

Usage : python montage.py SOURCE.mp4 SORTIE_SANS_SON.mp4
"""
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

SRC, OUT = sys.argv[1:3]
RACINE = __file__.rsplit("/", 2)[0]
W, H, FPS = 720, 1280, 30
T_CHOIX = 6.2  # Jerry se colle à KamForms

# Zones des flacons d'origine (x0, y0, x1, y1), ombres et reflets compris
FLACON_G = (60, 445, 282, 905)
FLACON_D = (448, 435, 672, 905)
FILIGRANE = (70, 78, 165, 172)  # petit logo du compte d'origine, en haut à gauche
SOL_HAUT, SOL_BAS = 832, 912  # bande des ombres portées au sol, refaite à la verticale


def lire_images():
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)


def fond_propre(images):
    """Médiane temporelle puis interpolation ligne par ligne à travers les flacons."""
    med = np.median(images[::3], axis=0).astype(np.float32)
    plaque = med.copy()
    cols = np.arange(W)
    for x0, y0, x1, y1 in (FLACON_G, FLACON_D, FILIGRANE):
        for y in range(y0, min(y1, SOL_HAUT)):
            a, b = med[y, x0 - 6:x0].mean(0), med[y, x1:x1 + 6].mean(0)
            k = ((cols[x0:x1] - x0) / (x1 - x0))[:, None]
            plaque[y, x0:x1] = a * (1 - k) + b * k
    # Ombres au sol : la ligne propre du dessous, décalée de la variation mesurée au bord gauche
    # (zone jamais couverte), pour ne pas reprendre les pieds de Jerry de la médiane.
    bas = med[SOL_BAS]
    for y in range(SOL_HAUT, SOL_BAS):
        plaque[y, 55:W] = bas[55:W] + (med[y, 25:50].mean(0) - bas[25:50].mean(0))
    plaque = np.asarray(Image.fromarray(plaque.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
    # le flou ne doit toucher que les zones refaites
    masque = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in (FLACON_G, FLACON_D, FILIGRANE):
        masque[y0:y1, x0 - 3:x1 + 3] = True
    masque[SOL_HAUT:SOL_BAS, 55:] = True
    out = med.astype(np.uint8)
    out[masque] = plaque[masque]
    return out


def police(nom, taille):
    return ImageFont.truetype(f"{RACINE}/fonts/{nom}", taille)


def produit(img, logo, cx, bas, hauteur, nom):
    """Logo debout sur la table : ombre de contact, reflet sur la table vernie, nom dessous."""
    lg = Image.open(logo).convert("RGBA")
    w = round(lg.width * hauteur / lg.height)
    lg = lg.resize((w, hauteur), Image.LANCZOS)
    x, y = cx - w // 2, bas - hauteur
    # ombre portée douce, vers la droite comme celle des flacons d'origine
    ombre = Image.new("L", img.size, 0)
    ImageDraw.Draw(ombre).ellipse((x + 4, bas - 10, x + w + 40, bas + 12), fill=120)
    ombre = ombre.filter(ImageFilter.GaussianBlur(9))
    img.paste(Image.new("RGB", img.size, (95, 100, 108)), (0, 0), ombre)
    # reflet : logo retourné, transparence qui s'éteint vers le bas
    refl = lg.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, w, min(70, hauteur)))
    fondu = np.linspace(0.16, 0, refl.height)[:, None] * np.asarray(refl.split()[3]) / 255
    refl.putalpha(Image.fromarray((fondu * 255).astype(np.uint8)))
    img.paste(refl, (x, bas + 2), refl)
    img.paste(lg, (x, y), lg)
    d = ImageDraw.Draw(img)
    f = police("InterTight-ExtraBold.ttf", 36)
    tw = d.textlength(nom, font=f)
    d.text((cx - tw / 2, bas + 28), nom, font=f, fill=(28, 28, 32))
    return (x, y, x + w, bas)


def masque_jerry(im):
    """Jerry = orange/brun/beige + son contour noir + le blanc des yeux (trous bouchés)."""
    r, g, b = (im[..., i].astype(np.int16) for i in range(3))
    zone = np.zeros(r.shape, bool)
    zone[540:900, 230:500] = True
    coeur = (r - b > 55) & (r > 100) & zone
    coeur = ndi.binary_opening(coeur, iterations=1)
    v = np.maximum(np.maximum(r, g), b)
    noir = (v < 95) & (b - r < 25) & ndi.binary_dilation(coeur, iterations=7)
    m = ndi.binary_closing(coeur | noir, iterations=3)
    m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n:
        tailles = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(tailles > 150))
    a = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    return np.asarray(a, np.float32)[..., None] / 255


def legende(t):
    """Calque texte : la question du mème en haut, « Et toi ? » qui tombe au moment du choix."""
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    gras = police("InterTight-ExtraBold.ttf", 54)
    d.text((64, 236), "Jerry a choisi son", font=gras, fill=(24, 24, 28))
    d.text((64, 298), "outil de formulaires.", font=gras, fill=(24, 24, 28))
    if t >= T_CHOIX:
        p = min(1, (t - T_CHOIX) / 0.18)
        echelle = 1 + 0.25 * (1 - p) * np.sin(p * np.pi)  # petit pop
        f = police("InstrumentSerif-Italic.ttf", round(78 * echelle))
        d.text((64, 362), "Et toi ?", font=f, fill=(24, 24, 28))
    return c


def badge(img, boite, t):
    """Cœur rouge qui pop sur KamForms quand Jerry le choisit."""
    if t < T_CHOIX:
        return
    p = min(1, (t - T_CHOIX) / 0.2)
    r = round(30 * (p + 0.3 * np.sin(p * np.pi)))
    x, y = boite[2] - 10, boite[1] + 8
    c = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 255))
    h = r * 0.62
    pts = [(x + h * 16 * np.sin(a) ** 3 / 17, y - h * (13 * np.cos(a) - 5 * np.cos(2 * a) - 2 * np.cos(3 * a) - np.cos(4 * a)) / 17 + 2)
           for a in np.linspace(0, 2 * np.pi, 60)]
    d.polygon(pts, fill=(235, 52, 64, 255))
    img.alpha_composite(c)


def main():
    images = lire_images()
    scene = Image.fromarray(fond_propre(images))
    boite_kf = produit(scene, f"{RACINE}/assets/logos/kamforms.png", 171, 846, 206, "KamForms")
    produit(scene, f"{RACINE}/assets/logos/googleforms.png", 559, 846, 250, "Google Forms")
    scene = np.asarray(scene, np.float32)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17",
                            "-preset", "slow", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    for i, im in enumerate(images):
        t = i / FPS
        a = masque_jerry(im)
        img = Image.fromarray((im * a + scene * (1 - a)).astype(np.uint8)).convert("RGBA")
        badge(img, boite_kf, t)
        img.alpha_composite(legende(t))
        enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
