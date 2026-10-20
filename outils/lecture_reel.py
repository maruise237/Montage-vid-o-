"""Lecture d'un Reel seconde par seconde, avant publication, en local.

Mesure ce qui est OBSERVABLE dans la vidéo (coupes, mouvement, visages, texte à l'écran,
voix, silences, débit) et sort une liste « Quoi modifier » avec le minutage et la preuve.
Ne prédit ni la rétention ni la viralité : seules les statistiques Instagram le disent
(voir `--stats`, qui compare chaque Reel à ta propre moyenne).

    python3 outils/lecture_reel.py video.mp4                      # rapport HTML + JSON à côté
    python3 outils/lecture_reel.py --stats stats_reels.csv nom    # compare un Reel publié à ta moyenne

stats_reels.csv : nom,duree,perdus_3s,part_regardee,partages,enregistrements (chiffres Instagram).
"""
import csv, html, json, os, subprocess, sys, tempfile

import numpy as np


def extraire_audio(video, dossier):
    wav = os.path.join(dossier, "a.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "1", "-ar", "16000", wav], check=True)
    import soundfile as sf
    a, sr = sf.read(wav)
    return wav, a, sr


def coupes(video):
    from scenedetect import detect, ContentDetector
    return [s[0].get_seconds() for s in detect(video, ContentDetector(threshold=27))][1:]


def images(video, fps=2):
    import cv2
    cap = cv2.VideoCapture(video)
    src = cap.get(cv2.CAP_PROP_FPS) or 30
    pas = max(1, round(src / fps))
    i = 0
    while True:
        ok, im = cap.read()
        if not ok:
            break
        if i % pas == 0:
            yield i / src, im
        i += 1


def mesurer_images(video):
    import cv2
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    # OpenCV 5 ne fournit plus les cascades : copie de celle d'OpenCV 4.10 dans outils/modeles/
    visage = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), "modeles", "haarcascade_frontalface_default.xml"))
    res, prec = [], None
    for t, im in images(video):
        petit = cv2.resize(im, (270, 480))
        gris = cv2.cvtColor(petit, cv2.COLOR_BGR2GRAY)
        mouv = 0.0 if prec is None else float(np.mean(cv2.absdiff(gris, prec))) / 255
        prec = gris
        f = visage.detectMultiScale(gris, 1.1, 5, minSize=(30, 30))
        part_visage = max((w * h for x, y, w, h in f), default=0) / (270 * 480)
        texte = ""
        if abs(t - round(t)) < 0.26:  # OCR une fois par seconde
            r, _ = ocr(cv2.resize(im, (540, 960)))
            # gros texte seulement (titres, sous-titres) : lettres de plus de 2,5 % de la hauteur.
            # Le petit texte des écrans filmés n'est pas « à lire ».
            texte = " ".join(x[1] for x in (r or []) if float(x[2]) > 0.6
                             and max(p[1] for p in x[0]) - min(p[1] for p in x[0]) > 960 * 0.025)
        res.append({"t": round(t, 2), "mouvement": round(mouv, 4), "visage": round(part_visage, 3), "texte": texte})
    return res


def voix(a):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a.astype(np.float32),  # tableau : PyAV récent casse decode_audio
                             language="fr", word_timestamps=True, vad_filter=True)
    return [{"mot": w.word.strip(), "debut": round(w.start, 2), "fin": round(w.end, 2)} for s in segs for w in s.words]


def niveau(a, sr):
    n = int(len(a) / sr * 10)
    return [float(20 * np.log10(np.sqrt(np.mean(a[int(i * sr / 10):int((i + 1) * sr / 10)] ** 2)) + 1e-9)) for i in range(n)]


def analyser(video):
    with tempfile.TemporaryDirectory() as d:
        wav, a, sr = extraire_audio(video, d)
        duree = len(a) / sr
        cps = coupes(video)
        ims = mesurer_images(video)
        mots = voix(a)
    db = niveau(a, sr)
    sec = []
    for s in range(int(np.ceil(duree))):
        ii = [x for x in ims if s <= x["t"] < s + 1]
        sec.append({
            "s": s,
            "coupes": sum(s <= c < s + 1 for c in cps),
            "mouvement": round(max((x["mouvement"] for x in ii), default=0), 4),
            "visage": max((x["visage"] for x in ii), default=0),
            "texte": next((x["texte"] for x in ii if x["texte"]), ""),
            "mots": [m["mot"] for m in mots if s <= m["debut"] < s + 1],
            "niveau_db": round(float(np.mean(db[s * 10:(s + 1) * 10] or [-90])), 1),
        })
    return {"video": os.path.basename(video), "duree": round(duree, 2), "coupes": cps, "mots": mots, "secondes": sec}


def a_modifier(r):
    """Règles tirées de la skill montage-pro. Chaque alerte = minutage + preuve + action."""
    out, sec, mots, d = [], r["secondes"], r["mots"], r["duree"]
    debut = sec[:2]
    if not any(x["texte"] for x in debut) and not any(x["mots"] for x in debut):
        out.append(("0:00", "ni texte ni voix dans les 2 premières secondes", "mettre le hook dès la 1re image (texte + voix)"))
    if sec and sec[0]["mouvement"] < 0.01 and sec[0]["coupes"] == 0:
        out.append(("0:00", "1re seconde presque immobile", "démarrer déjà en mouvement"))
    if mots and mots[0]["debut"] > 0.8:
        out.append(("0:00", f"la voix commence à {mots[0]['debut']:.1f} s", "couper le blanc du début"))
    # Texte NOUVEAU à l'écran (l'OCR lit aussi les écrans filmés, qui ne sont pas « à lire »)
    vus, avant = set(), set()
    for x in sec:
        m = {w.lower() for w in x["texte"].split() if len(w) > 2}
        x["texte_nouveau"] = len(m - vus - avant)  # 2 s de mémoire : l'OCR hésite d'une image à l'autre
        vus, avant = m, vus
    # Temps mort visuel : 3 s de suite sans coupe, sans mouvement et sans texte nouveau
    mort = []
    for x in sec + [None]:
        if x and not x["coupes"] and x["mouvement"] < 0.015 and x["texte_nouveau"] < 2:
            mort.append(x["s"])
            continue
        if len(mort) >= 3:
            out.append((f"{mort[0]//60}:{mort[0]%60:02d}", f"{len(mort)} s sans coupe, sans mouvement ni texte nouveau", "couper, zoomer ou faire apparaître un élément"))
        mort = []
    for m1, m2 in zip(mots, mots[1:]):
        if m2["debut"] - m1["fin"] > 0.7:
            out.append((f"{int(m1['fin'])//60}:{int(m1['fin'])%60:02d}", f"silence de {m2['debut']-m1['fin']:.1f} s entre « {m1['mot']} » et « {m2['mot']} »", "resserrer la coupe"))
    for x in sec:
        if x["texte_nouveau"] > 10:
            out.append((f"{x['s']//60}:{x['s']%60:02d}", f"{x['texte_nouveau']} mots nouveaux à l'écran d'un coup", "si c'est à lire : en montrer moins à la fois"))
    fin = sec[-3:]
    if fin and not any(x["texte"] or x["mots"] for x in fin):
        out.append(("fin", "rien à lire ni à entendre dans les 3 dernières secondes", "finir sur l'appel à l'action ou boucler"))
    return out


def rapport(r, alertes, sortie):
    lignes = "".join(
        f"<tr><td>{x['s']//60}:{x['s']%60:02d}</td><td>{'✂' * x['coupes']}</td>"
        f"<td><div class=b style='width:{min(100, x['mouvement']*2000):.0f}%'></div></td>"
        f"<td>{'●' if x['visage'] > 0.01 else ''}</td><td>{x['niveau_db']}</td>"
        f"<td>{html.escape(' '.join(x['mots']))}</td><td class=t>{html.escape(x['texte'])}</td></tr>" for x in r["secondes"])
    al = "".join(f"<li><b>{a}</b> — {html.escape(p)} → {html.escape(c)}</li>" for a, p, c in alertes) or "<li>Rien à signaler.</li>"
    open(sortie, "w").write(f"""<!doctype html><meta charset=utf-8><title>Lecture {html.escape(r['video'])}</title>
<style>body{{font:14px system-ui;margin:24px;max-width:1100px}}td{{padding:3px 8px;border-bottom:1px solid #ddd;vertical-align:top}}
.b{{height:8px;background:#e44}}.t{{color:#666;font-size:12px}}</style>
<h1>{html.escape(r['video'])} — {r['duree']} s, {len(r['coupes'])} coupes, {len(r['mots'])} mots</h1>
<h2>Quoi modifier</h2><ul>{al}</ul>
<p><i>Mesures de la vidéo, pas une prévision d'audience. Comparer ensuite aux statistiques Instagram (--stats).</i></p>
<h2>Seconde par seconde</h2><table><tr><th>t</th><th>coupe</th><th>mouvement</th><th>visage</th><th>dB</th><th>voix</th><th>texte à l'écran</th></tr>{lignes}</table>""")


def stats(fichier, nom):
    rows = list(csv.DictReader(open(fichier)))
    cle = ["perdus_3s", "part_regardee", "partages", "enregistrements"]
    cible = next(x for x in rows if x["nom"] == nom)
    autres = [x for x in rows if x["nom"] != nom]
    print(f"{nom} comparé à {len(autres)} Reels (médiane) :")
    for k in cle:
        v = float(cible[k]); med = float(np.median([float(x[k]) for x in autres])) if autres else v
        rang = 1 + sum(float(x[k]) > v for x in autres) if k != "perdus_3s" else 1 + sum(float(x[k]) < v for x in autres)
        print(f"  {k:16} {v:>8g}   d'habitude {med:>8g}   rang {rang}/{len(rows)}")
    if len(rows) < 30:
        print(f"  ({len(rows)} Reels : moins de 30, la comparaison reste indicative)")


if __name__ == "__main__":
    if sys.argv[1] == "--stats":
        stats(sys.argv[2], sys.argv[3])
    else:
        v = sys.argv[1]
        r = analyser(v)
        al = a_modifier(r)
        base = os.path.splitext(v)[0]
        json.dump({**r, "a_modifier": al}, open(base + "_lecture.json", "w"), ensure_ascii=False, indent=1)
        rapport(r, al, base + "_lecture.html")
        for a in al:
            print(" · ".join(a))
        print("→", base + "_lecture.html")
