# Valex L'infographiste — publicités vidéo 9:16

| Fichier | Contenu |
|---|---|
| `valex_pub_voix.mp4` | **Version principale** : 39 s, voix off, sous-titres incrustés, 1080×1920 |
| `valex_pub_voix_leger.mp4` | Même vidéo compressée pour WhatsApp |
| `valex_motion_design.mp4` | Première version, 36 s, sans voix off |

## Sources

- `v2/animation.html` — tout le montage (`render(t)` place chaque élément à partir du temps seul)
- `v2/son.py` — musique 120 BPM, bruitages et mixage de la voix
- `v2/mots.json` — la voix transcrite mot à mot, c'est elle qui cale les scènes
- `v2/textes-campagne.md` — textes pour le gestionnaire de publicités
- `assets/` — réalisations, portrait détouré

## Refaire la vidéo

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

## Choix de montage

9:16 1080×1920, 30 i/s. Tout le contenu tient entre y=300 et y=1600, la zone
visible sur Reels et TikTok. Sous-titres incrustés synchronisés mot à mot
(le mot prononcé passe en jaune) : ils font gagner environ 12 % de temps de
visionnage et servent les 20 à 30 % de personnes qui regardent sans le son.
La première image est pleine et déjà en mouvement, ce qui compte pour le
taux d'accroche à 3 secondes. Pas de fondu au noir final : la vidéo boucle
proprement. Son à -14 LUFS, voix 9 dB au-dessus de la musique.
