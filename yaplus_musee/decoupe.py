"""Resserre la narration : coupe sur les vrais silences, raccourcit les pauses, garde les respirations voulues.
Sortie : voix/narr_montee.wav (24 kHz), timeline.json (décalage source→vidéo), mots_video.js (mots en temps vidéo)."""
import json, numpy as np, librosa, soundfile as sf
SR = 24000
y, _ = librosa.load('voix/narr.wav', sr=SR)
W = json.load(open('voix/narr.mots.json'))
hop = 240
rms = librosa.feature.rms(y=y, frame_length=960, hop_length=hop)[0]
db = 20 * np.log10(rms / rms.max() + 1e-9); q = db < -38; t = np.arange(len(db)) * hop / SR
gaps = []; i = 0
while i < len(q):
    if q[i]:
        j = i
        while j < len(q) and q[j]: j += 1
        if (j - i) * hop / SR > .25: gaps.append([t[i], t[min(j, len(t) - 1)]])
        i = j
    else: i += 1
# respirations voulues (début du silence source → durée gardée)
GARDE = {5.40: .95, 7.00: .55, 24.07: .85, 25.20: .55, 40.28: .85, 61.58: .55, 62.78: 2.25, 64.13: .60, 82.71: .70}
VOIX0 = 0.35  # la voix démarre à 0,35 s de la vidéo (le projecteur s'allume d'abord)
out = []; carte = []  # carte : (début source, fin source, début vidéo)
pos = VOIX0; src = 0.0
for a, b in gaps:
    a, b = float(a), float(b)
    garde = next((v for k, v in GARDE.items() if abs(k - a) < .06), min(b - a, .42))
    reel = min(garde, b - a)  # silence pris dans la source ; s'il en faut plus, on ajoute du vide
    fin = a + reel / 2  # moitié de la pause après la phrase, moitié avant la suivante
    carte.append((src, fin, pos)); seg = y[int(src * SR):int(fin * SR)]; out.append((pos, seg))
    pos += fin - src + (garde - reel); src = b - reel / 2
carte.append((src, len(y) / SR, pos)); out.append((pos, y[int(src * SR):])); pos += len(y) / SR - src
total = pos
piste = np.zeros(int((total + .5) * SR))
for p, seg in out:
    i = int(p * SR); k = min(len(seg), len(piste) - i); s = seg[:k].copy()
    f = int(.008 * SR); s[:f] *= np.linspace(0, 1, f); s[-f:] *= np.linspace(1, 0, f)
    piste[i:i + k] += s
sf.write('voix/narr_montee.wav', piste, SR)
def v(ts):
    for a, b, p in carte:
        if a - 1e-3 <= ts <= b + 1e-3: return round(p + ts - a, 3)
    for a, b, p in carte:
        if ts < a: return round(p, 3)
    return round(total, 3)
MV = [[w, v(s), v(e)] for w, s, e in W]
json.dump({'carte': carte, 'fin_voix': total}, open('timeline.json', 'w'))
open('mots_video.js', 'w').write('const MOTS=' + json.dumps(MV, ensure_ascii=False) + ';\n')
print('voix montée', round(total, 2), 's ; source', round(len(y) / SR, 2))
for w, s, e in MV:
    if w.lower().strip('.,?') in ('ici', 'salle', 'savoir', 'lien', 'manque', 'là', 'yaplus', 'trois', 'bar', 'laser', 'histoire'): print(w, s, e)
