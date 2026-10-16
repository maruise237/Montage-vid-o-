# Pub à partir des vidéos d'un client (exemple : NGUELEK PRINT, 2 pubs livrées en oct. 2026)

Pour : une boutique / un atelier qui a déjà des dizaines de petites vidéos (Facebook, WhatsApp) et veut
1–2 pubs d'une minute qui les mettent en avant.

## Étapes
1. `yt-dlp` sur chaque lien → `sources/vNN.mp4` (+ `--write-info-json` : la description donne adresse, téléphone,
   horaires, slogans).
2. Planche contact par vidéo (1 image / 2 s) → noter les meilleurs plans, les **incrustations à recadrer**
   (numéros, textes), les sources basse définition (→ mode « cadre »).
3. Son des sources : `faster-whisper` (qui parle ? chanson ?) + `demucs` 4 pistes (basse/batterie fortes = musique).
   Garder **les voix** et **le son direct des machines** ; jamais les chansons des sources (droits).
4. Logo du client découpé en calques (`calques.py`) → animation pièce par pièce.
5. Musique réelle (`mixkit_catalogue.mjs` → catalogue ; licence à vérifier), bruitages enregistrés
   (`sons_bruitages/`, ids Mixkit, voir `catalogue.json`).
6. Décrire la pub dans un module (`pub1.py`, `pub2.py` = exemples complets) : PLANS, CALQUE, VOIX, son().
7. `python3 moteur.py pub1 base` → `planche` (vérifier !) → `son` → `calque` → `final <nom>.mp4`.

## Fichiers
| Fichier | Rôle |
|---|---|
| `moteur.py` | plans ffmpeg (plein écran avec zoom/position, « tirage photo » sur fond flouté, noir), planche, final ; chaque plan au nombre exact d'images |
| `calque.html` + `rendu_calque.mjs` | calque graphique `render(t)` → PNG transparents (titres, chapitres numérotés, sous-titres, balayage CMJN, logo animé, écran de fin avec WhatsApp) |
| `son_reel.py` | `affiner()` coupes de voix sur les silences · `grille()` temps de la musique · `musique_montee()` · `ambiance()` son direct · `bruit()` bruitage enregistré varié · `mixer()` ducking + -14 LUFS |
| `outils_pub.py` | `P()`, `C()`, `caler()` (coupes sur les temps), `sous_titres()` |
| `pub1.py` / `pub2.py` | exemples : « L'atelier » (services, musique afro) et « Cadeaux » (voix du patron, guitare) |

Chemins attendus : `sources/`, `sep/htdemucs/<src>/vocals.wav`, `sons/musique/<id>.mp3`, `sons/bruit/<id>.mp3`,
`logo/calque_*.png`, polices dans `../fonts/`, logos d'outils dans `../assets/logos/`. Règles son : `01-competences/D-son/05-son-humain-anti-ia.md`.
