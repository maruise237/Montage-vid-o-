"""PUB 2 — « Le cadeau qui ne finit pas dans la cuisine » (cible : particuliers, cadeaux personnalisés).
Portée par la voix du patron (v31) : hook punchline · présentation · produits · « contactez-nous » · fin."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outils_pub import P, C, sous_titres, plans_vers_temps

from son_reel import grille, affiner
from outils_pub import caler

# voix du patron recalées sur leurs vrais silences (plus de mots coupés)
H = affiner('v31', 36.45, 39.75)        # « N'offrez plus… dans la cuisine »
BJ = affiner('v31', .55, 4.35)          # « Bonjour, bonjour… Nguelek Print »
BS = affiner('v31', 5.0, 11.25)         # « Alors vous êtes dans le besoin… N'allez pas chercher problème »
CO = affiner('v31', 20.7, 23.4)         # « Forme de notre continent »
MS = affiner('v31', 26.35, 30.9)        # « Vous pouvez y mettre le message… autant de photos… »
CT = affiner('v31', 31.9, 34.9)         # « Alors, contactez-nous… votre commande »
MA = affiner('v17', 41.3, 45.98)        # « votre cérémonie reste gravée dans la mémoire à jamais »

B31 = dict(z0=1.25, z1=1.30, py=1.0)    # patron : on coupe le numéro incrusté en haut
L = lambda a, b, queue=.12: round(b - a + queue, 3)   # durée d'un plan synchro voix
PLANS = [
    P('v31', H[0], L(*H), z0=1.25, z1=1.38, py=1.0, cale=False),   # 0  hook (voix sèche, pas de musique)
    C('v27', 0.0, 2.0, crop=(0, 0, 1, .60)),                        # 1  « offrez un souvenir » : la musique entre
    P('v31', BJ[0], L(*BJ), cale=False, **B31),                      # 2  bonjour… Nguelek Print
    P('v31', BS[0], 7.0 - BS[0], z0=1.30, z1=1.36, py=1.0, cale=False),  # 3  dans le besoin…
    C('v25', 4.0, 9.80 - 7.0, crop=(0, 0, 1, .76), cale=False),     # 4  cadeau précieux (B-roll)
    P('v31', 9.80, L(9.80, BS[1], .15), z0=1.45, z1=1.55, py=.9, px=.6, min=L(9.80, BS[1], .15)),  # 5 problème
    # veilleuses
    P('v24', 0.3, 1.5, z0=1.10, z1=1.18),                        # 6
    C('v25', 18.0, 1.5, crop=(0, 0, 1, .76)),                    # 7
    C('v26', 4.0, 1.5, crop=(0, 0, 1, .68)),                     # 8
    C('v27', 8.0, 1.5, crop=(0, 0, 1, .60)),                     # 9
    # gourdes
    P('v22', 0.5, 1.5, z0=1.30, z1=1.36, py=.1),                 # 10
    P('v22', 20.0, 1.5, z0=1.30, z1=1.36, py=.1),                # 11
    P('v21', 14.3, 1.5, z0=1.30, z1=1.36, py=.2),                # 12
    # thermos
    P('v32', 0.3, 1.5, z0=1.10, z1=1.18),                        # 13
    P('v32', 9.0, 1.5, z0=1.10, z1=1.16),                        # 14
    P('v32', 24.0, 1.5, z0=1.10, z1=1.16),                       # 15
    # horloges
    P('v18', 2.0, 1.5, z0=1.40, z1=1.46, py=.1),                 # 16
    P('v31', CO[0], L(*CO), cale=False, **B31),                  # 17 forme de notre continent
    P('v31', MS[0], 1.70, cale=False, **B31),                    # 18 vous pouvez y mettre…
    P('v17', 44.3, 1.4, z0=1.50, z1=1.56, py=.5, cale=False),    # 19 photos
    C('v25', 0.5, 1.9, crop=(0, 0, 1, .76), min=L(*MS, .1) - 3.1),  # 20
    # porte-clés
    P('v02', 18.2, 1.5, z0=1.45, z1=1.50, py=.15),               # 21
    P('v19', 8.2, 1.5, z0=1.50, z1=1.56, py=.55),                # 22
    P('v17', 8.4, 1.5, z0=1.40, z1=1.46, py=.45),                # 23
    # mariages (voix v17)
    P('v30', 55.7, 1.6, z0=1.20, z1=1.26, py=.3, cale=False),    # 24
    P('v30', 69.6, 1.5, z0=1.20, z1=1.26, py=.3, cale=False),    # 25
    C('v26', 25.3, 2.6, crop=(0, 0, 1, .68), min=L(*MA, .15) - 3.1),  # 26
    # entreprises
    P('v29', 30.8, 1.2, z0=1.15, z1=1.20, py=.1),                # 27
    P('v28', 22.3, 1.2, z0=1.15, z1=1.20, py=.1),                # 28
    P('v20', 10.6, 1.2, z0=1.30, z1=1.34, py=.15),               # 29
    P('v16', 20.0, 1.2, z0=1.15, z1=1.20),                       # 30
    # CTA
    P('v31', CT[0], L(*CT), min=L(*CT), **B31),                  # 31 contactez-nous
    P(None, 0, 9.0, mode='noir', cale=False),                    # 32 fin : vraie fin du morceau
]
MUS = 5                                    # « Feeling Happy » (Mixkit, licence Stock Music Free)
BEATS = grille(MUS)
T0M = PLANS[0]['d']                        # la musique démarre après le hook, son 1er temps sur la coupe
DEP = T0M - BEATS[0]
caler(PLANS[1:-1], [b + DEP for b in BEATS], T0M)
SAUT = min(BEATS, key=lambda b: abs(b - 137.1))
FIN_MUS = 147.0
PLANS[-1]['d'] = round(round((FIN_MUS - SAUT) * 30) / 30, 4)
T = plans_vers_temps(PLANS)
MORCEAUX_MUS = [(BEATS[0], T[32] - DEP, T0M), (SAUT, None, T[32])]
COUPE_MUS = (T[5], T[6])                   # silence musical sous « N'allez pas chercher problème »

VOIX = [('v31', *H, T[0]), ('v31', *BJ, T[2]), ('v31', *BS, T[3]), ('v31', *CO, T[17]), ('v31', *MS, T[18]),
        ('v17', *MA, T[24] + .1), ('v31', *CT, T[31])]

def st(mots, groupes, src_debut, t_debut, y=1450, ys=None):
    return sous_titres(mots, groupes, decalage=t_debut - src_debut, y=y, ys=ys)

M_BONJOUR = [('Bonjour,', .62, 1.28), ('bonjour.', 1.46, 1.86), ('Vous êtes ici', 2.42, 3.04),
             ('chez', 3.04, 3.28), ('Nguelek Print', 3.28, 4.24, 1)]
M_BESOIN = [('Alors vous êtes', 5.0, 5.6), ('dans le besoin', 5.6, 6.3), ("d'offrir un", 6.3, 7.02),
            ('cadeau', 7.02, 7.46, 1), ('précieux', 7.46, 8.18, 1), ("à quelqu'un", 8.18, 8.82), ('de', 8.82, 8.98),
            ('spécial.', 8.98, 9.42, 1)]
M_CONT = [('Forme de', 20.74, 21.82), ('notre', 21.82, 22.58), ('continent.', 22.58, 23.38, 1)]
M_MSG = [('Vous pouvez', 26.4, 26.84), ('y mettre', 26.84, 27.2), ('le', 27.2, 27.5), ('message', 27.5, 27.88, 1),
         ('que vous désirez.', 27.88, 28.84), ('Autant de', 28.84, 29.8), ('photos', 29.8, 30.1, 1),
         ('que vous désirez.', 30.1, 30.84)]
M_MARI = [('votre', 41.34, 42.26), ('cérémonie', 42.26, 43.32, 1), ('reste', 43.32, 43.72), ('gravée', 43.72, 44.6, 1),
          ('dans la', 44.6, 45.06), ('mémoire', 45.06, 45.92, 1), ('à jamais.', 45.95, 46.5)]
M_CTA = [('Alors,', 31.92, 32.42), ('contactez-nous', 32.42, 33.04, 1), ('tout simplement', 33.04, 33.6),
         ('pour passer', 33.6, 34.32), ('votre', 34.32, 34.58), ('commande.', 34.58, 34.84, 1)]

def etiquette_produit(i0, i1, haut, bas, coul='m'):
    """titre de rubrique en haut : un mot en capitales sur bande de couleur + précision en serif"""
    return [{'type': 'degrade', 't0': T[i0], 't1': T[i1], 'haut': True, 'h': 640, 'force': .5},
            {'type': 'titre', 't0': T[i0] + .05, 't1': T[i1], 'x': 66, 'y': 210, 'lignes': [
                {'txt': haut, 'police': 'sans', 'px': 104, 'coul': '#111' if coul in ('j', 'b') else 'b', 'fond': coul},
                {'txt': bas, 'police': 'serif', 'px': 76, 'coul': 'b', 'dt': .15}]}]

CALQUE = [
    # hook (voix sèche, texte au mot près)
    {'type': 'degrade', 't0': 0, 't1': T[1], 'haut': False, 'h': 900, 'force': .7},
    {'type': 'titre', 't0': 36.45 - H[0], 't1': T[1], 'x': 66, 'y': 1180, 'lignes': [
        {'txt': "N'offrez plus", 'police': 'serif', 'px': 128, 'coul': 'b', 'dt': 0.1},
        {'txt': 'de cadeaux qui', 'police': 'sans', 'px': 104, 'coul': 'b', 'dt': 0.95},
        {'txt': 'finissent', 'police': 'sans', 'px': 104, 'coul': 'b', 'dt': 2.15},
        {'txt': 'dans la cuisine.', 'police': 'serif', 'px': 150, 'coul': 'j', 'dt': 2.62}]},
    # souvenir
    {'type': 'titre', 't0': T[1], 't1': T[2], 'x': 66, 'y': 1560, 'lignes': [
        {'txt': 'Offrez un', 'police': 'serif', 'px': 120, 'coul': 'b'},
        {'txt': 'souvenir.', 'police': 'sans', 'px': 150, 'coul': '#111', 'fond': 'j', 'dt': .2}]},
    # présentation
    st(M_BONJOUR, [[0, 1], [2], [3, 4]], BJ[0], T[2], y=760),
    {'type': 'logo', 't0': T[2] + (3.28 - BJ[0]) - .05, 't1': T[3], 'fond': 'transparent', 'taille': 500, 'y': 1120},
    st(M_BESOIN, [[0], [1], [2, 3], [4], [5, 6, 7]], BS[0], T[3], ys=[760, 760, 1450, 1450, 1450]),
    {'type': 'degrade', 't0': T[5], 't1': T[6], 'haut': False, 'h': 1000, 'force': .75},
    {'type': 'titre', 't0': T[5] + .05, 't1': T[6], 'x': 66, 'y': 1240, 'lignes': [
        {'txt': "N'allez pas", 'police': 'serif', 'px': 130, 'coul': 'b'},
        {'txt': 'chercher', 'police': 'sans', 'px': 140, 'coul': 'b', 'dt': .2},
        {'txt': 'problème.', 'police': 'sans', 'px': 160, 'coul': 'b', 'fond': 'm', 'dt': .5}]},
    # produits
    {'type': 'balayage', 't': T[6], 'couleurs': ['c', 'm', 'j', 'n']},
    *etiquette_produit(6, 10, 'Veilleuses LED', 'votre photo, votre message', 'm'),
    {'type': 'detail', 't0': T[6] + .15, 't1': T[7], 'txt': 'impression directe', 'coul': 'c', 'y': 1560},
    {'type': 'detail', 't0': T[8] + .15, 't1': T[10], 'txt': '7 couleurs', 'coul': 'j', 'y': 1640},
    *etiquette_produit(10, 13, 'Gourdes bambou', 'gravées au laser', 'j'),
    *etiquette_produit(13, 16, 'Coffret thermos', '+ 3 tasses, à votre image', 'c'),
    *etiquette_produit(16, 17, 'Horloges', 'bois sculpté & résine', 'm'),
    st(M_CONT, [[0, 1], [2]], CO[0], T[17]),
    st(M_MSG, [[0, 1], [2, 3], [4], [5, 6], [7]], MS[0], T[18]),
    *etiquette_produit(21, 24, 'Porte-clés', 'bois · métal · photo', 'j'),
    *etiquette_produit(24, 27, 'Mariages', '& anniversaires', 'm'),
    st(M_MARI, [[0, 1], [2, 3], [4, 5], [6]], MA[0], T[24] + .1),
    *etiquette_produit(27, 31, 'Et pour vos', 'trophées & cadeaux d’entreprise', 'c'),
    # appel
    {'type': 'balayage', 't': T[31], 'couleurs': ['j', 'c', 'm', 'n']},
    st(M_CTA, [[0, 1], [2], [3], [4, 5]], CT[0], T[31]),
    # fin
    {'type': 'balayage', 't': T[32]},
    {'type': 'fin', 't0': T[32], 't1': T[33],
     'accroche': [{'txt': 'Le cadeau qui ne finit', 'police': 'serif', 'px': 92, 'coul': 'n'},
                  {'txt': 'pas dans la cuisine.', 'police': 'sans', 'px': 84, 'coul': 'b', 'fond': 'm'}],
     'lieu1': 'Carrefour Messassi', 'lieu2': 'face au commissariat · Yaoundé',
     'tel': '676 11 30 57', 'horaires': 'Lun – Sam · 7h30 – 18h00',
     'plus': 'Livraison & expédition partout'},
]


PAPIER = [1530, 2380, 1105, 2386]
DECLIC = [1133, 1430, 1434, 1440]


def son(dossier):
    from son_reel import Bus, musique_montee, bruit, voix, mixer, SR
    D = T[-1]
    M = musique_montee(MUS, MORCEAUX_MUS, D)
    a, b = int(COUPE_MUS[0] * SR), int(COUPE_MUS[1] * SR)     # la musique se tait sur la punchline
    q = int(.04 * SR); M.x[:, a:b] = 0; M.x[:, a - q:a] *= np.linspace(1, 0, q)
    A = Bus(D); B = Bus(D)
    bruit(B, [2585], T[1] - .02, .7, varier=False)            # la veilleuse s'allume
    for e in CALQUE:
        if e['type'] == 'balayage': bruit(B, PAPIER, e['t'] - .22, .55)
    bruit(B, [1104], T[16] + .02, .45)                          # page qu'on tourne : nouvelle rubrique
    bruit(B, [2839], T[21] + .05, .4, d=.7)                     # vrai trousseau de clés
    for k, t in enumerate(T[27:31]):
        if k != 2: bruit(B, DECLIC, t, .4)
    V = voix(D, VOIX)
    mixer(os.path.join(dossier, 'son.wav'), D, M, A, B, V, g_mus=.6, g_bru=.55)
