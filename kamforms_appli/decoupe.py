"""Resserre la narration : on retire la consigne lue à voix haute, on raccourcit les pauses sur les vrais silences
(énergie < -38 dB), on garde les respirations voulues. Sortie : voix/narr_montee.wav, mots_video.js (mots en temps vidéo)."""
import json, numpy as np, librosa, soundfile as sf
SR = 24000
y, _ = librosa.load('voix/narr.wav', sr=SR)
W = json.load(open('voix/narr.mots.json'))
DEBUT, FIN = 13.89, 55.03          # « Il est vingt-trois heures » … « le lien. » (calés sur l'énergie)
hop = 240
rms = librosa.feature.rms(y=y, frame_length=960, hop_length=hop)[0]
db = 20 * np.log10(rms / rms.max() + 1e-9); q = db < -38; t = np.arange(len(db)) * hop / SR
gaps = []; i = 0
while i < len(q):
    if q[i]:
        j = i
        while j < len(q) and q[j]: j += 1
        a, b = t[i], t[min(j, len(t) - 1)]
        if b - a > .25 and a > DEBUT + .1 and b < FIN: gaps.append([a, b])
        i = j
    else: i += 1
# respirations voulues : début du silence source → durée gardée
GARDE = {14.96: .55, 16.47: .50, 19.91: .60, 22.69: .55, 24.76: .90, 31.32: .45, 36.24: .80, 39.07: .55, 45.45: .55, 48.57: .45}
VOIX0 = 0.55  # la voix entre après le premier plan (ambiance nuit seule)
out = []; carte = []; pos = VOIX0; src = DEBUT
for a, b in gaps:
    a, b = float(a), float(b)
    garde = next((v for k, v in GARDE.items() if abs(k - a) < .06), min(b - a, .32))
    reel = min(garde, b - a); fin = a + reel / 2
    carte.append((src, fin, pos)); out.append((pos, y[int(src * SR):int(fin * SR)]))
    pos += fin - src + (garde - reel); src = b - reel / 2
carte.append((src, FIN, pos)); out.append((pos, y[int(src * SR):int(FIN * SR)])); pos += FIN - src
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
MV = [[w, v(s), v(e)] for w, s, e in W if s >= DEBUT - .1]
json.dump({'carte': carte, 'fin_voix': total}, open('timeline.json', 'w'))
open('mots_video.js', 'w').write('const MOTS=' + json.dumps(MV, ensure_ascii=False) + ';\n')
print('voix montée', round(total, 2), 's')
for w, s, e in MV: print(f'{s:6.2f} {e:6.2f} {w}')
