"""Avatar 3D de Mariuse via Cloudflare Workers AI (FLUX.2 klein), quota GRATUIT quotidien.

Variables d'environnement : CLOUDFLARE_ACCOUNT_ID et CLOUDFLARE_API_TOKEN (jeton Workers AI).
Les photos de Mariuse partent directement dans la requête multipart à Cloudflare,
JAMAIS sur un hébergeur public.

COÛT (vérifié oct. 2026, developers.cloudflare.com/workers-ai/platform/pricing) :
  10 000 neurons gratuits par jour (remis à zéro à 00:00 UTC). Compte Workers Free : au-delà,
  les requêtes sont refusées, rien n'est facturé.
  klein-9b  @cf/black-forest-labs/flux-2-klein-9b  1 363,64 neurons le 1er mégapixel de sortie
            + 181,82 par MP suivant + 181,82 par MP d'image de référence
            → ~1 410 neurons pour une image 768x1344 avec 1 référence 512 px → ~7 images/jour.
  klein-4b  @cf/black-forest-labs/flux-2-klein-4b  26,05 neurons par tuile 512² de sortie
            + 5,37 par tuile 512² de référence → ~170 neurons → ~55 images/jour (moins fidèle).
Chaque appel est noté dans assets/avatar/depenses.csv (neurons réels, en-tête cf-ai-neurons).

Usage :
  python3 outils/avatar_cloudflare.py maitre  sortie.png [modele] photo1.jpg [photo2.jpg ...]
  python3 outils/avatar_cloudflare.py pose NOM sortie.png [modele]   (part de assets/avatar/maitre.png)
  python3 outils/avatar_cloudflare.py poses                          (liste des poses prévues)
  python3 outils/avatar_cloudflare.py libre "prompt" sortie.png [modele] [ref1.jpg ...]
"""
import base64, csv, datetime, io, math, os, sys

import requests
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avatar_gemini import AVATAR, MAITRE, POSES, RACINE, STYLE, STYLE_REF, TENUE, VISAGE  # noqa: E402

MODELES = {'klein-9b': '@cf/black-forest-labs/flux-2-klein-9b',
           'klein-4b': '@cf/black-forest-labs/flux-2-klein-4b'}
LARGEUR, HAUTEUR = 768, 1344          # 9:16, multiples de 16, < 1 MP
REF_MAX = 512                         # chaque référence redimensionnée sous 512x512


def _neurons(modele, refs):
    """Estimation d'après la grille tarifaire (l'API ne renvoie pas toujours la consommation)."""
    if modele == 'klein-9b':
        mp = LARGEUR * HAUTEUR / 1024 ** 2
        sortie = 1363.64 + max(0, mp - 1) * 181.82
        return round(sortie + sum(w * h / 1024 ** 2 * 181.82 for w, h in refs))
    tuiles = lambda w, h: math.ceil(w / 512) * math.ceil(h / 512)
    return round(tuiles(LARGEUR, HAUTEUR) * 26.05 + sum(tuiles(w, h) * 5.37 for w, h in refs))


def _ref(chemin):
    im = Image.open(chemin).convert('RGB')
    im.thumbnail((REF_MAX, REF_MAX), Image.LANCZOS)
    tampon = io.BytesIO()
    im.save(tampon, 'JPEG', quality=92)
    return tampon.getvalue(), im.size


def _appel(modele, texte, refs):
    compte, jeton = os.environ.get('CLOUDFLARE_ACCOUNT_ID'), os.environ.get('CLOUDFLARE_API_TOKEN')
    if not compte or not jeton:
        sys.exit('CLOUDFLARE_ACCOUNT_ID ou CLOUDFLARE_API_TOKEN absent.')
    champs = {'prompt': (None, texte), 'width': (None, str(LARGEUR)), 'height': (None, str(HAUTEUR))}
    tailles = []
    for i, chemin in enumerate(refs[:4]):
        octets, taille = _ref(chemin)
        champs[f'input_image_{i}'] = (f'ref{i}.jpg', octets, 'image/jpeg')
        tailles.append(taille)
    r = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{compte}/ai/run/{MODELES[modele]}',
                      headers={'Authorization': f'Bearer {jeton}'}, files=champs, timeout=300)
    return r, tailles


def generer(texte, refs, sortie, modele='klein-9b'):
    r, tailles = _appel(modele, texte, refs)
    if r.status_code >= 500 and modele == 'klein-9b':
        print(f'klein-9b indisponible ({r.status_code}), repli sur klein-4b', file=sys.stderr)
        modele = 'klein-4b'
        r, tailles = _appel(modele, texte, refs)
    try:
        rep = r.json()
    except ValueError:
        sys.exit(f'Erreur {r.status_code} : {r.text[:500]}')
    if not rep.get('success') or 'image' not in rep.get('result', {}):
        sys.exit(f'Erreur {r.status_code} : {str(rep)[:800]}')
    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
    Image.open(io.BytesIO(base64.b64decode(rep['result']['image']))).save(sortie)  # l'API renvoie du JPEG
    neurons = r.headers.get('cf-ai-neurons')  # consommation réelle renvoyée par Cloudflare
    _noter(MODELES[modele], neurons if neurons is not None else _neurons(modele, tailles),
           'api' if neurons is not None else 'estime', sortie)
    return sortie


def _noter(nom, neurons, source, sortie):
    chemin = os.path.join(AVATAR, 'depenses.csv')
    neuf = not os.path.exists(chemin)
    with open(chemin, 'a', newline='') as f:
        w = csv.writer(f)
        if neuf:
            w.writerow(['date', 'modele', 'cout', 'fichier'])
        w.writerow([datetime.datetime.now().isoformat(timespec='seconds'), nom,
                    f'{neurons} neurons ({source}, gratuit)', os.path.relpath(sortie, RACINE)])


def maitre(sortie, modele, photos):
    texte = (f"Turn the real person of image 1 (his face photo) into a {STYLE} {VISAGE} The other photos "
             f"show the exact KAMTECH logo of his t-shirt: reproduce it faithfully. The last image is only a "
             f"STYLE reference, do not copy that character. {TENUE} Pose: {POSES['face']}.")
    return generer(texte, list(photos)[:3] + [STYLE_REF], sortie, modele)


def pose(nom, sortie, modele):
    texte = (f"Same exact character as in the image (same face, hair, body, outfit, same 3D style), "
             f"new pose: {POSES.get(nom, nom)}. {VISAGE} {TENUE} {STYLE}")
    return generer(texte, [MAITRE], sortie, modele)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == 'poses':
        print('\n'.join(f'{k:12} {v}' for k, v in POSES.items()))
    elif a[0] == 'maitre' and len(a) >= 3:
        mod = a[2] if a[2] in MODELES else 'klein-9b'
        print(maitre(a[1], mod, a[3:] if a[2] in MODELES else a[2:]))
    elif a[0] == 'pose' and len(a) >= 3:
        print(pose(a[1], a[2], a[3] if len(a) > 3 else 'klein-9b'))
    elif a[0] == 'libre' and len(a) >= 3:
        mod = a[3] if len(a) > 3 and a[3] in MODELES else 'klein-9b'
        reste = a[4:] if len(a) > 3 and a[3] in MODELES else a[3:]
        print(generer(a[1], reste, a[2], mod))
    else:
        sys.exit(__doc__)
