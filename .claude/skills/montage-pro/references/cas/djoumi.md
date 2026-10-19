# Reel Djoumi (salons de beauté)

**Situation** : Appli de réservation pour salons de beauté. Facecam « liste de 3 outils » + pub motion officielle de la marque fournie.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## Reel Djoumi « 3 meilleures applis pour un salon de beauté » (22 s)
- Prise 22,9 s : ChatGPT (images de pub) → Google Flow (animer) → **Djoumi** (réservations, relances, lien
  personnel dans la bio). Mariuse a fourni la pub motion officielle de Djoumi (29 s, vraies interfaces).
- Même recette que le reel KamForms : liste, l'outil de Mariuse en dernier, écrans partagés identiques.
- **Réutiliser une vidéo motion de la marque** : planche 1 image/s pour lire ses sous-titres incrustés, puis
  associer chaque phrase de la voix à SON passage (tableau de bord ↔ « gérer ta réservation », rappel WhatsApp ↔
  « relances », carte du lien ↔ « un lien personnel », bios ↔ « TikTok, Facebook, Instagram », parcours
  cliente ↔ « prennent rendez-vous »). Recadrer sous les sous-titres incrustés (y > 360 sur 1920), accélérer
  le passage pour qu'il tienne dans la phrase, serrer (×1,3) quand l'élément est petit (carte du lien).
- Couleur de marque Djoumi : **#C70136** (theme-color du site) ; logo = `djoumi.com/icon.svg` recoloré blanc
  sur pastille rouge (`assets/logos/djoumi.png`). Google Flow : pas de logo propre → visuel officiel og-image.
- Ponctuation : musique coupée sur « et ensuite le tout dernier outil », riser, impact + écran rouge plein
  sur « Djoumi », la musique repart.
- Erreurs évitées / vues :
  - whisper avait sauté « à utiliser » (il étirait « si » sur 1,3 s) → si un mot dure > 0,8 s, réécouter.
  - un whoosh sur la 1re syllabe masque le mot (« Chat-GPT ») → whoosh fini AVANT le mot (t − 0,40).
  - transcrire aussi la SOURCE au même endroit pour savoir si un mot manque à cause de la coupe ou de whisper.
- Fichiers : `djoumi/montage.py`, `djoumi/son.py`, `djoumi/finir.sh` → `reel_djoumi.mp4`.
