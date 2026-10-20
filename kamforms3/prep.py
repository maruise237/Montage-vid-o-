"""Découpe les captures APKPure (store KamForms) en calques pour l'animation → img/*.png + couleurs.json"""
from PIL import Image
import json
S=lambda i: Image.open(f'dl/screen-{i}.jpg').convert('RGB')
C={ 'chat':(1,(0,640,1080,1920)),
    'lien':(2,(30,480,1050,800)),
    'partage':(2,(170,880,1010,1920)),
    'whatsapp':(3,(60,560,1060,1760)),
    'reponse':(4,(60,90,1020,850)),
    'notif':(4,(100,878,1000,1078)),
    'perso':(5,(20,620,1060,1920)),
    'stats':(6,(150,540,1080,1920)),
    'fonctions':(7,(100,510,980,1435)),
    'installer':(7,(100,100,980,330)),
}
for k,(i,b) in C.items(): S(i).crop(b).save(f'img/{k}.png')
coul={i:'#%02x%02x%02x'%S(i).getpixel(p) for i,p in [(1,(20,900)),(2,(20,1000)),(3,(20,1000)),(4,(20,1300)),(5,(20,1000)),(6,(20,1000)),(7,(20,1000)),(0,(60,1500))]}
json.dump(coul,open('img/couleurs.json','w'),indent=1); print(coul)
