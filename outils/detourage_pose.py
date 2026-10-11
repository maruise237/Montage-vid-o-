"""Détourage d'une pose d'avatar (fond crème uni) → PNG transparent recadré.

Masque rembg isnet-general-use, couleurs reprises de l'image d'origine (rembg assombrit ce qu'il juge
transparent), petits trous de la tête rebouchés (le blanc des yeux part souvent avec le fond crème),
bord adouci de 1 px. Les vrais vides (bras sur la hanche) restent transparents.
Usage : python3 outils/detourage_pose.py source.png sortie.png [...]   (par paires)
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove
from scipy import ndimage

_SESSION = None


def detourer(src, sortie):
    global _SESSION
    _SESSION = _SESSION or new_session('isnet-general-use')
    rgb = Image.open(src).convert('RGB')
    m = np.array(remove(rgb, session=_SESSION, only_mask=True, post_process_mask=True)) > 127
    trous = ndimage.binary_fill_holes(m) & ~m
    lab, n = ndimage.label(trous)
    H = m.shape[0]
    for k in range(1, n + 1):
        z = lab == k
        if z.sum() < 4000 and np.where(z)[0].mean() < 0.35 * H:
            m |= z
    lab, n = ndimage.label(m)  # garder la plus grosse pièce (miettes de fond)
    if n > 1:
        tailles = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, [i + 1 for i, t in enumerate(tailles) if t > 0.02 * tailles.max()])
    a = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    im = rgb.convert('RGBA')
    im.putalpha(a)
    im = im.crop(a.getbbox())
    im.save(sortie)
    return sortie


if __name__ == '__main__':
    a = sys.argv[1:]
    for s, d in zip(a[::2], a[1::2]):
        print(detourer(s, d))
