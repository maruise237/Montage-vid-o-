"""Bande son de la pub KamForms (type pub / motion design). Voix Fish Audio (9 phrases), musique synthétisée,
bruitages pris dans sons.json (exporté par l'animation : chaque bruit colle à une action visible).
Ouverture : pad + charleston léger sous le hook, riser, DROP sur « Le principe est simple ».
Ponctuation : musique coupée juste avant « GRATUIT », boom, elle repart. Fin : carillon + extinction.
Usage : node kamforms3/rendu.mjs sons && python3 kamforms3/son.py → kamforms3/son.wav"""
import json, os, sys
import numpy as np
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{os.path.dirname(ICI)}/outils')
from bruitages import *
os.chdir(ICI)
TL = json.load(open('timeline.json')); S = json.load(open('sons.json'))
DUREE = TL['duree']; N = int(SR * (DUREE + .1)); P = TL['phrases']
w = lambda p, k: P[p - 1]['mots'][k][1]
VOIX = np.zeros(N)
for p in P:
    v = lire(f"voix/p{p['i']}.wav", 'highpass=f=70,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3500:t=q:w=1.4:g=2,'
             'acompressor=threshold=-20dB:ratio=3:attack=6:release=110:makeup=3dB')
    i = int(p['off'] * SR); VOIX[i:i + len(v)] += v[:N - i]
ML, MR, BL, BR = (np.zeros(N) for _ in range(4))
def add(l, r, s, t, pan=0, g=1):
    i = int(t * SR)
    if i < 0: s = s[-i:]; i = 0
    if i < N: s = s[:N - i] * g; l[i:i + len(s)] += s * min(1, 1 - pan); r[i:i + len(s)] += s * min(1, 1 + pan)
mus = lambda s, t, pan=0, g=1: add(ML, MR, s, t, pan, g)
bru = lambda s, t, pan=0, g=1: add(BL, BR, s, t, pan, g)

DROP = P[2]['debut'] - .02                     # « Le principe est simple »
GRAT = w(8, 2) - .07                           # « gratuit »
FIN = P[8]['fin'] + .25
NOIRE = 60 / 120; ACC = [57.0, 43.65, 65.41, 49.0]          # La m – Fa – Do – Sol (graves)
ARP = {57.0: [220, 261.6, 329.6, 440], 43.65: [174.6, 220, 261.6, 349.2], 65.41: [261.6, 329.6, 392, 523.3], 49.0: [196, 246.9, 293.7, 392]}
def mesure(t, m, plein):
    f = ACC[m % 4]; mus(pad(f * 4, 4 * NOIRE + .3), t, 0, .6 if plein else .9)
    for b in range(4):
        tb = t + b * NOIRE
        mus(hat(.35 if plein else .22), tb + NOIRE / 2, .2)
        if plein:
            if b in (0, 2): mus(kick(.9), tb)
            if b in (1, 3): mus(clap(.55), tb, .05)
            mus(basse(f, NOIRE * .5), tb); mus(basse(f, NOIRE * .3, .6), tb + NOIRE * .75)
            mus(pluck(ARP[f][(b + m) % 4], .3, .5), tb + NOIRE / 2, (-.3, .3)[b % 2])
        elif b % 2 == 0:
            mus(pluck(ARP[f][b // 2 % 4] * 2, .5, .35), tb, (-.25, .25)[b // 2])
def boucle(t0, t1, plein, m0=0):
    t, m = t0, m0
    while t < t1 - .05: mesure(t, m, plein); t += 4 * NOIRE; m += 1
boucle(0, DROP, False); boucle(DROP, GRAT - .3, True); boucle(GRAT, FIN + 1.2, True, 2)
mus(kick(1.1), DROP); mus(impact(.5), DROP)

# ---- bruitages (depuis l'animation) ----
PAN = [-.25, .25]; n = 0
for t, k, x in S['sons']:
    n += 1; pan = PAN[n % 2]
    if k == 'touche': bru(touche(.38), t, pan * .6)
    elif k == 'clic': bru(tic(.9), t); bru(touche(.5), t + .01)
    elif k == 'pop': bru(pop(x or 800, .55), t, pan * .5)
    elif k == 'whoosh': bru(whoosh(.42, True, .7), t - .12, pan)
    elif k == 'whoosh2': bru(whoosh(.3, False, .55), t - .06, -pan)
    elif k == 'coche': bru(pop(1250, .45), t); bru(tic(.6), t + .04)
    elif k == 'impact': bru(impact(.9), t)
    elif k == 'impact2': bru(impact(.5), t); bru(pop(520, .35), t)
    elif k == 'boom': bru(impact(1.1), t); bru(kick(.9), t)
    elif k == 'surligne': bru(whoosh(.22, True, .35), t, pan)
    elif k == 'raye': bru(whoosh(.28, False, .5), t)
    elif k == 'etincelle': bru(etincelle(1.0), t, pan)
    elif k == 'message': bru(pop(1100, .5), t); bru(pop(1650, .4), t + .09)
    elif k == 'ding': bru(caisse(.8), t)
    elif k == 'verrou': bru(tic(.9), t); bru(tic(.7), t + .07)
    elif k == 'compte':
        for i in range(10): bru(tic(.6), t + .6 * (i / 9) ** 1.6)
    elif k == 'telecharge': bru(riser(1.5, .45), t)
    elif k == 'fin': bru(caisse(1.0), t)
    elif k == 'riser': bru(riser(1.1, .8), t)
    elif k == 'drop': pass

# ---- mixage : ducking sous la voix, coupure avant GRATUIT, extinction finale ----
blk = int(SR * .01); nb = N // blk + 1
e = np.sqrt((np.pad(VOIX, (0, nb * blk - N)) ** 2).reshape(nb, blk).mean(1)); e /= np.percentile(e, 95) + 1e-9
sm = np.zeros(nb); p = 0
for i, v in enumerate(e): p = v if v > p else p * .93 + v * .07; sm[i] = p
duck = np.interp(np.arange(N) / blk, np.arange(nb), 1 - .45 * np.clip(sm * 1.8, 0, 1))
tt = np.arange(N) / SR; g = np.ones(N)
g[(tt > GRAT - .32) & (tt < GRAT)] = 0
g[tt < DROP] = .75
g[tt > FIN + .6] = np.clip(1 - (tt[tt > FIN + .6] - FIN - .6) / 1.0, 0, 1)
duck *= g
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
parle = np.repeat(sm > .3, blk)[:N]; mm = (ML + MR) / 2 * duck
GM = 10 ** ((db(VOIX[parle]) - 16 - db(mm[parle & (tt > DROP)])) / 20)
bb = (BL + BR) / 2
GB = 10 ** ((db(VOIX[parle]) - 12 - db(bb[np.abs(bb) > 1e-3])) / 20)
L = VOIX + ML * GM * duck + BL * GB; R = VOIX + MR * GM * duck + BR * GB
pk = max(np.abs(L).max(), np.abs(R).max()); L /= pk / .89; R /= pk / .89
ecrire('son.wav', L, R)
print(f'musique sous la voix : {db(VOIX[parle]) - db(mm[parle & (tt > DROP)] * GM):.1f} dB ; durée {N / SR:.1f} s')
