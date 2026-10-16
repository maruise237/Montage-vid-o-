"""PUB 2 — « Le cadeau qui ne finit pas dans la cuisine » (cible : particuliers, cadeaux personnalisés).
Portée par la voix du patron (v31) : hook punchline · présentation · produits · « contactez-nous » · fin."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outils_pub import P, C, sous_titres, plans_vers_temps

B31 = dict(z0=1.25, z1=1.30, py=1.0)          # patron : on coupe le numéro incrusté en haut
PLANS = [
    P('v31', 36.40, 3.30, z0=1.25, z1=1.38, py=1.0),            # 0  hook « n'offrez plus… cuisine »
    C('v27', 0.0, 2.0, crop=(0, 0, 1, .60)),                     # 1  3.3  offrez un souvenir
    P('v31', 0.55, 3.80, **B31),                                 # 2  5.3  bonjour… Nguelek Print
    P('v31', 5.00, 2.00, z0=1.30, z1=1.36, py=1.0),              # 3  9.1  vous êtes dans le besoin…
    C('v25', 4.0, 2.80, crop=(0, 0, 1, .76)),                    # 4  11.1 cadeau précieux
    P('v31', 9.80, 1.40, z0=1.45, z1=1.55, py=.9, px=.6),        # 5  13.9 n'allez pas chercher problème
    # veilleuses
    P('v24', 0.3, 1.5, z0=1.10, z1=1.18),                        # 6  15.3
    C('v25', 18.0, 1.5, crop=(0, 0, 1, .76)),                    # 7  16.8
    C('v26', 4.0, 1.5, crop=(0, 0, 1, .68)),                     # 8  18.3
    C('v27', 8.0, 1.5, crop=(0, 0, 1, .60)),                     # 9  19.8
    # gourdes
    P('v22', 0.5, 1.5, z0=1.30, z1=1.36, py=.1),                 # 10 21.3
    P('v22', 20.0, 1.5, z0=1.30, z1=1.36, py=.1),                # 11 22.8
    P('v21', 14.3, 1.5, z0=1.30, z1=1.36, py=.2),                # 12 24.3
    # thermos
    P('v32', 0.3, 1.3, z0=1.10, z1=1.18),                        # 13 25.8
    P('v32', 9.0, 1.4, z0=1.10, z1=1.16),                        # 14 27.1
    P('v32', 24.0, 1.3, z0=1.10, z1=1.16),                       # 15 28.5
    # horloges
    P('v18', 2.0, 1.6, z0=1.40, z1=1.46, py=.1),                 # 16 29.8
    P('v31', 20.60, 2.80, **B31),                                # 17 31.4 forme de notre continent
    P('v31', 26.30, 1.70, **B31),                                # 18 34.2 vous pouvez y mettre…
    P('v17', 44.3, 1.4, z0=1.50, z1=1.56, py=.5),                # 19 35.9 photos
    C('v25', 0.5, 1.35, crop=(0, 0, 1, .76)),                    # 20 37.3
    # porte-clés
    P('v02', 18.2, 1.5, z0=1.45, z1=1.50, py=.15),               # 21 38.65
    P('v19', 8.2, 1.5, z0=1.50, z1=1.56, py=.55),                # 22 40.15
    P('v17', 8.4, 1.5, z0=1.40, z1=1.46, py=.45),                # 23 41.65
    # mariages (voix v17)
    P('v30', 55.7, 1.6, z0=1.20, z1=1.26, py=.3),                # 24 43.15
    P('v30', 69.6, 1.5, z0=1.20, z1=1.26, py=.3),                # 25 44.75
    C('v26', 25.3, 1.55, crop=(0, 0, 1, .68)),                   # 26 46.25
    # entreprises
    P('v29', 30.8, 1.2, z0=1.15, z1=1.20, py=.1),                # 27 47.8
    P('v28', 22.3, 1.2, z0=1.15, z1=1.20, py=.1),                # 28 49.0
    P('v20', 10.6, 1.2, z0=1.30, z1=1.34, py=.15),               # 29 50.2
    P('v16', 20.0, 1.2, z0=1.15, z1=1.20),                       # 30 51.4
    # CTA
    P('v31', 31.90, 3.00, **B31),                                # 31 52.6 contactez-nous
    P(None, 0, 9.0, mode='noir'),                                # 32 55.6 fin
]
T = plans_vers_temps(PLANS)

VOIX = [('v31', 36.45, 39.75, T[0] + .05), ('v31', 0.55, 4.35, T[2]), ('v31', 5.00, 11.25, T[3]),
        ('v31', 20.70, 23.40, T[17] + .1), ('v31', 26.35, 30.90, T[18] + .05), ('v17', 41.30, 45.98, T[24] + .1),
        ('v31', 31.90, 34.90, T[31])]

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
          ('dans la', 44.6, 45.06), ('mémoire.', 45.06, 45.92, 1)]
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
    {'type': 'titre', 't0': 0.05, 't1': T[1], 'x': 66, 'y': 1180, 'lignes': [
        {'txt': "N'offrez plus", 'police': 'serif', 'px': 128, 'coul': 'b', 'dt': 0.1},
        {'txt': 'de cadeaux qui', 'police': 'sans', 'px': 104, 'coul': 'b', 'dt': 0.95},
        {'txt': 'finissent', 'police': 'sans', 'px': 104, 'coul': 'b', 'dt': 2.15},
        {'txt': 'dans la cuisine.', 'police': 'serif', 'px': 150, 'coul': 'j', 'dt': 2.62}]},
    # souvenir
    {'type': 'titre', 't0': T[1], 't1': T[2], 'x': 66, 'y': 1560, 'lignes': [
        {'txt': 'Offrez un', 'police': 'serif', 'px': 120, 'coul': 'b'},
        {'txt': 'souvenir.', 'police': 'sans', 'px': 150, 'coul': '#111', 'fond': 'j', 'dt': .2}]},
    # présentation
    st(M_BONJOUR, [[0, 1], [2], [3, 4]], 0.55, T[2], y=760),
    {'type': 'logo', 't0': T[2] + (3.28 - .55) - .05, 't1': T[3], 'fond': 'transparent', 'taille': 500, 'y': 1120},
    st(M_BESOIN, [[0], [1], [2, 3], [4], [5, 6, 7]], 5.0, T[3], ys=[760, 760, 1450, 1450, 1450]),
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
    st(M_CONT, [[0, 1], [2]], 20.74, T[17] + .1),
    st(M_MSG, [[0, 1], [2, 3], [4], [5, 6], [7]], 26.4, T[18] + .05),
    *etiquette_produit(21, 24, 'Porte-clés', 'bois · métal · photo', 'j'),
    *etiquette_produit(24, 27, 'Mariages', '& anniversaires', 'm'),
    st(M_MARI, [[0, 1], [2, 3], [4, 5]], 41.30, T[24] + .1),
    *etiquette_produit(27, 31, 'Et pour vos', 'trophées & cadeaux d’entreprise', 'c'),
    # appel
    {'type': 'balayage', 't': T[31], 'couleurs': ['j', 'c', 'm', 'n']},
    st(M_CTA, [[0, 1], [2], [3], [4, 5]], 31.90, T[31]),
    # fin
    {'type': 'balayage', 't': T[32]},
    {'type': 'fin', 't0': T[32], 't1': T[33],
     'accroche': [{'txt': 'Le cadeau qui ne finit', 'police': 'serif', 'px': 92, 'coul': 'n'},
                  {'txt': 'pas dans la cuisine.', 'police': 'sans', 'px': 84, 'coul': 'b', 'fond': 'm'}],
     'lieu1': 'Carrefour Messassi', 'lieu2': 'face au commissariat · Yaoundé',
     'tel': '676 11 30 57', 'horaires': 'Lun – Sam · 7h30 – 18h00',
     'plus': 'Livraison & expédition partout'},
]


def son(dossier):
    from son_commun import (Piste, musique, voix, mixer, whoosh, impact, pop, riser, carillon, caisse, etincelle,
                            declic, touche)
    D = T[-1]
    M = musique(D, 100, [(0, 'calme'), (T[1], 'plein'), (T[2], 'groove'), (T[5], 'coupe'), (T[6], 'plein'),
                         (T[17], 'groove'), (T[21], 'plein'), (T[24], 'groove'), (T[27], 'plein'), (T[31], 'groove'),
                         (T[32], 'fin')], 'doux',
                courbe=[(0, .55), (T[1], 1), (D - 3, 1.1), (D, 1.1)])
    B = Piste(D)
    B.add(riser(1.0, .8), T[1] - 1.0, 0, .6)
    B.add(impact(1.0), T[1]); B.add(etincelle(1.0), T[1] + .05, .2)
    B.add(pop(600, .8), T[1] + .2)
    lg = T[2] + (3.28 - .55) - .05
    for k, dt in enumerate((.08, .16, .34, .41, .48, .55)): B.add(pop(520 + 70 * k, .7), lg + dt, (-.2, .2)[k % 2])
    B.add(impact(.8), T[5] + .05); B.add(pop(380, 1.0, .2), T[5] + .55)
    for t in [e['t'] for e in CALQUE if e['type'] == 'balayage']:
        B.add(whoosh(.5, True, .9), t - .3, .2); B.add(impact(.5), t)
    for e in CALQUE:
        if e['type'] == 'titre' and e['y'] == 210: B.add(whoosh(.35, False, .6), e['t0'] - .05, -.2); B.add(pop(720, .6), e['t0'] + .1)
        if e['type'] == 'detail': B.add(pop(860, .5, .1), e['t0'], .25)
    for t in T[27:31]: B.add(declic(1.0), t)
    f = T[32]
    for k, dt in enumerate((.08, .16, .34, .41, .48, .55)): B.add(pop(480 + 70 * k, .8), f + dt)
    B.add(carillon(1568, 1.8, .8), f + 1.6); B.add(carillon(2093, 1.6, .5), f + 1.66, .2)
    V = voix(D, VOIX)
    mixer(os.path.join(dossier, 'son.wav'), D, M, B, V, g_mus=.55, g_bru=.5)
