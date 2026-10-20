"""Série de mèmes marketing KamForms (format « page mème » : légende noire sur fond blanc,
mème en dessous, petite signature kamforms.com).

Clips sources : Tenor (YouTube est bloqué depuis le conteneur), rangés dans DL.
Les faits KamForms viennent du site : l'IA crée les questions à partir d'une description,
partage dans les groupes WhatsApp, réponses en privé, 10 formulaires gratuits.

Usage : python memes.py DOSSIER_CLIPS DOSSIER_SORTIE [nom ...]
"""
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

DL, OUT = sys.argv[1:3]
QUOI = sys.argv[3:]
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS, SR = 1080, 1920, 30, 44100
NOIR, GRIS = (17, 17, 20), (110, 110, 118)
MARGE = 72


def police(nom, taille):
    return ImageFont.truetype(f"{RACINE}/fonts/{nom}", taille)


GRAS = lambda t: police("InterTight-ExtraBold.ttf", t)
SERIF = lambda t: police("InstrumentSerif-Italic.ttf", t)
LOGO_KF = Image.open(f"{RACINE}/assets/logos/kamforms.png").convert("RGBA")
LOGO_GF = Image.open(f"{RACINE}/assets/logos/googleforms.png").convert("RGBA")


def clip(nom, crop=None, vitesse=1.0):
    """Images du clip Tenor (RGB), recadrées, au rythme FPS (ralenti si vitesse < 1)."""
    vf = [f"setpts=PTS/{vitesse}", f"fps={FPS}"]
    if crop:
        vf.insert(0, "crop={}:{}:{}:{}".format(*crop))
    src = f"{DL}/{nom}.mp4"
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", src],
                                   capture_output=True, text=True).stdout.strip().split(","))
    if crop:
        w, h = crop[0], crop[1]
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", ",".join(vf), "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return [Image.fromarray(a) for a in np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w, 3)]


def a_la_largeur(im, largeur):
    return im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)


def lignes(d, texte, f, largeur):
    mots, out, cur = texte.split(), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if d.textlength(essai, font=f) <= largeur:
            cur = essai
        else:
            out.append(cur)
            cur = m
    return out + [cur]


def legende(d, texte, y, taille=64, couleur=NOIR, f=None):
    """Légende alignée à gauche (style page mème). Renvoie le bas du bloc."""
    f = f or GRAS(taille)
    for l in lignes(d, texte, f, W - 2 * MARGE):
        d.text((MARGE, y), l, font=f, fill=couleur)
        y += round(f.size * 1.18)
    return y


def signature(img, y):
    lg = LOGO_KF.resize((58, 58), Image.LANCZOS)
    img.paste(lg, (MARGE, y), lg)
    ImageDraw.Draw(img).text((MARGE + 74, y + 8), "kamforms.com", font=GRAS(36), fill=GRIS)


def pop(t, t0, duree=0.18):
    """Échelle d'apparition 0 → 1 avec léger dépassement."""
    if t < t0:
        return 0.0
    p = min(1.0, (t - t0) / duree)
    return p + 0.18 * np.sin(p * np.pi)


def coller_centre(img, im, cx, cy, echelle=1.0):
    if echelle <= 0.01:
        return
    im = im.resize((max(1, round(im.width * echelle)), max(1, round(im.height * echelle))), Image.LANCZOS)
    img.paste(im, (round(cx - im.width / 2), round(cy - im.height / 2)), im if im.mode == "RGBA" else None)


def soustitre_meme(d, texte, cx, y_bas, largeur, taille=50):
    """Texte blanc contour noir, en bas de la vidéo (comme un sous-titre de mème)."""
    f = GRAS(taille)
    ls = lignes(d, texte, f, largeur)
    y = y_bas - len(ls) * round(taille * 1.15)
    for l in ls:
        tw = d.textlength(l, font=f)
        d.text((cx - tw / 2, y), l, font=f, fill="white", stroke_width=5, stroke_fill="black")
        y += round(taille * 1.15)


# ---------------------------------------------------------------- les mèmes

def drake():
    im = clip("drake-hotline-bling-meme_5")
    cell = 540

    def carre(x, x0):
        s = x.height
        return x.crop((x0, 0, x0 + s, s)).resize((cell, cell), Image.LANCZOS)

    def aller_retour(a, b, x0):
        seg = [carre(f, x0) for f in im[round(a * FPS):round(b * FPS)]]
        return seg + seg[::-1]
    # le clip est la danse : Drake refuse à gauche du cadre (0,8–1,1 s), sourit à droite (2,2–2,6 s)
    non, oui = aller_retour(0.8, 1.1, 0), aller_retour(2.2, 2.6, im[0].width - im[0].height)
    duree = 6.5

    def rendu(t):
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        y = legende(d, "Pour prendre les commandes de ta boutique :", 300)
        y0 = y + 50
        for i, (photo, logo, nom, t0) in enumerate(((non, LOGO_GF, "Un lien Google Forms", 0.0),
                                                    (oui, LOGO_KF, "KamForms dans tes groupes WhatsApp", 2.2))):
            yy = y0 + i * cell
            if t < t0:
                continue
            img.paste(photo[int((t - t0) * FPS) % len(photo)], (0, yy))
            lg = logo.resize((round(logo.width * 190 / logo.height), 190), Image.LANCZOS)
            coller_centre(img, lg, W - cell / 2, yy + 175, pop(t, t0 + 0.15))
            f = GRAS(42)
            for k, l in enumerate(lignes(d, nom, f, cell - 80)):
                tw = d.textlength(l, font=f)
                d.text((W - cell / 2 - tw / 2, yy + 300 + k * 50), l, font=f, fill=NOIR)
        d.line((0, y0 + cell, W, y0 + cell), fill=(225, 225, 228), width=3)
        signature(img, y0 + 2 * cell + 40)
        return img
    return rendu, duree, [0.15, 2.35], 96


def leo():
    im = clip("leonardo-dicaprio-pointing_2")
    duree = 5.5

    def rendu(t):
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        y = legende(d, "Moi quand je vois un formulaire KamForms dans le groupe WhatsApp du quartier :", 300)
        v = a_la_largeur(im[int(t * FPS) % len(im)], W)
        img.paste(v, (0, y + 40))
        signature(img, y + 40 + v.height + 40)
        return img
    return rendu, duree, [], 104


def panik():
    im = clip("panik-kalm-panik_5", crop=(550, 480, 45, 0), vitesse=0.7)
    t_kalm = 1.55 / 0.7
    duree = 6.5

    def rendu(t):
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        if t < t_kalm:
            y = legende(d, "Le client : « Il me faut un formulaire de commande pour ce soir »", 300)
        else:
            y = legende(d, "Moi : je le décris à KamForms, l'IA crée les questions", 300)
        v = im[min(int(t * FPS), len(im) - 1)]
        v = v.resize((round(v.width * 980 / v.height), 980), Image.LANCZOS)
        img.paste(v, ((W - v.width) // 2, max(y + 40, 640)))
        signature(img, max(y + 40, 640) + 980 + 30)
        return img
    return rendu, duree, [t_kalm], 88


def cricket():
    im = clip("disappointed-cricket-fan_4", crop=(560, 320, 37, 0), vitesse=0.8)
    t_rep = 1.6
    duree = 6.0

    def rendu(t):
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        y = legende(d, "Mon lien Google Forms partagé il y a une semaine :", 300)
        v = a_la_largeur(im[min(int(t * FPS), len(im) - 1)], W)
        img.paste(v, (0, y + 40))
        yb = y + 40 + v.height
        if t >= t_rep:
            e = pop(t, t_rep)
            f = GRAS(round(120 * max(e, 0.01)))
            txt = "Réponses : 3"
            tw = d.textlength(txt, font=f)
            d.text((W / 2 - tw / 2, yb + 60), txt, font=f, fill=(214, 40, 52))
        if t >= 3.6:
            legende(d, "Partage-le plutôt dans tes groupes WhatsApp avec KamForms.", yb + 240, 46, GRIS)
        signature(img, yb + 420)
        return img
    return rendu, duree, [t_rep, 3.6], 80


def bernie():
    im = clip("bernie-sanders-once-again-asking_1", crop=(400, 290, 50, 55), vitesse=0.85)
    duree = 6.0

    def rendu(t):
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        y = legende(d, "Moi dans le groupe WhatsApp de la famille :", 300)
        v = a_la_largeur(im[int(t * FPS) % len(im)], W)
        img.paste(v, (0, y + 40))
        if t >= 0.4:
            soustitre_meme(d, "Je vous demande encore une fois de remplir mon formulaire", W / 2,
                           y + 40 + v.height - 40, W - 140)
        signature(img, y + 40 + v.height + 40)
        return img
    return rendu, duree, [0.4], 76


def rock():
    im = clip("the-rock-eyebrow_3")
    duree = 5.5

    def rendu(t):
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        y = legende(d, "Quand on me dit que Google Forms suffit pour prendre les commandes sur WhatsApp :", 300)
        v = a_la_largeur(im[min(int(t * FPS), len(im) - 1)], W)
        img.paste(v, (0, y + 40))
        signature(img, y + 40 + v.height + 40)
        return img
    return rendu, duree, [], 92


MEMES = {"1_drake": drake, "2_leo": leo, "3_panik_kalm": panik, "4_cricket": cricket,
         "5_bernie": bernie, "6_rock": rock}


# ---------------------------------------------------------------- son

def bande_son(duree, pops, bpm, chemin, graine):
    """Petite boucle lo-fi synthétisée (basse + accords + charley) et un pop sur chaque apparition.
    À remplacer dans l'appli par un son tendance si besoin."""
    rng = np.random.default_rng(graine)
    n = int(duree * SR)
    s = np.zeros(n)
    t = lambda d: np.arange(int(d * SR)) / SR
    def add(sig, t0, g=1.0):
        i = int(t0 * SR)
        j = min(n, i + len(sig))
        if i < n:
            s[i:j] += g * sig[:j - i]
    temps = 60 / bpm
    racines = [[220, 277.2, 329.6], [196, 246.9, 293.7], [174.6, 220, 261.6], [196, 246.9, 293.7]]
    racines = racines[graine % 2:] + racines[:graine % 2]
    k = 0
    while k * temps < duree:
        tt = k * temps
        acc = racines[(k // 4) % 4]
        if k % 4 == 0:
            for f in acc:
                x = t(temps * 4)
                add(np.sin(2 * np.pi * f * x) * np.exp(-1.2 * x) * 0.09, tt)
            x = t(temps * 2)
            add(np.sin(2 * np.pi * acc[0] / 2 * x) * np.exp(-2 * x) * 0.35, tt)
        if k % 2 == 0:
            x = t(0.25)
            add(np.sin(2 * np.pi * (50 + 90 * np.exp(-30 * x)) * x) * np.exp(-14 * x) * 0.6, tt)
        x = t(0.05)
        add(rng.standard_normal(len(x)) * np.exp(-90 * x) * 0.05, tt + temps / 2)
        k += 1
    for p in pops:
        x = t(0.16)
        add(np.sin(2 * np.pi * (520 + 900 * x) * x) * np.exp(-26 * x) * 0.5, p)
    fondu = np.minimum(1, np.minimum(np.arange(n) / (0.05 * SR), (n - np.arange(n)) / (0.3 * SR)))
    s = (s * fondu / (np.abs(s).max() + 1e-9) * 0.8 * 32767).astype(np.int16)
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(s.tobytes())


def centre(rendu, duree):
    """Centre verticalement le bloc légende + mème + signature (mesuré sur la dernière image),
    dans la zone visible entre l'en-tête et la légende de l'appli (≈ 220–1600 px)."""
    a = np.asarray(rendu(duree - 1 / FPS).convert("L"))
    lignes_pleines = np.flatnonzero((a < 245).any(1))
    haut, bas = lignes_pleines[0], lignes_pleines[-1]
    dy = round((220 + 1600) / 2 - (haut + bas) / 2)

    def decale(t):
        img = Image.new("RGB", (W, H), "white")
        img.paste(rendu(t), (0, dy))
        return img
    return decale


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, (nom, fab) in enumerate(MEMES.items()):
        if QUOI and nom not in QUOI:
            continue
        rendu, duree, pops, bpm = fab()
        rendu = centre(rendu, duree)
        muet, wav = f"{OUT}/{nom}_muet.mp4", f"{OUT}/{nom}.wav"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                                "-preset", "medium", "-pix_fmt", "yuv420p", muet], stdin=subprocess.PIPE)
        for k in range(int(duree * FPS)):
            enc.stdin.write(np.asarray(rendu(k / FPS).convert("RGB")).tobytes())
        enc.stdin.close()
        enc.wait()
        bande_son(duree, pops, bpm, wav, i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", muet, "-i", wav, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11,volume=2dB,alimiter=limit=0.89", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "44100", "-shortest", f"{OUT}/meme_kamforms_{nom}.mp4"], check=True)
        os.remove(muet)
        os.remove(wav)
        print("ok", nom, flush=True)


if __name__ == "__main__":
    main()
