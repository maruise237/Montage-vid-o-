# Bruitages

## Quantité selon le type
| Type | Bruitages / minute |
|---|---|
| Tuto à captures | 60–80 (Toprak 81) |
| Vulgarisation | 20–40 |
| Long format | ~20 |

> ⚠️ Depuis oct. 2026 : **bruitages ENREGISTRÉS uniquement**, voir `05-son-humain-anti-ia.md`.
> Les sons synthétisés de `bruitages.py` ne servent plus qu'aux maquettes, jamais en livrable.

## Quel son pour quelle action
| Son | Quand |
|---|---|
| **whoosh** | Transition d'écran — environ **une coupe sur deux**, pas toutes |
| **clic / touche** | Chaque clic du curseur, chaque lettre tapée |
| **pop** | Apparition d'un logo, sticker, mot, bulle |
| **impact grave** | Mot géant, B-roll choc, nom du produit (Faro : 27 impacts sur une vidéo) |
| **riser** | 1–1,5 s avant la coupe qui lance la musique |
| **carillon** | Fin, URL, réussite |
| **glitch** | Effet tech / erreur |
| **tic** | Compteur, étape |

## Règles
- Un bruitage doit coller à une **action visible**.
- Pas de bruitage sur une coupe « invisible » (punch-in, multicam simulé).
- **Un whoosh ne masque jamais un mot** : le finir AVANT le mot (démarrer à t − 0,40 s).
- Caler les bruitages sur un fichier d'événements (`evenements.json` : temps + type) généré depuis l'animation.

## Code
- Livrable : `04-outils/pub-depuis-videos/son_reel.py` → `bruit(B, [ids…], t)` pose un vrai échantillon
  (Mixkit SFX), jamais le même deux fois de suite, hauteur ± 3,5 %, gain ± 2 dB, décalage 10–20 ms ;
  `ambiance(A, source, a, d, t)` pose le son direct d'une vidéo source.
- Maquette seulement : `04-outils/python/bruitages.py` (sons synthétisés = repérables comme « IA »).
