"""Bande son : voix, vraie musique Mixkit montée sur ses temps, vrai son de notification de l'appli, bruitages rares."""
import numpy as np, librosa, soundfile as sf, scipy.signal as sg
SR = 48000; DUREE = 45.4
def charge(p): return librosa.load(p, sr=SR, mono=True)[0]
def db(x): return 10 ** (x / 20)
mix = np.zeros(int(DUREE * SR)); mus = np.zeros_like(mix)
def pose(piste, x, t, g=0):
    i = int(t * SR); k = min(len(x), len(piste) - i)
    if k > 0: piste[i:i + k] += x[:k] * db(g)
def fondu(x, a=.012, b=.012):
    x = x.copy(); fa, fb = int(a * SR), int(b * SR)
    if fa: x[:fa] *= np.linspace(0, 1, fa)
    if fb: x[-fb:] *= np.linspace(1, 0, fb)
    return x
voix = charge('voix/narr_finale.wav'); pose(mix, voix, 0)
M = charge('musique/738.mp3')
seg = lambda a, b: M[int(a * SR):int(b * SR)]
# 1. problème : la musique est étouffée (passe-bas), elle s'arrête juste avant « Avec KamForms »
b, a = sg.butter(4, 420 / (SR / 2), 'low')
p1 = sg.lfilter(b, a, seg(0.07, 0.07 + 13.62)); pose(mus, fondu(p1, .3, .06), 0, -3)
# 2. elle tombe en entier sur « Avec KamForms » (14,36 s), calée sur une mesure (95,7 BPM, mesure 2,508 s)
BAR = 2.508; DEP = 0.07 + 8 * BAR
pose(mus, fondu(seg(DEP, DEP + 11 * BAR)), 14.36)
# 3. sa vraie fin (mesure 44) raccordée sur la mesure suivante
pose(mus, fondu(seg(0.07 + 44 * BAR, 115.0), .01, .2), 14.36 + 11 * BAR)
# niveau : musique ~17 dB sous la voix, un peu plus haute quand la voix se tait (fin)
env = np.ones_like(mus) * db(-19)
i = int(42.85 * SR); env[i:] = np.linspace(db(-19), db(-11), int(.4 * SR)).tolist() + [db(-11)] * (len(env) - i - int(.4 * SR))
mix += mus * env
# bruitages : le vrai son de notification de KamForms, frappe sur téléphone, tapotements
rng = np.random.default_rng(7)
def bruit(p, t, g=0, dur=None):
    x = charge(p)
    if dur: x = fondu(x[:int(dur * SR)], .005, .08)
    r = 1 + rng.uniform(-.03, .03); x = librosa.resample(x, orig_sr=SR, target_sr=int(SR / r))
    pose(mix, x, t + rng.uniform(.01, .02), g + rng.uniform(-2, 2))
bruit('assets/reponse.wav', 14.36, -6); bruit('assets/reponse.wav', 16.04, -8); bruit('assets/reponse.wav', 16.75, -9)
bruit('sfx/1395.mp3', 9.95, -16, 1.6)
bruit('sfx/1393.mp3', 31.62, -17, .9)
bruit('sfx/1109.mp3', 17.76, -12); bruit('sfx/1109.mp3', 19.05, -13); bruit('sfx/1109.mp3', 23.13, -14)
bruit('sfx/2577.mp3', 29.84, -14)
sf.write('mix_brut.wav', mix, SR)
print('ok', round(len(mix) / SR, 2), 'pic', round(20 * np.log10(np.abs(mix).max()), 1))
