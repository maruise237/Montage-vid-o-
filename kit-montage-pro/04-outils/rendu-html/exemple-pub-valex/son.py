"""Bande son v2 : voix off fournie + musique synthétisée + un bruitage par action.
Sortie : v2/son.wav (stéréo 44,1 kHz) et les pistes séparées pour contrôle."""
import numpy as np, wave, os
SR=44100; DUREE=39.0; N=int(SR*DUREE)
rng=np.random.default_rng(11)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def lire(p):
    with wave.open(p,'rb') as w:
        n,sw,ch,sr=w.getnframes(),w.getsampwidth(),w.getnchannels(),w.getframerate()
        d=np.frombuffer(w.readframes(n),dtype='<i2').astype(np.float64)/32768
    if ch>1: d=d.reshape(-1,ch).mean(1)
    if sr!=SR: d=np.interp(np.arange(0,len(d),sr/SR), np.arange(len(d)), d)
    return d
def ecrire(p,L,R):
    x=(np.stack([L,R],1).clip(-1,1)*32767).astype('<i2')
    with wave.open(p,'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())

t_=lambda d: np.arange(int(d*SR))/SR
def lp(x,fc,n=1):
    a=np.exp(-2*np.pi*fc/SR)
    for _ in range(n):
        y=np.empty_like(x); p=0.0
        for i,v in enumerate(x): p=(1-a)*v+a*p; y[i]=p
        x=y
    return x
def hp(x,fc): return x-lp(x,fc)

# ---------- briques sonores (toutes originales) ----------
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

# ---------- pistes ----------
MUS_L=np.zeros(N); MUS_R=np.zeros(N); BR_L=np.zeros(N); BR_R=np.zeros(N)
def add(buf_l,buf_r,sig,t,pan=0.0,g=1.0):
    i=int(t*SR)
    if i<0 or i>=N: return
    s=sig[:N-i]*g
    buf_l[i:i+len(s)]+=s*min(1,1-pan); buf_r[i:i+len(s)]+=s*min(1,1+pan)
mus=lambda sig,t,pan=0,g=1: add(MUS_L,MUS_R,sig,t,pan,g)
bru=lambda sig,t,pan=0,g=1: add(BR_L,BR_R,sig,t,pan,g)

# ================= MUSIQUE : 120 BPM, une noire = 0,5 s =================
TEMPS=.5
ACCORDS=[55.00,55.00,43.65,49.00]        # la1 la1 fa1 sol1
ARP=[220.0,261.6,329.6,392.0,329.6,261.6,392.0,440.0]
mesure=0; t=0.0
while t<DUREE-.5:
    phase=('intro' if t<6.9 else 'groove' if t<17.0 else 'pont' if t<24.6 else
           'montee' if t<31.6 else 'final')
    f=ACCORDS[mesure%4]
    mus(pad(f*2,2.1),t,0,.9 if phase in('intro','pont') else .5)
    for b in range(4):
        tb=t+b*TEMPS
        if tb>=DUREE-.2: break
        if phase=='intro':
            mus(kick(.75),tb); mus(basse(f,TEMPS*.5,.7),tb)
            if b%2: mus(hat(.35),tb+TEMPS/2)
        elif phase in('groove','pont','final'):
            mus(kick(1.0),tb); mus(basse(f,TEMPS*.46),tb); mus(basse(f*2,TEMPS*.4,.55),tb+TEMPS/2)
            if b in(1,3): mus(clap(.85),tb,.08)
            mus(hat(.7),tb+TEMPS/2,.18); mus(hat(.4),tb+TEMPS/4,-.18)
            mus(pluck(ARP[(b*2)%8]*(2 if phase=='final' else 1)),tb+TEMPS/2,.35,.85)
            if phase=='final':
                mus(pluck(ARP[(b*2+1)%8]*2),tb+TEMPS/4,-.35,.6)
                mus(hat(.5,.04),tb+3*TEMPS/4,.3); mus(clap(.5),tb+TEMPS/2,-.1)
        else:   # montée
            mus(kick(.9),tb); mus(basse(f,TEMPS*.46),tb)
            mus(hat(.6),tb+TEMPS/2,.2); mus(hat(.5),tb+TEMPS/4,-.2); mus(hat(.45),tb+3*TEMPS/4,.1)
            mus(pluck(ARP[(b*2)%8]*2),tb,.3,.7)
    t+=4*TEMPS; mesure+=1
mus(riser(1.1,1.0),30.5,0,.8)          # montée avant l'appel à l'action
mus(riser(.9,.8),5.9,0,.6)             # montée avant la rafale de services
mus(impact(1.0),31.6,0,1.0)            # impact du drop final

# ================= BRUITAGES : un par action visible =================
COUPES=[6.92,12.80,17.10,19.90,24.62,29.56,31.60]
for i,c in enumerate(COUPES):
    bru(whoosh(.45,i%2==0,1.0),c-.18,(-.3 if i%2 else .3)); bru(impact(.75),c)
    bru(etincelle(1.0),c,.2)
bru(whoosh(.7,True,.75),0.0,0,.9)                       # les bandes démarrent
for tt,g in ((0.42,1.0),(1.66,1.15)):                   # mots qui claquent
    bru(impact(g),tt); bru(pop(420,.9,.18),tt,.15)
bru(whoosh(.4,False,.8),2.42,-.2)                       # sortie des bandes
bru(whoosh(.45,True,.7),2.80,.2)                        # entrée du portrait
bru(impact(.9),3.52); bru(impact(1.1),4.88); bru(carillon(1046,1.4,.75),4.92,.1)
bru(pop(760,.9),5.52,-.1)
for i,(tt,n) in enumerate(((6.92,3),(8.88,3),(9.60,1),(10.44,2),(11.10,2),(11.82,2))):
    for k in range(n): bru(pop(560+90*k,.95),tt+.06+k*.07,(-.25,.25)[k%2])
for k in range(9): bru(tic(.9),12.88+k*.05,(-.3,0,.3)[k%3])   # le mur se construit
bru(impact(1.0),13.42)
bru(whoosh(.5,True,.8),17.10,.25)
for k in range(5): bru(tic(.7),17.3+k*.22,-.2)                # horloge : la question
bru(pop(240,1.1,.3),18.50); bru(carillon(880,1.0,.5),18.52)
bru(pop(700,.9),19.46,.2)
bru(whoosh(.5,False,.9),19.88,-.3)                            # le coffret glisse
bru(caisse(1.0),20.66)                                        # prix de la formation
bru(whoosh(.5,True,.9),22.10,.3)                              # le guide glisse
bru(impact(.85),22.82); bru(caisse(.9),23.42)
for tt in (25.70,26.32,27.14):                                # trois validations
    bru(touche(1.1),tt); bru(carillon(1760,.7,.5),tt+.02,.15)
bru(impact(.95),28.14); bru(impact(1.0),29.56); bru(impact(.95),30.26)
bru(whoosh(.45,True,.7),30.30,.2)                             # le cercle devient carré
bru(carillon(1318,1.6,.8),30.68); bru(carillon(1976,1.6,.55),30.74,.2)
bru(pop(820,1.0),32.26,-.15)                                  # cadre du numéro
for tt in (33.12,34.52,35.02,35.80,36.66,37.58): bru(touche(1.25),tt,.0)
bru(carillon(1568,1.9,.9),32.80); bru(carillon(2093,1.9,.6),32.86,.2)   # bouton WhatsApp
bru(caisse(.8),37.58); bru(carillon(1318,2.6,.85),37.62,-.1)            # signature finale

# courbe d'énergie : la musique monte vers l'appel à l'action
_t=np.arange(N)/SR
_courbe=np.interp(_t,[0,6.9,17.0,24.6,29.5,31.6,39.0],[0.80,0.95,1.00,1.00,1.10,1.32,1.32])
MUS_L*=_courbe; MUS_R*=_courbe

# ================= VOIX + MIXAGE =================
voix=lire('voix.wav')
V=np.zeros(N); V[:min(N,len(voix))]=voix[:N]
V=hp(V,90)                                  # on dégage le bas inutile
V=np.tanh(V*2.6)*.72                        # compression douce, voix en avant

# enveloppe de la voix -> la musique s'efface dessous (sidechain)
env=np.abs(V)
env=lp(env,6.0); env=env/(env.max()+1e-9)
duck=1.0-0.62*np.clip(env*2.6,0,1)
duck=lp(duck,10.0)

G_MUS,G_BRU=0.52,0.62
L=V*1.0+MUS_L*G_MUS*duck+BR_L*G_BRU
R=V*1.0+MUS_R*G_MUS*duck+BR_R*G_BRU
# fondu de sortie court : la fin reste pleine pour la lecture en boucle
q=int(.35*SR); fin=np.ones(N); fin[-q:]=np.linspace(1,0,q)
deb=np.ones(N); deb[:int(.03*SR)]=np.linspace(0,1,int(.03*SR))
L*=fin*deb; R*=fin*deb
c=max(np.abs(L).max(),np.abs(R).max())
L=np.tanh(L/c*1.25)*.92; R=np.tanh(R/c*1.25)*.92
ecrire('son.wav',L,R)
ecrire('_voix_seule.wav',V,V); ecrire('_musique_seule.wav',MUS_L*G_MUS*duck,MUS_R*G_MUS*duck)

# contrôle : la voix doit dominer la musique
db=lambda x: 20*np.log10(np.sqrt((x**2).mean())+1e-12)
parle=env>0.06
print(f"voix {db(V[parle]):.1f} dB | musique sous la voix {db(MUS_L[parle]*G_MUS*duck[parle]):.1f} dB"
      f" | écart {db(V[parle])-db(MUS_L[parle]*G_MUS*duck[parle]):.1f} dB")
print("niveau par tranche de 3 s :", " ".join(
    f"{db(L[int(i*3*SR):int((i*3+3)*SR)]):.0f}" for i in range(13)))
