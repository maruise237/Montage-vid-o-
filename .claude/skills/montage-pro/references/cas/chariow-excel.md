# Pub Facebook Ads e-book Excel (Chariow)

**Situation** : pub payante pour un produit numérique vendu sur Chariow.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## 2026-10 — Pub Facebook Ads « Excel sans apprendre les formules » (e-book Chariow, 39 s)
- Demande : vidéo publicitaire dynamique avec voix off pour le produit Chariow
  `kamtech.mychariow.com/excel-sans-formules`, « tu gères tout, surprends-moi » ; puis précisé en cours de route :
  **optimisée pour Facebook Ads** (« Vango » en dictée = Facebook Ads), voix via **treg** (« Track »), bonne voix au choix.
- Retour de Mariuse : le visuel noir / bleu / rose de la fiche est son **ANCIEN logo** → ne jamais l'utiliser
  (supprimé de `dl/img`). Logo actuel : « K » dans un carré + KAMTECH, vert sapin.
- Sources : le MCP chariow ne trouve pas le produit par slug (autre boutique liée) → `curl` de la page suffit
  (texte, prix dans le JSON : `price 13,2 $` / `sale_price 4,4 $` = −67 %, 2 500 F ; images `assets.chariowcdn.com`,
  icônes de paiement `assets.orqexcdn.com/icons/methods/*.svg`). Les maquettes de téléphone du store se découpent
  automatiquement (contour noir de la moitié droite, `prep.py`).
- Charte reprise de la fiche : vert sapin #06331c, citron #c8f05a, menthe #f4f8f2 ; typo Inter Tight + Instrument Serif.
- Spécial Facebook Ads (appliqué) :
  - hook visible **dès l'image 0** (mot « Excel » + tableur en #N/A), lisible **sans le son** (chaque phrase a son titre) ;
  - tout le contenu utile entre y ≈ 400 et 1500 (`DY = 120` dans le moteur) → bandeau du haut et légende/CTA de Reels
    libres, et **recadrage 4:5 centré** (`crop=1080:1350:0:330`) pour le fil sans rien perdre ;
  - CTA d'achat (« Clique sur le bouton, télécharge-le maintenant ») au lieu de « commente MOT » (une pub payante a un bouton) ;
  - preuve concrète tirée du livre (la vraie erreur de ChatGPT 427 500 000 au lieu de 15 000) + prix barré −67 %.
- Voix treg Fish Audio « africain » `b4d2…` (persuasive, faite pour la pub) : ~0,01 $ pour tout. Pièges de prononciation
  vérifiés à whisper **medium** : « prompts » → « pondes » (dire « messages »), « tontine » → « comptine »
  (écrire « tonne-tine » + articles « le stock, la paie… »), « pour l'IA » → « polya » (éviter « l'IA » en fin de groupe).
- faster-whisper : `av.open(... metadata_errors)` plante avec la version d'av installée → décoder avec ffmpeg en
  float32 16 kHz et passer le tableau numpy (`voix/mots.py`).
- Piège moteur : un élément avec une seule animation `o:[.75,0]` est visible AVANT t0 (valeur de départ) → mettre
  d'abord `A(o,0,.01,{o:[0,0]})` (le flash rouge couvrait toute la scène 6).
- Fichiers : `chariow_excel/` (`prep.py`, `voix/mots.py`, `construire.py`, `animation.html`, `son.py`, `finir.sh`)
  → `pub_excel_sans_formules.mp4` (9:16) + `_4x5.mp4` (fil) + `_partage.mp4` (720p).
