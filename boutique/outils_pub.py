"""Petits utilitaires partagés par pub1.py et pub2.py."""


def P(src, t, d, **k):
    """plan plein écran"""
    return dict(src=src, t=t, d=d, mode=k.pop('mode', 'plein'), **k)


def C(src, t, d, **k):
    """plan « tirage photo » sur fond flouté"""
    return dict(src=src, t=t, d=d, mode='cadre', **k)


def plans_vers_temps(plans):
    t, L = 0.0, []
    for p in plans:
        L.append(round(t, 3)); t += p['d']
    L.append(round(t, 3))
    return L


def sous_titres(mots, groupes, decalage, y=1180, ys=None):
    """mots : [(texte, début, fin[, emphase])] dans la source ; groupes : listes d'indices (1 à 3 mots).
    Chaque groupe reste affiché jusqu'au début du suivant (ou sa fin + 0,3 s)."""
    G = []
    for gi, g in enumerate(groupes):
        t0 = mots[g[0]][1] + decalage
        t1 = mots[g[-1]][2] + decalage + .3
        if gi + 1 < len(groupes):
            t1 = min(t1 + .5, mots[groupes[gi + 1][0]][1] + decalage)
        html = ' '.join(f'<em>{mots[i][0]}</em>' if len(mots[i]) > 3 and mots[i][3] else mots[i][0] for i in g)
        G.append({'t0': round(t0, 3), 't1': round(t1, 3), 'html': html, **({'y': ys[gi]} if ys else {})})
    return {'type': 'sous', 'y': y, 'groupes': G}
