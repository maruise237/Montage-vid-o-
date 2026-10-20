# Vidéos avec l'avatar 3D de Mariuse (KAMTECH)

**Situation** : vidéos faceless où l'avatar remplace la facecam (voir aussi la skill `video-avatar`).

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## 2026-10 — Avatar 3D : passage de Pollinations à Google Gemini
- Crédit Pollinations à 0 → nouvelle clé Google dans l'environnement : variable **`google_api`**.
- Coût vérifié (pricing Gemini, oct. 2026) : **pas de quota gratuit** pour les modèles d'image.
  `gemini-3.1-flash-lite-image` ≈ 0,034 $/image 1K (défaut), `gemini-3.1-flash-image` ≈ 0,067 $.
  Avatar maître + ~14 poses avec retouches ≈ 30 images ≈ **1 à 2 $**.
- Construit : `outils/avatar_gemini.py` (photos en base64 inline, jamais d'hébergeur public ; journal
  des dépenses dans `assets/avatar/depenses.csv` ; liste des poses) et la compétence
  `.claude/skills/video-avatar/` (demander voix off ou script, demander le style si flou).
- En attente : les 2 photos de Mariuse (face fond gris + dos logo KAMTECH), puis validation du maître.
- Test réel (11 oct.) : la clé `google_api` renvoie **429 « free_tier limit: 0 »** sur les modèles d'image
  → il faut activer la facturation dans AI Studio. Alternative : treg (crédit 0,57 $), Nano Banana Pro via
  reAPI à 0,03 $/image, mais les images de référence doivent être des URL publiques (pas d'inline).
  Les poses partent de l'avatar maître (pas de la photo de Mariuse) : seules elles peuvent passer par URL.

## 2026-10 — Avatar 3D : passage à Cloudflare Workers AI (gratuit)
- Google `google_api` : 429 « limit 0 » sur les images → Mariuse a ajouté `CLOUDFLARE_ACCOUNT_ID` et
  `CLOUDFLARE_API_TOKEN` (jeton Workers AI). Quota gratuit : **10 000 neurons/jour**, refus au-delà, pas de facture.
- Construit : `outils/avatar_cloudflare.py` (mêmes commandes maitre / pose / poses que la version Gemini,
  mêmes STYLE / TENUE / POSES importés, + `libre`). FLUX.2 klein 9B, repli klein 4B si erreur serveur.
  REST `…/ai/run/@cf/black-forest-labs/flux-2-klein-9b`, multipart `prompt`, `width`, `height`,
  `input_image_0..3` (réf. < 512x512). Réponse JSON `result.image` = **JPEG** en base64 (converti en PNG).
  La doc du modèle ne donne pas les noms de champs : validés par test.
- Test sans photo (référence de style seule, 768x1344) : **1 393,91 neurons** (en-tête `cf-ai-neurons`),
  résultat très propre (logo KAMTECH lisible, fond crème, corps entier) → ~7 images/jour gratuites.
  klein-4b : ~170 neurons/image → ~55/jour pour les brouillons.
- En attente : les photos de Mariuse (face fond gris + dos logo) → `assets/avatar/photos/` (ignoré par git).

## 2026-10 — Vidéo avatar n°1 « cette vidéo est entièrement montée avec du code » (1 min 18)
- Matière : un vocal de Mariuse de 2 min 16 (16 kHz, téléphone) plein d'hésitations et de reprises, avec des
  consignes dites à voix haute (« Claude, mets ton logo », « change l'arrière-plan », « mets-le dans une ville »,
  « une salle où on voit KAMTECH », « un avatar de toi qui marche avec des lunettes sur la plage », « mets mon avatar
  derrière toi »). **On exécute chaque consigne à l'écran au mot prononcé** : c'est la démonstration.
- Voix : nettoyage `arnndn` (modèle sh.rnnn) + `afftdn` + dé-essage + compresseur ; 23 phrases gardées sur l'énergie
  → 75,7 s de voix. Coupé : un premier essai (« nous venons de… » repris 3 s plus loin), « Nano Banana » (c'est un
  modèle d'IMAGE, pas de vidéo), « ByteDance » (une société, Seedance est son modèle), le passage inaudible
  « aucun outil Steam ni d'API XFIL » (remplacé à l'écran par une facture à 0 €).
- Transcription : ElevenLabs à court de crédit → **Whisper de Cloudflare** (106 neurons pour 2 min 16). Whisper invente
  parfois (« Sous-titres réalisés par Amara.org » sur un blanc, phrase répétée) : retranscrire la zone seule.
- Images : 28 générations ≈ 7 000 neurons sur 10 000 gratuits, **0 €**. Poses et décors en klein-4b (~105 neurons),
  mascotte Claude en klein-9b (1re version en klein-4b = « pieuvre », refusée à l'œil).
- Retours de Mariuse pendant le travail : « tu as d'autres outils, Cloudflare » (ne pas s'arrêter sur un quota
  épuisé), « le bras de victoire est doublé » (regarder chaque pose en grand), **« pas de bordure blanche »**
  (personnage, mots géants, sous-titres : retirées, règle ajoutée à video-avatar).
- Erreur vue sur la planche : le décor changeait 0,3 s avant la phrase (début de mot de whisper trop tôt) → scènes
  calées sur les débuts de phrase mesurés à l'énergie.
- Mot à vérifier avec Mariuse : « si vous ne *suivez* pas les hésitations » (3 transcriptions) affiché « sentez ».
- CTA ajouté à l'écran seulement : « abonne-toi, commente AVATAR » (Mariuse ne le dit pas dans le vocal).
- Fichiers : `avatar1/coupe.py` (voix), `avatar1/montage.py` (image, rendu sur 4 cœurs, `planche` pour vérifier),
  `avatar1/son.py`, `avatar1/finir.sh` → `video_avatar_1.mp4` (-14,1 LUFS, musique 17 dB sous la voix).
- Après livraison, Mariuse : « garde les images et classe-les » → `assets/banque/` (poses par humeur, décors,
  personnages, illustrations), `CATALOGUE.md` court + `apercu.jpg`. Règle : piocher dans la banque avant de générer.
