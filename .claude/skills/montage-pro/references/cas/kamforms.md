# Reels KamForms (outil de Mariuse)

**Situation** : Promouvoir le propre SaaS de Mariuse sans faire pub, sur une facecam courte. Public : créateurs / petits business.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## Reel « 3 outils IA » qui met KamForms en avant (sans faire pub)
- Brief : mettre kamforms.com (outil de Mariuse) en avant « sans avoir l'air d'une vidéo publicitaire,
  grâce à la preuve sociale ». Source : facecam 1728x3072, 16,5 s, 3 phrases « si tu veux faire de la
  génération de vidéos / photos / formulaires, utilise ça » + « les liens sont en description, commente l'outil ».
- Type (§0) : tuto outil / liste. Choix faits :
  - **Preuve sociale par association** : KamForms est le 3e d'une liste avec KlingAI et Nano Banana (Google),
    **même format d'écran, même durée**, vraie capture du site, vrai logo. Il ne se distingue que parce
    qu'il est en dernier (place de la chute) et dans le CTA (le champ commentaire tape « KamForms »).
  - Aucun « mon outil », aucun chiffre ni témoignage inventé (le site n'affiche pas de stats réelles).
  - Silences coupés : 16,5 s → 11,5 s. Écrans décalés des coupes audio (l'outil apparaît sur « utilise ça »
    et reste jusqu'au « génération de » suivant) : coupes image ≠ coupes son, ça fait monté à la main.
  - Texte derrière la tête **sur le hook seulement** (« VIDÉOS »). Les mots des étapes 2 et 3 sont sur une
    **étiquette crème inclinée** : sur un pagne très chargé, du texte blanc flottant est illisible et on ne
    veut pas assombrir l'image à chaque étape.
  - Écran partagé crème (capture en haut, personne en bas) = ambiance claire qui alterne avec la facecam.
- Outils : captures mobiles via Playwright + proxy (`--ignore-certificate-errors`, `waitUntil: domcontentloaded`,
  8 s d'attente) ; logo Gemini recadré depuis la capture officielle (`assets/logos/geminisparkle.png`).
- Fichiers : `kamforms/montage.py` (image), `kamforms/son.py`, `kamforms/finir.sh` → `reel_kamforms.mp4`.
- À faire si Mariuse fournit de VRAIES preuves (capture du tableau de bord, messages clients) : les ajouter
  sur l'écran KamForms. Ne jamais en fabriquer.

## Reel « ChatGPT / KamForms » rallongé (7,5 s → 10,5 s)
- Prise : « ChatGPT génère des photos personnalisées. KamForms génère des formulaires interactifs
  directement sur WhatsApp. » Demande : « trouver un moyen de faire un peu durer la vidéo ».
- Transcription : whisper se trompait (« formes », « je l'ai pour mes… ») ; **Scribe sur des morceaux de 3 s**
  (≈ 1 crédit chacun) a donné la vraie phrase. Avec peu de crédits : découper l'audio, pas tout envoyer.
- **Comment rallonger sans remplissage** (règle à retenir) :
  1. couper quand même les silences (la parole doit rester nerveuse) ;
  2. ajouter une **démo réelle** après la phrase produit : l'animation du téléphone de kamforms.com, capturée
     image par image (Playwright, `page.screenshot` en boucle + horodatage), **accélérée sur les temps morts**
     (×4 pendant l'attente, ×2 pendant la frappe, ×1 sur la réponse) ;
  3. des étapes écrites à lire pendant la démo (« 1. tu décris / 2. l'IA crée / 3. tu partages ») ;
  4. la musique remonte de 6 dB quand la voix s'arrête (ponctuation), pop sur chaque bulle ;
  5. finir sur l'URL en pastille, la musique s'arrête sur un carillon.
- Hook : ChatGPT = mention rapide → logo officiel qui pop sous le sous-titre ; « PHOTOS » derrière la tête,
  assombrissement qui arrive **progressivement** avec le titre (pas avant).
- Note loudness : sur une vidéo < 10 s, `loudnorm` en un passage reste ~1 dB trop bas → viser -12,8 pour
  obtenir -14,2 (vérifier avec ebur128).
- Le site a une page « études de cas » (Amina à Abidjan, Seydou à Dakar, Chez Mado à Douala) : NE PAS
  l'utiliser comme preuve sociale en vidéo tant que Mariuse n'a pas confirmé que ce sont de vrais clients.
- Fichiers : `kamforms2/montage.py`, `kamforms2/son.py`, `kamforms2/finir.sh` → `reel_kamforms_2.mp4`.
- Retour de Mariuse : « ChatGPT » était coupé au début. Cause : je me suis fié à l'horodatage de whisper
  (0,74 s) alors que la voix démarre à 0,13 s (« Tchat-dji-pi-ti » dure ~1 s). **Leçon : le point de coupe
  d'entrée se cale sur l'ÉNERGIE du signal (RMS par 50 ms), jamais sur le premier mot de whisper**, et on
  réécoute/retranscrit les 3 premières secondes du rendu avant de livrer.

## Vidéo « KamForms est maintenant une application » (oct. 2026)
- **Erreur de départ (retour de Mariuse)** : j'avais écrit l'histoire d'une vendeuse de pagnes au marché, recopiée des
  données de démo de l'appli. Mariuse : « c'est rare qu'une femme qui vend au marché utilise Google Forms », « cherche qui
  utilise vraiment les formulaires », « je ne dois pas toujours te dire de faire les recherches web ». Il a aussi rappelé
  la vraie fonction : notification en temps réel dans l'appli à chaque réponse (même sans passer par WhatsApp), et la
  redirection WhatsApp n'est qu'une **option qu'on active ou coupe**.
- Recherche faite : Google Forms sert surtout aux enquêtes et aux **inscriptions** (formations, événements), utilisé par
  petites structures, formateurs, associations, écoles. Cible retenue avec Mariuse : **le formateur qui remplit sa
  masterclass via ses réseaux sociaux** (« sur les réseaux sociaux c'est comme ça que ça fonctionne »).
- Concept : avant (Google Forms : tableau, mails, numéros recopiés le soir, inscrits refroidis) → avec KamForms
  (notification qui sonne, WhatsApp/Appeler en un geste, option WhatsApp, import du Google Form, création en une phrase).
  Honnêteté : Google Forms envoie aussi des emails, donc on dit « dans un tableau ou dans tes mails », pas « tu ne vois rien ».
- Images : vraies prises de l'appli filmées par `kamforms_appli/filmer.mjs` (export web Expo + données de démo
  `donnees.mjs`, capture CDP 2× ≈ 20 i/s ; le screencast CDP sort en 390 px, inutilisable). Prénom du compte de démo changé
  localement dans `mobile/screenshots/mocks/clerk.tsx` le temps de l'export (non commité dans le repo kamforms).
- Son : musique étouffée (passe-bas 420 Hz) sur le problème, ~0,45 s de silence, elle tombe pleine sur « Avec KamForms »
  avec le **vrai son de notification de l'appli** ; vraie fin du morceau sur l'écran final.
- treg vide (0,04 $, estimation 0,05 $) → voix via vidIQ (ElevenLabs, 14 crédits). `alimiter` : mettre `level=disabled`,
  sinon il renormalise et le pic remonte à 0 dBFS.
- Fichiers : `kamforms_appli/` → `KamForms_appli.mp4`, `KamForms_appli_partage.mp4`.
