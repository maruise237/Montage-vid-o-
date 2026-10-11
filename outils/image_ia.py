"""Génère une image IA verticale (9:16) via Pollinations (gen.pollinations.ai).

Clé API lue dans la variable d'environnement `pollinationsai` (ou POLLINATIONS_API_KEY).
Modèles testés OK avec la clé (oct. 2026), du plus rapide au plus soigné :
  zimage           ~6 s   1088x1920  photo réaliste, bon défaut
  flux-schnell     ~7 s    768x1280  rendu ciné contrasté, plus petit
  flux-klein      ~11 s   1072x1920  scènes vivantes, couleurs riches
  gpt-image-2     ~35 s   1088x1920  le plus pro, SEUL fiable pour écrire du texte
  mai             ~40 s   1088x1920  décors détaillés (peut inventer des enseignes)
Sans clé : seulement 576x1024, filigrane imposé et quota vite épuisé, à éviter.
TOUJOURS regarder l'image obtenue avant de la monter (mains, texte, logos inventés).

Usage : python3 outils/image_ia.py "prompt en anglais" sortie.jpg [modele] [seed]
"""
import os, sys, urllib.parse, urllib.request, urllib.error

MODELES = {
    'zimage': ('zimage', 1080, 1920),
    'flux-schnell': ('black-forest-labs/flux.1-schnell', 1080, 1920),
    'flux-klein': ('black-forest-labs/flux.2-klein-4b', 1080, 1920),
    'gpt-image-2': ('gpt-image-2', 1080, 1920),
    'mai': ('microsoft/mai-image-2.6', 1088, 1920),  # exige des multiples de 16
}


def generer(prompt, sortie, modele='zimage', seed=42):
    cle = os.environ.get('pollinationsai') or os.environ.get('POLLINATIONS_API_KEY')
    if not cle:
        sys.exit('Clé Pollinations absente (variable pollinationsai).')
    nom, l, h = MODELES[modele]
    params = urllib.parse.urlencode({'model': nom, 'width': l, 'height': h, 'seed': seed, 'nologo': 'true'})
    url = f'https://gen.pollinations.ai/image/{urllib.parse.quote(prompt)}?{params}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {cle}'})
    try:
        donnees = urllib.request.urlopen(req, timeout=240).read()
    except urllib.error.HTTPError as e:
        sys.exit(f'Erreur {e.code} : {e.read().decode()[:300]}')
    with open(sortie, 'wb') as f:
        f.write(donnees)
    return sortie


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    generer(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or ['zimage']), *[int(s) for s in sys.argv[4:5]])
    print(sys.argv[2])
