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

## 2026-10 — Mème « Jerry a choisi son parfum » → KamForms vs Google Forms
- Brief : reprendre un mème viral (Jerry hésite entre deux flacons Acqua di Giò puis en serre un dans
  ses bras) et remplacer les produits par les logos Google Forms et KamForms, nom écrit dessous.
  « Pour la suite, surprends-moi. » Mariuse a demandé en cours de route d'enlever le petit logo du
  compte d'origine en haut à gauche.
- Fait (`meme_jerry/montage.py` → `meme_jerry/meme_kamforms_jerry.mp4`, 7 s, -13,3 LUFS) :
  - Plan fixe → fond propre = médiane temporelle + interpolation ligne par ligne à travers les flacons
    et le filigrane ; ombres au sol refaites depuis une ligne propre décalée (sinon la médiane reprend
    les pieds de Jerry → traînée orange).
  - Jerry détouré par couleur (R−B > 55, + contour noir dans un voisinage, + trous bouchés), pas besoin
    de RVM pour un dessin animé sur fond gris.
  - **KamForms à GAUCHE parce que Jerry choisit le flacon de gauche** : regarder la fin du mème avant
    de placer les marques.
  - Logos debout sur la table : ombre de contact, reflet sur la table vernie, nom en Inter Tight dessous.
  - Surprise : légende qui reprend la légende d'origine (« Jerry a choisi son outil de formulaires. »)
    + « *Et toi ?* » en serif italique et un cœur qui pop sur KamForms au moment du choix (6,2 s), avec un pop sonore.
- Leçon : `outils/logo.py "Google Forms"` renvoie le favicon Google (faux) → logo pris sur Wikimedia
  (`Google_Forms_2020_Logo.svg`), rangé dans `assets/logos/googleforms.png`. Toujours regarder le PNG.

## 2026-10 — Série de 6 mèmes marketing KamForms
- Brief : « cherche des vidéos de mème, plusieurs variantes, fais-moi des mèmes marketing viraux pour
  KamForms, surprends-moi ».
- Source des clips : **YouTube bloqué depuis le conteneur** (403 / « confirm you're not a bot », tous
  les player_client essayés). **Tenor marche** : page `tenor.com/search/<mots>-gifs`, puis remplacer le
  suffixe d'ID par `AAAPo` pour avoir le MP4 (≈ 500–640 px, sans son). Toujours regarder les images :
  beaucoup ont du texte incrusté ou un filigrane → choisir les versions propres ou recadrer.
- Livré (`memes/memes.py` → `memes/meme_kamforms_*.mp4`, 5,5–6,5 s, ≈ -13,5 LUFS) :
  Drake (Google Forms non / KamForms dans les groupes WhatsApp oui), Leonardo DiCaprio qui pointe,
  Panik → Kalm (le client veut un formulaire pour ce soir → l'IA de KamForms crée les questions),
  supporter de cricket déçu (« Réponses : 3 »), Bernie (« je vous demande encore une fois de remplir
  mon formulaire » dans le groupe de la famille), The Rock sourcil levé.
- Format « page mème » : légende noire alignée à gauche sur fond blanc, mème pleine largeur, signature
  logo + kamforms.com ; bloc centré verticalement (mesuré sur la dernière image). Les arguments viennent
  du site (WhatsApp, réponses en privé, l'IA crée les questions), rien d'inventé.
- Son : boucle synthétisée + pops. Conseil donné : en publiant, mettre un son tendance de l'appli.
- Leçon Drake : le clip Tenor « hotline bling » est la danse, pas les deux poses du mème ; Drake refuse
  à gauche du cadre (0,8–1,1 s) et sourit à droite (2,2–2,6 s) → recadrages différents par case.
- Retour de Mariuse sur le mème Jerry : « à la fin, quand Jerry saute, une version de lui reste sur
  place ». Cause : fond propre = médiane temporelle, or Jerry est au centre presque tout le temps →
  il s'imprime dans le fond. Correction : au centre, médiane des seules images où le pixel n'est pas
  couvert par Jerry (masque élargi de 10 px, `np.nanmedian`). **Règle : un fond propre par médiane
  n'est valable que si le sujet bouge beaucoup ; sinon exclure ses pixels avant la médiane.**

## 2026-10 — 10 pubs KamForms tirées des hooks de @theo.vizuals
- Brief : prendre les 10 reels les plus vus de @theo.vizuals (compte qui classe les hooks viraux),
  extraire les hooks, faire 10 vidéos publicitaires KamForms.
- Récupération : `vidiq_ig_profile_reels` (12 reels max, vues incluses, 5 crédits) pour le classement ;
  vidéos via treg `tikhub.x.instagram-v1-fetch-post-by-url` (0,001 $ l'appel, champ `video_url`) —
  yt-dlp sur instagram.com renvoie 429. Réponse JSON énorme → déléguer les appels à un sous-agent.
- Theo ne fait que nommer des hooks sur des extraits d'autres créateurs → on reprend les MÉCANIQUES
  (anticipation, visuel, stitch, danger, stress, illusion, avant/après, question, valeur, coulisses),
  pas les images. Relevé dans `pubs_hooks/hooks_theo.md`.
- Livré : `pubs_hooks/pubs.py` → `pubs_hooks/pub_kamforms_01…10_*.mp4` (10–12 s, motion design, sans voix).
  Chaque pub : hook 2–4 s → vraie démo du téléphone kamforms.com (`kamforms2/tel`, cycle 7,6–17,0 s,
  vitesse adaptée à la durée) → carte de fin commune (logo, « La *façon simple* de créer des
  formulaires. » comme sur le site, pastille kamforms.com, « 10 formulaires gratuits · Réponses illimitées »).
- DA KamForms mesurée sur le site : vert **#0F6F3C**, ciel (129,189,217) → crème, serif Instrument.
- Illusion : le gros plan ne doit pas montrer l'en-tête « Nouveau formulaire » (ça casse la surprise)
  → bandeau crème opaque au-dessus et centre du zoom calé pour que l'en-tête passe dessous.
- Piège PIL : une taille de police animée qui part de 0 plante (`font size must be > 0`) → ne rien
  dessiner tant que l'échelle < 0,02.
- **Retours de Mariuse sur la v1 (2 corrections importantes)** :
  1. « Tu devais utiliser ces hooks avec une bonne transition vers le contenu de KamForms » → il voulait
     les VRAIS extraits viraux en ouverture (pratique courante, Theo fait pareil), pas seulement la mécanique.
     v3 : `pubs_hooks/pubs_v2.py` (extraction des passages + transitions) + `pubs_v3.py` (contenu) →
     `pubs_hooks/v3/pub_kamforms_hookNN_*.mp4`. Transition calée sur l'action de l'extrait : flash + secousse
     sur un impact (immeuble, collision, pastèque), whip sur un mouvement (mât, train), zoom avant
     (enclos, rivière), carte qui s'envole (illusion, avant/après), glitch (hamac). Le passage de Theo
     « THIS is a … hook » est toujours exclu ; une légende incrustée dans l'extrait se cache sous la nôtre.
  2. **KamForms n'est PAS un outil de commandes WhatsApp.** C'est un outil de formulaires pour tout
     (inscriptions, événements, formations, avis, dons, sondages, institutions), créé depuis le téléphone.
     Sa seule vraie différence : **les réponses arrivent sur WhatsApp** (option « Redirection WhatsApp » :
     le répondant arrive sur ton WhatsApp avec ses réponses) **+ notification push** pour qui a l'appli.
     Pas d'appli ni de compte pour répondre, import de Google Forms, export CSV, 10 formulaires gratuits.
     → Les « commandes » ne sont qu'UN exemple (celui des captures du site), jamais le message principal.
- Vraies captures de l'appli téléchargées depuis kamforms.com (`pubs_hooks/site/` : création IA, détail
  d'un formulaire avec « Redirection WhatsApp », réponse avec « Répondre sur WhatsApp », boîte de réception,
  import Google Forms, statistiques, 4 mascottes d'usages). Pour lister les images d'un site : Playwright
  + `document.querySelectorAll('img')` (les sections « apparaissent au défilement » sont vides en capture
  pleine page → défiler par pas de 700 px avec 1,6 s d'attente, ou télécharger les images directement).

## 2026-10 — Pub motion design « KamForms disponible sur APKPure » (46 s)
- Demande : annoncer que l'appli Android KamForms est publiée et vérifiée sur APKPure (« Apple » dans la dictée
  vocale = **APKPure**), avec captures, clics, bruitages, voix off Fish Audio, « surprends-moi ».
- Type (§0) : **pub / motion design** → typo animée, couleurs de la marque, la voix dicte le rythme, pas de sous-titres
  continus (le titre cinétique de chaque scène EST le sous-titre).
- Sources :
  - APKPure : `apkpure.com/p/…` renvoie le défi Cloudflare (curl ET Chromium headless) ; **`apkpure.com/<nom>/<paquet>`
    passe** (curl avec UA mobile, Playwright avec proxy). Captures du store en 1080x1920 sur `image.winudf.com/…/screen-N.jpg`
    **avec `?fakeurl=1&type=.jpg`** (sans ces paramètres → 404). Capture de la page en ×3 → en-tête + carte « Security Check
    Completed / No Virus / VERIFIED by APKPURE » = la preuve à montrer.
  - Les 8 visuels du store ont déjà des titres : on les **découpe en calques** (`prep.py` : téléphone, bulle de lien,
    notification, carte WhatsApp…) et on remet NOTRE typo par-dessus, fond = couleur échantillonnée + grille CSS,
    bords des découpes en fondu (`mask-image`).
- Voix : Fish Audio direct = 0 crédit API (402). **Passer par treg `fishaudio.tts.s2-1-pro`** (`call_media`, fichier
  sauvé dans tool-results) : ~0,013 $ pour tout le script. Voix « africain » `b4d249c2468940f791068ffbc3fe446b`
  (claire, persuasive, faite pour la pub), `prosody.speed 1.1`, une requête par phrase, même voix. Horodatage des mots :
  faster-whisper `small` sur chaque phrase.
- Moteur (`animation.html`) : x/y des animations = **décalages** autour de `def.x/def.y` (base). Pièges vus :
  - un `div` absolu sans largeur est limité à 1080 px → une capture plus large est rognée : `.crop{width:max-content}` ;
  - une animation de sortie `s:[1,…]` impose s=1 AVANT de démarrer → partir de l'échelle réelle de l'élément ;
  - les bruitages sont émis par l'animation (`son(t,'clic')`) → `sons.json` → `son.py` : chaque bruit colle à un geste.
- Ponctuation : pad seul sous le hook, riser, **drop** sur « Le principe est simple », musique **coupée 0,3 s** avant
  « GRATUIT » + boom + tremblement, carillon sur la carte finale.
- Fichiers : `kamforms3/` (`prep.py`, `construire.py`, `animation.html`, `rendu.mjs`, `son.py`, `finir.sh`)
  → `reel_kamforms_apkpure.mp4` (+ `_partage`).
