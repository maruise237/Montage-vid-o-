"""Rendu de texte multi-segments (polices mélangées, dégradés) sur calque RGBA."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
F = '/home/user/Montage-vid-o-/fonts/'
POLICES = {'serif': F+'InstrumentSerif-Regular.ttf', 'serif-i': F+'InstrumentSerif-Italic.ttf',
           'sans': F+'Inter-SemiBold.woff', 'sans-b': F+'Inter-Bold.woff', 'sans-m': F+'Inter-Medium.woff',
           'mono': F+'JetBrainsMono-Medium.ttf'}
_cache = {}
def police(nom, taille):
    k = (nom, int(taille))
    if k not in _cache: _cache[k] = ImageFont.truetype(POLICES[nom], int(taille))
    return _cache[k]
ARC = [(240, 100, 60), (226, 170, 40), (120, 190, 80), (40, 170, 180), (70, 120, 240), (140, 90, 220)]
def degrade(w, cols):
    xs = np.linspace(0, len(cols)-1, max(w, 2)); i = np.minimum(xs.astype(int), len(cols)-2); f = (xs - i)[:, None]
    c = np.array(cols, float); return (c[i]*(1-f) + c[i+1]*f)
def largeur(segs, taille, esp=0):
    return sum(police(f, taille).getlength(t) for t, f, _ in segs) + esp*max(0, sum(len(t) for t, _, _ in segs)-1)
def calque(segs, taille, coul_def, esp=0):
    """segs = [(texte, police, couleur|None|'arc'|liste)] -> image RGBA serrée + (ascent)"""
    asc = max(police(f, taille).getmetrics()[0] for _, f, _ in segs)
    desc = max(police(f, taille).getmetrics()[1] for _, f, _ in segs)
    W = int(largeur(segs, taille, esp)) + 8; H = asc + desc + 4
    out = np.zeros((H, W, 4), np.float32); x = 2.0
    for t, f, c in segs:
        ft = police(f, taille)
        for ch in (t if esp else [t]):
            m = Image.new('L', (W, H)); ImageDraw.Draw(m).text((x, 2 + asc), ch, font=ft, fill=255, anchor='ls')
            a = np.asarray(m, np.float32)/255
            w = ft.getlength(ch)
            if c is None: col = np.broadcast_to(np.array(coul_def, float), (H, W, 3))
            elif isinstance(c, str) or (isinstance(c, list)):
                cols = ARC if c == 'arc' else c
                g = degrade(int(w)+1, cols); col = np.zeros((H, W, 3)); xi = int(x)
                col[:, xi:xi+len(g)] = g[:max(0, min(len(g), W-xi))]
                col[:, :xi] = g[0]; col[:, xi+len(g):] = g[-1]
            else: col = np.broadcast_to(np.array(c, float), (H, W, 3))
            out[..., :3] = out[..., :3]*(1-a[..., None]) + col*a[..., None]
            out[..., 3] = np.maximum(out[..., 3], a)
            x += w + esp
    return out, asc
def coller(img, cal, x, y, alpha=1.0, revele=1.0):
    """colle le calque RGBA float (coin haut-gauche x,y) sur img RGB uint8 ; revele = fraction visible depuis la gauche"""
    H, W = img.shape[:2]; h, w = cal.shape[:2]
    a = cal[..., 3]*alpha
    if revele < 1: a = a.copy(); a[:, int(w*revele):] = 0
    x, y = int(round(x)), int(round(y))
    X0, Y0, X1, Y1 = max(0, x), max(0, y), min(W, x+w), min(H, y+h)
    if X1 <= X0 or Y1 <= Y0: return
    aa = a[Y0-y:Y1-y, X0-x:X1-x, None]; cc = cal[Y0-y:Y1-y, X0-x:X1-x, :3]
    img[Y0:Y1, X0:X1] = (img[Y0:Y1, X0:X1]*(1-aa) + cc*aa).astype(np.uint8)
