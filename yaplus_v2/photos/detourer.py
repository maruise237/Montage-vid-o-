"""Détoure les photos reçues (rembg) et recadre au plus juste : photos/det/<nom>.png"""
import sys
from PIL import Image
from rembg import remove, new_session
R = 'recus/'
SRC = {  # nom : (fichier, recadrage avant détourage ou None)
    'tuyau': ('c7ce5e60-image.jpg', None),
    'seau': ('fb7cd313-image.jpg', None),
    'chargeur': ('d9452ae3-image.jpg', None),
    'riz': ('18a35027-image.jpg', None),
    'disj': ('disj_abb.jpg', None),
    'billet1000': ('faf08354-image.jpg', (0, 0, 447, 205)),
    'client': ('1e112818-image.jpg', (0, 300, 330, 1152)),
}
ses = new_session('isnet-general-use')
for nom, (f, box) in SRC.items():
    if len(sys.argv) > 1 and nom not in sys.argv[1:]: continue
    im = Image.open(R + f).convert('RGB')
    if box: im = im.crop(box)
    out = remove(im, session=ses, alpha_matting=nom in ('client',))
    out = out.crop(out.getchannel('A').point(lambda a: 255 if a > 20 else 0).getbbox())
    out.save(f'photos/det/{nom}.png'); print(nom, out.size)
