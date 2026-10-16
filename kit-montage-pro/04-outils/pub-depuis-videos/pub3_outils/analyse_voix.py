import librosa,numpy as np,sys
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
for f in sys.argv[1:]:
    y,sr=librosa.load(f,sr=16000)
    segs=list(m.transcribe(y,language='fr',word_timestamps=True)[0]); words=[w for s in segs for w in s.words]
    dur=(words[-1].end-words[0].start) if words else 0
    f0=librosa.pyin(y,fmin=70,fmax=400,sr=sr)[0]; f0=f0[~np.isnan(f0)]
    rms=librosa.feature.rms(y=y)[0]; rms=rms[rms>rms.max()*.1]
    print(f"{f.split('/')[-1]:28s} {len(y)/sr:4.1f}s {len(words)/max(dur,.1):.1f} mots/s | écart F0 {np.std(12*np.log2(f0/np.median(f0))):.1f} dt | dyn {20*np.log10(np.percentile(rms,95)/np.percentile(rms,20)):.1f}dB | {' '.join(s.text.strip() for s in segs)}")
