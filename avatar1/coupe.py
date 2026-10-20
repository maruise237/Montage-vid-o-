"""Montage de la voix : garde les bonnes phrases, coupes calées sur l'énergie (RMS 10 ms), pas sur whisper."""
import json, subprocess, unicodedata
import numpy as np

SR = 48000
MOTS = json.load(open('avatar1/mots.json'))
# (premier mot, dernier mot, occurrence à partir de t) : phrases gardées, dans l'ordre du montage
GARDE = [
    ('cette vidéo est entièrement montée avec du code', 44),
    ((13.57, 18.07), 'nous venons de passer à un nouveau cap pour la génération de vidéos avec l\'intelligence artificielle'),
    ('Maintenant, nous sommes dans les vidéos illustrées avec Avatar', 17),
    ((23.70, 25.15), 'pour générer cette vidéo,'),
    ('donc tout a été généré de façon 100 % gratuite', 32),
    ((37.45, 41.84), 'mon ami Claude va faire le montage, il va animer mon personnage'),
    ((56.45, 60.77), 'ce n\'est pas un modèle de génération de vidéos comme VO3,'),
    ('ou Clean AI,', 61),
    ('ou Seedense,', 69.5),
    ('cette vidéo va être illustrée par Claude,', 75),
    ('comme je parle de Claude, Claude, tu dois mettre ton logo,', 80),
    ('Change l\'arrière -plan du personnage', 84),
    ((88.80, 90.56), 'mets le personnage dans une ville'),
    ((91.90, 95.09), 'mets maintenant le personnage dans une salle où on voit KAMTECH'),
    ((96.40, 101.08), 'tous ces exemples que je viens de prendre, c\'est juste pour vous montrer la puissance de Claude'),
    ((101.45, 107.97), 'Claude, génère un avatar de toi qui est en train de marcher avec les lunettes sur la plage'),
    ('Ok, mets maintenant mon avatar derrière toi', 108.5),
    ('Ok Claude, merci', 112),
    ('Et si vous ne suivez pas les hésitations, ça veut dire que Claude a encore bien fait son travail, les gars', 116.5),
    ((128.28, 134.62), 'C\'est juste un vocal que j\'ai fait et j\'ai envoyé à Claude. Donc, si vous voyez la vidéo, ça veut dire que Claude m\'a encore surpris'),
]
PAUSE = {  # silence ajouté APRÈS la phrase (s) : respiration, ou place pour un effet visuel
    0: 0.35, 1: 0.3, 2: 0.25, 4: 0.35, 5: 0.3, 8: 0.35, 10: 0.5, 11: 0.7, 12: 0.7, 13: 0.7, 14: 0.4,
    15: 0.8, 16: 0.6, 17: 0.5, 18: 0.4, 19: 1.2,
}


def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    return ''.join(c for c in t if c.isalnum() or c == '%')


def trouver(phrase, apres):
    cibles = [norm(w) for w in phrase.replace("'", " '").split()]
    cibles = [c for c in cibles if c]
    mots = [(norm(m['w']), m) for m in MOTS]
    mots = [(n, m) for n, m in mots if n]
    for i in range(len(mots)):
        if mots[i][1]['s'] < apres - 0.01:
            continue
        if [n for n, _ in mots[i:i + len(cibles)]] == cibles:
            return mots[i][1]['s'], mots[i + len(cibles) - 1][1]['e']
    raise SystemExit(f'introuvable : {phrase}')


def lire(p):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ar', str(SR), '-ac', '1',
                                                  '-f', 's16le', '-']), np.int16).astype(np.float32) / 32768


def caler(a, t, sens, fen):
    """Point le plus calme (RMS 10 ms) dans la fenêtre avant (sens -1) ou après (+1) t."""
    h = SR // 100
    i0, i1 = (t - fen, t + 0.05) if sens < 0 else (t - 0.05, t + fen)
    i0, i1 = max(0, int(i0 * SR)), min(len(a), int(i1 * SR))
    rms = [np.sqrt(np.mean(a[j:j + h] ** 2)) for j in range(i0, i1 - h, h // 2)]
    seuil = min(rms) * 1.5 + 1e-4
    idx = [k for k, r in enumerate(rms) if r <= seuil]
    k = idx[-1] if sens < 0 else idx[0]  # le plus proche de la parole
    return (i0 + k * (h // 2)) / SR


if __name__ == '__main__':
    a = lire('avatar1/voix_propre.wav')
    morceaux, plan, t = [], [], 0.0
    fondu = int(0.012 * SR)
    for k, (x, y) in enumerate(GARDE):
        if isinstance(x, tuple):  # temps source posés à la main (whisper mal aligné à cet endroit)
            (s2, e2), phrase = x, y
        else:
            phrase = x
            s, e = trouver(phrase, y)
            s2, e2 = caler(a, s, -1, 0.35), caler(a, e, +1, 0.45)
        m = a[int(s2 * SR):int(e2 * SR)].copy()
        m[:fondu] *= np.linspace(0, 1, fondu); m[-fondu:] *= np.linspace(1, 0, fondu)
        p = PAUSE.get(k, 0.2)
        morceaux += [m, np.zeros(int(p * SR), np.float32)]
        plan.append({'k': k, 'texte': phrase, 'src': [round(s2, 3), round(e2, 3)], 'debut': round(t, 3),
                     'fin': round(t + len(m) / SR, 3), 'decalage': round(t - s2, 3)})
        t += len(m) / SR + p
    v = np.concatenate([np.zeros(int(0.15 * SR), np.float32)] + morceaux)
    for x in plan:
        x['debut'] += 0.15; x['fin'] += 0.15; x['decalage'] += 0.15
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    'avatar1/voix_montee.wav'], input=v.tobytes(), check=True)
    json.dump(plan, open('avatar1/plan.json', 'w'), ensure_ascii=False, indent=1)
    for x in plan:
        print(f"{x['debut']:6.2f}-{x['fin']:6.2f}  src {x['src'][0]:6.2f}-{x['src'][1]:6.2f}  {x['texte']}")
    print('durée', round(len(v) / SR, 2))
