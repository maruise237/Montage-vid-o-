"""Découpe les répliques TTS sur les vrais silences (énergie), pas sur les horodatages whisper."""
import soundfile as sf, numpy as np, json
CL = {  # nom: (fichier, début approx, fin approx)
 'N1':('narr',6.52,10.04),'N2':('narr',10.92,14.04),'N3':('narr',14.78,16.94),'N4':('narr',18.2,20.64),
 'N5':('narr',21.32,24.28),'N6':('narr',24.78,25.6),'N7':('narr',26.18,30.0),'N8':('narr',30.26,31.9),
 'N9':('narr',32.6,35.38),'N10':('narr',35.64,36.2),
 'P1':('paul',10.56,11.72),'Pnon':('paul',13.54,13.88),'P2':('paul',15.5,16.08),'P3':('paul',17.8,18.26),
 'P4':('paul',19.9,20.4),'P5':('paul',21.84,22.44),'P6':('paul',23.9,24.78),
 'PL1':('plombier',8.42,10.72),'PL2':('plombier',11.58,14.1),'E1':('electricien',6.26,8.58),
 'C1':('peinture',8.3,11.12),'RIZ':('peinture',11.76,13.34),'TC':('cliente3',7.14,8.54),
}
def affiner(y, sr, a, b, seuil=-40, tenue=0.06):
    h = int(0.01*sr); e = np.array([20*np.log10(np.sqrt((y[i:i+h]**2).mean())+1e-9) for i in range(0, len(y)-h, h)])
    n = int(tenue/0.01); i = int(a/0.01)
    while i > 0 and not all(e[max(0,i-n):i] < seuil): i -= 1
    j = int(b/0.01)
    while j < len(e)-n and not all(e[j:j+n] < seuil): j += 1
    return max(0, i*0.01-0.02), min(len(y)/sr, j*0.01+0.03)
out = {}
for k,(f,a,b) in CL.items():
    y, sr = sf.read(f'voix/{f}.wav'); a2, b2 = affiner(y, sr, a, b)
    c = y[int(a2*sr):int(b2*sr)].copy(); r = int(0.008*sr); c[:r] *= np.linspace(0,1,r); c[-r:] *= np.linspace(1,0,r)
    sf.write(f'clips/{k}.wav', c, sr); out[k] = round(len(c)/sr, 3)
    print(k, f, round(a2,2), round(b2,2), out[k])
json.dump(out, open('clips/durees.json','w'))
