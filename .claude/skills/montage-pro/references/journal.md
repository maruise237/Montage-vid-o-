# Journal des projets

Une entrée par projet : ce qui a été livré, le retour de Mariuse, la leçon. Les plus récents en haut.

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
