"""Découpe les visuels de la fiche Chariow (dl/img) en calques : logo KAMTECH, téléphones, coffret, modèle Stock."""
import numpy as np
from PIL import Image
D = 'dl/img/'
o = lambda f: Image.open(D + f).convert('RGB')
# logo KAMTECH : fond menthe → transparent
im = o('44VxcaBWS9ZjN3MCANzvkxcEfWygoq1KY0xLifCv.png').crop((70, 70, 270, 126))
a = np.asarray(im).astype(float); d = np.abs(a - [244, 248, 242]).sum(2)
al = np.clip((d - 12) * 4, 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([a.astype(np.uint8), al])).save('img/kamtech.png')
# téléphones (maquettes du store), coins du fond menthe rendus transparents hors de l'écran
BOX = None
def tel(f, nom):
    im = o(f); a0 = np.asarray(im).astype(float)
    sombre = (a0.sum(2) < 150); sombre[:, :420] = False          # contour noir du téléphone (moitié droite)
    ys, xs = np.nonzero(sombre); box = BOX or (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    print(nom, box); globals()['DERNIER'] = box
    im = im.crop(box); a = np.asarray(im).astype(float)
    d = np.abs(a - a[5, 5]).sum(2); al = np.where(d < 6, 0, 255).astype(np.uint8)
    Image.fromarray(np.dstack([a.astype(np.uint8), al])).save(f'img/{nom}.png')
tel('44VxcaBWS9ZjN3MCANzvkxcEfWygoq1KY0xLifCv.png', 'tel_prompt'); BOXP = DERNIER
tel('KsfVPHgfbc0mq1IbapOUqstC4RWTlxo7XTn4KrZk.png', 'tel_livre')
BOX = (int(BOXP[0]), int(BOXP[1]), int(BOXP[2]), int(BOXP[3]))   # même maquette : on reprend le cadre détecté
tel('sAkHApTpysrKt53aP2L59lvVZ4n4e9jICZPS1gq3.png', 'tel_capture')
o('yxd7fRz0rCcEyipb03Oczlh3Jdiy3b4Jb3uaJMxl.png').save('img/coffret.png')
