"""Bande son « Y'a plus » v2 : musique Lyria montée sur ses mesures, voix treg, ambiances et bruitages Mixkit enregistrés."""
import json, numpy as np, librosa, soundfile as sf
SR, DUREE = 48000, 58.6
n = int(DUREE * SR)
ch = lambda f: librosa.load(f, sr=SR, mono=True)[0]
rng = np.random.default_rng(3)

def fondu(x, a=.012, b=.012):
    x = x.copy(); ka, kb = int(a * SR), int(b * SR)
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x

def poser(piste, x, t, g=1.0):
    i = int(round(t * SR)); x = x[:max(0, len(piste) - i)]; piste[i:i + len(x)] += g * x

# ---------- musique : 4 morceaux raccordés sur des temps forts ----------
m = ch('musique.mp3')
MONT = [  # (début musique, fin musique, instant vidéo)
    (0.00, 29.83, 0.00),    # intro clairsemée, puis la basse entre avec la cliente (13,32 s)
    (31.48, 35.60, 29.83),  # 1 mesure retirée : le roulement tombe sur les tampons qui s'empilent
    (45.32, 56.93, 36.40),  # après le silence : le drop (45,37) sur le bouton pressé
    (66.84, 78.50, 48.01),  # 6 mesures retirées : coup final (75,50) à 56,67 s, juste après « aujourd'hui »
]
mus = np.zeros(n)
for a, b, t in MONT:
    poser(mus, fondu(m[int(a * SR):int(b * SR)], .02, .02), t)
mus[int(58.25 * SR):] *= np.linspace(1, 0, n - int(58.25 * SR))

# ---------- voix ----------
tl = json.load(open('timeline.json'))['voix']
voix = np.zeros(n)
for k, t in tl:
    poser(voix, ch(f'clips/{k}.wav'), t)
gv = np.sqrt(np.mean(voix[np.abs(voix) > 1e-3] ** 2)); pv = np.percentile(np.abs(voix[np.abs(voix) > 1e-3]), 99.5)

# ducking : musique ~17 dB sous la voix, plus franche dans les respirations
env = np.convolve(np.abs(voix), np.ones(int(.05 * SR)) / int(.05 * SR), 'same')
parle = np.convolve((env > .01).astype(float), np.ones(int(.3 * SR)) / int(.3 * SR), 'same').clip(0, 1)
gm = np.sqrt(np.mean(mus[np.abs(mus) > 1e-3] ** 2))
mus_g = (gv / gm) * (10 ** (-17 / 20) * parle + 10 ** (-8 / 20) * (1 - parle))

# ---------- bruitages enregistrés ----------
def sfx(id_, dmax=None):
    y = ch(f'sfx/{id_}.mp3'); e = np.abs(y); i = np.argmax(e > e.max() * .12)  # on cale l'attaque
    y = y[max(0, i - int(.004 * SR)):]
    if dmax: y = fondu(y[:int(dmax * SR)], .002, .04)
    return y / (np.abs(y).max() + 1e-9)

def varie(y):  # jamais deux fois le même son à l'identique : hauteur ±3 %
    r = 1 + rng.uniform(-.03, .03)
    return np.interp(np.arange(0, len(y) - 1, r), np.arange(len(y)), y)

BRUITS = [  # (instant, son, gain dB / crête voix, durée max)
    (3.50, 1989, -7, 1.0),            # « très cher » : sac de pièces
    (4.15, 1490, -15, .8),             # entrée boutique
    (5.33, 483, -11, .6),              # le tuyau PVC claque
    (7.87, 2182, -3, .8), (7.88, 2114, -9, .6),   # tampon
    (8.08, 1939, -13, .8),             # le compteur tombe
    (8.48, 1489, -17, 1.0),
    (9.42, 2580, -9, .5),              # levier du disjoncteur
    (12.51, 2114, -4, .6), (12.52, 2182, -10, .8),
    (14.97, 1530, -18, .7),            # seau posé (feuille sous le seau)
    (16.88, 2182, -3, .8), (16.90, 483, -13, .5),
    (17.05, 1993, -13, .8),
    (18.18, 175, -12, .7),             # bascule alimentation
    (18.62, 2389, -16, .8),            # sac de riz
    (20.46, 2114, -4, .6), (20.47, 2182, -11, .8),
    (21.50, 166, -12, .7),             # bascule téléphonie
    (23.63, 2182, -4, .8),
    (24.86, 2299, -5, 1.2), (24.90, 1989, -10, 1.0),  # total de la journée
    (27.25, 1606, -11, 1.5),           # le client part à moto
    (29.52, 2354, -22, .5),            # téléphone du patron : rien
    (30.41, 2300, -9, 2.0),            # « rien »
    (31.48, 2182, -14, .5), (32.20, 2114, -15, .5), (32.85, 2182, -13, .5),
    (36.23, 2580, -7, .5),             # le bouton pressé
    (40.85, 2573, -10, .5), (40.92, 2354, -13, .6),   # tap + bandeau « ajouté »
    (41.48, 1490, -15, .8),            # chez le patron
    (42.90, 2357, -12, .7),            # la ligne arrive
    (43.66, 2356, -17, .5),            # pastille réseau
    (45.95, 1120, -10, .5), (46.65, 1120, -11, .5), (47.15, 1120, -9, .5),  # coches
    (47.93, 1489, -16, 1.0),           # retour boutique
    (49.02, 483, -11, .6),
    (51.19, 2182, -5, .8), (51.30, 2003, -9, 1.0), (51.48, 1939, -14, .8),  # Y'en a ! + monnaie
    (52.55, 931, -9, 1.5),             # sonnette de comptoir sur le logo
    (54.75, 2364, -17, .4), (55.23, 2364, -18, .4),
    (56.30, 1393, -16, .7),            # l'adresse se tape
]
fx = np.zeros(n)
for t, i, g, d in BRUITS:
    poser(fx, varie(sfx(i, d)), t + rng.uniform(-.012, .012), pv * 10 ** ((g + rng.uniform(-1.5, 1.5)) / 20))

# ambiances : rue (boutique) et marché, sous tout le reste
amb = np.zeros(n)
def ambiance(id_, a, b, g, off=0):
    y = ch(f'sfx/{id_}.mp3')[int(off * SR):]; L = int((b - a) * SR); y = np.resize(y, L)
    poser(amb, fondu(y, .4, .5) / (np.sqrt(np.mean(y ** 2)) + 1e-9), a, gv * 10 ** (g / 20))
ambiance(375, 4.15, 24.95, -24, 3)
ambiance(361, 28.5, 31.5, -22, 20)
ambiance(361, 41.45, 47.95, -25, 40)
ambiance(375, 47.9, 52.5, -25, 20)

mix = voix + mus * mus_g + fx + amb
sf.write('mix_brut.wav', mix / np.abs(mix).max() * .9, SR)
print('ok', len(BRUITS), 'bruitages')
