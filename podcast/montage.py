"""Construit la timeline du podcast : coupes de la vidéo source, réponses de Claude,
voix traitées, images de la caméra.  Sortie : timeline.json, voix_claude/*.wav, lui/*, pip/*"""
import json, os, subprocess, wave, numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SR=44100; FPS=30; TEMPO=1.07          # la voix de Claude est accélérée de 7 % (hauteur conservée)
def sh(*a): subprocess.run(a,check=True)
def lire(p):
    d=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(SR),'-f','s16le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(d,'<i2').astype(np.float64)/32768
def ecrire(p,x):
    with wave.open(p,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x.clip(-1,1)*32767).astype('<i2').tobytes())

# ---------- 1. voix de Claude : pauses resserrées puis tempo ----------
os.makedirs('voix_claude',exist_ok=True)
def preparer(k, garde=(None,None), sauter=()):
    x=lire(f'voix/{k}.mp3'); mots=json.load(open(f'voix/{k}.json'))
    mots=[m for i,m in enumerate(mots) if not any(a<=i<b for a,b in sauter)]
    if garde[0] is not None: mots=mots[garde[0]:garde[1]]
    morceaux=[]; nm=[]; pos=0.0
    deb=max(0,mots[0][1]-.04)
    for i,(m,a,b) in enumerate(mots):
        fin=b+.12 if i==len(mots)-1 else None
        if i<len(mots)-1:
            g=mots[i+1][1]-b
            fin=b+min(g/2,.13) if g>.30 else mots[i+1][1]
        s=x[int(deb*SR):int(fin*SR)]
        nm.append([m,pos+(a-deb),pos+(b-deb)])
        pos+=len(s)/SR; morceaux.append(s)
        if i<len(mots)-1:
            g=mots[i+1][1]-b; deb=mots[i+1][1]-min(g/2,.13) if g>.30 else mots[i+1][1]
    # fondus de 6 ms à chaque raccord
    f=int(.006*SR)
    for s in morceaux:
        if len(s)>2*f: s[:f]*=np.linspace(0,1,f); s[-f:]*=np.linspace(1,0,f)
    y=np.concatenate(morceaux)
    tmp=f'voix_claude/_{k}.wav'; ecrire(tmp,y)
    nom=(f'{k}' if garde[0] is None else f'{k}_accroche')+('_court' if sauter else '')
    sh('ffmpeg','-v','error','-y','-i',tmp,'-af',f'atempo={TEMPO}','-ar',str(SR),f'voix_claude/{nom}.wav'); os.remove(tmp)
    nm=[[m,round(a/TEMPO,3),round(b/TEMPO,3)] for m,a,b in nm]
    return nom, nm, round(pos/TEMPO,3)

def enveloppe(p):
    # 3 bandes (grave / médium / aigu) à 30 i/s, normalisées 0..1 : pilotent le logo
    x=lire(p); h=SR//FPS; n=len(x)//h+1; x=np.pad(x,(0,n*h-len(x)))
    fr=np.abs(np.fft.rfft(x.reshape(n,h)*np.hanning(h),axis=1)); f=np.fft.rfftfreq(h,1/SR)
    out=[]
    for lo,hi in ((80,400),(400,2000),(2000,8000)):
        e=np.sqrt((fr[:,(f>=lo)&(f<hi)]**2).mean(1)); e=e/(np.percentile(e,97)+1e-9)
        out.append(np.clip(e,0,1.2))
    return [[round(float(v),3) for v in col] for col in zip(*out)]

# ---------- 2. plan de montage ----------
# (début, fin) dans la source ; chaque sous-plan = une coupe franche (jump cut)
PLAN=[
 ('claude','r1',(4,11)),                         # accroche : « Ce montage, c'est moi qui l'ai fait. »
 ('lui',[(0.00,3.40),(3.50,6.55),(6.78,10.80)],1),
 ('claude','r1',(10.62,13.00)),
 ('lui',[(13.05,13.86),(14.44,15.30),(15.74,17.92),(18.60,20.88)],2),
 ('claude','r2',(20.88,22.90)),
 ('lui',[(22.90,25.50),(34.30,37.05)],3),
 ('claude','r3',(37.05,39.15)),
 ('lui',[(39.18,40.27),(40.86,42.35),(47.02,53.54)],4),
 ('claude','r4',(43.72,47.00)),
 ('lui',[(57.55,62.30)],5),
 ('claude','r5',(62.30,64.22)),
 ('lui',[(64.25,67.42),(67.80,71.62),(71.98,73.40)],6),
]
V=os.environ.get('V','')            # '' = version complète, '_court' = extrait
if V=='_court':
    # 1 min 30 : sans la question 3, intro et fin resserrées, une phrase en moins dans la réponse 4
    PLAN=[PLAN[0],('lui',[(0.00,3.40),(6.78,10.80)],1),('claude','r1',(10.62,13.00),[(22,26)]),PLAN[3],PLAN[4],
          ('lui',[(47.02,53.54)],4),('claude','r4',(43.72,47.00),[(16,27)]),
          ('lui',[(57.96,62.30)],5),PLAN[10],('lui',[(68.02,71.62),(71.98,73.40)],6)]
AVANT=.42; APRES=.30          # respiration avant/après chaque réponse (logo qui se forme)
src=json.load(open('mots_source.json'))
for w in src:
    w[0]=w[0].replace('CamTek','KAMTECH')
T=0.0; segs=[]; mots=[]; nclip=50 if V else 0
os.makedirs('lui',exist_ok=True); os.makedirs('pip',exist_ok=True)
for p in PLAN:
    if p[0]=='claude':
        k=p[1]; acc=isinstance(p[2],tuple) and p[2][0]==4 and p[2][1]==11
        if acc: nom,nm,d=preparer(k,(4,11)); avant,apres=.12,.22
        else: nom,nm,d=preparer(k,sauter=p[3] if len(p)>3 else ()); avant,apres=AVANT,APRES
        t0=T; tv=T+avant; T=tv+d+apres
        seg={'type':'claude','cle':k,'accroche':acc,'t0':round(t0,3),'tv':round(tv,3),'t1':round(T,3),'voix':f'voix_claude/{nom}.wav'}
        seg['env']=enveloppe(f'voix_claude/{nom}.wav')
        segs.append(seg)
        mots+= [[m,round(tv+a,3),round(tv+b,3),'c',len(segs)-1] for m,a,b in nm]
    else:
        q=p[2]; clips=[]
        for (a,b) in p[1]:
            clips.append({'src':[a,b],'t0':round(T,3),'t1':round(T+b-a,3),'n':nclip})
            for m,wa,wb in src:
                if a<=(wa+wb)/2<b: mots.append([m,round(T+wa-a,3),round(T+wb-a,3),'l',len(segs)])
            T+=b-a; nclip+=1
        segs.append({'type':'lui','q':q,'t0':clips[0]['t0'],'t1':round(T,3),'clips':clips})
DUREE=round(T,3)
json.dump({'version':V,'duree':DUREE,'fps':FPS,'segs':segs,'mots':mots},open(f'timeline{V}.json','w'),ensure_ascii=False,indent=1)
print('durée',DUREE,'s |',sum(1 for s in segs if s['type']=='lui'),'blocs lui,',sum(1 for s in segs if s['type']=='claude'),'réponses')
for s in segs: print(f"  {s['type']:6} {s['t0']:6.2f} → {s['t1']:6.2f}  ({s['t1']-s['t0']:.2f}s)", s.get('cle',s.get('q')))
