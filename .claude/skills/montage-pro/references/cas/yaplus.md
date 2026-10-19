# Yaplus (appli « y'a plus » pour boutiques)

**Situation** : Appli de Mariuse (dépôt maruise237/Yaplus) : signaler les ruptures au patron. Aucune vidéo tournée au départ → motion design + vrais écrans + photos/vidéos réelles fournies par Mariuse. Cible qui paie : quincailleries.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

## Lancement Yaplus (57,9 s, 9:16) : style « SaaS launch » (réf. Luminovo) en motion design
- Demande : vidéo de lancement de l'appli Yaplus (dépôt maruise237/Yaplus), dans le style d'une référence motion
  design (fond bleu nuit, traits lumineux bleu/orange, cartes en verre, écrans de l'appli inclinés en 3D), voix off treg.
- Fait : `yaplus_lancement/` (lancement.html = render(t), rendu.mjs, son.py). **Vrais écrans** de l'appli capturés en
  mode démo (`/?demo=1`, Playwright 390×844 ×3, sombre ; masquer `nextjs-portal` du serveur de dev), avant/après d'un vrai
  tap (toast « KG5 ajouté à la liste »). Récit : chaos (bulles de l'équipe) → cahier illisible → groupe WhatsApp →
  conséquences → silence → logo sur le drop → tap → patron en direct → WhatsApp → hors ligne → oubliés → CTA.
- treg (~0,10 $) : narratrice Laomedeia (posée, « présentatrice de lancement ») + employé Fenrir. Musique Lyria
  « tech launch + touche afro, 100 BPM, intro tendue 16 s, riser, drop ~0:22 » : drop réel à 22,92 s (onset), on y pose
  « Y'a plus » ; 4 mesures retirées (38,94 → 48,09 s) pour que le coup final tombe juste après le CTA.
- Pièges : (1) un `<feGaussianBlur>` sur un trait SVG est **coupé net** par la boîte du filtre → `filterUnits="userSpaceOnUse"`
  avec une grande zone ; (2) un élément `#tel` sans `position:absolute` → `left:50%` ignoré, téléphone hors cadre ;
  (3) TTS criée : « Patron ! » entendu « Tintron » par 2 modèles whisper → regénéré avec « en articulant bien chaque mot ».
  Toujours retranscrire la bande finale (small + medium sur les passages douteux).

### Retour de Mariuse sur le lancement Yaplus v1
- « Tu as bien travaillé, mais ta vidéo manque de bruitages comparée à la référence. » → un lancement motion design
  vit de ses bruitages (la réf. Luminovo en a un sur presque chaque mouvement). 3 clics, c'était trop peu.
- En cours de v2 : « ne te focus pas que sur les boutiques tech, prends un secteur où le problème est pire, qui a les
  moyens et est prêt à payer un petit outil régulièrement ». → toujours se demander QUI paie, pas seulement qui utilise.

## Yaplus v2 « Y'a plus. » (58,6 s, 9:16), concept libre (« surprends-moi »)
- Concept : « le mot qui coûte le plus cher dans ta boutique ». Des clients demandent, Paul répond « y'a plus »,
  un tampon rouge s'abat sur le produit et un compteur de ventes perdues monte (−81 500 F). Puis un client part chez
  le voisin, le patron au marché n'en sait rien, un silence, et « on a fait de ce mot un bouton ». Drop, puis l'appli :
  Paul tape, le patron voit et coche, le plombier revient et on lui répond « Y'en a ! » (tampon bleu, +18 000 F).
- Cible choisie : la **quincaillerie** (des milliers de petites références, artisans pressés qui vont chez le voisin,
  patron souvent chez les grossistes, paniers élevés). L'appli a déjà le modèle « quincaillerie ». Flashs alimentation
  et téléphonie pour montrer que tout commerce vit la même chose.
- DA : papier crème + encre noire, illustrations produits au trait épais (tuyau PVC, disjoncteur, seau, sac de riz,
  chargeur) dessinées en SVG, tampon avec texture d'encre (filtre SVG feTurbulence, `<defs>` dans un svg 0×0 hors des
  scènes masquées), rouge = « y'a plus », bleu Yaplus = solution. Vrais écrans en mode **clair** pour coller au papier.
- Écrans : `demo.ts` de Yaplus modifié EN LOCAL (catalogue quincaillerie, boutique « Quincaillerie Ndokoti », session
  « Paul ») puis restauré avec `git checkout` ; `capture.mjs` (tap sur « Tuyau PVC 40 », toast, À racheter, 3 coches).
- treg (~0,11 $) : musique Lyria (makossa/afro-pop, intro clairsemée, basse qui entre, roulement, silence, drop, fin
  franche ; elle a fait 10 s de silence au lieu d'une mesure → on le raccourcit au montage) ; 8 voix : narrateur
  Sadachbia, Paul = Puck, plombier = Charon, électricien = Fenrir, clientes = Aoede et Leda. Clips coupés sur l'énergie
  (`decoupe.py`), mots replacés en temps vidéo (`mots_video.js`) pour caler texte et tampons sur la syllabe « plus ».
- Son : **46 bruitages Mixkit enregistrés** + ambiances rue/marché sous les scènes, chacun sur une action visible
  (tampon = bois + coup sourd superposés, pièces au compteur, levier du disjoncteur, moto du client qui part, sonnette de
  comptoir sur le logo, coches, frappe de l'URL), hauteur ±3 %, gain ±1,5 dB, ±12 ms. Les liens envato (« Stamp »,
  « Cash register ») sont des aperçus filigranés : ne garder que `assets.mixkit.co`.
- Pièges : (1) grain papier qui bouge à chaque image → HD de 260 Mo ; grain FIXE → 42 Mo (et plus réaliste) ;
  (2) voix TTS très pointues : loudnorm linéaire bloqué à -15,7 → compresseur doux + limiteur → -14,2 LUFS.
- **Retour Mariuse (v2 → v2 photos)** : « tu as dessiné des trucs bizarres alors que tu pouvais chercher les vraies
  images et les détourer, où est ton autocritique ? » → les objets réels (produits, billets, boutiques, marché) se
  montrent en **photo détourée**, jamais en dessin SVG fait main. Remplacés : produits (rembg `isnet-general-use`,
  `u2net` si halo, `u2net_human_seg` pour une personne + garder la plus grande composante), billets CFA (rectangles :
  recadrage manuel + coins arrondis, pas rembg), façades réelles + client détouré qui marche, plans drone du marché
  extraits image par image (`photos/marche/`, `rendu.mjs` attend `img.decode()` à chaque frame). Mariuse fournit
  volontiers les images : lui donner une liste précise tôt. Wikimedia renvoie 429 → passer par `i0.wp.com/<url>?w=1000`.
  Autocritique faite sur planche : billets qui cachaient « UN MOT » → ils glissent par la droite sous le texte.
- **Retour final Mariuse** : « J'ai adoré ton concept, c'était trop bien. » → ce qui a marché : UN mot du quotidien
  (« y'a plus ») transformé en coût visible (tampon + compteur en francs), une histoire avec des personnages, un
  retournement (« on a fait de ce mot un bouton ») et la même mécanique inversée à la fin (« Y'en a ! », +18 000 F).
  Mariuse précise aussitôt : **ce n'est pas une norme**. C'était juste pour CE cas (secteur, cible, mot du
  quotidien). La prochaine fois, repartir de la situation et oser autre chose (voir règle mère, SKILL.md §0).
