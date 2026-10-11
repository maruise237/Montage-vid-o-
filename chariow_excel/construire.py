"""Place les 12 phrases de voix (Fish Audio) sur la timeline → timeline.js (mots horodatés globaux) + timeline.json"""
import json
M=json.load(open('voix/mots.json'))
GAP={1:.15,2:.25,3:.45,4:.3,5:.3,6:.35,7:.55,8:.35,9:.3,10:.3,11:.45,12:.35}   # silence avant chaque phrase
t=0; phr=[]
for i in range(1,13):
    d=M[str(i)]; debut=t+GAP[i]; off=debut-d['debut']
    mots=[[w,round(a+off,3),round(b+off,3)] for w,a,b in d['mots']]
    phr.append({'i':i,'off':round(off,3),'debut':round(debut,3),'fin':round(d['fin']+off,3),'mots':mots})
    t=d['fin']+off
DUREE=round(t+2.6,2)
json.dump({'phrases':phr,'duree':DUREE},open('timeline.json','w'),ensure_ascii=False,indent=0)
open('timeline.js','w').write('window.TL='+json.dumps({'phrases':phr,'duree':DUREE},ensure_ascii=False)+';')
for p in phr: print(p['i'],p['debut'],p['fin'],' '.join(f"{w}@{a:.2f}" for w,a,b in p['mots']))
print('DUREE',DUREE)
