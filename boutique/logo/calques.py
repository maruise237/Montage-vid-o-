"""Découpe le logo NGUELEK PRINT en calques (anneau, N, P, 4 vagues CMJN, GUELEK, PRINT) pour l'animer."""
from PIL import Image
import numpy as np
from scipy import ndimage
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
im = np.asarray(Image.open('logo.jpg').convert('RGB')).astype(float)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx = im.max(2); mn = im.min(2); sat = mx - mn
alpha = np.maximum(np.clip((255 - mn) / 90, 0, 1), np.clip(sat / 80, 0, 1))
H, W = mn.shape
yy, xx = np.mgrid[0:H, 0:W]
cyan = (b > 150) & (r < 120)
mag = (r > 170) & (g < 90) & (b > 60)
yel = (r > 180) & (g > 170) & (b < 120)
dark = mx < 110
gray = (sat < 30) & (mn > 100) & (mn < 215)
d = np.sqrt(((xx - 532) / 512) ** 2 + ((yy - 518) / 415) ** 2)
ring = dark & (d > 0.9)
L = {}
L['anneau'] = ring
L['N'] = dark & ~ring & (((xx < 440) & (yy < 675)) | ((xx < 300) & (yy >= 675)))
L['P'] = cyan & (xx < 665) & (yy < 672) & (yy > 310) & ~((xx > 548) & (yy > 540))
L['vague_c'] = cyan & ~L['P'] & (yy < 680)
L['vague_m'] = mag
L['vague_j'] = yel
L['vague_n'] = (dark | gray) & ~ring & (xx > 560) & (yy > 540) & (yy < 680)
L['guelek'] = dark & ~ring & (yy > 675) & (xx >= 300) & (xx < 630)
L['print'] = cyan & (yy > 675)
tot = np.zeros((H, W), bool)
for k, m in L.items():
    m = ndimage.binary_dilation(m, iterations=2)
    a = (alpha * m * 255).astype(np.uint8)
    Image.fromarray(np.dstack([im.astype(np.uint8), a]), 'RGBA').save(f'calque_{k}.png')
    tot |= m
Image.fromarray(np.dstack([im.astype(np.uint8), (alpha * 255).astype(np.uint8)]), 'RGBA').save('logo_detoure.png')
# contrôle : calques réunis | logo détouré | ce qui n'est dans aucun calque (rouge = couvert)
prev = Image.new('RGB', (W * 3, H), (90, 90, 90))
c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for k in L: c.alpha_composite(Image.open(f'calque_{k}.png'))
prev.paste(c, (0, 0), c)
lt = Image.open('logo_detoure.png'); prev.paste(lt, (W, 0), lt)
reste = im.copy(); reste[tot] = [255, 0, 0]
prev.paste(Image.fromarray(reste.astype(np.uint8)), (2 * W, 0))
prev.resize((W, H // 3)).save('controle.jpg')
