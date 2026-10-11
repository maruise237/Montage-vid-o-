"""Avatar 3D de Mariuse via l'API Google Gemini (Nano Banana), photos envoyées en inline (base64).

Clé lue dans la variable d'environnement `google_api` (ou GEMINI_API_KEY).
Les photos de Mariuse ne passent JAMAIS par un hébergeur public : elles partent en base64
directement dans la requête à Google.

COÛT (vérifié oct. 2026, ai.google.dev/gemini-api/docs/pricing) : AUCUN quota gratuit pour les
modèles d'image. Une clé sans facturation renvoie 429 « limit: 0 ».
  flash-lite  gemini-3.1-flash-lite-image  ~0,034 $ / image 1K   (défaut : le moins cher)
  flash       gemini-3.1-flash-image       ~0,067 $ / image 1K   (plus fidèle au visage)
  pro         gemini-3-pro-image           le plus cher, seulement si les autres échouent
Chaque appel est noté dans assets/avatar/depenses.csv pour suivre la dépense.

Usage :
  python3 outils/avatar_gemini.py maitre  sortie.png [modele] photo1.jpg [photo2.jpg ...]
  python3 outils/avatar_gemini.py pose NOM sortie.png [modele]      (part de assets/avatar/maitre.png)
  python3 outils/avatar_gemini.py poses                             (liste des poses prévues)
"""
import base64, csv, datetime, json, mimetypes, os, sys, urllib.error, urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AVATAR = os.path.join(RACINE, 'assets', 'avatar')
STYLE_REF = os.path.join(AVATAR, 'style_reference', 'ref_bureau_vert.jpg')
MAITRE = os.path.join(AVATAR, 'maitre.png')

MODELES = {
    'flash-lite': ('gemini-3.1-flash-lite-image', 0.034),
    'flash': ('gemini-3.1-flash-image', 0.067),
    'pro': ('gemini-3-pro-image', 0.134),
}

STYLE = ("3D animated character in the style of a Pixar film: big head, large expressive eyes, soft "
         "skin shading, smooth stylized proportions, full body visible from head to sneakers, "
         "soft studio lighting, plain flat uniform cream background (#F1EBE0) with nothing else, "
         "no text, no watermark, vertical 9:16 framing with margin around the character.")
TENUE = ("Outfit always identical: black crew-neck t-shirt with the white KAMTECH logo on the chest "
         "(a small stylized person icon, a blue bar, and the word KAMTECH), blue jeans, white sneakers.")

POSES = {
    'face': 'standing straight facing the camera, arms relaxed, friendly smile',
    'bras_croises': 'arms crossed, confident smirk',
    'pointe': 'pointing with the index finger toward the upper left of the frame, excited',
    'haussement': 'shrugging with both palms up, puzzled face',
    'ordinateur': 'holding an open laptop in one arm and typing with the other hand, focused',
    'telephone': 'looking at a smartphone held in one hand, amused',
    'choque': 'shocked, mouth wide open, hands on cheeks',
    'pouce': 'big thumbs up with a wide smile, winking',
    'argent': 'fanning out a handful of banknotes, happy',
    'reflechit': 'thinking, hand on chin, eyes looking up',
    'camera': 'holding a vlog camera filming himself, smiling',
    'explique': 'explaining with both open hands in front of him, calm teacher attitude',
    'triste': 'disappointed, shoulders down, hands in pockets',
    'victoire': 'jumping with a fist in the air, celebrating',
}


def _cle():
    cle = os.environ.get('google_api') or os.environ.get('GEMINI_API_KEY')
    if not cle:
        sys.exit('Clé Google absente (variable google_api).')
    return cle


def _image(chemin):
    mime = mimetypes.guess_type(chemin)[0] or 'image/jpeg'
    return {'inline_data': {'mime_type': mime, 'data': base64.b64encode(open(chemin, 'rb').read()).decode()}}


def generer(texte, images, sortie, modele='flash-lite'):
    nom, prix = MODELES[modele]
    corps = {'contents': [{'parts': [_image(i) for i in images] + [{'text': texte}]}],
             'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '9:16'}}}
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{nom}:generateContent',
        data=json.dumps(corps).encode(),
        headers={'x-goog-api-key': _cle(), 'Content-Type': 'application/json'})
    try:
        rep = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        sys.exit(f'Erreur {e.code} : {e.read().decode()[:500]}')
    for part in rep['candidates'][0]['content']['parts']:
        donnees = part.get('inlineData') or part.get('inline_data')
        if donnees:
            os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
            open(sortie, 'wb').write(base64.b64decode(donnees['data']))
            _noter(nom, prix, sortie)
            return sortie
    sys.exit('Pas d\'image dans la réponse : ' + json.dumps(rep)[:500])


def _noter(nom, prix, sortie):
    chemin = os.path.join(AVATAR, 'depenses.csv')
    neuf = not os.path.exists(chemin)
    with open(chemin, 'a', newline='') as f:
        w = csv.writer(f)
        if neuf:
            w.writerow(['date', 'modele', 'prix_usd_estime', 'fichier'])
        w.writerow([datetime.datetime.now().isoformat(timespec='seconds'), nom, prix, os.path.relpath(sortie, RACINE)])


def maitre(sortie, modele, photos):
    texte = (f"Turn the real person in the photos into a {STYLE} Keep his face shape, skin tone, "
             f"hairstyle and beard recognisable. The last image is only a STYLE reference, do not copy "
             f"that character. {TENUE} Pose: {POSES['face']}.")
    return generer(texte, list(photos) + [STYLE_REF], sortie, modele)


def pose(nom, sortie, modele):
    texte = (f"Same exact character as in the image (same face, hair, body, outfit, same 3D style), "
             f"new pose: {POSES.get(nom, nom)}. {TENUE} {STYLE}")
    return generer(texte, [MAITRE], sortie, modele)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == 'poses':
        print('\n'.join(f'{k:12} {v}' for k, v in POSES.items()))
    elif a[0] == 'maitre' and len(a) >= 4:
        mod = a[2] if a[2] in MODELES else 'flash-lite'
        print(maitre(a[1], mod, a[3:] if a[2] in MODELES else a[2:]))
    elif a[0] == 'pose' and len(a) >= 3:
        print(pose(a[1], a[2], a[3] if len(a) > 3 else 'flash-lite'))
    else:
        sys.exit(__doc__)
