"""Bande son de mystere1 : la piste de Mariuse (voix + musique déjà mixées, brut.mp3) passe telle quelle ;
on ajoute seulement quelques bruitages discrets sur les actions visibles : glitch à la coupe vers la ruelle,
flash (impact) sur la scène des fans, impact sur « FAN », glitch sur le retour du regard.
Usage : python3 mystere1/son.py → mystere1/son.wav"""
import json, os, sys
import numpy as np
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{os.path.dirname(ICI)}/outils')
from bruitages import *
os.chdir(ICI)
R = json.load(open('reperes.json')); SC = [s[0] for s in R['SC']]; N = int(SR * (R['DUREE'] + .1))
piste = lire('brut.mp3'); P = np.zeros(N); P[:min(N, len(piste))] = piste[:N]
B = np.zeros(N)
def bru(s, t, g=1):
    i = int(t * SR); s = s[:N - i] * g; B[i:i + len(s)] += s
bru(glitch(.25), SC[1] - .1); bru(whoosh(.35, True), SC[1] - .3, .6)
bru(impact(), SC[2], .8)
bru(impact(), R['T_FAN'], .7)
if len(SC) > 4: bru(glitch(.2), SC[4] - .05, .7)
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
B *= 10 ** ((db(P) - 12 - db(B[np.abs(B) > 1e-4])) / 20)      # bruitages ~12 dB sous la piste
L = P + B; pk = np.abs(L).max(); ecrire('son.wav', L / pk * .89, L / pk * .89)
print('son.wav')
