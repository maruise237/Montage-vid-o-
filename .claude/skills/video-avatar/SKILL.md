---
name: video-avatar
description: Fabrique une vidéo short-form (Reel, TikTok, Short) où l'avatar 3D de Mariuse (style Pixar, t-shirt noir KAMTECH) remplace sa facecam, dans le style « 2D sticker » de Le Dev ULTIME (fond crème quadrillé, sous-titres en haut, cartes néo-brutalistes, une pose par phrase). Déclencher sur : vidéo avatar, vidéo faceless, sans visage, avec mon avatar, mon personnage 3D, style Le Dev ULTIME, banque de poses, nouvelle pose d'avatar.
---

# Vidéo avatar — mode d'emploi

Toujours lire d'abord `.claude/skills/montage-pro/SKILL.md` (règles anti-slop) et la fiche
« Créateur F » de `montage-pro/references/inspirations.md`. Mariuse veut **dépenser le moins possible**.

## 1. Avant de commencer : obtenir la matière (poser les questions, ne rien inventer)

1. **Voix off OU script.** Demander lequel Mariuse fournit :
   - un fichier audio (sa voix) → transcrire avec horodatage par mot (ElevenLabs Scribe, sinon
     `faster-whisper` `small`, `word_timestamps=True`) ;
   - un script texte → générer la voix off avec ElevenLabs (`podcast/tts.py` : variable `ELEVENLABS`,
     endpoint `with-timestamps`, donne directement les temps par mot) ;
   - ni l'un ni l'autre → proposer un script (structure Hook → Build-up → Valeur → CTA « commente MOT »,
     montage-pro §3) et le faire **valider avant** de générer la voix.
2. **Style de montage.** Si la demande est vague, demander (une seule question, avec choix) :
   - *2D sticker* (défaut, celui qui marche le mieux : 2 477 likes vs 204 pour la 3D) ;
   - *variante sombre / couleur de marque* ;
   - *mix* avatar + captures d'écran (tuto outil).
   Rappeler aussi : format (9:16 par défaut), durée visée, mot du CTA.

## 2. La DA « 2D sticker » (avec l'avatar 3D de Mariuse)

- Fond papier crème **#F1EBE0** + quadrillage très léger ; accent rouge brique **#D9442B** ; texte noir.
- **Sous-titres en haut** (~25 % de la hauteur), 1–3 mots, Inter Bold, **1 mot en couleur**.
- Mot géant en capitales (Montserrat Black ou Inter Tight ExtraBold) sur les mots forts.
- Avatar détouré, **contour blanc épais + fine ombre portée** (effet sticker), **une pose par phrase**,
  taille/position qui changent (plein pied, buste, tête seule, gauche/droite). Jamais la même pose 2 fois de suite.
- Cartes **néo-brutalistes** : cadre noir 3 px + ombre décalée dure, étiquette rouge au-dessus.
  Outil cité = vrai logo (`outils/logo.py`). Fenêtres code/navigateur, champ commentaire, chiffres.
- Rythme : **1 changement / 1,5 s**. Fin : écran rouge plein « ABONNE-TOI » + CTA « commente MOT ».
- Son : -14 LUFS, musique 12–25 dB sous la voix, pop à chaque apparition de pose/carte (`podcast/son.py`).

## 3. Banque de poses (générée une fois, complétée au fil des vidéos)

- Avatar maître validé par Mariuse : `assets/avatar/maitre.png` (3D Pixar, grosse tête, grands yeux,
  corps entier, t-shirt noir logo KAMTECH, jean, baskets blanches, fond crème uni).
- Poses : `assets/avatar/poses/NOM.png` (détourées, PNG transparent). Liste et prompts :
  `python3 outils/avatar_cloudflare.py poses`.
- **Générateur par défaut : Cloudflare Workers AI** (`outils/avatar_cloudflare.py`, FLUX.2 klein 9B,
  variables `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`). **Gratuit** : 10 000 neurons/jour
  (remise à zéro 00:00 UTC), au-delà la requête est refusée, jamais facturée.
  klein-9b ≈ 1 400 neurons/image (1 réf.) à ~1 500 (3–4 réf.) → **6 à 7 images/jour** ;
  klein-4b ≈ 170 neurons → ~55/jour mais moins fidèle (brouillons). Consommation réelle lue dans
  l'en-tête `cf-ai-neurons` et notée dans `assets/avatar/depenses.csv`.
- **Réutiliser avant de générer.** Une pose manque → la générer depuis le maître :
  `python3 outils/avatar_cloudflare.py pose NOM sortie.png [klein-9b|klein-4b]`, la regarder (mains, logo,
  visage identique au maître), puis la détourer et la ranger dans `poses/`. Banque complète (14 poses)
  = 2 à 3 jours de quota gratuit : étaler, ne pas payer.
- Secours payant uniquement si Mariuse l'accepte : `outils/avatar_gemini.py` (Google, aucun quota
  gratuit, ≈ 0,034 $/image, facturation à activer dans AI Studio).
- Images de référence : redimensionnées sous 512x512 et envoyées en multipart (`input_image_0..3`).
- Photos de Mariuse : envoyées directement dans la requête (Cloudflare ou Google), **jamais** sur un hébergeur public, jamais commitées.

## 4. Fabrication (pipeline maison HTML → Playwright → ffmpeg, cf. `podcast/`)

1. Découper la voix en phrases (temps par mot) → une ligne de timeline par phrase : pose, position,
   mot géant / carte / logo, mot en couleur du sous-titre.
2. Prévisualiser toutes les compositions en planche contact AVANT le rendu.
3. Rendu render(t) déterministe, mix son, loudnorm -14 LUFS.
4. Checklist anti-slop de montage-pro §4, puis entrée dans `montage-pro/references/journal.md`,
   commit + push.
