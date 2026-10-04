# Journal des projets

Une entrée par projet : ce qui a été livré, le retour de Mariuse, la leçon. Les plus récents en haut.

---

## 2026-10 — Podcast « Mariuse × Claude » remonté avec la compétence (versions courte et longue)
- Demande : « refais le podcast avec ta nouvelle compétence », puis « fais les deux versions ».
- Type identifié (§0) : podcast. Choix : Mariuse en image NATURELLE + multicam simulé + sous-titres sous le
  menton ; texte derrière seulement 4 fois (PODCAST, RÉVOLUTION, KAMTECH, T'ABONNER) ; Claude (personne
  à l'écran) = motion design typo, une composition par phrase, alternance nuit / papier crème, preuves
  réelles (transcription au mot près, forme d'onde avec les hésitations coupées, vrai code du montage,
  10 vraies images + cadre de sélection), vrai logo Claude (étiquette « Claude répond » + pop sur « Opus 5.5 »).
- Son (§2bis) : hook sec + riser → musique à la 1re coupe, musique mesurée à 17 dB sous la voix, musique
  COUPÉE pendant « je ne peux pas entendre le son », bruitages seulement sur actions visibles (88 en 90 s),
  rien sur les coupes multicam. -14,2 LUFS.
- Faits : « depuis Douala » coupé dans la voix de Claude (crédits ElevenLabs épuisés → coupe au mot près,
  vérifiée par retranscription : « Expliquer l'IA en français, avec des exemples concrets »).
- CTA : Mariuse dit « abonnez-vous, likez, partagez » ; ajout à l'écran d'un champ commentaire qui se tape
  (« la tâche que tu vas confier à l'IA ») : pas de promesse de ressource qui n'existe pas.
- Fichiers : `podcast/pro.py` (image), `podcast/son_pro.py` (son), `podcast/finir_pro.sh`,
  `outils/bruitages.py` (bruitages réutilisables) → `podcast_claude_court_pro.mp4`, `podcast_claude_pro.mp4`.
- Corrigé après la 1re planche : (1) cartes vides 0,3–0,6 s en attendant le 1er mot déclencheur → le 1er
  élément apparaît dès la coupe ; (2) sous-titres blancs gras sur les cartes typo = doublon criard →
  sous-titres discrets (plus petits, couleur douce) quand le texte géant porte déjà la phrase.
- Leçons : sur une carte typo, ne jamais laisser l'écran vide ; prévisualiser toutes les cartes en planche
  AVANT le rendu complet (fait : a évité des chevauchements de lignes et une pellicule qui débordait).

---

## 2026-10 — Retours de Mariuse : contexte, logos, assombrissement, son, abonnés
- « Toutes les techniques ne vont pas sur toutes les vidéos » → §0 du skill : tableau type de vidéo →
  techniques à utiliser / à éviter, conditions par technique.
- « Pas d'usine à gaz pour la zone Instagram » → règle simplifiée (sous le menton), outil optionnel.
- « L'assombrissement se voit, on voit le détourage » → `FOND` 0,30 → 0,45, flou 5 → 3. Démo re-rendue.
- « Quand je cite un outil, mettre son VRAI logo » → `outils/logo.py` (Wikimedia → Simple Icons → favicon,
  cache `assets/logos/`, `coller()` pour le pop). 1er essai : Instagram renvoyait un logo Instagram+Threads
  → filtrage des titres resserré. Leçon : toujours regarder le logo téléchargé.
- « Tu n'as rien appris sur les bruitages, la musique, les abonnés » : juste, je n'avais analysé que l'image.
  Fait : séparation demucs des 14 vidéos + spectrogrammes → §2bis (deux ouvertures selon le type,
  ponctuation musicale, bruitages sur actions visibles) et stratégie abonnés chiffrée (§3).
- Leçon : analyser une inspiration = image + **son** + **CTA/légende**, pas seulement l'image.

---

## 2026-10 — 6 nouvelles inspirations (Fabien Faro, Toprak, Mickaël Wu)
- Livré : créateurs C–E dans `inspirations.md` (14 vidéos au total), règle 11 (look pro au tournage),
  `outils/zone_securite.py`.
- Découverte : Faro (144 k likes) n'a qu'une caméra, comme Mariuse. Il fait ses gros plans en
  **marchant vers son grand-angle**, ce qui confirme la piste des micro-zooms et donne une option au tournage.
- **Erreur trouvée sur notre démo** grâce à l'astuce de Toprak : sous-titres à y = 1480 (77 %) = dans la
  zone des boutons Instagram. Corrigé à y = 1300 (sous le menton), démo re-rendue et vérifiée.
- Outil : quota ElevenLabs épuisé en cours d'analyse (7 crédits restants) → faster-whisper local en secours.
- Leçon : passer la vérification de zone de sécurité sur CHAQUE rendu, pas seulement le contenu.

---

## 2026-10 — Texte derrière la personne (détourage vidéo)
- Retour de Mariuse : « on a déjà fait du détourage, ne te limite pas, essaie plusieurs façons ».
  J'avais écrit « pas encore construit » alors que la pub Valex v2 avait un portrait détouré. Erreur d'oubli.
- Banc d'essai sur la facecam du podcast (fond tissu à motifs, le pire cas) :
  - rembg u2net_human_seg : perd la personne sur certaines images. ✗
  - rembg isnet-general-use : garde parfois seulement le visage. ✗
  - mediapipe selfie multiclass : masque flou, laisse passer le tissu (besoin de `apt install libegl1`). ✗
  - BiRefNet portrait : très propre mais 30 s/image et saturation mémoire au 2e passage. ✗
  - **RVM resnet50 (ONNX) : propre, cheveux OK, 0,1 s/image, stable dans le temps. ✓ retenu**
  - RVM mobilenet : 0,05 s/image, pour les longues vidéos.
- Livré : `outils/detourage.py`, `outils/demo_derriere.py`, `demo_texte_derriere.mp4` (10,7 s, hook du podcast).
- Leçon : relire le journal AVANT de dire qu'une technique manque, et tester plusieurs outils.
- Retour suivant de Mariuse : la vidéo est tournée sous un seul angle → simuler les changements de caméra
  par micro-zooms. Fait : 3 caméras virtuelles (large/serré/gros plan), 7 plans en 10,7 s, coupes sur les
  phrases, titre recalé sur la tête à chaque plan.

---

## 2026-10 — Analyse de 8 vidéos d'inspiration (MedTheDesigner, Loucash)
- Livré : ce skill + `inspirations.md`.
- Demande de Mariuse : des vidéos comme les vrais pros, pas du slop IA ; une compétence qui grandit.
- **Autocritique de nos vidéos passées face à ces références** :
  - Podcast Claude : layout identique pendant toutes les réponses (logo centré + titre + fenêtre de code)
    → trop « gabarit ». Les pros changent de composition à chaque idée.
  - Sous-titres karaoké jaune/corail mot par mot → plus « app auto-sous-titres » que « créateur ».
    Les pros : 1–3 mots blancs propres, emphase par la taille ou l'italique serif.
  - Une seule police (Poppins) → pas de contraste typographique. Il faut un duo sans serré + serif italique.
  - Aucun plan clair : tout était sombre. Il manque l'alternance sombre/clair.
  - Icônes SVG génériques → remplacer par de vraies captures, des logos réels, ou une DA d'illustration unique.
  - Ce qui était bien : rythme des coupes, logo qui réagit à la voix, mix à -14 LUFS, hook placé en tête.
- À construire : détourage de la personne (texte derrière le sujet), kit de polices, cercle loupe sur captures,
  composant CTA « dossier + MOT ».

## 2026-10 — Podcast « Mariuse × Claude » (versions 2 min 05 et 1 min 30)
- Livré : `podcast_claude_partage.mp4`, `podcast_claude_court_partage.mp4` (pipeline `podcast/`).
- Retour : « travail impeccable ». Erreur : j'ai dit « depuis Douala », Mariuse vit à **Yaoundé**.
- Leçons : vérifier les faits personnels avant la voix off ; Mariuse confond parfois temps de rendu et durée
  → toujours annoncer la durée finale de la vidéo clairement ; voix Claude = Brian (ElevenLabs), Antoine
  indisponible sur le plan gratuit.

## 2026-10 — Pub motion design « Valex L'infographiste » (v1 sans voix, v2 voix off)
- Livré : `valex_motion_design.mp4`, `valex_pub_voix*.mp4`.
- Leçon : la voix off fournie dicte le rythme ; caler les animations sur les timestamps des mots.

## 2026-10 — Reel « 3 outils IA » qui met KamForms en avant (sans faire pub)
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
