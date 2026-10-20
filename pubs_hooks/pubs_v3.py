"""Version 3 des 10 pubs KamForms (retour de Mariuse) :
- chaque pub ouvre sur le vrai hook viral repris des 10 reels les plus vus de @theo.vizuals (pubs_v2.SPECS),
  avec une transition calée sur l'action ;
- KamForms est présenté comme ce qu'il est : un OUTIL DE FORMULAIRES pour tout (inscriptions, événements,
  avis, dons, formations, institutions), créé depuis le téléphone. Sa différence : les réponses arrivent sur
  WhatsApp (« Redirection WhatsApp ») et une notification arrive sur le téléphone pour qui a l'appli ;
- les écrans sont les VRAIES captures de l'appli publiées sur kamforms.com (pubs_hooks/site/).

Usage : python pubs_v3.py DOSSIER_REELS SORTIE_DIR [01 ..]
"""
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REELS, OUT = sys.argv[1:3]
QUOI = sys.argv[3:]
sys.argv = [sys.argv[0], REELS, OUT]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pubs_v2 as V2  # noqa: E402
P = V2.P
W, H, FPS, SR = P.W, P.H, P.FPS, P.SR
ICI = os.path.dirname(os.path.abspath(__file__))
SITE = f"{ICI}/site"
NOIR, GRIS, VERT, ROUGE, CREME = P.NOIR, P.GRIS, P.VERT, P.ROUGE, P.CREME
F, SANS, SERIF = P.F, P.SANS, P.SERIF
D_SC = 0.25  # transition entre deux scènes de contenu (poussée vers le haut)

# ------------------------------------------------------------ téléphone avec une vraie capture

MOCKUP = f"{P.RACINE}/kamforms/km_mockup.CaU8f2dR_2tpJUW.webp"


@lru_cache(None)
def telephone(ecran):
    """Cadre de téléphone du site + capture réelle (780x1688) dans l'écran."""
    cadre = Image.open(MOCKUP).convert("RGBA")
    scr = Image.open(f"{SITE}/{ecran}").convert("RGB")
    k = 970 / scr.width
    scr = scr.resize((970, round(scr.height * k)), Image.LANCZOS).crop((0, 0, 970, 2030))
    cadre.alpha_composite(P.arrondi(scr, 112), (26, 26))
    return cadre


ECHELLE_ECRAN = 970 / 780  # px capture → px cadre


def dessine_telephone(img, ecran, cx, cy, largeur, halo=None, t=0.0, zoom=1.0):
    """halo = (y0, y1) en px de la capture 780x1688 : cadre vert qui pulse + zoom centré dessus."""
    tel = telephone(ecran)
    s = largeur / tel.width * zoom
    if halo:
        yc = 26 + (halo[0] + halo[1]) / 2 * ECHELLE_ECRAN
        cy = cy + (tel.height / 2 - yc) * s * (zoom - 1) / zoom
    im = tel.resize((round(tel.width * s), round(tel.height * s)), Image.LANCZOS)
    x0, y0 = cx - im.width / 2, cy - im.height / 2
    P.ombre_portee(img, im, x0, y0, 40, 70)
    img.alpha_composite(im, (round(x0), round(y0)))
    if halo:
        d = ImageDraw.Draw(img)
        a = 0.6 + 0.4 * np.sin(t * 7)
        ya = y0 + (26 + halo[0] * ECHELLE_ECRAN) * s - 10
        yb = y0 + (26 + halo[1] * ECHELLE_ECRAN) * s + 10
        d.rounded_rectangle((x0 + 30 * s, ya, x0 + im.width - 30 * s, yb), 28, outline=VERT + (int(255 * a),),
                            width=9)


def fond_ciel():
    return P.fond_ciel()


@lru_cache(None)
def _bandeau(h):
    b = P.fond_ciel().crop((0, 0, W, h))
    a = np.full((h, W), 255, np.uint8)
    f = 70
    a[h - f:] = np.linspace(255, 0, f).astype(np.uint8)[:, None]
    b.putalpha(Image.fromarray(a))
    return b


def bandeau(img, h):
    """Fond du titre par-dessus le téléphone zoomé, pour que le texte reste lisible."""
    img.alpha_composite(_bandeau(h))


def titre(img, l1, l2=None, t=0.0, y=190):
    d = ImageDraw.Draw(img)
    a = int(255 * P.ease(t / 0.25))
    yy = P.bloc(d, l1, W / 2, y, F(SERIF, 92), NOIR + (a,), centre=True, largeur=960)
    if l2:
        P.bloc(d, l2, W / 2, yy + 8, F(SANS, 44), (70, 70, 76, a), centre=True, largeur=940)


# ------------------------------------------------------------ scènes de contenu
# chaque scène : (durée, rendu(t_local) -> RGBA, [(t_local, bruitage)])

def sc_ecran(ecran, l1, l2=None, halo=None, duree=1.9, zoom_max=1.32):
    def r(t):
        img = fond_ciel()
        z = 1 + (zoom_max - 1) * P.ease_io((t - 0.5) / 0.7) if halo else 1.0
        dessine_telephone(img, ecran, W / 2, 1260, 640, halo if t > 0.35 else None, t, z)
        bandeau(img, 560)
        titre(img, l1, l2, t)
        return img
    return duree, r, [(0.35, "pop")] if halo else []


def sc_decris(duree=3.4, debut=9.0):
    vit = (17.0 - debut) / (duree - 0.3)

    def r(t):
        img = fond_ciel()
        titre(img, "Tu décris ton formulaire.", "L'IA crée les questions, depuis ton téléphone.", t)
        P.coller(img, P.demo_carte(P.demo_r(t, debut, vitesse=vit), 820), W / 2, 1250)
        return img
    return duree, r, []


GROUPE = [("Awa", "Moi je viens !"), ("Paul", "Inscris-moi stp"), ("Brenda", "On sera 3"),
          ("Ibrahim", "C'est à quelle heure ?"), ("Sandrine", "Moi aussi"), ("Paul", "J'ai déjà dit oui hier"),
          ("Kevin", "Il reste des places ?"), ("Mireille", "Mettez-moi sur la liste"), ("Awa", "+1"),
          ("Junior", "Je confirme demain"), ("Brenda", "Vous avez la liste ?"), ("Ibrahim", "Mon frère vient aussi"),
          ("Kevin", "C'est où exactement ?"), ("Sandrine", "Je ne vois pas mon nom")]


def sc_groupe(duree=3.6, t_aspire=2.3):
    rng = np.random.default_rng(4)
    pos = [(rng.uniform(250, W - 250), rng.uniform(600, H - 260), rng.uniform(-6, 6)) for _ in GROUPE]

    def r(t):
        img = Image.new("RGBA", (W, H), P.WA_FOND + (255,))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, W, 150), fill=(0, 128, 105))
        d.text((60, 52), "Groupe · Séminaire de samedi", font=P._f_reg(40), fill="white")
        for i, ((nom, msg), (x, y, rot)) in enumerate(zip(GROUPE, pos)):
            ti = 0.1 + 1.8 * (i / len(GROUPE)) ** 1.2
            if t < ti:
                continue
            b = P.bulle(msg, taille=40, nom=nom).rotate(rot, expand=True, resample=Image.BICUBIC)
            s = P.pop(t, ti, 0.15)
            if t > t_aspire:
                k = P.ease((t - t_aspire) / 0.5)
                x, y = x + (W / 2 - x) * k, y + (1180 - y) * k
                s *= 1 - k
            P.coller(img, b, x, y, s)
        if t < t_aspire:
            P.texte_pop(img, "Les inscriptions dans le groupe WhatsApp :", W / 2, 300, F(SANS, 60), NOIR, t, 0.0,
                        largeur=900, fond=(255, 255, 255))
            if t > 1.3:
                P.texte_pop(img, "le chaos.", W / 2, 470, F(SERIF, 130), ROUGE, t, 1.3)
        else:
            P.texte_pop(img, "Avec KamForms :", W / 2, 300, F(SANS, 60), NOIR, t, t_aspire + 0.1,
                        fond=(255, 255, 255))
            P.texte_pop(img, "un lien, un formulaire.", W / 2, 440, F(SERIF, 110), VERT, t, t_aspire + 0.25)
            if t > t_aspire + 0.35:
                carte = P.carte_formulaire(t, t_aspire + 0.35, ("Nom complet", "E-mail", "Créneau préféré",
                                                                "Nombre de personnes"))
                carte = carte.crop((0, 0, carte.width, 170 + 4 * 118 + 40))
                ImageDraw.Draw(carte).rectangle((56, 50, 804, 130), fill=(255, 255, 255))
                ImageDraw.Draw(carte).text((56, 50), "Inscription samedi", font=F(SANS, 58), fill=NOIR)
                P.coller(img, carte, W / 2, 1150, P.pop(t, t_aspire + 0.35, 0.25))
        return img
    ev = [(0.0, "pop")] + [(0.1 + 1.8 * (i / len(GROUPE)) ** 1.2, "pop_l") for i in range(0, len(GROUPE), 2)]
    ev += [(t_aspire - 0.1, "whoosh"), (t_aspire + 0.35, "impact")]
    return duree, r, ev


def notif(img, x, y, l1, l2, s=1.0):
    c = Image.new("RGBA", (940, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, 939, 189), 44, fill=(250, 250, 252, 240))
    c.alpha_composite(P.LOGO.resize((96, 96), Image.LANCZOS), (34, 46))
    d.text((158, 36), "KamForms", font=P._f_reg(32), fill=GRIS)
    d.text((740, 36), "maintenant", font=P._f_reg(28), fill=GRIS)
    d.text((158, 78), l1, font=F(SANS, 42), fill=NOIR)
    d.text((158, 130), l2, font=P._f_reg(34), fill=(60, 60, 66))
    P.coller(img, c, x, y, s)


@lru_cache(None)
def _fond_nuit():
    im = P.fond_ciel().convert("RGB").filter(ImageFilter.GaussianBlur(30))
    a = np.asarray(im).astype(np.float32) * 0.35
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def sc_notifs(duree=1.9, formulaire="Inscription samedi"):
    ts = [0.25, 0.7, 1.1]

    def r(t):
        img = _fond_nuit().copy()
        d = ImageDraw.Draw(img)
        f = F(SANS, 200)
        d.text((W / 2 - d.textlength("20:41", font=f) / 2, 330), "20:41", font=f, fill=(255, 255, 255, 230))
        d.text((W / 2 - d.textlength("samedi 10 octobre", font=P._f_reg(44)) / 2, 300), "samedi 10 octobre",
               font=P._f_reg(44), fill=(255, 255, 255, 200))
        for k, tk in enumerate(ts):
            if t >= tk:
                notif(img, W / 2, 760 + 215 * (len([x for x in ts if t >= x]) - 1 - k), "Nouvelle réponse",
                      f"Quelqu'un a rempli {formulaire}", P.pop(t, tk, 0.18))
        P.texte_pop(img, "Une notification à chaque réponse.", W / 2, 1500, F(SERIF, 84), "white", t, 0.15,
                    largeur=960)
        P.texte_pop(img, "avec l'appli KamForms", W / 2, 1640, F(SANS, 44), (220, 220, 225), t, 0.35)
        return img
    return duree, r, [(x, "ding") for x in ts]


MASCOTTES = [("teachers.webp", "Formations"), ("events.webp", "Événements"), ("shops.webp", "Avis clients"),
             ("creators.webp", "Dons, sondages…")]


def sc_usages(duree=2.6):
    def r(t):
        img = P.fond_creme()
        d = ImageDraw.Draw(img)
        a = int(255 * P.ease(t / 0.25))
        P.bloc(d, "Un seul outil pour tous tes formulaires.", W / 2, 200, F(SERIF, 96), NOIR + (a,), centre=True,
               largeur=940)
        for i, (f, lab) in enumerate(MASCOTTES):
            ti = 0.3 + 0.35 * i
            s = P.pop(t, ti, 0.2)
            if s <= 0:
                continue
            c = Image.new("RGBA", (440, 520), (0, 0, 0, 0))
            m = P.arrondi(Image.open(f"{SITE}/{f}").convert("RGB").resize((440, 440), Image.LANCZOS), 40)
            c.alpha_composite(m, (0, 0))
            dc = ImageDraw.Draw(c)
            fl = F(SANS, 44)
            dc.text((220 - dc.textlength(lab, font=fl) / 2, 458), lab, font=fl, fill=NOIR)
            P.coller(img, c, W / 2 - 245 + 490 * (i % 2), 760 + 580 * (i // 2), s)
        return img
    return duree, r, [(0.3 + 0.35 * i, "pop") for i in range(4)]


def sc_texte(l1, l2=None, duree=1.3, fond=VERT, coul="white"):
    def r(t):
        img = Image.new("RGBA", (W, H), fond + (255,))
        P.texte_pop(img, l1, W / 2, H / 2 - 80, F(SERIF, 120), coul, t, 0.0, largeur=940)
        if l2:
            P.texte_pop(img, l2, W / 2, H / 2 + 120, F(SANS, 56), coul, t, 0.25, largeur=920)
        return img
    return duree, r, [(0.0, "impact")]


def sc_fin():
    return P.FIN, P.carte_fin, [(0.0, "whoosh"), (0.35, "pop")]


def sc_pub(nom, debut=0.0):
    """Reprend une pub de pubs.py (illusion, coulisses) telle quelle à partir de `debut`."""
    rendu, duree, ev, _ = P.PUBS[nom]()
    return duree - debut, (lambda t: rendu(debut + t)), [(a - debut, b) for a, b in ev if a >= debut]


PARTAGE = lambda: sc_ecran("form.jpg", "Tu partages le lien dans tes groupes WhatsApp.",
                           "Pas d'appli ni de compte pour répondre.", halo=(380, 488))
REDIRECTION = lambda: sc_ecran("form.jpg", "Les réponses arrivent sur ton WhatsApp.",
                               "La personne arrive sur ton WhatsApp avec ses réponses.",
                               halo=(820, 980), duree=2.2)
DETAIL = lambda: sc_ecran("detail.jpg", "Chaque réponse, prête à lire.", "Et tu réponds sur WhatsApp en un geste.",
                          halo=(320, 428))
INBOX = lambda: sc_ecran("inbox.jpg", "Toutes tes réponses au même endroit.", "Et tout s'exporte en CSV.",
                         duree=1.8)
IMPORT = lambda: sc_ecran("import.jpg", "Tu as déjà des Google Forms ?", "Colle le lien : KamForms les reprend.",
                          duree=2.0)

CONTENUS = {
    "01": lambda: [sc_groupe(), PARTAGE(), REDIRECTION(), sc_notifs(), sc_fin()],
    "02": lambda: [sc_decris(3.6, 9.0), PARTAGE(), REDIRECTION(), sc_fin()],
    "03": lambda: [sc_notifs(1.9), REDIRECTION(), INBOX(), sc_fin()],
    "04": lambda: [sc_texte("Fais plutôt un formulaire.", "Avec KamForms.", 1.2, fond=CREME, coul=NOIR),
                   sc_decris(2.8, 11.0), PARTAGE(), REDIRECTION(), sc_fin()],
    "05": lambda: [PARTAGE(), DETAIL(), sc_notifs(), sc_fin()],
    "06": lambda: [sc_usages(), sc_decris(3.0, 11.0), REDIRECTION(), sc_fin()],
    "07": lambda: [INBOX(), DETAIL(), sc_notifs(1.7, "Avis clients"), sc_fin()],
    "08": lambda: [sc_pub("06_illusion")],
    "09": lambda: [IMPORT(), REDIRECTION(), sc_notifs(), sc_fin()],
    "10": lambda: [sc_pub("10_coulisses", 0.0)],
}

# légendes de hook réécrites (formulaires en général, pas seulement des commandes)
CAPS = {
    "01": [(0.0, "Quand tu organises un événement et que les inscriptions se font dans le groupe WhatsApp :")],
    "02": [(0.0, "Moi qui appuie sur « Créer » dans KamForms…"), (1.7, "…et adieu les listes faites à la main.")],
    "03": [(0.0, "Moi qui recopie à la main les inscriptions reçues dans le groupe :")],
    "04": [(0.0, "Si tu collectes encore tes inscriptions dans un groupe WhatsApp…"),
           (2.0, "…ça finit toujours comme ça.")],
    "05": [(0.0, "Les membres de ton groupe quand tu partages un lien KamForms :")],
    "06": [(0.0, "Moi qui garde toutes les réponses de mon sondage en tête :")],
    "07": [(0.0, "Ma tête après avoir compté les avis clients un par un dans mes messages :")],
    "08": [(0.0, "Tout n'est pas ce qu'il paraît…")],
    "09": [(0.0, "Mes formulaires avant KamForms…"), (2.7, "…et après.")],
    "10": [(0.0, "Moi qui organise une formation sans formulaire d'inscription :")],
}


def sequence(scenes):
    """Assemble les scènes : poussée vers le haut de D_SC entre deux scènes, whoosh au passage."""
    debuts, t = [], 0.0
    for dur, _, _ in scenes:
        debuts.append(t)
        t += dur
    total = t
    ev = []
    for (dur, _, e), t0 in zip(scenes, debuts):
        ev += [(t0 + a, b) for a, b in e]
    ev += [(t0 - 0.12, "whoosh") for t0 in debuts[1:]]

    def rendu(t):
        i = max(k for k, t0 in enumerate(debuts) if t >= t0 or k == 0)
        u = t - debuts[i]
        img = scenes[i][1](u)
        if i > 0 and u < D_SC:
            prev = scenes[i - 1][1](scenes[i - 1][0] - 1 / FPS).convert("RGBA")
            k = P.ease_io(u / D_SC)
            out = Image.new("RGBA", (W, H))
            out.alpha_composite(prev, (0, int(-H * k)))
            out.alpha_composite(img.convert("RGBA"), (0, int(H * (1 - k))))
            return out
        return img
    return total, rendu, ev


def fabriquer(cle):
    spec = dict(V2.SPECS[cle])
    spec["caps"] = CAPS[cle]
    nom = f"hook{cle}_{spec['hook'].replace('/', '_').replace(' ', '_')}"
    tmp = f"{OUT}/_tmp3_{cle}"
    n_hook, son_hook = V2.extraire(spec, tmp)
    T_H = n_hook / FPS
    d_contenu, rendu, ev = sequence(CONTENUS[cle]())
    duree = T_H + d_contenu
    imgs = [f"{tmp}/{i:05d}.jpg" for i in range(n_hook)]

    def hook(t):
        img = Image.open(imgs[min(n_hook - 1, int(t * FPS))]).convert("RGBA")
        if cle == "09":  # cache toute la ligne « Same bathroom 2.5 years later » incrustée dans l'extrait
            ImageDraw.Draw(img).rounded_rectangle((70, 200, W - 70, 470), 30, fill=(255, 255, 255))
        V2.legende(img, spec, t)
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
            b = rendu(u)
            img = V2.transition(spec["trans"], derniere, b, u / V2.D_TR, t) if u < V2.D_TR else b
        enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    enc.stdin.close()
    enc.wait()

    # son : hook d'origine → bruitage de transition → musique KamForms + bruitages du contenu
    rng = np.random.default_rng(int(cle))
    n = int(duree * SR)
    s = np.zeros(n + SR)
    hk = son_hook / (np.abs(son_hook).max() + 1e-9) * 0.8
    f = int(0.12 * SR)
    hk[-f:] *= np.linspace(1, 0, f)
    s[:len(hk)] += hk
    i0 = int(T_H * SR)
    mus = P.musique(d_contenu, int(cle) % 10, []) * 0.5
    m = int(0.1 * SR)
    mus[:m] *= np.linspace(0, 1, m)
    s[i0:i0 + len(mus)] += mus
    for t0, nomb in ev:
        x = P.sfx(nomb, rng)
        j = i0 + int(t0 * SR)
        if 0 <= j < len(s):
            s[j:j + len(x)] += x[: len(s) - j]
    tr = V2.son_transition(spec["trans"])
    j0 = max(0, i0 - int(0.12 * SR))
    s[j0:j0 + len(tr)] += tr[: len(s) - j0]
    s = s[:n]
    fin = int(0.35 * SR)
    s[-fin:] *= np.linspace(1, 0, fin)
    s = (s / (np.abs(s).max() + 1e-9) * 0.9 * 32767).astype(np.int16)
    wav = f"{tmp}/final.wav"
    with wave.open(wav, "wb") as fw:
        fw.setnchannels(1); fw.setsampwidth(2); fw.setframerate(SR); fw.writeframes(s.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", muet, "-i", wav, "-af",
                    "loudnorm=I=-13:TP=-1.5:LRA=11,volume=1dB,alimiter=limit=0.89", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "44100", "-shortest", f"{OUT}/pub_kamforms_{nom}.mp4"], check=True)
    os.remove(muet)
    subprocess.run(["rm", "-rf", tmp])
    print("ok", nom, round(duree, 1), "hook", round(T_H, 1), flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for cle in V2.SPECS:
        if not QUOI or cle in QUOI:
            fabriquer(cle)
