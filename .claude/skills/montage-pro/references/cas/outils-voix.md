# Essais d'outils de voix

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## 2026-10 — Test de clonage de voix locale (VoiceStudio / OmniVoice)
- Test seulement, pas de vidéo. Clone de la voix de Mariuse (enregistrement de 72 s, avec son accord dit dans
  l'enregistrement) → monologue de 63 s. Retranscription du rendu presque mot pour mot.
- Retour de Mariuse : « sur le chemin » mais pas encore sa voix, accent « belge / anglais qui parle français ».
  Pas besoin de sa voix pour l'instant ; rassuré que ça marche.
- Technique : `outils/voix_omnivoice.py`. CPU seul ≈ 4 min pour 15 s d'audio. Référence = 10–20 s max
  (au-delà le modèle coupe) + transcription exacte OBLIGATOIRE (sinon il faut un modèle ASR en plus).
  `torchaudio.save` exige torchcodec → sauvegarde avec soundfile. Transcrire la référence avec
  faster-whisper `large-v3-turbo` (le `small` a massacré l'accent camerounais + bruit de fond).
- Leçon : choisir le passage de référence le plus propre (ici 14–30 s), pas le début de l'enregistrement.
- Piste : voix Claude de secours sans crédits ElevenLabs (Brian) → mode « voice design » d'OmniVoice
  (`instruct=`), à tester avant le prochain podcast.
