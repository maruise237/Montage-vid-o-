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

## 2026-10 — Reel « ChatGPT / KamForms » rallongé (7,5 s → 10,5 s)
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

## 2026-10 — Reel Djoumi « 3 meilleures applis pour un salon de beauté » (22 s)
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

## 2026-10 — Légendes et hashtags par plateforme (5 vidéos)
- Livré : `publications/legendes.html` (page avec bouton copier, compteurs de caractères et de hashtags).
- Règles 2026 vérifiées sur le web (4 oct. 2026) :
  - Instagram : **5 hashtags max** (limite imposée depuis déc. 2025), dans la légende, CTA en 1re ligne (~125 car. visibles).
  - TikTok : la légende est lue par la recherche → mots-clés que les gens tapent ; 3–5 hashtags précis, pas #fyp.
  - YouTube Shorts : titre 60–80 car. sans hashtag ; 3–5 hashtags en fin de description dont #shorts
    (les 3 premiers s'affichent au-dessus du titre) ; liens de description NON cliquables → « vidéo associée ».
- Chaque légende reprend le CTA « commente MOT » de la vidéo (ou en ajoute un) ; vérifier dans la timeline que
  ce qu'on annonce est bien dans la version publiée (ex. la réponse r2 est dans la version courte du podcast).

## Pubs NGUELEK PRINT (imprimerie / gadgets, Yaoundé-Messassi) — 2 pubs de 1 min+ à partir de 32 reels Facebook
- Livré : `boutique/livrables/` → pub1 « L'atelier » (73 s, services, sans voix sauf extrait porte-stylos 2 000 F) et
  pub2 « Cadeaux » (65 s, portée par la voix du patron), + versions 720p WhatsApp + légendes.
- Pipeline réutilisable : `boutique/moteur.py` (plans ffmpeg : mode plein avec zoom/position, mode « tirage photo » sur
  fond flouté pour les sources basse déf ou paysage) + `calque.html` (titres, chapitres numérotés, sous-titres, balayage
  CMJN, logo animé en calques, écran de fin) + `son_commun.py` (musique afro-house / douce synthétisée, demucs, -14 LUFS).
- Logo client découpé en calques par couleur (`boutique/logo/calques.py`) → animation N, P, 4 vagues CMJN, texte, anneau.
- Leçons : téléchargement Facebook OK avec `yt-dlp` ; quota ElevenLabs épuisé → faster-whisper `small` (passer un tableau
  numpy, PyAV incompatible) ; recadrer pour retirer les numéros incrustés dans les sources ; l'identité CMJN du logo sert
  de transition (balayage 4 bandes) = DA propre à la marque, pas un effet générique ; ne jamais réutiliser les chansons
  des sources (droits) : seules les voix sont gardées.

### Retour de Mariuse sur les pubs NGUELEK (v1) → v2
- Retour 1 : « les bruitages, effets d'apparition, tchou-tchou… trop génériques, on détecte que c'est monté par
  Claude ». Cause : bruitages SYNTHÉTISÉS (sinus/bruit blanc), un son sur chaque élément, placement mécanique,
  musique synthétisée. → Règle 12 + §2ter du SKILL ; `boutique/son_reel.py` : son direct des machines (v07 CNC,
  v12 brodeuse, v15 laser, v04/v11 UV, v09 pose), vraie musique Mixkit (« Let's Play Africa » pub 1,
  « Feeling Happy » pub 2) montée sur ses temps avec sa vraie fin, bruitages enregistrés (papier, imprimante
  matricielle, frappe, interrupteur, clés, déclencheurs photo), rares et variés.
- Retour 2 : « tu as mal coupé la voix du boss, petits décalages ». Causes : fins de mots de whisper trop tôt
  (« cuisine », « problème », « continent », « désirez » tronqués), coupe qui mordait le mot suivant, plans pas au
  nombre exact d'images (dérive ±0,13 s), plan source plus court que prévu. → `affiner()` sur l'énergie,
  `-frames:v`, `tpad` ; contrôle par retranscription de la bande son finale. La règle « coupe sur l'énergie »
  existait déjà dans la fiche transcription mais n'était pas appliquée : elle est maintenant dans le code.

## Pub 3 NGUELEK « Tu commandes, on fabrique » (1 min 50) — voix et musique via treg
- Demande : version complètement différente, voix adaptée avec plus d'énergie, 2 min max, « surprends-moi ».
- Concept : animateur (voix) passe 9 commandes → vraie machine → tampon rouge « C'EST FAIT » (réponses d'une 2e voix)
  → bon de commande imprimé ligne par ligne ; finale enseigne lumineuse ; fin = ticket complet + WhatsApp.
  DA propre : Anton + police machine (ticket thermique dentelé) + encre rouge (texture de grain), pas de CMJN.
- treg (solde ~0,58 $, dépensé ~0,15 $) :
  - Voix : `google-ai.voice-gen.gemini-3-8-flash-tts` (~0,002 $/7 s). Fenrir (animateur) et Laomedeia (réponses)
    = les plus vivantes (≈ 5,6 demi-tons d'écart de hauteur, 11 dB de dynamique, mesurés). **La consigne de style est
    LUE à voix haute** (en français comme en anglais ; `systemInstruction` refusé) → la garder (elle rend la voix
    plus expressive) puis la couper au mot près (whisper word timestamps + silence). Écrire les noms en phonétique
    (« Mé-ssa-ssi »). Un « Fait ! » isolé est ambigu (« Fe ») → réponses de 3 mots minimum.
  - Musique : `google-ai.music-gen.lyria-3-5` (0,08 $ le morceau de ~2 min, MP3). Demander « instrumental only », le
    BPM, des sections et « a clear final hit and a dead stop, no fade out » : respecté (118 BPM, fin franche).
    Vérifier quand même : demucs (pas de chant) + grille des mesures (librosa, phase des 1ers temps par le kick).
  - Les réponses audio arrivent en base64 trop gros pour la conversation : Claude Code les sauvegarde dans
    `tool-results/*.txt` → `pub3/extraire.py` décode en WAV/MP3.
- Montage : timeline construite sur les MESURES (question au 1er temps, tampon sur la mesure suivante, 3 mesures par
  commande), 4 mesures retirées au milieu de la musique pour que son coup final tombe sur la fin de la vidéo,
  silence de 0,45 s avant le grand « C'EST FAIT ! » + petite foule enregistrée.
- Piège : `mask-image: url(fichier.png)` est bloqué par Chromium en file:// (CORS) → le tampon était invisible.
  Mettre les textures de masque en data URI.
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
