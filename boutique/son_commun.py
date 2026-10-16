"""Bande son des pubs NGUELEK PRINT : musique originale synthétisée + bruitages + voix (séparée par demucs).
Aucune musique commerciale : tout est généré ici (bruitages = outils/bruitages.py)."""
import numpy as np, os, sys, subprocess, wave
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outils'))
from bruitages import *   # kick, hat, clap, basse, pluck, pad, whoosh, impact, pop, tic, touche, carillon, caisse, riser, etincelle, glitch, allumage, lire, ecrire, lp, hp, t_, SR

ICI = os.path.dirname(os.path.abspath(__file__))
rng2 = np.random.default_rng(23)


def conga(f=210, g=1.0):
    t = t_(.22); fr = f * (1 + .5 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 22) * g * .45


def shaker(g=1.0):
    d = .07; n = rng2.standard_normal(int(d * SR))
    return hp(n, 5000) * np.sin(np.pi * np.clip(t_(d) / d, 0, 1)) ** 2 * g * .22


def logdrum(f, d=.5, g=1.0):
    """basse percussive glissée (couleur afro-house / amapiano)"""
    t = t_(d); fr = f * (1 + .9 * np.exp(-t * 18))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    return np.tanh(s * 2.2) * np.exp(-t * 5) * g * .42


def marimba(f, d=.45, g=1.0):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)) * np.exp(-t * 9) * g * .2


def declic(g=1.0):
    """déclencheur d'appareil photo"""
    t = t_(.09); n = hp(rng2.standard_normal(len(t)), 1500)
    e = np.exp(-t * 90) + .6 * np.exp(-np.maximum(t - .045, 0) * 120) * (t > .045)
    return n * e * g * .35


class Piste:
    def __init__(s, duree):
        s.N = int(SR * duree); s.L = np.zeros(s.N); s.R = np.zeros(s.N)

    def add(s, sig, t, pan=0.0, g=1.0):
        i = int(t * SR)
        if i < 0 or i >= s.N: return
        x = sig[:s.N - i] * g
        s.L[i:i + len(x)] += x * min(1, 1 - pan); s.R[i:i + len(x)] += x * min(1, 1 + pan)


def musique(duree, bpm, sections, style='energie', courbe=None):
    """sections : [(t_debut, nom)], noms : 'calme','montee','groove','plein','coupe','fin'"""
    M = Piste(duree)
    T = 60 / bpm
    acc = [55.0, 43.65, 65.41, 49.0]                  # la1 fa1 do2 sol1 (Am F C G)
    gam = [220.0, 261.6, 293.7, 329.6, 392.0, 440.0, 523.3, 587.3]
    def sec(t):
        n = sections[0][1]
        for t0, nm in sections:
            if t >= t0 - 1e-6: n = nm
        return n
    t = 0.0; mes = 0
    while t < duree - .05:
        f = acc[mes % 4]
        ph = sec(t)
        if ph not in ('coupe',):
            M.add(pad(f * 4, 4 * T + .6), t, 0, .8 if ph in ('calme', 'montee') else .55)
        for b in range(4):
            for dc in range(4):                        # doubles croches
                tb = t + b * T + dc * T / 4
                if tb >= duree - .05: break
                ph = sec(tb); k = b * 4 + dc
                if ph == 'coupe': continue
                if ph == 'calme':
                    if dc == 0 and b in (0, 2): M.add(logdrum(f * 2, .6, .5), tb)
                    if dc == 2: M.add(shaker(.6), tb, .3)
                    if style == 'doux' and dc == 0: M.add(marimba(gam[(b * 3 + mes) % 8], .6, .9), tb, -.2)
                    continue
                if ph == 'montee':
                    if dc == 0: M.add(kick(.7), tb)
                    M.add(shaker(.5 + .1 * dc), tb, (-.3, .3)[dc % 2])
                    if dc == 0: M.add(pluck(gam[(b * 2) % 8] * 2, .3, .8), tb, .3)
                    continue
                plein = ph in ('plein', 'fin')
                # batterie
                if dc == 0: M.add(kick(1.0 if style == 'energie' else .75), tb)
                if dc == 0 and b in (1, 3): M.add(clap(.8 if style == 'energie' else .5), tb, .06)
                if dc == 2: M.add(hat(.7 if style == 'energie' else .45), tb, .2)
                M.add(shaker(.55 if dc % 2 else .35), tb, (-.35, .35)[dc % 2])
                # congas : motif afro
                if style == 'energie' and k in (3, 6, 10, 11, 14):
                    M.add(conga(250 if k in (6, 14) else 190, .9), tb, (-.4, .4)[k % 2])
                # log drum / basse
                if k in (0, 6, 10) and style == 'energie': M.add(logdrum(f * (2 if k else 1.5), .45), tb)
                if style == 'doux' and k in (0, 8): M.add(basse(f, T * 1.8, .8), tb)
                # mélodie
                if style == 'energie' and k in (2, 7, 12) and plein:
                    M.add(pluck(gam[(k + mes * 3) % 8] * 2, .3, .75), tb, .35)
                if style == 'doux' and dc == 0:
                    M.add(marimba(gam[(b * 2 + mes * 3) % 8] * (2 if plein else 1), .5, .9), tb, (-.25, .25)[b % 2])
                if style == 'doux' and plein and dc == 2 and b % 2:
                    M.add(marimba(gam[(b + mes) % 8] * 2, .35, .6), tb, .3)
        t += 4 * T; mes += 1
    if courbe:
        tt = np.arange(M.N) / SR; c = np.interp(tt, [a for a, _ in courbe], [b for _, b in courbe])
        M.L *= c; M.R *= c
    # coupes franches (silence) : fondu court pour éviter les clics
    for t0, nm in sections:
        if nm == 'coupe':
            i = int(t0 * SR); q = int(.03 * SR)
            M.L[max(0, i - q):i] *= np.linspace(1, 0, min(q, i)); M.R[max(0, i - q):i] *= np.linspace(1, 0, min(q, i))
    return M


def voix(duree, morceaux):
    """morceaux : [(src, a, b, t)] — voix séparée par demucs (sep/htdemucs/<src>/vocals.wav)"""
    V = np.zeros(int(SR * duree))
    for src, a, b, t in morceaux:
        x = lire(os.path.join(ICI, 'sep', 'htdemucs', src, 'vocals.wav'))
        seg = x[int(a * SR):int(b * SR)].copy()
        q = int(.02 * SR); seg[:q] *= np.linspace(0, 1, q); seg[-q:] *= np.linspace(1, 0, q)
        i = int(t * SR); seg = seg[:len(V) - i]
        V[i:i + len(seg)] += seg
    V = hp(V, 80)
    pk = np.abs(V).max() + 1e-9
    V = np.tanh(V / pk * 2.2) * .7                     # compression douce
    return V


def mixer(sortie, duree, M, B, V=None, g_mus=.5, g_bru=.6):
    N = int(SR * duree)
    if V is None: V = np.zeros(N)
    env = lp(np.abs(V), 6.0); env = env / (env.max() + 1e-9)
    duck = lp(1.0 - .78 * np.clip(env * 3.0, 0, 1), 8.0)
    L = V + M.L * g_mus * duck + B.L * g_bru
    R = V + M.R * g_mus * duck + B.R * g_bru
    q = int(.25 * SR); L[-q:] *= np.linspace(1, 0, q); R[-q:] *= np.linspace(1, 0, q)
    c = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    L = np.tanh(L / c * 1.2) * .9; R = np.tanh(R / c * 1.2) * .9
    brut = sortie.replace('.wav', '_brut.wav')
    ecrire(brut, L, R)
    # -14 LUFS (2 passes loudnorm)
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', brut, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    import json
    m = json.loads(o[o.rfind('{'):o.rfind('}') + 1])
    f = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', brut, '-af', f, '-ar', '44100', sortie], check=True)
    if V.any():
        db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
        parle = env > .08
        print(f"voix {db(V[parle]):.1f} dB | musique sous la voix {db((M.L * g_mus * duck)[parle]):.1f} dB")
    print('son :', sortie)
