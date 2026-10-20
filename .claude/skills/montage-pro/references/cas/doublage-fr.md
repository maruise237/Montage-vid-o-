# Doublage FR d'un reel anglais

**Situation** : traduire voix off et textes à l'écran d'un reel motion design sans personne filmée.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## 2026-10 — Doublage FR d'un reel anglais (motion design « Dots vs Muse vs Grok Bot », 50 s)
- Demande : « je veux cette vidéo en français » : voix off FR + tous les textes à l'écran traduits « en temps réel ».
- Livré : `reel_doublage_fr.mp4` (1080x1920, 60 i/s) + `reel_doublage_fr_partage.mp4`. Pipeline : `doublage/`.
- Méthode (réutilisable pour tout reel motion design sans personne à l'écran) :
  1. `yt-dlp` → `demucs --two-stems=vocals` : on garde `no_vocals` (musique + bruitages d'origine), vérifié sans
     anglais résiduel (whisper sur la piste musique à +15 dB → rien).
  2. Transcription faster-whisper `small.en` (horodatage des mots) → script FR en **morceaux ancrés** sur le mot
     anglais correspondant (`script_fr.py`) : le visuel de chaque mot clé arrive au même moment en FR.
  3. Voix : ElevenLabs à sec (1 crédit) → **Edge TTS `fr-FR-RemyMultilingualNeural`** (gratuit, horodatage des
     mots ; patch `certifi.where` vers le CA du proxy). Une vitesse par phrase (max ×1,18), jamais par morceau
     (sinon voix hachée) ; pauses ajoutées aux virgules quand on est en avance. Écrire « I.A. » pour que le TTS
     épelle (« IA » est lu « ya »). Le texte FR doit être **plus court** que l'anglais (~15 %) : réécrire, pas accélérer.
  4. Textes à l'écran (`elements.py` + `doubler.py`) : effacement = écart à un **fond médian** (k = 61, ou 13–31
     pour les petits textes / pastilles) puis remplissage par ce fond ; la taille de police FR est **calibrée sur la
     largeur du texte anglais**, alignement sur la **ligne de base** anglaise, opacité = contraste mesuré (suit les
     fondus), couleur échantillonnée (suit les surlignages), « frappe » révélée selon la largeur tapée. Position de
     référence = **médiane** des boîtes (sinon on prend une image au milieu de l'animation d'entrée → texte trop bas).
  5. Rangées de puces (« Bookings… ») : on efface les puces (interpolation verticale du fond) et on **redessine des
     puces à la taille du mot FR** avec la couleur échantillonnée image par image (la puce bleue active suit).
  6. Sous-titres : bande effacée entièrement, sous-titres FR redessinés sur la voix FR (mots clés en dégradé arc-en-ciel
     / bleu / orange comme l'original).
- Pièges : `pkill -f motif` tue aussi le shell qui le lance ; les polices Instrument Serif + Inter collent au style
  « éditorial » de ces reels ; les petits statuts (THINKING/WORKING ~10 px) et les textes DANS les vidéos filmées
  sont laissés en anglais.
- Droits : la vidéo est de @sanjai.builds ; doubler pour un test OK, mais pour publier il faut l'accord / créditer
  et avoir SON propre guide derrière « Commente AGENT ».
