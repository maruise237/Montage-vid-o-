"""Version 2 des 10 pubs KamForms : chaque pub OUVRE sur le vrai hook viral repéré dans les 10 reels les
plus vus de @theo.vizuals (extrait de la vidéo), avec une légende française qui relie l'image au problème
des vendeurs sur WhatsApp, puis une TRANSITION calée sur l'action (flash sur l'impact, whip, zoom, carte,
glitch) vers le contenu KamForms (repris de pubs.py à partir d'un décalage) et la carte de fin.

Usage : python pubs_v2.py DOSSIER_REELS SORTIE_DIR [n ...]   (n = 01..10)
"""
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw

REELS, OUT = sys.argv[1:3]
QUOI = sys.argv[3:]
sys.argv = [sys.argv[0], OUT]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pubs as P  # noqa: E402

W, H, FPS, SR = P.W, P.H, P.FPS, P.SR
D_TR = 0.4  # durée de la transition

# rang = classement par vues des reels de Theo ; segs = passages gardés (s) ; caps = légendes (t, texte)
SPECS = {
    "01": dict(src="DdE-CVfOdnU", hook="anticipation", segs=[(0.0, 3.0)],
               caps=[(0.0, "Ta boutique quand toutes les commandes passent par tes messages WhatsApp :")],
               trans="whip", pub="02_visuel", off=0.15),
    "02": dict(src="DdzXvSrOLTA", hook="anticipation", segs=[(0.5, 2.2), (9.6, 12.8)],
               caps=[(0.0, "Moi qui appuie sur Entrée dans KamForms…"),
                     (1.7, "…et tout le bazar des commandes s'effondre.")],
               trans="flash", pub="01_anticipation", off=4.4),
    "03": dict(src="Dd18EpaOFb_", hook="stress", segs=[(0.8, 5.0)],
               caps=[(0.0, "Moi qui gère 50 commandes à la fois dans mes messages WhatsApp :")],
               trans="whip", pub="05_stress", off=0.3),
    "04": dict(src="Dc4G45kugdW", hook="danger", segs=[(0.4, 3.5)],
               caps=[(0.0, "Si tu prends encore tes commandes dans tes messages WhatsApp…"),
                     (2.0, "…ça finit toujours comme ça.")],
               trans="flash", pub="04_danger", off=3.7),
    "05": dict(src="Ddo78efOZFk", hook="anticipation", segs=[(2.4, 6.6)], cap_y=1340,
               caps=[(0.0, "Mes clients quand je partage mon formulaire KamForms dans le groupe :")],
               trans="zoom", pub="08_question", off=3.5),
    "06": dict(src="DduM5aZOcLA", hook="stress", segs=[(8.5, 12.7)],
               caps=[(0.0, "Moi qui garde toutes les commandes de la semaine dans ma tête :")],
               trans="zoom", pub="09_valeur", off=0.0),
    "07": dict(src="Dd7DJXmuX-u", hook="anticipation", segs=[(9.6, 13.6)],
               caps=[(0.0, "Ma tête après avoir relu 50 messages pour retrouver UNE adresse :")],
               trans="flash", pub="03_stitch", off=0.0),
    "08": dict(src="DeFWAu0uV0Y", hook="illusion", segs=[(4.3, 6.0), (8.0, 11.2)],
               caps=[(0.0, "Tout n'est pas ce qu'il paraît…")],
               trans="carte", pub="06_illusion", off=0.0),
    "09": dict(src="DdrpUqqOyM7", hook="avant/après", segs=[(22.3, 25.0), (26.2, 28.4)],
               caps=[(0.0, "Ma boutique WhatsApp avant KamForms…"), (2.7, "…et après.")],
               trans="carte", pub="07_avant_apres", off=0.0),
    "10": dict(src="DeCzvKsOqPz", hook="messed up", segs=[(0.0, 4.2)], cap_y=540,
               caps=[(0.0, "Moi qui lance ma boutique sans formulaire de commande :")],
               trans="glitch", pub="10_coulisses", off=0.0),
}


def extraire(spec, dossier):
    """Images du hook (1080x1920, jpg) et son (wav mono) des passages choisis."""
    os.makedirs(dossier, exist_ok=True)
    src = f"{REELS}/{spec['src']}.mp4"
    n = 0
    sons = []
    for k, (a, b) in enumerate(spec["segs"]):
        sub = f"{dossier}/s{k}"
        os.makedirs(sub, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", src, "-vf",
                        f"fps={FPS},scale={W}:{H}:flags=lanczos", "-q:v", "3", f"{sub}/%05d.jpg"], check=True)
        imgs = sorted(os.listdir(sub))
        for f in imgs:
            os.rename(f"{sub}/{f}", f"{dossier}/{n:05d}.jpg")
            n += 1
        os.rmdir(sub)
        w = f"{dossier}/a{k}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", src, "-ac", "1", "-ar",
                        str(SR), w], check=True)
        with wave.open(w) as f:
            x = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
        m = int(0.03 * SR)  # micro fondu entre deux passages
        if len(x) > 2 * m:
            x[:m] *= np.linspace(0, 1, m)
            x[-m:] *= np.linspace(1, 0, m)
        sons.append(x)
    return n, np.concatenate(sons)


def flou_h(im, force):
    """Flou de bougé horizontal (whip)."""
    if force < 1.5:
        return im
    k = max(1, int(W / force))
    return im.resize((k, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def transition(kind, a, b, p, t):
    """a = dernière image du hook, b = image du contenu, p ∈ [0,1]."""
    a, b = a.convert("RGBA"), b.convert("RGBA")
    if kind == "whip":
        x = int(-W * P.ease_io(p))
        img = Image.new("RGBA", (W, H))
        img.alpha_composite(a, (x, 0))
        img.alpha_composite(b, (x + W, 0))
        return flou_h(img, 1 + 60 * np.sin(np.pi * p))
    if kind == "flash":
        rng = np.random.default_rng(int(t * 1000))
        base = a if p < 0.35 else b
        dx, dy = (rng.integers(-28, 28, 2) * (1 - p)).astype(int)
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        s = 1.0 + 0.08 * (1 - p)
        coller_plein(img, base, s, dx, dy)
        blanc = 1 - abs(p - 0.35) / 0.65 if p > 0.35 else p / 0.35
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * np.clip(blanc, 0, 1)))))
        return img
    if kind == "zoom":
        img = Image.new("RGBA", (W, H))
        coller_plein(img, b, 1.25 - 0.25 * P.ease(p))
        za = a.copy()
        za.putalpha(int(255 * (1 - P.ease(p))))
        coller_plein(img, za, 1 + 1.6 * P.ease_io(p))
        return img
    if kind == "carte":
        img = b.copy()
        s = 1 - 0.7 * P.ease_io(p)
        c = P.arrondi(a.convert("RGB"), int(60 + 40 * p)).resize((max(1, int(W * s)), max(1, int(H * s))))
        y = H / 2 - 1400 * P.ease_io(max(0, p - 0.35) / 0.65)
        P.ombre_portee(img, c, W / 2 - c.width / 2, y - c.height / 2, 30, 80)
        img.alpha_composite(c, (int(W / 2 - c.width / 2), int(y - c.height / 2)))
        return img
    if kind == "glitch":
        base = a if p < 0.5 else b
        r, g, bl, al = base.split()
        d = int(30 * np.sin(np.pi * p))
        r = ImageChops.offset(r, d, 0)
        bl = ImageChops.offset(bl, -d, 0)
        img = Image.merge("RGBA", (r, g, bl, al))
        rng = np.random.default_rng(int(t * 1000))
        for _ in range(5):
            y0 = int(rng.integers(0, H - 80))
            h = int(rng.integers(20, 80))
            band = img.crop((0, y0, W, y0 + h))
            img.paste(band, (int(rng.integers(-60, 60)), y0))
        return img
    return b


def coller_plein(img, im, s, dx=0, dy=0):
    if s != 1:
        im = im.resize((int(W * s), int(H * s)), Image.BILINEAR)
    img.alpha_composite(im, (int((W - im.width) / 2 + dx), int((H - im.height) / 2 + dy)))


def legende(img, spec, t):
    caps = spec["caps"]
    cur = [c for c in caps if t >= c[0]]
    if not cur:
        return
    t0, txt = cur[-1]
    P.texte_pop(img, txt, W / 2, spec.get("cap_y", 330), P.F(P.SANS, 62), P.NOIR, t, t0, largeur=900,
                fond=(255, 255, 255))


def son_transition(kind):
    rng = np.random.default_rng(5)
    if kind == "flash":
        return P.sfx("impact", rng)
    if kind == "glitch":
        return P.sfx("glitch", rng)
    return P.sfx("whoosh", rng)


def fabriquer(cle):
    spec = SPECS[cle]
    nom = f"hook{cle}_{spec['hook'].replace('/', '_').replace(' ', '_')}"
    tmp = f"{OUT}/_tmp_{cle}"
    n_hook, son_hook = extraire(spec, tmp)
    T_H = n_hook / FPS
    rendu, duree_pub, ev, reglage = P.PUBS[spec["pub"]]()
    off = spec["off"]
    duree = T_H + (duree_pub - off)
    images_hook = [f"{tmp}/{i:05d}.jpg" for i in range(n_hook)]

    def hook(t):
        i = min(n_hook - 1, int(t * FPS))
        img = Image.open(images_hook[i]).convert("RGBA")
        legende(img, spec, t)
        return img

    muet = f"{OUT}/{nom}_muet.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                            "-pix_fmt", "yuv420p", muet], stdin=subprocess.PIPE)
    derniere = hook(T_H - 1 / FPS)
    for k in range(int(round(duree * FPS))):
        t = k / FPS
        if t < T_H:
            img = hook(t)
        else:
            u = t - T_H
            b = rendu(off + u)
            img = transition(spec["trans"], derniere, b, u / D_TR, t) if u < D_TR else b
        enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    enc.stdin.close()
    enc.wait()

    # son : hook d'origine → bruitage de transition → bande son du contenu à partir du décalage
    wav_pub = f"{tmp}/pub.wav"
    P.bande_son(duree_pub, ev, reglage, wav_pub)
    with wave.open(wav_pub) as f:
        contenu = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
    contenu = contenu[int(off * SR):]
    m = int(0.08 * SR)
    contenu[:m] *= np.linspace(0, 1, m)
    n = int(duree * SR) + SR
    s = np.zeros(n)
    hk = son_hook / (np.abs(son_hook).max() + 1e-9) * 0.8
    hk[-int(0.12 * SR):] *= np.linspace(1, 0, int(0.12 * SR))
    s[:len(hk)] += hk
    i0 = int(T_H * SR)
    s[i0:i0 + len(contenu)] += contenu[: n - i0] * 0.9
    tr = son_transition(spec["trans"])
    j0 = max(0, i0 - int(0.12 * SR))
    s[j0:j0 + len(tr)] += tr[: n - j0]
    s = s[: int(duree * SR)]
    s = (s / (np.abs(s).max() + 1e-9) * 0.9 * 32767).astype(np.int16)
    wav = f"{tmp}/final.wav"
    with wave.open(wav, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", muet, "-i", wav, "-af",
                    "loudnorm=I=-13:TP=-1.5:LRA=11,volume=1dB,alimiter=limit=0.89", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "44100", "-shortest", f"{OUT}/pub_kamforms_{nom}.mp4"], check=True)
    os.remove(muet)
    subprocess.run(["rm", "-rf", tmp])
    print("ok", nom, round(duree, 1), "hook", round(T_H, 1), flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for cle in SPECS:
        if not QUOI or cle in QUOI:
            fabriquer(cle)
