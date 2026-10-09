"""Place les 9 phrases de voix (Fish Audio) sur la timeline → timeline.js (mots horodatés globaux) + timeline.json"""
import json
M=json.load(open('voix/mots.json'))
GAP={1:.25,2:.25,3:.8,4:.35,5:.35,6:.4,7:.35,8:.75,9:.35}   # silence avant chaque phrase
t=0; phr=[]
for i in range(1,10):
    d=M[str(i)]; debut=t+GAP[i]; off=debut-d['debut']
    mots=[[w,round(a+off,3),round(b+off,3)] for w,a,b in d['mots']]
    phr.append({'i':i,'off':round(off,3),'debut':round(debut,3),'fin':round(d['fin']+off,3),'mots':mots})
    t=d['fin']+off
DUREE=round(t+2.6,2)
json.dump({'phrases':phr,'duree':DUREE},open('timeline.json','w'),ensure_ascii=False,indent=0)
open('timeline.js','w').write('window.TL='+json.dumps({'phrases':phr,'duree':DUREE},ensure_ascii=False)+';')
for p in phr: print(p['i'],p['debut'],p['fin'],' '.join(f"{w}@{a:.2f}" for w,a,b in p['mots']))
print('DUREE',DUREE)
