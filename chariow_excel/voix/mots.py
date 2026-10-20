"""Horodatage des mots de chaque phrase (faster-whisper small) → voix/mots.json"""
import json, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
os.chdir(os.path.dirname(os.path.abspath(__file__)))
m = WhisperModel('small', device='cpu', compute_type='int8'); R = {}
for i in range(1, 13):
    seg, _ = m.transcribe(np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f'p{i}.wav','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32), language='fr', word_timestamps=True)
    mots = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in seg for w in s.words]
    R[str(i)] = {'debut': mots[0][1], 'fin': mots[-1][2], 'mots': mots}
    print(i, ' '.join(f'{w}@{a:.2f}' for w, a, b in mots))
json.dump(R, open('mots.json', 'w'), ensure_ascii=False)
