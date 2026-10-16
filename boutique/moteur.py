"""Moteur de montage des pubs NGUELEK PRINT.

Une pub = un module (pub1.py, pub2.py) qui décrit :
  PLANS   : liste de plans {src, t, d, mode, z0, z1, px0, px1, py0, py1, crop, v}
  CALQUE  : éléments graphiques (titres, chapitres, sous-titres, balayages, logo, écran de fin)
  VOIX    : morceaux de voix {src, a, b, t} (a-b dans la source, t sur la timeline)
  SON     : réglages musique + bruitages
Étapes : base (vidéo des plans) → calque (HTML render(t) → PNG transparents) → son → final.

Plans :
  mode 'plein' : la source remplit l'écran 1080x1920 ; zoom z0→z1 ; position px/py de 0 à 1
                 (0 = bord gauche/haut visible, 1 = bord droit/bas) pour choisir la zone gardée.
  mode 'cadre' : source posée en « tirage photo » (bord blanc) sur sa propre version floutée.
  mode 'noir'  : écran noir (le calque HTML couvre tout : logo, écran de fin).
  crop = (x0, y0, x1, y1) en fractions de la source, appliqué avant (bandes noires, incrustations).
  v = vitesse (1 = normal, 0.5 = ralenti).
"""
import json, os, subprocess, sys, shutil
from concurrent.futures import ThreadPoolExecutor

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, 'sources')
W, H, FPS = 1080, 1920, 30


def info(src):
    p = os.path.join(SRC, src + '.mp4')
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                        'stream=width,height', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout
    w, h = o.strip().split('\n')[0].split(',')[:2]
    return p, int(w), int(h)


def filtre_plan(pl, w, h):
    d = pl['d']; z0 = pl.get('z0', 1.0); z1 = pl.get('z1', z0 * 1.04)
    px0 = pl.get('px0', pl.get('px', .5)); px1 = pl.get('px1', px0)
    py0 = pl.get('py0', pl.get('py', .5)); py1 = pl.get('py1', py0)
    v = pl.get('v', 1.0)
    f = []
    if 'crop' in pl:
        x0, y0, x1, y1 = pl['crop']
        f.append(f"crop={int(w*(x1-x0))//2*2}:{int(h*(y1-y0))//2*2}:{int(w*x0)}:{int(h*y0)}")
        w, h = int(w * (x1 - x0)) // 2 * 2, int(h * (y1 - y0)) // 2 * 2
    if v != 1.0:
        f.append(f"setpts=PTS/{v}")
    f.append('fps=30')
    zt = f"({z0}+({z1}-{z0})*min(t/{d}\\,1))"
    if pl.get('mode', 'plein') == 'plein':
        cov = max(W / w, H / h)
        f.append(f"scale=w='trunc({w*cov:.3f}*{zt}/2)*2+2':h='trunc({h*cov:.3f}*{zt}/2)*2+2':eval=frame")
        pxt = f"({px0}+({px1}-{px0})*min(t/{d}\\,1))"; pyt = f"({py0}+({py1}-{py0})*min(t/{d}\\,1))"
        f.append(f"crop={W}:{H}:'(iw-{W})*{pxt}':'(ih-{H})*{pyt}'")
        return ','.join(f) + ',setsar=1,format=yuv420p', None
    # cadre : fond flouté + tirage photo à bord blanc
    lw = pl.get('largeur', 940)
    fit = min(lw / w, (H * .62) / h)
    fw, fh = int(w * fit) // 2 * 2, int(h * fit) // 2 * 2
    bord = 14
    cy = pl.get('cy', .5)
    base = ','.join(f)
    cov = max(W / w, H / h) * 1.15
    g = (f"[0:v]{base},split[a][b];"
         f"[a]scale={int(w*cov)//2*2}:{int(h*cov)//2*2},crop={W}:{H},boxblur=28:3,eq=brightness=-0.18:saturation=1.2[fond];"
         f"[b]scale=w='trunc({fw}*{zt}/2)*2':h='trunc({fh}*{zt}/2)*2':eval=frame,"
         f"pad=iw+{2*bord}:ih+{2*bord}:{bord}:{bord}:color=white[img];"
         f"[fond][img]overlay=x='(W-w)/2':y='{H*cy:.0f}-h/2':eval=frame,setsar=1,format=yuv420p[v]")
    return None, g


def rendre_plan(i, pl, dossier):
    out = os.path.join(dossier, f'p{i:03d}.mp4')
    d = pl['d']
    if pl.get('mode') == 'noir':
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=black:s={W}x{H}:r={FPS}:d={d}',
               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', out]
    else:
        p, w, h = info(pl['src'])
        v = pl.get('v', 1.0)
        simple, graphe = filtre_plan(pl, w, h)
        cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(pl['t']), '-t', str(d * v + .2), '-i', p]
        cmd += (['-vf', simple] if simple else ['-filter_complex', graphe, '-map', '[v]'])
        cmd += ['-an', '-t', str(d), '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16',
                '-pix_fmt', 'yuv420p', out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'plan {i} {pl}: {r.stderr[-800:]}')
    return out


def base(pub, dossier):
    tmp = os.path.join(dossier, 'plans'); os.makedirs(tmp, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        fichiers = list(ex.map(lambda a: rendre_plan(a[0], a[1], tmp), enumerate(pub.PLANS)))
    lst = os.path.join(tmp, 'liste.txt')
    open(lst, 'w').write(''.join(f"file '{f}'\n" for f in fichiers))
    sortie = os.path.join(dossier, 'base.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', sortie],
                   check=True)
    print('base :', sortie, round(sum(p['d'] for p in pub.PLANS), 2), 's')


def temps_plans(pub):
    """Début de chaque plan sur la timeline."""
    t, L = 0.0, []
    for p in pub.PLANS:
        L.append(round(t, 3)); t += p['d']
    return L, t


def donnees(pub, dossier):
    debuts, duree = temps_plans(pub)
    D = {'duree': duree, 'elements': pub.CALQUE, 'coupes': debuts}
    open(os.path.join(dossier, 'donnees.js'), 'w').write('window.D=' + json.dumps(D, ensure_ascii=False) + ';')
    for f in ('calque.html',):
        shutil.copy(os.path.join(ICI, f), os.path.join(dossier, f))
    print('donnees.js écrit, durée', round(duree, 2))


def planche(dossier, instants, sortie='planche.jpg', cols=6, tw=270):
    """Composite base + calque aux instants donnés → une planche contact."""
    from PIL import Image, ImageDraw
    subprocess.run(['node', os.path.join(ICI, 'rendu_calque.mjs'), dossier] + [str(t) for t in instants], check=True)
    th = tw * 16 // 9
    rows = (len(instants) + cols - 1) // cols
    pl = Image.new('RGB', (tw * cols, th * rows), (30, 30, 30))
    for i, t in enumerate(instants):
        f = os.path.join(dossier, 'planche', f'b{i:02d}.jpg')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', os.path.join(dossier, 'base.mp4'),
                        '-frames:v', '1', f], check=True)
        im = Image.open(f).convert('RGBA')
        c = Image.open(os.path.join(dossier, 'planche', f'c{i:02d}.png')).convert('RGBA')
        im.alpha_composite(c)
        im = im.convert('RGB').resize((tw, th))
        dr = ImageDraw.Draw(im); dr.rectangle([0, 0, 70, 22], fill=(0, 0, 0)); dr.text((4, 4), f'{t:.2f}', fill=(255, 255, 0))
        pl.paste(im, ((i % cols) * tw, (i // cols) * th))
    pl.save(os.path.join(dossier, sortie), quality=88)
    print('planche :', os.path.join(dossier, sortie))


def final(dossier, nom):
    sortie = os.path.join(dossier, nom)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(dossier, 'base.mp4'),
                    '-framerate', str(FPS), '-i', os.path.join(dossier, 'images', 'f%05d.png'),
                    '-i', os.path.join(dossier, 'son.wav'),
                    '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]',
                    '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
                    '-profile:v', 'high', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    sortie], check=True)
    print('final :', sortie)


if __name__ == '__main__':
    import importlib
    nom, etape = sys.argv[1], sys.argv[2]
    pub = importlib.import_module(nom)
    dossier = os.path.join(ICI, nom); os.makedirs(dossier, exist_ok=True)
    if etape in ('base', 'tout'): base(pub, dossier)
    if etape in ('donnees', 'tout', 'planche'): donnees(pub, dossier)
    if etape == 'planche':
        inst = [float(x) for x in sys.argv[3:]] or [round(t + .6, 2) for t in temps_plans(pub)[0]]
        planche(dossier, inst)
    if etape in ('son', 'tout'): pub.son(dossier)
    if etape in ('calque', 'tout'):
        donnees(pub, dossier)
        subprocess.run(['node', os.path.join(ICI, 'rendu_calque.mjs'), dossier], check=True)
    if etape in ('final', 'tout'): final(dossier, sys.argv[3] if len(sys.argv) > 3 else nom + '.mp4')
