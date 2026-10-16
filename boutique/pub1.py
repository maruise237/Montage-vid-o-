"""PUB 1 — « L'atelier » : NGUELEK PRINT fabrique tout sur place (cible : entreprises, commerces, événements).
Structure : hook avant/après (planche → enseigne allumée) · « tout est fabriqué ici » · logo ·
7 services numérotés (couleurs CMJN du logo) · « et tout le reste » · écran de fin (adresse + WhatsApp)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outils_pub import P, C, sous_titres, plans_vers_temps

# ---------------------------------------------------------------- PLANS (timeline)
PLANS = [
    # HOOK avant / après
    P('v07', 3.0, 1.5, z0=1.30, z1=1.42),                       # 0.0  planche découpée (CNC)
    P('v10', 3.0, 1.5, z0=1.50, z1=1.62, py=.29),               # 1.5  enseigne allumée la nuit
    # « tout est fabriqué ici » : les machines
    P('v12', 0.4, .6, z0=1.25, z1=1.32),                        # 3.0  brodeuse
    P('v04', 4.1, .6, z0=1.40, z1=1.48, py=0),                  # 3.6  UV (lumière bleue)
    P('v15', 0.6, .6, z0=1.70, z1=1.80, py=.45),                # 4.2  laser
    P('v13', 12.6, .6, z0=1.25, z1=1.32),                       # 4.8  UV stylos
    P('v07', 20.0, .6, z0=1.70, z1=1.80, px=.85, py=.05),       # 5.4  broche CNC
    # LOGO
    P(None, 0, 2.0, mode='noir'),                               # 6.0
    # 01 ENSEIGNES LUMINEUSES
    P('v07', 14.5, 2.0, z0=1.12, z1=1.22),                      # 8.0
    P('v08', 1.0, 2.5, z0=1.15, z1=1.20, px0=.15, px1=.85),     # 10.0 lettres en relief
    P('v09', 2.0, 2.0, z0=1.10, z1=1.18),                       # 12.5 pose sur le toit
    P('v09', 12.9, 1.5, z0=1.05, z1=1.12, py=.4),               # 14.5 de jour
    C('v14', 45.5, 1.5, crop=(0, .31, 1, .70)),                 # 16.0 de nuit
    C('v14', 0.3, 1.25, crop=(0, .23, 1, .77)),                 # 17.5 Daina beauty
    C('v14', 4.0, 1.25, crop=(0, .18, 1, .82)),                 # 18.75 An's glow home
    C('v23', 4.5, 1.5, largeur=980),                            # 20.0 Lik Andres shop
    # 02 HABILLAGE DE FAÇADE
    P('v06', 0.3, 2.0, z0=1.65, z1=1.72, py=0),                 # 21.5
    P('v06', 10.6, 1.0, z0=1.65, z1=1.70, py=0),                # 23.5
    P('v06', 23.4, 1.5, z0=1.60, z1=1.66, py=0),                # 24.5
    # 03 IMPRESSION UV
    P('v13', 2.2, 1.5, z0=1.15, z1=1.24),                       # 26.0
    P('v11', 9.4, 2.0, z0=1.10, z1=1.18),                       # 27.5
    P('v32', 0.3, 1.5, z0=1.20, z1=1.28, px=.4),                # 29.5
    P('v16', 2.0, 2.3, z0=1.08, z1=1.15),                       # 31.0  voix : porte-stylos
    P('v16', 6.0, 2.3, z0=1.10, z1=1.17),                       # 33.3
    P('v16', 15.5, 2.3, z0=1.10, z1=1.18),                      # 35.6
    P('v16', 20.0, 2.4, z0=1.15, z1=1.25),                      # 37.9
    # 04 BRODERIE & TEXTILE
    P('v12', 0.3, 1.5, z0=1.15, z1=1.22),                       # 40.3
    P('v12', 11.3, 1.5, z0=1.20, z1=1.28),                      # 41.8
    P('v01', 8.5, 1.5, z0=1.08, z1=1.15),                       # 43.3
    P('v01', 17.0, 1.5, z0=1.08, z1=1.15),                      # 44.8
    # 05 GRAVURE LASER
    P('v15', 0.5, 2.0, z0=1.50, z1=1.62, py=.45),               # 46.3
    P('v15', 9.0, 1.5, z0=1.50, z1=1.58, py=.45),               # 48.3
    P('v30', 42.0, 2.0, z0=1.30, z1=1.36, py=.15),               # 49.8
    # 06 SACS & AGENDAS
    P('v03', 2.0, 2.0, z0=1.35, z1=1.42, py=1.0),               # 51.8
    P('v05', 8.6, 2.0, z0=1.35, z1=1.42, py=0),                 # 53.8
    # 07 TROPHÉES
    P('v29', 18.4, 2.0, z0=1.15, z1=1.22, py=.1),               # 55.8
    P('v28', 20.3, 2.0, z0=1.15, z1=1.22, py=.1),               # 57.8
    P('v20', 8.5, 2.0, z0=1.30, z1=1.36, py=.15),               # 59.8
    # ET TOUT LE RESTE (rafale)
    P('v26', 4.5, .4, z0=1.30, py=.1),                          # 61.8
    P('v21', 14.3, .4, z0=1.40, py=.3),
    P('v18', 21.0, .4, z0=1.40, py=.1),
    P('v17', 44.3, .4, z0=1.50, py=.5),
    P('v02', 18.3, .4, z0=1.45, py=.15),
    P('v31', 22.0, .4, z0=1.20, py=1.0),
    P('v19', 8.2, .4, z0=1.50, py=.55),
    P('v30', 56.0, .4, z0=1.20, py=.3),
    # FIN
    P(None, 0, 8.0, mode='noir'),                               # 65.0
]
T = plans_vers_temps(PLANS)   # T[i] = début du plan i

# ---------------------------------------------------------------- CALQUE
def chap(i0, i1, num, nom, nom2, sous, coul):
    return {'type': 'chapitre', 't0': T[i0], 't1': T[i1], 'num': num, 'nom': nom, 'nom2': nom2, 'sous': sous, 'coul': coul}

def det(i, txt, coul='m', y=1500, d=None):
    t1 = T[i] + d if d else T[i + 1]
    return {'type': 'detail', 't0': T[i] + .12, 't1': t1, 'txt': txt, 'coul': coul, 'y': y}

VOIX = [('v16', 2.30, 11.55, T[22])]
MOTS16 = [  # transcription corrigée (faster-whisper + écoute) — temps dans la source v16
    ('Personnalisez', 2.37, 3.87), ('les', 3.87, 4.05), ('porte-stylos', 4.05, 5.21, 1), ('de', 5.21, 5.51),
    ('votre', 5.51, 5.95), ('entreprise', 5.95, 7.07, 1), ('et', 7.07, 7.33), ('chez', 7.33, 7.47),
    ('Nguelek Print', 7.47, 8.31, 1), ('à partir', 8.31, 8.97), ('de…', 8.97, 9.77)]
GROUPES16 = [[0], [1, 2], [3, 4, 5], [6, 7, 8], [9, 10]]

CALQUE = [
    # hook
    {'type': 'degrade', 't0': 0, 't1': 3.0, 'haut': True, 'h': 760, 'force': .55},
    {'type': 'titre', 't0': 0.0, 't1': 1.5, 'x': 70, 'y': 240, 'lignes': [
        {'txt': 'De ça…', 'police': 'serif', 'px': 230, 'coul': 'b'}]},
    det(0, 'une planche brute', 'j', y=1560),
    {'type': 'titre', 't0': 1.5, 't1': 3.0, 'x': 70, 'y': 1180, 'lignes': [
        {'txt': '…à ça.', 'police': 'serif', 'px': 250, 'coul': 'j'}]},
    det(1, 'une enseigne lumineuse', 'c', y=1560),
    # tout est fabriqué ici
    {'type': 'degrade', 't0': 3.0, 't1': 6.0, 'haut': False, 'h': 1100, 'force': .7},
    {'type': 'titre', 't0': 3.0, 't1': 6.0, 'x': 70, 'y': 1070, 'lignes': [
        {'txt': 'Tout est', 'police': 'serif', 'px': 150, 'coul': 'b', 'dt': 0},
        {'txt': 'fabriqué', 'police': 'sans', 'px': 190, 'coul': 'b', 'dt': .6},
        {'txt': 'ici.', 'police': 'sans', 'px': 190, 'coul': '#111', 'fond': 'j', 'dt': 1.8}]},
    # logo
    {'type': 'balayage', 't': T[7]},
    {'type': 'logo', 't0': T[7], 't1': T[8], 'taille': 880, 'y': 380, 'slogan': [
        {'txt': 'Vos gadgets publicitaires', 'police': 'serif', 'px': 76, 'coul': 'n'},
        {'txt': 'en un clic.', 'police': 'sans', 'px': 84, 'coul': 'm'}]},
    # 01
    {'type': 'balayage', 't': T[8]},
    chap(8, 16, '01', 'Enseignes', 'lumineuses', '2D & 3D', 'c'),
    det(8, 'découpe numérique', 'c'), det(9, 'lettres en relief', 'c'), det(10, 'pose sur votre façade', 'c'),
    det(11, 'de jour…', 'j'), det(12, '…comme de nuit', 'j', y=1650),
    # 02
    {'type': 'balayage', 't': T[16], 'couleurs': ['m', 'j', 'c', 'n']},
    chap(16, 19, '02', 'Habillage', 'de façade', 'vitrophanie · bâches', 'm'),
    det(16, 'pose sur place', 'm'), det(18, 'un relooking complet', 'm'),
    # 03
    {'type': 'balayage', 't': T[19], 'couleurs': ['j', 'c', 'm', 'n']},
    chap(19, 26, '03', 'Impression', 'UV', 'sur tous vos objets', 'j'),
    det(19, 'stylos', 'j'), det(20, 'à votre logo', 'j'), det(21, 'gourdes & thermos', 'j'),
    sous_titres(MOTS16, GROUPES16, decalage=T[22] - 2.30, y=1440),
    {'type': 'etiquette', 't0': T[22] + (9.77 - 2.30), 't1': T[26], 'x': 640, 'y': 1180, 'rot': -9,
     'haut': 'dès', 'milieu': '2 000', 'bas': 'FCFA'},
    # 04
    {'type': 'balayage', 't': T[26], 'couleurs': ['n', 'c', 'm', 'j']},
    chap(26, 30, '04', 'Broderie', '& textile', 'polos · casquettes · écussons', 'n'),
    det(26, 'machine multi-têtes', 'c'), det(28, 'casquettes', 'c'), det(29, 'polos brodés', 'c'),
    # 05
    {'type': 'balayage', 't': T[30]},
    chap(30, 33, '05', 'Gravure', 'laser', 'métal · bois · bambou', 'c'),
    det(31, 'ouvre-bouteilles', 'm'),
    det(32, 'votre message, gravé', 'm'),
    # 06
    {'type': 'balayage', 't': T[33], 'couleurs': ['m', 'j', 'c', 'n']},
    chap(33, 35, '06', 'Sacs', '& agendas', 'à vos couleurs', 'm'),
    det(33, 'sacs personnalisés', 'j'), det(34, 'agendas & blocs-notes', 'j'),
    # 07
    {'type': 'balayage', 't': T[35], 'couleurs': ['j', 'c', 'm', 'n']},
    chap(35, 38, '07', 'Trophées', None, 'pour vos cérémonies', 'j'),
    det(36, 'awards & galas', 'c'), det(37, 'fêtes & concours', 'c'),
    # et tout le reste
    {'type': 'degrade', 't0': T[38], 't1': T[46], 'haut': False, 'h': 1100, 'force': .65},
    {'type': 'titre', 't0': T[38], 't1': T[46], 'x': 70, 'y': 1150, 'lignes': [
        {'txt': 'Et tout', 'police': 'serif', 'px': 170, 'coul': 'b', 'dt': 0},
        {'txt': 'le reste.', 'police': 'sans', 'px': 200, 'coul': 'b', 'dt': .25}]},
    # fin
    {'type': 'balayage', 't': T[46]},
    {'type': 'fin', 't0': T[46], 't1': T[46] + 8.0,
     'accroche': [{'txt': 'Votre idée,', 'police': 'serif', 'px': 120, 'coul': 'n'},
                  {'txt': 'on la fabrique.', 'police': 'sans', 'px': 100, 'coul': 'n'}],
     'lieu1': 'Carrefour Messassi', 'lieu2': 'face au commissariat · Yaoundé',
     'tel': '676 11 30 57', 'horaires': 'Lun – Sam · 7h30 – 18h00',
     'plus': 'Livraison & expédition partout'},
]

# ---------------------------------------------------------------- SON
def son(dossier):
    from son_commun import (Piste, musique, voix, mixer, whoosh, impact, pop, riser, carillon, caisse, allumage,
                            tic, declic, etincelle, glitch, touche)
    D = T[-1] + PLANS[-1]['d']
    M = musique(D, 120, [(0, 'montee'), (1.5, 'groove'), (6.0, 'montee'), (8.0, 'plein'), (31.0, 'groove'),
                         (40.3, 'plein'), (61.8, 'plein'), (65.0, 'fin')], 'energie',
                courbe=[(0, .7), (1.5, 1), (60, 1), (65, 1.15), (D, 1.15)])
    B = Piste(D)
    B.add(riser(1.4, 1.0), 0.1, 0, .7)
    B.add(impact(1.0), 1.5); B.add(allumage(.45, 1.0), 1.5, .2)          # l'enseigne s'allume
    for k, t in enumerate(T[2:7]): B.add(declic(1.0), t, (-.3, .3)[k % 2])  # rafale machines
    B.add(pop(520, .9), 3.0 + .6); B.add(pop(700, 1.0), 3.0 + 1.8)
    B.add(riser(1.0, .9), T[7] - 1.0)
    for t in [e['t'] for e in CALQUE if e['type'] == 'balayage']:
        B.add(whoosh(.5, True, 1.0), t - .3, .2); B.add(impact(.6), t)
    lg = T[7]   # pops du logo : N, P, 4 vagues, texte
    for k, dt in enumerate((.08, .16, .34, .41, .48, .55)): B.add(pop(480 + 70 * k, .8), lg + dt, (-.2, .2)[k % 2])
    B.add(carillon(1318, 1.4, .7), lg + 1.0)
    for e in CALQUE:                                                       # chaque étiquette qui apparaît
        if e['type'] == 'detail': B.add(pop(820, .55, .1), e['t0'], .25)
        if e['type'] == 'chapitre': B.add(impact(.5), e['t0'] + .05)
        if e['type'] == 'etiquette': B.add(caisse(1.0), e['t0'])
    for k, t in enumerate(T[38:46]): B.add(declic(1.1), t, (-.3, .3)[k % 2])
    f = T[46]
    for k, dt in enumerate((.08, .16, .34, .41, .48, .55)): B.add(pop(480 + 70 * k, .8), f + dt)
    B.add(carillon(1568, 1.8, .8), f + 1.6); B.add(carillon(2093, 1.6, .5), f + 1.66, .2)
    V = voix(D, VOIX)
    mixer(os.path.join(dossier, 'son.wav'), D, M, B, V, g_mus=.5, g_bru=.55)
