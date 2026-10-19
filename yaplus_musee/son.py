"""Bande son « La machine qui manquait » : musique Lyria montée sur ses mesures, narration treg resserrée,
ambiances et bruitages Mixkit enregistrés, chacun sur une action visible."""
import json, numpy as np, librosa, soundfile as sf
SR, DUREE = 48000, 82.2
n = int(DUREE * SR)
ch = lambda f: librosa.load(f, sr=SR, mono=True)[0]
rng = np.random.default_rng(7)

def fondu(x, a=.012, b=.012):
    x = x.copy(); ka, kb = int(a * SR), int(b * SR)
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x
def poser(piste, x, t, g=1.0):
    i = int(round(t * SR))
    if i < 0: x = x[-i:]; i = 0
    x = x[:max(0, len(piste) - i)]; piste[i:i + len(x)] += g * x

# ---------- musique : le silence de la partition tombe juste après « savoir », le drop sur la salle 3 ----------
m = ch('musique.mp3')
OFF1 = 4.26                 # vidéo = musique − OFF1 (silence 61,34 → 57,08 ; drop 63,115 → 58,855)
MES = 4 * .5341             # une mesure du groove (112,3 BPM)
A = 63.163 + 4 * MES        # après 4 mesures de groove…
B = A + 6 * MES             # … on saute 6 mesures pour que le coup final (96,4) tombe à ~79,3 s
OFF2 = OFF1 + 6 * MES
mus = np.zeros(n)
poser(mus, fondu(m[int(4.26 * SR):int(A * SR)], .01, .02), 0)
poser(mus, fondu(m[int(B * SR):], .02, .01), B - OFF2)
mus[int(81.6 * SR):] *= np.linspace(1, 0, n - int(81.6 * SR))

# ---------- voix ----------
voix = np.zeros(n); poser(voix, ch('voix/narr_montee.wav'), 0)
vv = voix[np.abs(voix) > 1e-3]; gv = np.sqrt(np.mean(vv ** 2))
env = np.convolve(np.abs(voix), np.ones(int(.05 * SR)) / int(.05 * SR), 'same')
parle = np.convolve((env > .01).astype(float), np.ones(int(.35 * SR)) / int(.35 * SR), 'same').clip(0, 1)
gm = np.sqrt(np.mean(mus[np.abs(mus) > 1e-3] ** 2))
tt = np.arange(n) / SR
sous = np.where(tt < 6.4, -12, np.where(tt < 58.85, -18, -14))   # hook porté par la musique, corps plus bas
mus_g = (gv / gm) * (10 ** (sous / 20) * parle + 10 ** ((sous + np.where(tt > 58.8, 11, 8)) / 20) * (1 - parle))

# ---------- ambiances ----------
amb = np.zeros(n)
def ambiance(id_, a, b, g, off=0):
    y = ch(f'sfx/{id_}.mp3'); y = y[int(off * SR):int((off + b - a) * SR)]
    poser(amb, fondu(y, .3, .4) / (np.sqrt(np.mean(y ** 2)) + 1e-9), a, gv * 10 ** (g / 20))
ambiance(3080, 0, 6.55, -30)          # salle du musée
ambiance(3080, 14.42, 18.86, -31, 8)
ambiance(3080, 23.38, 28.86, -31, 15)
ambiance(352, 28.86, 31.95, -27, 5)   # supermarché
ambiance(361, 37.62, 41.62, -23, 20)  # marché
ambiance(375, 41.62, 48.12, -29, 10)  # rue derrière le comptoir
ambiance(3080, 58.85, 64.62, -31, 22)
ambiance(361, 68.0, 70.76, -24, 45)
ambiance(3080, 70.76, 82.2, -32, 30)

# ---------- bruitages enregistrés ----------
def sfx(id_, dmax=None):
    y = ch(f'sfx/{id_}.mp3'); e = np.abs(y); i = np.argmax(e > e.max() * .12)
    y = y[max(0, i - int(.004 * SR)):]
    if dmax: y = fondu(y[:int(dmax * SR)], .002, .04)
    return y / (np.abs(y).max() + 1e-9)
def varie(y):
    r = 1 + rng.uniform(-.03, .03); return np.interp(np.arange(0, len(y) - 1, r), np.arange(len(y)), y)
pv = np.percentile(np.abs(vv), 99.5)
MOTS = json.loads(open('mots_video.js').read().split('=', 1)[1].rstrip(';\n'))
M = lambda i: MOTS[i][1]
BRUITS = [  # (instant, son, gain dB / crête voix, durée max)
    (.55, 2585, -9, .4), (1.05, 2579, -10, .4), (M(10) - .1, 2585, -8, .4),   # les projecteurs s'allument
    (6.62, 1530, -16, .8),                       # le brevet glisse sous la lumière
    (M(28), 1939, -13, 1.0),                     # « se servent » : pièces
    (M(39), 1365, -11, .4), (M(39) + .32, 1382, -13, .4),   # touches de la caisse
    (M(43), 1368, -12, 1.2),                     # sonnette de caisse sur « caisse enregistreuse »
    (M(68) - .1, 1061, -10, .5),                 # l'horloge passe à 8 h 01
    (M(85) + .42, 1073, -7, .32),                # bip du scanner, au bout du laser
    (M(121) + .05, 2383, -15, .4), (M(124) + .05, 2383, -16, .4),   # barres rouges
    (M(155), 2299, -15, .6),                     # le produit disparaît du rayon
    (M(164) + .05, 461, -20, 1.0),               # le client s'en va
    (M(174) + .35, 2383, -13, .4),               # « vendre » barré
    (57.08, 2579, -7, .4),                       # lumière coupée : silence
    (58.83, 2585, -6, .4),                       # projecteur de la salle 3 sur le drop
    (M(190), 2383, -14, .4),                     # le million barré
    (M(199) + .05, 2573, -10, .4), (M(199) + .2, 2354, -14, .6),   # tap + bandeau « ajouté »
    (M(203) - .05, 2354, -13, .6),               # chez le patron
    (M(212), 1120, -14, .5),                     # « même sans réseau »
    (M(215) - .08, 2585, -11, .4), (M(225) - .08, 2579, -12, .4), (M(231) - .08, 2585, -10, .4),   # récap
    (M(240), 2573, -14, .3),                     # on tape le mot
]
fx = np.zeros(n); dern = None
for t, s, g, d in BRUITS:
    y = varie(sfx(s, d)); dt = rng.uniform(-.012, .012); gg = g + rng.uniform(-1.5, 1.5)
    poser(fx, y, t + dt, pv * 10 ** (gg / 20))

mix = voix + mus * mus_g + amb + fx
sf.write('mix_brut.wav', mix / (np.abs(mix).max() + 1e-9) * .9, SR)
print('ok', len(BRUITS), 'bruitages', 'fin', DUREE)
