"""Bande son du lancement Yaplus : voix treg (Laomedeia + Fenrir), musique Lyria montée sur ses mesures, 2 clics enregistrés."""
import numpy as np, librosa, soundfile as sf
SR, DUREE = 48000, 57.9
ch = lambda f: librosa.load(f, sr=SR, mono=True)[0]
n = int(DUREE * SR)

def bout(y, a, b, fondu=0.012):
    x = y[int(a * SR):int(b * SR)].copy(); k = int(fondu * SR)
    x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x

def poser(piste, x, t, g=1.0):
    i = int(t * SR); x = x[:max(0, len(piste) - i)]; piste[i:i + len(x)] += g * x

# musique : on retire 4 mesures (38,94 → 48,09 s) pour que le coup final tombe sur la fin de la vidéo
m = ch('musique.mp3')
A, B, X = int(38.94 * SR), int(48.089 * SR), int(.02 * SR)
mus = np.concatenate([m[:A - X], m[A - X:A] * np.linspace(1, 0, X) + m[B - X:B] * np.linspace(0, 1, X), m[B:]])[:n]
mus = np.pad(mus, (0, n - len(mus)))

# voix : (fichier, début, fin dans le fichier, instant dans la vidéo)
narr, cris = ch('voix/narr.wav'), ch('voix/cris2.wav')
voix = np.zeros(n)
for src, a, b, t in [(cris, 5.30, 8.2, 0.6), (cris, 9.05, 10.98, 3.6),
                     (narr, 9.72, 22.62, 6.32), (narr, 22.85, 55.75, 22.05)]:
    poser(voix, bout(src, a, b), t)

# ducking : musique ~16 dB sous la voix quand elle parle, plus présente dans les respirations
env = np.convolve(np.abs(voix), np.ones(int(.05 * SR)) / int(.05 * SR), 'same')
parle = (env > 0.01).astype(float)
k = int(.35 * SR); parle = np.convolve(parle, np.ones(k) / k, 'same').clip(0, 1)
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2))
gv = rms(voix); gm = rms(mus)
mus_g = (gv / gm) * (10 ** (-16 / 20) * parle + 10 ** (-7 / 20) * (1 - parle))

# clics enregistrés (Mixkit) sur les 3 taps visibles, variés
sfx = np.zeros(n)
c1, c2 = ch('assets/1109.mp3'), ch('assets/2568.mp3')
for t, s, g in [(25.62, c2, .5), (26.95, c1, .45), (35.71, c2, .42)]:
    poser(sfx, s[:int(.4 * SR)], t + 0.012, g * gv / rms(s))
mix = voix + mus * mus_g + sfx * .35
sf.write('mix_brut.wav', mix / np.abs(mix).max() * .9, SR)
