"""Bande son du podcast : voix de Mariuse (coupes), voix de Claude, musique synthétisée
(deux ambiances : caméra / écran Claude), bruitages calés sur evenements.json.  Sortie : son.wav"""
import numpy as np, wave, os, json, subprocess
os.chdir(os.path.dirname(os.path.abspath(__file__)))
V=os.environ.get('V','')
SR=44100; rng=np.random.default_rng(7)
TL=json.load(open(f'timeline{V}.json')); EV=json.load(open(f'evenements{V}.json'))
DUREE=TL['duree']+0.6; N=int(SR*DUREE)
def lire(p,filtre=None):
    a=['ffmpeg','-v','error','-i',p]+(['-af',filtre] if filtre else [])+['-ac','1','-ar',str(SR),'-f','s16le','-']
    return np.frombuffer(subprocess.run(a,capture_output=True,check=True).stdout,'<i2').astype(np.float64)/32768
def ecrire(p,L,R):
    x=(np.stack([L,R],1).clip(-1,1)*32767).astype('<i2')
    with wave.open(p,'wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(x.tobytes())
t_=lambda d: np.arange(int(d*SR))/SR
def lp(x,fc,n=1):
    a=np.exp(-2*np.pi*fc/SR)
    for _ in range(n):
        y=np.empty_like(x); p=0.0
        for i,v in enumerate(x): p=(1-a)*v+a*p; y[i]=p
        x=y
    return x
def hp(x,fc): return x-lp(x,fc)
def kick(g=1.0):
    t=t_(.42); f=48+120*np.exp(-t*30)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8.5)+rng.standard_normal(len(t))*np.exp(-t*160)*.25)*g
def hat(g=1.0,d=.055):
    n=np.diff(rng.standard_normal(int(d*SR)),prepend=0)
    return hp(n,6000)*np.exp(-t_(d)*78)*g*.5
def clap(g=1.0):
    d=.26; t=t_(d); n=np.diff(rng.standard_normal(int(d*SR)),prepend=0)
    e=sum(np.exp(-np.maximum(t-o,0)*55)*(t>=o) for o in (0,.013,.026))*np.exp(-t*12)
    return hp(n,1200)*e*g*.4
def basse(f,d,g=1.0):
    t=t_(d); s=np.sin(2*np.pi*f*t)+.35*np.sin(4*np.pi*f*t)+.12*np.sin(6*np.pi*f*t)
    e=np.minimum(t/.008,1)*np.exp(-t*(2.2/max(d,.05)))
    return np.tanh(s*1.4)*e*g*.42
def pluck(f,d=.34,g=1.0):
    t=t_(d); s=sum(np.sin(2*np.pi*f*k*t)/k for k in (1,2,3,4,5))
    return s*np.exp(-t*8.5)*g*.14
def pad(f,d,g=1.0):
    t=t_(d); s=sum(np.sin(2*np.pi*f*r*t+p) for r,p in ((1,0),(1.5,1.1),(2,2.3),(3,.7)))
    e=np.minimum(t/.5,1)*np.minimum((d-t)/.8,1).clip(0)
    return lp(s,1400)*e*g*.07
def whoosh(d=.5,montant=True,g=1.0):
    t=t_(d); n=rng.standard_normal(len(t))
    f=np.linspace(260,5200,len(t)) if montant else np.linspace(5200,260,len(t))
    s=hp(n,400)*.45+np.sin(2*np.pi*np.cumsum(f)/SR)*.18
    return s*(np.sin(np.pi*np.clip(t/d,0,1))**1.6)*g*.55
def impact(g=1.0):
    t=t_(.9); f=120*np.exp(-t*9)+38
    corps=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5.5)
    air=hp(rng.standard_normal(len(t)),900)*np.exp(-t*20)*.3
    return (corps+air)*g*.85
def pop(f=640,g=1.0,d=.14):
    t=t_(d); fr=f*(1+1.7*np.exp(-t*55))
    return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*34)*g*.5
def tic(g=1.0):
    t=t_(.05); return (np.sin(2*np.pi*2400*t)+hp(rng.standard_normal(len(t)),3000)*.6)*np.exp(-t*110)*g*.3
def touche(g=1.0):
    t=t_(.09); return (np.sin(2*np.pi*1100*t)*.6+hp(rng.standard_normal(len(t)),2500)*.5)*np.exp(-t*60)*g*.35
def carillon(f=1320,d=1.7,g=1.0):
    t=t_(d); s=sum(a*np.sin(2*np.pi*f*r*t) for a,r in ((1,1),(.55,2.76),(.33,5.4),(.2,8.9)))
    return s*np.exp(-t*3.1)*g*.17
def caisse(g=1.0):
    s=np.zeros(int(1.5*SR))
    for i,(f,o) in enumerate([(1568,0),(2093,.06),(2637,.12)]):
        c=carillon(f,1.3,1.0); k=int(o*SR); s[k:k+len(c)]+=c*(1-i*.22)
    return s*g*.9
def riser(d=1.2,g=1.0):
    t=t_(d); n=rng.standard_normal(len(t)); f=np.linspace(180,5600,len(t))
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*.35+hp(n,800)*.3)*(t/d)**2.2*g*.5
def etincelle(g=1.0):
    d=.6; t=t_(d)
    return sum(np.sin(2*np.pi*f*t)*np.exp(-t*(7+i*2.5)) for i,f in enumerate((2093,2637,3136,4186)))*g*.09

def glitch(d=.2,g=1.0):
    t=t_(d); n=len(t); s=np.sign(np.sin(2*np.pi*np.repeat(rng.uniform(180,1400,int(d*40)+1),int(SR/40))[:n]*t))
    gate=(np.sin(2*np.pi*32*t)>0).astype(float)
    bruit=np.round(rng.standard_normal(n)*3)/3
    return (s*.5+bruit*.35)*gate*np.exp(-t*6)*g*.22
def allumage(d=.4,g=1.0):
    t=t_(d); f=np.geomspace(180,1500,len(t))
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/d)**1.5*g*.2

# ---------- pistes ----------
VOIX=np.zeros(N); MUS_L=np.zeros(N); MUS_R=np.zeros(N); BR_L=np.zeros(N); BR_R=np.zeros(N)
def add(bl,br,sig,t,pan=0.0,g=1.0):
    i=int(t*SR)
    if i<0 or i>=N: return
    s=sig[:N-i]*g; bl[i:i+len(s)]+=s*min(1,1-pan); br[i:i+len(s)]+=s*min(1,1+pan)
mus=lambda sig,t,pan=0,g=1: add(MUS_L,MUS_R,sig,t,pan,g)
bru=lambda sig,t,pan=0,g=1: add(BR_L,BR_R,sig,t,pan,g)

# ---------- voix ----------
lui=lire('source.wav','highpass=f=90,afftdn=nf=-28,equalizer=f=3200:t=q:w=1.2:g=3,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4dB')
def rms_parole(x): a=np.abs(x); return np.sqrt((x[a>np.percentile(a,60)]**2).mean())
F=int(.008*SR); cible=None
for s in TL['segs']:
    if s['type']=='lui':
        for c in s['clips']:
            a,b=c['src']; m=lui[int(a*SR):int(b*SR)].copy(); m[:F]*=np.linspace(0,1,F); m[-F:]*=np.linspace(1,0,F)
            i=int(c['t0']*SR); VOIX[i:i+len(m)]+=m[:N-i]
r_lui=rms_parole(VOIX[VOIX!=0])
CL=np.zeros(N)
for s in TL['segs']:
    if s['type']=='claude':
        v=lire(s['voix'],'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=6:release=100:makeup=2dB')
        i=int(s['tv']*SR); CL[i:i+len(v)]+=v[:N-i]
CL*=r_lui/rms_parole(CL[CL!=0])          # même niveau perçu pour les deux voix
VOIX+=CL

# ---------- musique : 100 BPM, deux ambiances ----------
NOIRE=.6; ACC=[55.0,43.65,65.41,49.0]      # la - fa - do - sol
ARP={55.0:[220,261.6,329.6,440],43.65:[174.6,220,261.6,349.2],65.41:[261.6,329.6,392,523.3],49.0:[196,246.9,293.7,392]}
type_a=lambda t: next((s for s in EV if t<s['t1']),EV[-1])
t=0.0; mes=0
while t<DUREE-.3:
    f=ACC[mes%4]; s=type_a(t+.01); cla=s['type']=='claude'; fin=s['type']=='lui' and s['q']==6
    mus(pad(f*4,4*NOIRE+.4),t,0,1.2 if cla else .55)
    for b in range(4):
        tb=t+b*NOIRE
        if tb>=DUREE-.2: break
        if cla:
            mus(kick(.55),tb); mus(basse(f,NOIRE*.8,.55),tb)
            for k in range(4):
                mus(pluck(ARP[f][(b*4+k)%4]*2,.22,.55 if k%2 else .8),tb+k*NOIRE/4,(-.4,.4)[k%2])
            mus(hat(.25,.03),tb+NOIRE/2,.3)
        else:
            mus(kick(1.0),tb) if b in (0,2) else None
            if b==2: mus(kick(.6),tb+NOIRE*.75)
            if b in (1,3): mus(clap(.85),tb,.06)
            mus(hat(.55),tb+NOIRE/2,.2); mus(hat(.3),tb+NOIRE/4,-.2); mus(hat(.3),tb+3*NOIRE/4,-.1)
            mus(basse(f,NOIRE*.45),tb); mus(basse(f*2,NOIRE*.3,.45),tb+NOIRE*.5)
            mus(pluck(ARP[f][b%4],.3,.6),tb+NOIRE/2,.35)
            if fin: mus(pluck(ARP[f][(b+2)%4]*2,.25,.5),tb+NOIRE/4,-.35)
    t+=4*NOIRE; mes+=1

# ---------- bruitages ----------
for k,s in enumerate(EV):
    B=s['t0']
    if B>0:
        bru(glitch(.22,1.0),B-.12,(-.2,.2)[k%2]); bru(whoosh(.36,s['type']=='claude',.9),B-.22,(.3,-.3)[k%2])
        bru(impact(.55 if s['type']=='lui' else .75),B)
    if s['type']=='claude':
        if not s['accroche']: bru(allumage(.42,1.0),B+.02); bru(etincelle(.9),s['tv']-.05,.15)
        for j,b in enumerate(s['beats']):
            bru(whoosh(.22,True,.45),b['t']-.12,(-.25,.25)[j%2]); bru(pop(520+60*(j%4),.55,.12),b['t'],(.2,-.2)[j%2])
            if b['n']:
                d=b['n']/b['vit']
                for c in np.arange(0,d,2/b['vit']): bru(touche(.22),b['t']+c,.35)
    else:
        for p in s['pops']:
            if p['cl']=='rouge': bru(pop(880,.8),p['t']); bru(carillon(1568,1.2,.7),p['t']+.05,.1)
            elif p['ic']=='heart': bru(pop(980,.8),p['t']); bru(pop(1300,.6),p['t']+.08,.2)
            elif p['ic']=='share': bru(whoosh(.3,True,.7),p['t']-.05,.3); bru(pop(760,.6),p['t']+.1)
            else: bru(pop(640,.8,.14),p['t'],.1); bru(tic(.5),p['t']+.02,-.1)
mus(riser(.9,.7),EV[0]['t1']-.9,0,.7)                    # fin de l'accroche
bru(impact(1.0),0.0); bru(etincelle(1.0),0.02)            # première image : ça démarre fort
bru(impact(.9),TL['duree']-.05); bru(caisse(.7),TL['duree']-.02)

# ---------- mixage : la musique s'efface sous les voix ----------
blk=int(SR*.01); nb=N//blk+1
e=np.sqrt((np.pad(VOIX,(0,nb*blk-N))**2).reshape(nb,blk).mean(1)); e=e/(np.percentile(e,95)+1e-9)
sm=np.zeros(nb); p=0
for i,v in enumerate(e): p=v if v>p else p*.93+v*.07; sm[i]=p      # attaque immédiate, retombée ~150 ms
duck=1-.72*np.clip(sm*1.8,0,1); duck=np.interp(np.arange(N)/blk,np.arange(nb),duck)
G_MUS,G_BRU=.42,.55
L=VOIX+MUS_L*G_MUS*duck+BR_L*G_BRU; R=VOIX+MUS_R*G_MUS*duck+BR_R*G_BRU
pk=max(np.abs(L).max(),np.abs(R).max()); L/=pk/.89; R/=pk/.89
ecrire(f'son{V}.wav',L,R)
db=lambda x: 20*np.log10(np.sqrt((x**2).mean())+1e-12)
parle=sm>.3; mm=(MUS_L*G_MUS*duck)
vi=np.repeat(parle,blk)[:N]
print(f'voix {db(VOIX[vi]):.1f} dB | musique sous la voix {db(mm[vi]):.1f} dB | écart {db(VOIX[vi])-db(mm[vi]):.1f} dB | bruitages {db(BR_L*G_BRU):.1f} dB')
