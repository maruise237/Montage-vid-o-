# Montage vidéo KAMTECH

Toutes les vidéos short-form (Reels, TikTok, Shorts, Facebook Ads) montées pour Mariuse / KAMTECH et ses clients.
Chaque vidéo est montée **avec du code** : une page HTML calée sur le temps (`render(t)`), rendue image par
image avec Playwright, puis encodée avec ffmpeg. Son mixé en Python, livré à -14 LUFS.
Règle de base : pas de vidéo générée par IA. Seulement de vraies images, de vraies prises et de vrais écrans.

## Projets

| Projet | Dossier | Vidéos livrées |
|---|---|---|
| Valex L'infographiste (pub freelance) | `v2/` | `valex_pub_voix.mp4`, `valex_pub_voix_leger.mp4`, `valex_motion_design.mp4` |
| Podcast « Une IA me répond » | `podcast/` | `podcast_claude_*_partage.mp4` (version longue et version courte) |
| KamForms : reel « 3 outils IA » | `kamforms/` | `reel_kamforms.mp4`, `reel_kamforms_partage.mp4` |
| KamForms : reel n°2 | `kamforms2/` | `reel_kamforms_2.mp4`, `reel_kamforms_2_partage.mp4` |
| KamForms : disponible sur APKPure | `kamforms3/` | `reel_kamforms_apkpure.mp4`, `reel_kamforms_apkpure_partage.mp4` |
| KamForms : « maintenant une application » | `kamforms_appli/` | `kamforms_appli/KamForms_appli.mp4`, `_partage.mp4` |
| KamForms : 10 pubs sur les hooks de @theo.vizuals | `pubs_hooks/` | `pubs_hooks/v3/*.mp4` |
| KamForms : mèmes | `memes/`, `meme_jerry/` | `memes/meme_kamforms_*.mp4`, `meme_jerry/meme_kamforms_jerry.mp4` |
| Djoumi (appli beauté) | `djoumi/` | `reel_djoumi.mp4`, `reel_djoumi_partage.mp4` |
| NGUELEK PRINT (imprimerie, Yaoundé) | `boutique/` | `boutique/livrables/` (pub 1 atelier, pub 2 cadeaux, pub 3 commande, plus les versions WhatsApp) |
| Yaplus : lancement | `yaplus_lancement/` | `yaplus_lancement/Yaplus_lancement_partage.mp4` |
| Yaplus v2 : quincailleries | `yaplus_v2/` | `yaplus_v2/Yaplus_v2_partage.mp4` |
| Yaplus v3 : musée des inventions | `yaplus_musee/` | `yaplus_musee/Yaplus_musee.mp4`, `_partage.mp4` |
| Pub Facebook Ads « Excel sans formules » (Chariow) | `chariow_excel/` | `pub_excel_sans_formules.mp4` (9:16), `_4x5.mp4`, `_partage.mp4` |
| Doublage FR d'un reel anglais | `doublage/` | `reel_doublage_fr.mp4`, `reel_doublage_fr_partage.mp4` |
| Vidéo avatar n°1 | `avatar1/` | `video_avatar_1.mp4`, `video_avatar_1_partage.mp4` |
| Citations « mon ennemi / mon fan » et « ne t'énerve jamais » | `mystere1/`, `calme1/` | `video_mystere_1_partage.mp4`, `video_calme_1_partage.mp4` |
| Genjutsu : remplacement de personnage en local (essai) | `genjutsu/` | voir `genjutsu/README.md` |

Les fichiers `*_partage.mp4` sont les versions légères (720p) pour WhatsApp. Les crédits des musiques, photos et
sons sont dans le `CREDITS.md` de chaque dossier quand il y en a un.

## Le reste du dépôt

| Dossier | Rôle |
|---|---|
| `.claude/skills/montage-pro/` | Skill Claude : le savoir-faire de montage. Les cas déjà faits sont dans `references/cas/`, pour garder la méthode générale séparée des projets |
| `.claude/skills/video-avatar/` | Skill Claude : vidéos avec l'avatar 3D de Mariuse |
| `kit-montage-pro/` (+ `.zip`) | Kit de montage à partager : la skill, le journal des projets et les outils |
| `assets/` | Logos, polices, avatar et images communes |
| `outils/` | Scripts réutilisables (logos, etc.). `outils/lecture_reel.py` lit un Reel seconde par seconde avant publication et liste quoi modifier |
| `publications/` | Légendes et hashtags pour TikTok, Instagram et YouTube Shorts |
| `rendu.mjs`, `render.js`, `planche.sh` | Rendu image par image et planche de contrôle |

## Valex L'infographiste : publicités vidéo 9:16
| Fichier | Contenu |
|---|---|
| `valex_pub_voix.mp4` | **Version principale** : 39 s, voix off, sous-titres incrustés, 1080×1920 |
| `valex_pub_voix_leger.mp4` | Même vidéo compressée pour WhatsApp |
| `valex_motion_design.mp4` | Première version, 36 s, sans voix off |

### Sources

- `v2/animation.html` — tout le montage (`render(t)` place chaque élément à partir du temps seul)
- `v2/son.py` — musique 120 BPM, bruitages et mixage de la voix
- `v2/mots.json` — la voix transcrite mot à mot, c'est elle qui cale les scènes
- `v2/textes-campagne.md` — textes pour le gestionnaire de publicités
- `assets/` — réalisations, portrait détouré

### Refaire la vidéo

```bash
npm install
python3 v2/son.py                       # son.wav
node rendu.mjs v2                        # images/
ffmpeg -y -framerate 30 -i v2/images/f%05d.jpg -i v2/son.wav \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v libx264 -preset slow -crf 19 \
  -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -shortest valex_pub_voix.mp4
```

Vérifier avant tout rendu complet :
`./planche.sh v2 0 3.6 7.3 13.9 18.7 26.6 30.9 33 38.9`

### Choix de montage

9:16 1080×1920, 30 i/s. Tout le contenu tient entre y=300 et y=1600, la zone
visible sur Reels et TikTok. Sous-titres incrustés synchronisés mot à mot
(le mot prononcé passe en jaune) : ils font gagner environ 12 % de temps de
visionnage et servent les 20 à 30 % de personnes qui regardent sans le son.
La première image est pleine et déjà en mouvement, ce qui compte pour le
taux d'accroche à 3 secondes. Pas de fondu au noir final : la vidéo boucle
proprement. Son à -14 LUFS, voix 9 dB au-dessus de la musique.

## Podcast « Une IA me répond » (`podcast/`)

| Fichier | Rôle |
|---|---|
| `podcast_claude_partage.mp4` | version longue, 2 min 05, 5 questions |
| `podcast_claude_court_partage.mp4` | version courte, 1 min 30, 4 questions |
| `podcast/reponses.json` | texte des réponses de Claude (voix ElevenLabs « Brian », multilingual v2) |
| `podcast/montage.py` | plan de montage : coupes de la caméra, voix de Claude resserrée, enveloppe de la voix pour le logo |
| `podcast/animation.html` | écran Claude (logo réactif, code animé, illustrations), mots-clés, sous-titres karaoké |
| `podcast/son.py` | musique (deux ambiances), bruitages calés sur `evenements*.json`, ducking |

Reconstruire (mettre la vidéo source dans `podcast/source.mp4`, puis `V=_court` pour la version courte) :
`python3 podcast/montage.py && python3 podcast/construire.py && node podcast/evenements.mjs && python3 podcast/son.py && node podcast/rendu.mjs`
