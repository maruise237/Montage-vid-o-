# Genjutsu local : remplacer le visage d'une vidéo, sans clé ni interface

Inspiré de [Genjustsu Open Source Workflow](https://github.com/sirioberati/Genjustsu-Open-Source-Workflow),
qui dépend d'API payantes (Enhancor/Seedance, Replicate). Ici tout tourne en local, sur processeur,
avec [FaceFusion](https://github.com/facefusion/facefusion) (version figée) :

- `hyperswap_1a_256` : met le visage de l'image de référence sur la personne de la vidéo
  (expressions, mouvements de bouche, lumière et décor conservés) ;
- `gfpgan_1.4` : rend le visage net.

Le son d'origine est recopié tel quel dans la vidéo finale.

```bash
python3 swap.py source.mp4 visage1.jpg [visage2.jpg ...]   # installe FaceFusion au premier lancement
python3 swap.py source.mp4 reference.jpg --sans-enhancer   # ~3x plus rapide, visage moins net
```

Par défaut seul le plus grand visage de chaque image change (`--tous-les-visages` pour tous).

Sortie : `runs/<date>/final.mp4` et `comparaison.jpg` (référence | source | résultat).

## À savoir

- **Seul le visage change.** Cheveux, corps et vêtements restent ceux de la vidéo : choisis une vidéo
  dont la coiffure et la carrure vont avec la référence.
- Vitesse sur 4 processeurs : ~3 s par image avec netteté, soit ~1 min 30 de calcul par seconde de vidéo à 30 i/s.
- Référence idéale : visage de face, net, bien éclairé, sans lunettes ni main devant.
- Licence FaceFusion : OpenRAIL-AS. Utilise uniquement des visages de personnes qui ont donné leur accord.
