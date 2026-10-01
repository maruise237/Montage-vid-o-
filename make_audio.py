"""Synthèse de la bande son (beat 120 bpm + bruitages) -> build/audio.wav"""
import numpy as np, wave
SR=44100; DUR=36; N=SR*DUR
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*SR)
    if i>=N: return
    s=sig[:N-i]*g
    L[i:i+len(s)]+=s*(1-max(pan,0)); R[i:i+len(s)]+=s*(1+min(pan,0))
def tt(d): return np.arange(int(d*SR))/SR
def env(d,a=.002,r=None):
    t=tt(d); r=r or d
    return np.minimum(t/a,1)*np.exp(-t/(r/4))
def lp(x,fc):  # filtre passe-bas 1 pole
    a=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); p=0
    for i,v in enumerate(x): p=(1-a)*v+a*p; y[i]=p
    return y
def kick(g=1):
    t=tt(.35); f=45+110*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)*g
def hat(g=1):
    n=rng.standard_normal(int(.06*SR)); n=np.diff(n,prepend=0)
    return n*np.exp(-tt(.06)*70)*g*.5
def clap(g=1):
    d=.22; n=rng.standard_normal(int(d*SR)); t=tt(d)
    e=sum(np.exp(-np.maximum(t-o,0)*60)*(t>=o) for o in (0,.012,.024))*np.exp(-t*14)
    return np.diff(n,prepend=0)*e*g*.35
def bass(f,d,g=1):
    t=tt(d); s=np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t)
    return np.tanh(s*1.5)*env(d,.01,d)*g*.5
def pluck(f,d=.35,g=1):
    t=tt(d); s=sum(np.sin(2*np.pi*f*k*t)/k for k in (1,2,3,4))
    return s*np.exp(-t*9)*g*.18
def whoosh(d=.5,up=True,g=1):
    n=rng.standard_normal(int(d*SR)); t=tt(d)
    # balayage par mélange de filtres : bruit modulé en amplitude + sinus glissant
    f=np.linspace(300,4000,len(t)) if up else np.linspace(4000,300,len(t))
    s=n*.3+np.sin(2*np.pi*np.cumsum(f)/SR)*.2
    s=np.diff(s,prepend=0)*.8+s*.2
    e=np.sin(np.pi*np.clip(t/d,0,1))**2
    return s*e*g*.6
def pop(f=700,g=1):
    t=tt(.12); fr=f*(1+1.5*np.exp(-t*60)); return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*38)*g*.6
def thud(g=1):
    t=tt(.4); fr=90*np.exp(-t*6)+40; return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*8)*g
def bell(f=1320,d=1.6,g=1):
    t=tt(d); s=sum(a*np.sin(2*np.pi*f*r*t) for a,r in ((1,1),(.6,2.76),(.4,5.4),(.25,8.9)))
    return s*np.exp(-t*3.2)*g*.22
def scribble(d=.5,g=1):
    n=rng.standard_normal(int(d*SR)); t=tt(d)
    return np.diff(n,prepend=0)*(0.5+0.5*np.sin(2*np.pi*14*t))*np.minimum(t/.03,1)*np.exp(-np.maximum(t-d*.7,0)*20)*g*.25
def riser(d=.35,g=1):
    n=rng.standard_normal(int(d*SR)); t=tt(d); f=np.linspace(200,6000,len(t))
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*.4+np.diff(n,prepend=0)*.3)*(t/d)**2*g
def sparkle(g=1):
    d=.5; t=tt(d); s=sum(np.sin(2*np.pi*f*t)*np.exp(-t*(6+i*2)) for i,f in enumerate((2093,2637,3136,4186)))
    return s*g*.12

BEAT=.5
# ---- Hook 0-4 : riser + impact ----
add(riser(.35),0,g=1); add(thud(1.4),.35); add(kick(1.2),.35); add(whoosh(.5,False,.8),.3)
add(bell(880,1.2,.6),.36)
for b in range(3,8): add(kick(.9),b*BEAT+.35)   # coups de grosse caisse qui montent
# ---- Beat principal 4-35 ----
notes=[55,55,43.65,49]  # A1 A1 F1 G1 (une note par mesure de 2s... 1 note / mesure)
arp=[220,261.6,329.6,261.6,220,261.6,392,329.6]
t=4.0
bar=0
while t<35.5:
    for beat in range(4):
        tb=t+beat*BEAT
        if tb>=35.5: break
        add(kick(1.0),tb,g=1)
        if beat in(1,3) and tb>=8: add(clap(1),tb,.1)
        add(hat(.8),tb+BEAT/2,.2)
        if tb>=8: add(hat(.5),tb+BEAT/4,-.2)
        # basse sur chaque croche
        f=notes[bar%4]
        add(bass(f,BEAT*.45),tb,g=.9); add(bass(f*(2 if beat%2 else 1),BEAT*.4),tb+BEAT/2,g=.6)
        if tb>=8 and tb<30: 
            add(pluck(arp[(beat*2)%8]*(2 if bar%2 else 1)),tb+BEAT/2,.4,.9)
        if tb>=30:
            add(pluck(arp[(beat*2)%8]*2),tb,-.3,.8); add(pluck(arp[(beat*2+1)%8]*2),tb+BEAT/2,.3,.8)
    t+=4*BEAT; bar+=1
# ---- Whooshes aux transitions ----
for x in (3.55,7.55,10.6,13.6,16.6,19.6,23.55,26.9,29.55): add(whoosh(.55,x%2<1,1),x)
for x in (4.0,8.0,11,14,17,20,24,27,30): add(whoosh(.45,True,.7),x-.1); add(sparkle(1),x,.2)
# ---- Bruitages sur les textes / cartes ----
pops=[.0,.1,.2,.3,.9,4.05,4.35,5.0,5.0,8.25,8.47,8.69,11.25,11.47,14.25,17.25,17.47,
      20.0,20.08,20.16,20.24,20.32,20.4,20.8,21.0,22.0,24.05,24.4,25.0,26.0,27.0,27.5,28.5,30.3,30.5,31.0,32.4,32.7,33.6]
for i,x in enumerate(pops): add(pop(600+80*(i%5)),x,(-.3,.3)[i%2],.9)
add(scribble(.5),5.0,0,1)
add(thud(1),6.6); add(bell(1760,.8,.7),6.6)           # tampon "livré"
add(whoosh(.4,True,.9),5.55); add(pop(300,1.2),5.6)  # badge -24H
add(thud(1),34.0)                                     # tampon final
for x in (25.6,28.0):                                 # ka-ching prix
    add(bell(1568,1.2,1),x); add(bell(2093,1.2,.8),x+.08); add(pop(1000,1),x)
add(bell(1046,1.8,1),31.3); add(bell(1568,1.8,.8),31.38)     # bouton CTA
add(bell(1318,2.4,1),33.2); add(bell(1760,2.4,.8),33.28); add(bell(2093,2.4,.6),33.36)
# ---- Master ----
fade=np.clip((DUR-np.arange(N)/SR)/1.0,0,1)
m=np.maximum(np.abs(L).max(),np.abs(R).max())
L=np.tanh(L/m*1.6)*fade*.9; R=np.tanh(R/m*1.6)*fade*.9
out=(np.stack([L,R],1)*32767).astype('<i2')
with wave.open('build/audio.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok')
