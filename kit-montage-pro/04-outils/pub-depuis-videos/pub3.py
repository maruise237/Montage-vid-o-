"""PUB 3 — « Tu commandes, on fabrique » (≈ 1 min 50, voix d'animateur + réponses, musique Lyria sur mesure via treg).
Concept : un animateur passe des commandes, la vraie machine les fabrique, un tampon rouge « C'EST FAIT » s'écrase,
et un bon de commande s'imprime ligne par ligne. Finale : l'enseigne lumineuse. Fin : le ticket complet + WhatsApp.
Voix : Gemini 3.8 Flash TTS (Fenrir = animateur, Laomedeia = réponses), musique : Lyria 3.5 (instrumentale)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outils_pub import P, C, plans_vers_temps

ICI = os.path.dirname(os.path.abspath(__file__))
CALQUE_HTML = 'calque3.html'
REP = json.load(open(os.path.join(ICI, 'pub3', 'voix', 'repliques.json')))
G = json.load(open(os.path.join(ICI, 'pub3', 'musique_grille.json')))
COUPE_A = min(G['mesures'], key=lambda m: abs(m - 58.70))    # 4 mesures retirées au milieu du morceau
COUPE_B = min(G['mesures'], key=lambda m: abs(m - 66.90))    # (raccord sur deux 1ers temps)
M = [m for m in G['mesures'] if m < COUPE_A - .01] + [round(m - (COUPE_B - COUPE_A), 3) for m in G['mesures'] if m >= COUPE_B - .01]
MUS_MORCEAUX = [(0.0, COUPE_A, 0.0), (COUPE_B, None, COUPE_A)]
DUREE = 110.0
d = lambda n: REP[n]['d']
f30 = lambda t: round(t * 30) / 30

# ---------------------------------------------------------------- voix (temps sur la timeline)
V = {}
V['A1'] = .25
V['A2'] = V['A1'] + d('A1') + .15
V['r1'] = V['A2'] + d('A2') + .15
V['B'] = M[3] - .1                                     # « C'est comment Yaoundé » sur un 1er temps
V['C'] = V['B'] + d('B') + .2
REPONSE = ['r9', 'r11', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r12']   # r2 (« Fait ! » seul) trop ambigu : remplacé
TAMPON = {'r1': "C'EST FAIT !", 'r2': 'FAIT !', 'r3': 'ET VOILÀ !', 'r4': 'DÉJÀ FAIT', 'r5': "C'EST FAIT, CHEF",
          'r6': 'FAIT · FAIT · FAIT', 'r7': "ET C'EST FAIT", 'r8': 'VOILÀ !', 'r9': "C'EST FAIT", 'r10': "C'EST FAIT !", 'r11': 'DÉJÀ PRÊT !', 'r12': "C'EST FAIT, PATRON"}
ITEMS = []
for k in range(9):
    s = M[8 + 3 * k]
    q = f'Q{k + 1}'; r = REPONSE[k]
    tq = s + .08
    tr = max(tq + d(q) + .12, M[8 + 3 * k + 1] - .08)
    ITEMS.append(dict(s=s, q=q, tq=tq, r=r, tr=tr, fin=M[8 + 3 * k + 3]))
    V[f'{q}'] = tq
FIN0 = M[35]
V['F1'] = FIN0 + .1
T_GRAND = M[39]                                        # grand « C'EST FAIT » après un silence
V['r10'] = T_GRAND - .12
T_CTA = M[43]
V['CTA2'] = T_CTA + .15

def mot_t(n, i):
    """temps (timeline) du i-ème mot de la réplique n"""
    return V[n] + REP[n]['mots'][i]['s']


# ---------------------------------------------------------------- plans
def B31(**k): return dict(z0=1.25, z1=1.30, py=1.0, **k)
SEQ = []                                              # (début timeline, constructeur de plan sans durée)
def plan(t, f, *a, **k): SEQ.append((f30(t), f, a, k))

# hook
plan(0, P, 'v11', 9.4, z0=1.10, z1=1.18)
plan(mot_t('A1', 6), P, 'v01', 8.5, z0=1.08, z1=1.16)             # « Sur une casquette »
plan(V['A2'], P, 'v10', 3.0, z0=1.50, z1=1.64, py=.29)
plan(V['r1'], C, 'v14', 45.5, crop=(0, .31, 1, .70))
plan(V['B'], P, 'v09', 2.0, z0=1.10, z1=1.20)                     # C'est comment Yaoundé !
plan(mot_t('B', 5), P, 'v31', .6, **B31())                        # Ici, chez Nguelek Print…
MACH = [('v12', .4, dict(z0=1.25, z1=1.32)), ('v04', 4.1, dict(z0=1.4, z1=1.48, py=0)), ('v15', .6, dict(z0=1.7, z1=1.8, py=.45)),
        ('v07', 20.0, dict(z0=1.7, z1=1.8, px=.85, py=.05)), ('v13', 12.6, dict(z0=1.25, z1=1.32)), ('v24', .3, dict(z0=1.1, z1=1.2))]
t = mot_t('B', 12)                                                 # « on ne sous-traite rien »
pas = (V['C'] - t) / len(MACH)
for i, (src, a, kw) in enumerate(MACH): plan(t + i * pas, P, src, a, **kw)
plan(V['C'], P, 'v32', .3, z0=1.15, z1=1.25, px=.4)
plan(V['C'] + REP['C']['mots'][5]['s'], P, 'v16', 20.0, z0=1.12, z1=1.2)   # « on fabrique »
# commandes : (machine, résultat 1, résultat 2)
CMD = [
    (('v12', .3, dict(z0=1.15, z1=1.22)), ('v01', 8.5, dict(z0=1.08, z1=1.15)), ('v01', 17.0, dict(z0=1.08, z1=1.15))),
    (('v13', 2.2, dict(z0=1.15, z1=1.24)), ('v11', 9.4, dict(z0=1.1, z1=1.18)), ('v04', 6.4, dict(z0=1.4, z1=1.46, py=0))),
    (('v16', 2.0, dict(z0=1.08, z1=1.15)), ('v16', 20.0, dict(z0=1.15, z1=1.25)), ('v16', 15.5, dict(z0=1.1, z1=1.18))),
    (('v03', 2.0, dict(z0=1.35, z1=1.42, py=1.0)), ('v05', 8.6, dict(z0=1.35, z1=1.42, py=0)), ('v03', 36.6, dict(z0=1.35, z1=1.42, py=1.0))),
    (('v29', 18.4, dict(z0=1.15, z1=1.22, py=.1)), ('v28', 20.3, dict(z0=1.15, z1=1.22, py=.1)), ('v20', 8.5, dict(z0=1.3, z1=1.36, py=.15))),
    (('v15', .5, dict(z0=1.5, z1=1.62, py=.45)), ('v02', 18.2, dict(z0=1.45, z1=1.5, py=.15)), ('v02', 8.0, dict(z0=1.45, z1=1.5, py=.15))),
    (('v24', .3, dict(z0=1.1, z1=1.18)), ('C', 'v25', 18.0, dict(crop=(0, 0, 1, .76))), ('C', 'v27', 0.0, dict(crop=(0, 0, 1, .60)))),
    (('v22', .5, dict(z0=1.3, z1=1.36, py=.1)), ('v22', 20.0, dict(z0=1.3, z1=1.36, py=.1)), ('v21', 14.3, dict(z0=1.3, z1=1.36, py=.2))),
    (('v06', .3, dict(z0=1.65, z1=1.72, py=0)), ('v06', 10.6, dict(z0=1.65, z1=1.7, py=0)), ('v06', 23.4, dict(z0=1.6, z1=1.66, py=0))),
]
for it, (m, r1, r2) in zip(ITEMS, CMD):
    for t0, sh in ((it['s'], m), (it['tr'], r1), (M[M.index(it['s']) + 2], r2)):
        if sh[0] == 'C': plan(t0, C, sh[1], sh[2], **sh[3])
        else: plan(t0, P, sh[0], sh[1], **sh[2])
# finale : l'enseigne, de la planche au toit allumé
F = lambda i: V['F1'] + REP['F1']['mots'][i]['s']
plan(FIN0, P, 'v07', 14.5, z0=1.12, z1=1.25)                     # Et le plus gros…
plan(F(4) - .05, P, 'v08', 1.0, z0=1.15, z1=1.2, px0=.15, px1=.7)  # ton nom en lettres géantes
plan(F(9) - .05, P, 'v07', 20.0, z0=1.7, z1=1.8, px=.85, py=.05)   # découpé
plan(F(10) - .05, P, 'v08', 8.0, z0=1.15, z1=1.22, px=.7)          # monté
plan(F(11) - .05, P, 'v09', 2.0, z0=1.1, z1=1.2)                    # posé sur ton toit
plan(F(15) - .05, P, 'v10', 3.0, z0=1.5, z1=1.75, py=.29)          # et allumé toute la nuit
for i, (src, a, kw) in enumerate([('v14', 45.5, dict(crop=(0, .31, 1, .70))), ('v14', .3, dict(crop=(0, .23, 1, .77))),
                                   ('v14', 4.0, dict(crop=(0, .18, 1, .82))), ('v23', 4.5, dict(largeur=980))]):
    plan(M[39 + i], C, src, a, **kw)
plan(T_CTA, P, None, 0, mode='noir')
SEQ.sort(key=lambda x: x[0])
PLANS = []
for i, (t0, f, a, k) in enumerate(SEQ):
    t1 = SEQ[i + 1][0] if i + 1 < len(SEQ) else f30(DUREE)
    PLANS.append(f(a[0], a[1], round(t1 - t0, 4), **k))
T = plans_vers_temps(PLANS)

# ---------------------------------------------------------------- calque
CORR = {'Ngelech': 'Nguelek', 'Gelec': 'Nguelek', 'yaoundé.': 'Yaoundé !', 'messassi,': 'Messassi,', 'relouquée': 'relookée',
        '2000': '2 000', 'illumineuse': 'lumineuse', 'portes': 'porte-', 'brodées': 'brodés', '-trait': '-traite'}
def jetons(n, cles=()):
    out = []
    for m in REP[n]['mots']:
        w = CORR.get(m['w'], m['w'])
        if w in ('?', '!', '.', ','): continue
        if out and (w.startswith('-') or w.startswith("'") or out[-1]['w'].endswith('-')):
            out[-1]['w'] = (out[-1]['w'] + w).replace('--', '-'); continue
        out.append({'w': w, 't': round(V[n] + m['s'], 3)})
    if n == 'B':                       # whisper entend « comme en » : la voix dit « C'est comment Yaoundé ! »
        i = next(i for i, o in enumerate(out) if o['w'] == 'comme'); out[i]['w'] = 'comment'
        if out[i + 1]['w'] == 'en': del out[i + 1]
    if n == 'Q3' and out[-1]['w'] != 'francs':
        fr = next(m for m in json.load(open(os.path.join(ICI, 'pub3', 'voix', 'items.mots.json'))) if m['w'].startswith('francs'))
        out.append({'w': 'francs', 't': round(V[n] + fr['s'] - REP[n]['a'], 3)})
    if n in ('F1',):
        for o in out: o['w'] = {'lettre': 'lettres', 'géante,': 'géantes,'}.get(o['w'], o['w'])
    if n.startswith('Q') or n in ('A1', 'A2'):
        out[-1]['w'] += ' ?'
        if n == 'A1': out[4]['w'] += ' ?'
    for o in out: o['cle'] = any(c in o['w'].lower() for c in cles)
    return out

CLES = {'Q1': ('brodés',), 'Q2': ('logo',), 'Q3': ('2 000', 'francs'), 'Q4': ('couleurs',), 'Q5': ('trophées',),
        'Q6': ('gravés',), 'Q7': ('photo',), 'Q8': ('maman',), 'Q9': ('relookée',)}
LIGNES = ['01 POLOS BRODÉS', '02 STYLOS LOGO', '03 PORTE-STYLOS', '04 SACS & AGENDAS', '05 TROPHÉES',
          '06 PORTE-CLÉS', '07 VEILLEUSE', '08 GOURDE', '09 FAÇADE']

def groupes(n, decoupe):
    """sous-titres en groupes de mots (indices de jetons), affichés jusqu'au groupe suivant"""
    J = jetons(n); G = []
    for gi, g in enumerate(decoupe):
        t0 = J[g[0]]['t']; t1 = J[decoupe[gi + 1][0]]['t'] if gi + 1 < len(decoupe) else V[n] + d(n) + .25
        G.append({'t0': t0, 't1': t1, 'html': ' '.join(f"<b>{J[i]['w']}</b>" if J[i]['w'].lower() in ('nguelek', 'print,', 'print', 'messassi,', 'yaoundé !', 'fabrique.') else J[i]['w'] for i in g)})
    return G

CALQUE = [
    {'type': 'degrade', 't0': 0, 't1': V['B'], 'haut': True, 'h': 760, 'force': .5},
    {'type': 'question', 't0': 0, 't1': V['A2'], 'y': 210, 'px': 118, 'mots': jetons('A1', ('stylo', 'casquette'))},
    {'type': 'question', 't0': V['A2'], 't1': V['B'], 'y': 210, 'px': 124, 'mots': jetons('A2', ('enseigne', 'lumineuse'))},
    {'type': 'tampon', 't': V['r1'] + .1, 't1': V['B'] - .1, 'txt': TAMPON['r1'], 'px': 170, 'y': 1420, 'vx': 0, 'vy': 0},
    {'type': 'degrade', 't0': V['B'], 't1': ITEMS[0]['s'], 'haut': False, 'h': 900, 'force': .65},
    {'type': 'sous', 'y': 1360, 'groupes': groupes('B', [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9], [10, 11, 12, 13], [14, 15, 16], [17, 18, 19, 20]])},
    {'type': 'pastille', 't0': mot_t('B', 7) - .1, 't1': mot_t('B', 12), 'x': 390, 'y': 760, 'taille': 300},
    {'type': 'sous', 'y': 1360, 'groupes': groupes('C', [[0, 1, 2], [3, 4], [5, 6]])},
    {'type': 'ticket', 't0': V['C'] + .7, 't1': FIN0, 'sortie': True,
     'lignes': [{'txt': LIGNES[k], 't': it['tr'] + 1.3} for k, it in enumerate(ITEMS)]},
]
for k, it in enumerate(ITEMS):
    CALQUE += [{'type': 'degrade', 't0': it['s'], 't1': it['tr'] + .3, 'haut': True, 'h': 720, 'force': .55},
               {'type': 'question', 't0': it['tq'] - .02, 't1': it['tr'] + .25, 'sortie': True, 'y': 200, 'px': 108,
                'mots': jetons(it['q'], CLES[it['q']])},
               {'type': 'tampon', 't': it['tr'] + .1, 't1': it['tr'] + 1.15, 'txt': TAMPON[it['r']], 'px': 175 if len(TAMPON[it['r']]) < 12 else 128,
                'rot': (-9, 7, -12, 5, -7, 10, -10, 6, -8)[k], 'y': 860 + (k % 3) * 40}]
CALQUE += [
    {'type': 'degrade', 't0': FIN0, 't1': T_GRAND, 'haut': False, 'h': 900, 'force': .65},
    {'type': 'sous', 'y': 1380, 'groupes': groupes('F1', [[0, 1, 2, 3], [4, 5, 6, 7, 8], [9], [10], [11, 12, 13, 14], [15, 16, 17, 18, 19]])},
    {'type': 'tampon', 't': T_GRAND, 't1': T_CTA - .2, 'txt': TAMPON['r10'], 'px': 210, 'rot': -8, 'y': 1450, 'vx': 0, 'vy': 0},
    {'type': 'fin', 't0': T_CTA, 't1': DUREE + 1, 'duree_impression': 3.2,
     'lignes': LIGNES + ['10 ENSEIGNE LUMINEUSE'],
     'numero': [{'txt': '676', 't': V['CTA2'] + REP['CTA2']['mots'][11]['s']}, {'txt': '11', 't': V['CTA2'] + REP['CTA2']['mots'][12]['s']},
                {'txt': '30', 't': V['CTA2'] + REP['CTA2']['mots'][13]['s']}, {'txt': '57', 't': V['CTA2'] + REP['CTA2']['mots'][14]['s']}],
     'tampon': 'ON EST ENSEMBLE !', 't_tampon': V['CTA2'] + REP['CTA2']['mots'][-1]['s'] + .05},
]

# ---------------------------------------------------------------- son
def son(dossier):
    import numpy as np
    from son_reel import Bus, charger, extrait, fondu, ambiance, bruit, mixer, SONS, SR, lp
    import shutil
    dst = os.path.join(SONS, 'musique', 'lyria_pub3.mp3')
    if not os.path.exists(dst): shutil.copy(os.path.join(ICI, 'pub3', 'musique_lyria.mp3'), dst)
    from son_reel import musique_montee
    Mu = musique_montee('lyria_pub3', MUS_MORCEAUX, DUREE)
    a, b = int((T_GRAND - .45) * SR), int(T_GRAND * SR)                # silence avant le grand « C'EST FAIT »
    q = int(.03 * SR); Mu.x[:, a - q:a] *= np.linspace(1, 0, q); Mu.x[:, a:b] = 0
    A = Bus(DUREE); Bb = Bus(DUREE); Vb = Bus(DUREE)
    for n, t in [(n, V[n]) for n in ('A1', 'A2', 'r1', 'B', 'C', 'F1', 'r10', 'CTA2')] + [(it['q'], it['tq']) for it in ITEMS] + [(it['r'], it['tr']) for it in ITEMS]:
        x = charger(os.path.join(ICI, 'pub3', 'voix', f'seg_{n}.wav'))
        Vb.poser(fondu(x, .006, .03), t, 1.0 if n[0] != 'r' else .9, .0 if n[0] != 'r' else .08)
    v = Vb.x.mean(0); v = v - lp(v, 80)                              # coupe-bas
    v = np.tanh(v / (np.abs(v).max() + 1e-9) * 2.2) * .75             # compression douce : la voix porte
    # son direct des machines (sources sans chanson)
    for i, (t0, f, a_, k) in enumerate(SEQ):
        src = a_[0]
        if src in ('v12', 'v04', 'v15', 'v07', 'v09', 'v11'):
            ambiance(A, src, a_[1], PLANS[i]['d'], t0, .55)
    TAMP = [2182]
    for e in CALQUE:
        if e['type'] == 'tampon':
            bruit(Bb, TAMP, e['t'] - .005, .9); bruit(Bb, [2380], e['t'] - .03, .35, d=.3)
        if e['type'] == 'ticket':
            for l in e['lignes']: bruit(Bb, [1371], l['t'] - .05, .28, d=.5)
        if e['type'] == 'fin':
            for k in range(5): bruit(Bb, [1371], e['t0'] + .2 + k * .62, .3, d=.62)
            bruit(Bb, TAMP, e['t_tampon'] - .005, 1.0); bruit(Bb, [2380], e['t_tampon'] - .03, .4, d=.3)
    bruit(Bb, [459], T_GRAND + .05, .32, varier=False)                    # petite foule sur la grande révélation
    bruit(Bb, [2585], V['A2'] + .55, .6, varier=False)                     # l'enseigne s'allume
    mixer(os.path.join(dossier, 'son.wav'), DUREE, Mu, A, Bb, v, g_mus=.42, g_amb=.55, g_bru=.6)


if __name__ == '__main__':
    print('mesures', M[:12], '…', len(M))
    for n in ('A1', 'A2', 'r1', 'B', 'C', 'F1', 'r10', 'CTA2'): print(n, round(V[n], 2), '→', round(V[n] + d(n), 2))
    for it in ITEMS: print(it['q'], round(it['s'], 2), 'Q', round(it['tq'], 2), '→', round(it['tq'] + d(it['q']), 2), it['r'], round(it['tr'], 2), 'fin', round(it['fin'], 2))
    print('plans', len(PLANS), 'durée', T[-1], 'grand', T_GRAND, 'cta', T_CTA, 'fin CTA', round(V['CTA2'] + d('CTA2'), 2))
    print('plans courts', [(i, p['src'], p['d']) for i, p in enumerate(PLANS) if p['d'] < .3])
