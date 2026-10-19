# Pubs NGUELEK PRINT (imprimerie / gadgets, Yaoundé)

**Situation** : Client commerce physique. Matière : 32 reels Facebook du client (machines, atelier, voix du patron). Pubs de 1 à 2 min.

> Cas déjà fait. Ce qui a marché ici a marché pour CETTE situation : s'en inspirer, ne pas le recopier.

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

### Retour de Mariuse sur la pub 3 → validée, référence « niveau agence »
- « Magnifique, j'adore le concept, tu m'as vraiment surpris, on dirait un vrai travail d'agence, pas des trucs
  génériques. » = la meilleure note des trois pubs.
- Ce qui a fait la différence (à refaire) : UN concept narratif tenu du début à la fin (commande → machine → tampon
  → ticket) au lieu d'un catalogue de plans ; une DA née du métier du client (ticket, encre, tampon) et non d'un
  modèle de pub ; deux voix qui dialoguent avec de l'énergie ; montage sur les MESURES de la musique ; une respiration
  (silence) avant le climax ; fin qui récapitule tout (le ticket complet) + appel à l'action concret.
- Quand Mariuse dit « surprends-moi » : changer de CONCEPT (structure, DA, voix), pas seulement d'habillage.
