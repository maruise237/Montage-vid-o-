"""Bande son « humaine » des pubs NGUELEK PRINT (v2, après retour de Mariuse : v1 = bruitages synthétisés = pattern IA).

Principes :
  - musique RÉELLE (Mixkit, licence « Stock Music Free » : pubs en ligne et réseaux autorisés), montée sur ses temps,
    sa vraie fin raccordée sur l'écran final (pas de fondu générique) ;
  - son DIÉGÉTIQUE d'abord : le vrai bruit des machines tiré des vidéos sources (CNC, brodeuse, laser, UV) ;
  - bruitages ENREGISTRÉS (Mixkit SFX), choisis pour leur sens (papier, frappe, imprimante, interrupteur, déclencheur,
    clés), rares, jamais deux fois le même échantillon d'affilée, gain et hauteur légèrement variés, léger décalage ;
  - voix coupée sur ses vrais silences (énergie mesurée), jamais sur les horodatages de la transcription."""
import numpy as np, os, sys, subprocess, json, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outils'))
from bruitages import lire, ecrire, lp, hp, SR

ICI = os.path.dirname(os.path.abspath(__file__))
SONS = os.path.join(ICI, 'sons')
_cache = {}


def charger(p, filtre=None):
    k = (p, filtre)
    if k not in _cache:
        a = ['ffmpeg', '-v', 'error', '-i', p] + (['-af', filtre] if filtre else []) + ['-ac', '2', '-ar', str(SR), '-f', 's16le', '-']
        x = np.frombuffer(subprocess.run(a, capture_output=True, check=True).stdout, '<i2').astype(np.float64) / 32768
        _cache[k] = x.reshape(-1, 2).T.copy()
    return _cache[k]


def energie_db(x, fen=.01):
    h = int(fen * SR); m = x.mean(0) if x.ndim == 2 else x
    return 20 * np.log10(np.sqrt(np.convolve(m ** 2, np.ones(h) / h, 'same')) + 1e-9)


def affiner(src, a, b, seuil=-38):
    """Recale (a, b) sur les silences réels de la voix séparée : on ne coupe jamais dans un mot."""
    e = energie_db(charger(os.path.join(ICI, 'sep', 'htdemucs', src, 'vocals.wav')))
    g = lambda t: e[min(len(e) - 1, max(0, int(t * SR)))]
    calme = lambda t0, t1: max(g(t0 + k * .01) for k in range(int((t1 - t0) / .01) + 1)) < seuil
    a2 = None
    for k in range(0, 55):                      # en arrière jusqu'à 0,55 s
        t = a + .03 - k * .01
        if calme(t - .05, t): a2 = t - .02; break
    if a2 is None:
        ts = np.arange(a - .4, a + .02, .01); a2 = float(ts[np.argmin([g(t) for t in ts])])
    b2 = None
    for k in range(0, 70):                      # en avant jusqu'à 0,6 s
        t = b - .1 + k * .01
        if calme(t, t + .06): b2 = t + .03; break
    if b2 is None:
        ts = np.arange(b - .1, b + .6, .01); b2 = float(ts[np.argmin([g(t) for t in ts])])
    return round(max(0, a2), 3), round(b2, 3)


class Bus:
    def __init__(s, duree):
        s.N = int(SR * duree); s.x = np.zeros((2, s.N))

    def poser(s, sig, t, g=1.0, pan=0.0):
        if sig.ndim == 1: sig = np.vstack([sig, sig])
        i = int(round(t * SR))
        if i < 0: sig = sig[:, -i:]; i = 0
        if i >= s.N: return
        n = min(sig.shape[1], s.N - i)
        s.x[0, i:i + n] += sig[0, :n] * g * min(1, 1 - pan); s.x[1, i:i + n] += sig[1, :n] * g * min(1, 1 + pan)


def fondu(sig, a=.015, b=.04):
    sig = sig.copy(); n = sig.shape[-1]
    qa, qb = min(int(a * SR), n // 2), min(int(b * SR), n // 2)
    if qa: sig[..., :qa] *= np.linspace(0, 1, qa)
    if qb: sig[..., -qb:] *= np.linspace(1, 0, qb)
    return sig


def extrait(x, a, b):
    return x[:, int(a * SR):int(b * SR)]


# ------------------------------------------------------------------ musique
def grille(id_musique):
    """temps (beats) du morceau, mis en cache"""
    f = os.path.join(SONS, 'musique', f'{id_musique}.beats.json')
    if not os.path.exists(f):
        import librosa
        y, sr = librosa.load(os.path.join(SONS, 'musique', f'{id_musique}.mp3'), sr=22050)
        _, b = librosa.beat.beat_track(y=y, sr=sr, units='time')
        json.dump([round(float(v), 4) for v in b], open(f, 'w'))
    return json.load(open(f))


def musique_montee(id_musique, morceaux, duree, xfade=.06):
    """morceaux : [(src_debut, src_fin, t_timeline)] raccordés sur des temps ; fondu court entre morceaux."""
    m = charger(os.path.join(SONS, 'musique', f'{id_musique}.mp3'))
    B = Bus(duree)
    for i, (a, b, t) in enumerate(morceaux):
        seg = extrait(m, max(0, a - (xfade if i else 0)), b + xfade if b else m.shape[1] / SR)
        seg = fondu(seg, xfade if i else .005, xfade if i < len(morceaux) - 1 else .02)
        B.poser(seg, t - (xfade if i else 0))
    return B


# ------------------------------------------------------------------ bruitages enregistrés
_rng = random.Random(4)
_dernier = {}


def bruit(B, ids, t, g=1.0, pan=0.0, varier=True, d=None):
    """pose un bruitage Mixkit ; ids = liste d'échantillons possibles (jamais le même deux fois de suite)"""
    ids = ids if isinstance(ids, (list, tuple)) else [ids]
    cle = tuple(ids); choix = [i for i in ids if i != _dernier.get(cle)] or ids
    i = _rng.choice(choix); _dernier[cle] = i
    x = charger(os.path.join(SONS, 'bruit', f'{i}.mp3'))
    if d: x = x[:, :int(d * SR)]
    if varier:
        r = 1 + _rng.uniform(-.035, .035)                       # hauteur ± 3,5 %
        n = int(x.shape[1] / r); idx = np.linspace(0, x.shape[1] - 1, n)
        x = np.vstack([np.interp(idx, np.arange(x.shape[1]), c) for c in x])
        g *= 10 ** (_rng.uniform(-2, 1.5) / 20)                 # gain ± 2 dB
        t += _rng.uniform(-.012, .018)                          # pas calé à l'image près
    B.poser(fondu(x, .002, .03), t, g, pan)


# ------------------------------------------------------------------ son direct des sources
def ambiance(B, src, a, d, t, g=1.0, fade=.04):
    """vrai son de la vidéo source (machine, atelier), synchrone avec l'image"""
    x = charger(os.path.join(ICI, 'sources', f'{src}.mp4'), 'highpass=f=60')
    B.poser(fondu(extrait(x, a, a + d), fade, fade), t, g)


# ------------------------------------------------------------------ voix + mixage
def voix(duree, morceaux):
    """morceaux : [(src, a, b, t)] avec (a, b) DÉJÀ affinés. Son d'origine de la caméra (vrai ambiant de pièce) :
    demucs sert seulement à mesurer les silences."""
    V = Bus(duree)
    for src, a, b, t in morceaux:
        x = charger(os.path.join(ICI, 'sources', f'{src}.mp4'), 'highpass=f=70')
        V.poser(fondu(extrait(x, a, b), .012, .05), t)
    v = V.x.mean(0); v = hp(v, 80)
    pk = np.abs(v).max() + 1e-9
    return np.tanh(v / pk * 2.0) * .7


def mixer(sortie, duree, M, A, B, V=None, g_mus=.5, g_amb=.6, g_bru=.5, duck_amb=True):
    N = int(SR * duree)
    v = V if V is not None else np.zeros(N)
    env = lp(np.abs(v), 6.0); env = env / (env.max() + 1e-9)
    duck = lp(1.0 - .75 * np.clip(env * 3.0, 0, 1), 8.0)
    # l'ambiance des machines baisse un peu la musique (comme un mixeur qui pousse le son direct)
    ea = lp(np.abs(A.x.mean(0)), 4.0); ea = ea / (ea.max() + 1e-9)
    duck_m = duck * (1 - .35 * np.clip(ea * 2.5, 0, 1)) if duck_amb else duck
    L = v + M.x[0] * g_mus * duck_m + A.x[0] * g_amb * duck + B.x[0] * g_bru
    R = v + M.x[1] * g_mus * duck_m + A.x[1] * g_amb * duck + B.x[1] * g_bru
    c = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    L = np.tanh(L / c * 1.15) * .9; R = np.tanh(R / c * 1.15) * .9
    brut = sortie.replace('.wav', '_brut.wav')
    ecrire(brut, L, R)
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', brut, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = json.loads(o[o.rfind('{'):o.rfind('}') + 1])
    f = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', brut, '-af', f, '-ar', '44100', sortie], check=True)
    if V is not None and V.any():
        db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
        parle = env > .08
        print(f"voix {db(v[parle]):.1f} dB | musique sous la voix {db((M.x[0] * g_mus * duck_m)[parle]):.1f} dB")
    print('son :', sortie)
