"""Effacement de texte sur fond uni / dégradé : masque = écart à un fond médian, puis remplissage par ce fond."""
import cv2, numpy as np
def analyser(img, box, k=61, seuil=20):
    x0, y0, x1, y1 = box; H, W = img.shape[:2]; p = k // 2 + 2
    X0, Y0, X1, Y1 = max(0, x0-p), max(0, y0-p), min(W, x1+p), min(H, y1+p)
    big = img[Y0:Y1, X0:X1]
    bg = cv2.medianBlur(big, k)
    d = np.abs(big.astype(np.int16) - bg.astype(np.int16)).sum(2)
    sl = (slice(y0-Y0, y1-Y0), slice(x0-X0, x1-X0))
    return big, bg, d, sl, (X0, Y0)
def effacer(img, box, k=61, seuil=20, dil=7, min_px=40, juste_info=False):
    big, bg, d, sl, (X0, Y0) = analyser(img, box, k, seuil)
    m = np.zeros(d.shape, np.uint8); m[sl] = (d[sl] > seuil)
    n = int(m.sum())
    if n < min_px: return None
    ys, xs = np.nonzero(m)
    dv = d[ys, xs]; top = dv >= np.percentile(dv, 75)
    info = dict(n=n, bbox=(X0+int(np.percentile(xs, .5)), Y0+int(np.percentile(ys, .5)),
                           X0+int(np.percentile(xs, 99.5))+1, Y0+int(np.percentile(ys, 99.5))+1),
                contraste=float(np.percentile(dv, 90)), couleur=big[ys[top], xs[top]].reshape(-1, 3).mean(0),
                fond=bg[ys, xs].reshape(-1, 3).mean(0))
    if juste_info: return info
    md = cv2.dilate(m, np.ones((dil, dil), np.uint8))
    md[:sl[0].start] = 0; md[sl[0].stop:] = 0; md[:, :sl[1].start] = 0; md[:, sl[1].stop:] = 0
    tmp = big.copy(); tmp[md > 0] = bg[md > 0]
    bg2 = cv2.medianBlur(tmp, k)
    a = np.clip(cv2.GaussianBlur(md.astype(np.float32), (0, 0), 1.5) * 1.6, 0, 1)[..., None]
    big[:] = (big * (1 - a) + bg2 * a).astype(np.uint8)
    return info
