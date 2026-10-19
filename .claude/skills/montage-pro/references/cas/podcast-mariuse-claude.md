# Podcast « Mariuse × Claude »

**Situation** : Contenu perso de Mariuse (chaîne IA en français). Podcast facecam tourné sous un seul angle + réponses de Claude en motion design. Réseaux : Reels/TikTok/Shorts.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## Podcast « Mariuse × Claude » (versions 2 min 05 et 1 min 30)
- Livré : `podcast_claude_partage.mp4`, `podcast_claude_court_partage.mp4` (pipeline `podcast/`).
- Retour : « travail impeccable ». Erreur : j'ai dit « depuis Douala », Mariuse vit à **Yaoundé**.
- Leçons : vérifier les faits personnels avant la voix off ; Mariuse confond parfois temps de rendu et durée
  → toujours annoncer la durée finale de la vidéo clairement ; voix Claude = Brian (ElevenLabs), Antoine
  indisponible sur le plan gratuit.

## Podcast « Mariuse × Claude » remonté avec la compétence (versions courte et longue)
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
