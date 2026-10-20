"""Découpe chaque phrase FR en morceaux et les pose sur les ancrages de la vidéo d'origine.
Sortie : voix/voix_fr.wav (mono 44,1 kHz) + voix/mots_fr.json [[mot, début, fin], ...]"""
import sys, json, subprocess, re, unicodedata
import numpy as np
sys.path.insert(0, '.')
from script_fr import PHRASES, FIN
SR = 44100
MAXT = 1.18          # accélération max d'un morceau
AVANCE = 0.30        # un morceau peut démarrer un peu avant son ancrage
def lire(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.float32).copy()
def tempo(x, t):
    if abs(t - 1) < 0.01: return x
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-af', f'atempo={t:.4f}', '-f', 'f32le', '-'], input=x.tobytes(), capture_output=True)
    return np.frombuffer(r.stdout, np.float32).copy()
def norm(w):
    w = unicodedata.normalize('NFD', w.lower()); w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9]", '', w)
out = np.zeros(int((FIN + 1) * SR), np.float32); mots = []; fin_prec = 0.0; rapport = []
for i, ph in enumerate(PHRASES):
    a = lire(f'voix/p{i}.mp3'); b = json.load(open(f'voix/p{i}.json'))
    # rattacher chaque mot TTS à un morceau (appariement séquentiel sur le texte normalisé)
    cible = []
    for k, (_, txt) in enumerate(ph):
        for w in txt.split():
            if norm(w): cible.append((norm(w), k, w))
    j = 0; idx = []; tokj = []          # idx[n] = morceau du mot TTS n
    buf = ''
    for w, s, e in b:
        nw = norm(w); idx.append(cible[min(j, len(cible)-1)][1]); tokj.append(min(j, len(cible)-1))
        buf += nw
        while j < len(cible) and buf.startswith(cible[j][0]):
            buf = buf[len(cible[j][0]):]; j += 1
        if j < len(cible) and buf and not cible[j][0].startswith(buf): buf = ''
    # bornes de coupe : milieu du silence entre le dernier mot d'un morceau et le 1er du suivant
    debuts = {}
    for n, k in enumerate(idx): debuts.setdefault(k, n)
    coupes = []
    for k in range(len(ph)):
        n = debuts[k]
        coupes.append(0.0 if n == 0 else (b[n-1][2] + b[n][1]) / 2)
    coupes.append(b[-1][2] + 0.08)
    suivant = PHRASES[i+1][0][0] if i + 1 < len(PHRASES) else FIN - 0.3
    # une seule vitesse par phrase (la voix reste naturelle), pauses ajoutées aux virgules si on est en avance
    slot = suivant - 0.15 - ph[0][0]
    T = min(max(1.0, (coupes[-1]) / slot), MAXT)
    for k, (anc, txt) in enumerate(ph):
        s0, s1 = coupes[k], coupes[k+1]
        m2 = tempo(a[int(s0*SR):int(s1*SR)], T)
        debut = max(anc - AVANCE, fin_prec) if k else max(anc, fin_prec)
        p = int(debut*SR); out[p:p+len(m2)] += m2[:len(out)-p]
        for n, (w, ws, we) in enumerate(b):
            if idx[n] == k:
                tj = tokj[n]; tx = cible[tj][2]
                if mots and mots[-1][5] == (i, tj): mots[-1][2] = round(debut + (we - s0)/T, 3); continue
                mots.append([tx, round(debut + (ws - s0)/T, 3), round(debut + (we - s0)/T, 3), i, k, (i, tj)])
        fin_prec = debut + len(m2)/SR
        rapport.append(f'{i}.{k} anc {anc:5.2f} -> {debut:5.2f} ({debut-anc:+.2f})  x{T:.2f}  fin {fin_prec:5.2f}  {txt}')
print('\n'.join(rapport))
import wave
pcm = (np.clip(out, -1, 1)*32767).astype(np.int16)
with wave.open('voix/voix_fr.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
json.dump([m[:5] for m in mots], open('voix/mots_fr.json', 'w'), ensure_ascii=False)
