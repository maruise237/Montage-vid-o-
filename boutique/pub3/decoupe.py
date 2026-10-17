"""Découpe les prises de voix (Gemini TTS via treg) en répliques, sur les vrais silences (jamais dans un mot),
en jetant la consigne de style lue en anglais au début de chaque prise."""
import numpy as np, json, subprocess, os
SR = 44100
def lire(p):
    x = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(x, '<i2').astype(np.float64) / 32768
def edb(x, h=int(.01 * SR)):
    return 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')) + 1e-9)
REPLIQUES = {
 'intro': {'A1': (5.0, 7.5), 'B': (9.26, 16.45), 'C': (16.92, 19.0)},
 'items': {'Q1': (4.68, 7.15), 'Q2': (7.58, 9.5), 'Q3': (9.98, 13.0), 'Q4': (13.12, 14.9), 'Q5': (15.24, 16.8),
           'Q6': (17.26, 19.35), 'Q7': (19.84, 21.5), 'Q8': (21.96, 23.85), 'Q9': (24.28, 25.95)},
 'finale': {'F1': (6.0, 12.95), 'CTA': (13.5, 24.7)},
 'correctif': {'A2': (7.2, 8.45)},
 'correctif2': {'CTA2': (8.54, 20.95)},          # CTA refait : « face au poste de police » (le commissariat a déménagé)
 'reponses2': {'r11': (6.32, 7.2), 'r12': (7.66, 8.3)},
 'reponses': {'r1': (7.54, 8.3), 'r2': (8.72, 9.3), 'r3': (10.06, 10.8), 'r4': (11.36, 12.1), 'r5': (12.62, 13.5),
              'r6': (13.9, 14.75), 'r7': (15.0, 15.95), 'r8': (16.24, 16.8), 'r9': (17.1, 17.8), 'r10': (18.08, 19.35)}}
out = {}
for f, R in REPLIQUES.items():
    x = lire(f'voix/{f}.wav'); e = edb(x); g = lambda t: e[min(len(e) - 1, max(0, int(t * SR)))]
    calme = lambda t0, t1: max(g(t0 + k * .01) for k in range(int((t1 - t0) / .01) + 1)) < -40
    noms = list(R); bornes = []
    for i, n in enumerate(noms):
        a, b = R[n]
        lim_a = bornes[-1][1] if bornes else 0
        lim_b = R[noms[i + 1]][0] if i + 1 < len(noms) else len(x) / SR
        a2 = next((t - .02 for t in np.arange(a + .04, max(lim_a, a - .35), -.01) if calme(t - .05, t)), a - .03)
        b2 = next((t + .04 for t in np.arange(b - .12, min(lim_b, b + .5), .01) if calme(t, t + .06)), b + .05)
        a2, b2 = max(a2, lim_a), min(b2, lim_b)
        bornes.append((round(a2, 3), round(b2, 3)))
        seg = x[int(a2 * SR):int(b2 * SR)].copy(); q = int(.008 * SR); seg[:q] *= np.linspace(0, 1, q); seg[-q:] *= np.linspace(1, 0, q)
        import wave
        w = wave.open(f'voix/seg_{n}.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((seg.clip(-1, 1) * 32767).astype('<i2').tobytes()); w.close()
        out[n] = {'src': f, 'a': a2, 'b': b2, 'd': round(b2 - a2, 3)}
        mots = [m for m in json.load(open(f'voix/{f}.mots.json')) if m['s'] >= a2 - .05 and m['e'] <= b2 + .1]
        out[n]['mots'] = [{'w': m['w'], 's': round(m['s'] - a2, 2), 'e': round(m['e'] - a2, 2)} for m in mots]
json.dump(out, open('voix/repliques.json', 'w'), ensure_ascii=False, indent=0)
for n, v in out.items(): print(n, v['d'], ' '.join(m['w'] for m in v['mots']))
