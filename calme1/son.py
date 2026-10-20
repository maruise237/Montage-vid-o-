"""Bande son de calme1 : la piste de Mariuse (voix + musique, brut.mp3) passe telle quelle ;
quelques bruitages discrets sur les coupes (whoosh, glitch), un impact sourd sur « personne » et sur le drop.
Usage : python3 calme1/son.py → calme1/son.wav"""
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
bru(whoosh(.35, True), SC[1] - .3, .7); bru(glitch(.2), SC[2] - .05, .6)
bru(whoosh(.45, False), SC[3] - .2, .6); bru(impact(), R['T_PERS'], .6)
bru(impact(), R['T_DROP'], .5)
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
B *= 10 ** ((db(P) - 12 - db(B[np.abs(B) > 1e-4])) / 20)      # bruitages ~12 dB sous la piste
L = P + B; pk = np.abs(L).max(); ecrire('son.wav', L / pk * .89, L / pk * .89)
print('son.wav')
