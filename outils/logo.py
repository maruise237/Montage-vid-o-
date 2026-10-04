"""Récupère le VRAI logo d'un outil cité dans la vidéo (jamais une forme inventée).

Sources, dans l'ordre :
1. Wikimedia Commons : logos officiels en couleur (SVG rendus en PNG 512 px).
2. Simple Icons : 3 000+ marques, forme officielle, peinte dans la couleur de la marque.
3. Favicon du site (si on donne le domaine) : dernier recours, petite taille.
Le PNG est mis en cache dans assets/logos/<nom>.png : on le réutilise d'une vidéo à l'autre.
TOUJOURS regarder le PNG obtenu avant de l'utiliser (Wikimedia peut renvoyer un vieux logo).

Usage : python3 outils/logo.py "CapCut" [domaine.com]
"""
import io, json, os, re, sys, urllib.parse, urllib.request
from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{RACINE}/assets/logos'
UA = {'User-Agent': 'KamtechMontage/1.0 (montage video)'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()


def slug(nom):
    return re.sub(r'[^a-z0-9]', '', nom.lower().replace('+', 'plus').replace('.', 'dot'))


def wikimedia(nom):
    q = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
                                'gsrsearch': f'{nom} logo', 'gsrlimit': 15, 'prop': 'imageinfo',
                                'iiprop': 'url|mime', 'iiurlwidth': 512})
    pages = json.loads(get(f'https://commons.wikimedia.org/w/api.php?{q}')).get('query', {}).get('pages', {})
    for p in sorted(pages.values(), key=lambda p: p.get('index', 99)):
        titre, info = p['title'].lower(), p['imageinfo'][0]
        # « File:Instagram logo 2016.svg » oui ; « File:Instagram and Threads logo.png » non
        nom_re = r'[ _-]*'.join(map(re.escape, nom.lower().split()))
        if re.match(rf'file:{nom_re}[ _-]*(\d{{4}}[ _-]*)?(logo|icon|glyph)[ _-]*(\d{{4}})?\.(svg|png)$', titre) \
                and info['mime'] in ('image/svg+xml', 'image/png'):
            return get(info.get('thumburl') or info['url'])


def simple_icons(nom):
    base = 'https://cdn.jsdelivr.net/npm/simple-icons@latest'
    data = json.loads(get(f'{base}/_data/simple-icons.json'))
    data = data if isinstance(data, list) else data.get('icons', [])
    icone = next((i for i in data if slug(i['title']) == slug(nom)), None)
    if not icone:
        return None
    import cairosvg
    svg = get(f"{base}/icons/{icone.get('slug') or slug(icone['title'])}.svg").decode()
    svg = svg.replace('<svg ', f'<svg fill="#{icone["hex"]}" ', 1)
    return cairosvg.svg2png(bytestring=svg.encode(), output_width=512)


def favicon(domaine):
    return get(f'https://www.google.com/s2/favicons?domain={domaine}&sz=256')


def logo(nom, domaine=None):
    """Chemin d'un PNG RGBA du logo officiel (téléchargé une seule fois)."""
    os.makedirs(CACHE, exist_ok=True)
    chemin = f'{CACHE}/{slug(nom)}.png'
    if os.path.exists(chemin):
        return chemin
    for source in (lambda: wikimedia(nom), lambda: simple_icons(nom), lambda: domaine and favicon(domaine)):
        try:
            png = source()
        except Exception:
            png = None
        if png:
            Image.open(io.BytesIO(png)).convert('RGBA').save(chemin)
            return chemin
    raise SystemExit(f'Aucun logo trouvé pour {nom} : donner le domaine, ou prendre une capture du site.')


if __name__ == '__main__':
    print(logo(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
