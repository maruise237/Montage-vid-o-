"""Bande son de la vidéo avatar n°1. Voix nettoyée (avatar1/voix_montee.wav), hook presque sec (frappe du code),
riser → la musique démarre sur « nouveau cap ». Ponctuation : musique coupée sur « si vous ne sentez pas les
hésitations », riser, elle repart sur « ça veut dire que Claude… ». Whoosh aux changements de décor, pops sur
cartes/logos/poses, impact sur les mots géants, carillon sur l'écran final. Musique ~17 dB sous la voix.
Usage : python3 avatar1/son.py → avatar1/son.wav"""
import json, os, sys
import numpy as np
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{os.path.dirname(ICI)}/outils')
from bruitages import *
os.chdir(ICI)
EV = json.load(open('evenements.json')); DUREE = EV['duree']; N = int(SR * (DUREE + .3))
sys.path.insert(0, ICI)
from montage import T, FIN_VOIX

v = lire('voix_montee.wav')
VOIX = np.zeros(N); VOIX[:min(N, len(v))] = v[:N]
ML, MR, BL, BR = (np.zeros(N) for _ in range(4))
def add(l, r, s, t, pan=0, g=1):
    i = int(t * SR)
    if 0 <= i < N: s = s[:N - i] * g; l[i:i + len(s)] += s * min(1, 1 - pan); r[i:i + len(s)] += s * min(1, 1 + pan)
mus = lambda s, t, pan=0, g=1: add(ML, MR, s, t, pan, g)
bru = lambda s, t, pan=0, g=1: add(BL, BR, s, t, pan, g)

NOIRE = 60 / 112; ACC = [55.0, 43.65, 65.41, 49.0]
ARP = {55.0: [220, 261.6, 329.6, 440], 65.41: [261.6, 329.6, 392, 523.3], 49.0: [196, 246.9, 293.7, 392], 43.65: [174.6, 220, 261.6, 349.2]}
def boucle(t0, t1, m0=0, brillant=False):
    t, m = t0, m0
    while t < t1:
        f = ACC[m % 4]; mus(pad(f * 4, 4 * NOIRE + .3), t, 0, .55)
        for b in range(4):
            tb = t + b * NOIRE
            if tb >= t1: break
            if b in (0, 2): mus(kick(.85), tb)
            if b in (1, 3): mus(clap(.55), tb, .05)
            mus(hat(.35), tb + NOIRE / 2, .2)
            if brillant: mus(hat(.25, .03), tb + NOIRE / 4, -.25); mus(hat(.25, .03), tb + 3 * NOIRE / 4, .25)
            mus(basse(f, NOIRE * .5), tb)
            mus(pluck(ARP[f][(b + m) % 4], .3, .45), tb + NOIRE / 2, (-.3, .3)[b % 2])
        t += 4 * NOIRE; m += 1

T_MUS = T['nous'] - .05
T_COUPE, T_REPRISE = T['et'] - .1, T['travail'] - 1.4   # « ça veut dire que Claude… »
boucle(T_MUS, T['marcher']); boucle(T['marcher'], DUREE + .1, 2, brillant=True)
mus(riser(1.1, .8), T_MUS - 1.15); mus(riser(1.2, .7), T_REPRISE - 1.2)
bru(impact(.7), T_MUS)

n_sc = 0; fond_prec = None
for t, k, x in EV['ev']:
    if k == 'scene':
        if x != fond_prec and fond_prec is not None: bru(whoosh(.36, True, .7), t - .30, (.3, -.3)[n_sc % 2])
        elif n_sc % 2 == 1: bru(pop(700, .45), t + .05)
        fond_prec = x; n_sc += 1
    elif k == 'impact': bru(impact(.75), t)
    elif k == 'pop': bru(pop(820 + 60 * (len(x) % 4), .5), t, ((len(x) % 3) - 1) * .2)
    elif k == 'croix': bru(impact(.35), t); bru(pop(420, .4), t)
    elif k == 'whoosh': bru(whoosh(.45, True, .8), t - .2)
    elif k == 'frappe':
        for j in range(int(x / .075)):
            if (j * 7) % 5 != 0: bru(touche(.35), t + .1 + j * .075, ((j % 3) - 1) * .15)
bru(impact(.9), FIN_VOIX + .05); bru(carillon(1320, 1.6, .35), FIN_VOIX + .1)

blk = int(SR * .01); nb = N // blk + 1
e = np.sqrt((np.pad(VOIX, (0, nb * blk - N)) ** 2).reshape(nb, blk).mean(1)); e /= np.percentile(e, 95) + 1e-9
sm = np.zeros(nb); p = 0
for i, val in enumerate(e): p = val if val > p else p * .93 + val * .07; sm[i] = p
duck = np.interp(np.arange(N) / blk, np.arange(nb), 1 - .5 * np.clip(sm * 1.8, 0, 1))
tt = np.arange(N) / SR; g = np.ones(N)
g[(tt > T_COUPE) & (tt < T_REPRISE)] = 0                         # silence musical sur la phrase-chute
g[(tt > T_COUPE - .15) & (tt <= T_COUPE)] = np.linspace(1, 0, ((tt > T_COUPE - .15) & (tt <= T_COUPE)).sum())
fin = DUREE - .4; g[tt > fin] = np.clip(1 - (tt[tt > fin] - fin) / .4, 0, 1)
duck *= g
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
parle = np.repeat(sm > .3, blk)[:N]; mm = (ML + MR) / 2 * duck
GM = 10 ** ((db(VOIX[parle]) - 17 - db(mm[parle])) / 20)
GB = 10 ** ((db(VOIX[parle]) - 13 - db(((BL + BR) / 2)[np.abs(BL) > 1e-4])) / 20)
L = VOIX + ML * GM * duck + BL * GB; R = VOIX + MR * GM * duck + BR * GB
pk = max(np.abs(L).max(), np.abs(R).max()); L /= pk / .89; R /= pk / .89
ecrire('son.wav', L, R)
print(f'musique sous la voix : {db(VOIX[parle]) - db(mm[parle] * GM):.1f} dB')
