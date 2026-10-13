# Remplacer le personnage entier (corps, habits, accessoires), en local sur processeur

Même principe que Genjustsu (masque du sujet + guide de mouvement + image de référence), mais
la génération tourne ici avec un modèle open source au lieu de Seedance :

| Étape | Outil | Script |
|---|---|---|
| Vidéo à 16 i/s, 480×832 | ffmpeg | voir ci-dessous |
| Masque du personnage sur toute la vidéo | SAM 2.1 small (`facebook/sam2.1-hiera-small`) | `masque.py` |
| Squelette du mouvement (personnage seul) | OpenPose (`lllyasviel/Annotators`) | `genere.py --pose-seule` |
| Description texte encodée une fois | UMT5 de Wan | `emb.py` |
| Génération : Kelvin redessiné dans le masque, décor gardé | Wan2.1-VACE-1.3B + LoRA CausVid (4 étapes) | `genere.py`, `tout.sh` |

```bash
bash setup.sh
mkdir job && cd job
ffmpeg -i reel.mp4 -vf "fps=16,scale=480:832" -an src16.mp4
cp chemin/vers/personnage_corps_entier.png reference.png
../.venv/bin/python ../masque.py src16.mp4 mask16.mp4 X1,Y1,X2,Y2   # boîte autour du personnage, image 0
../.venv/bin/python ../genere.py src16.mp4 mask16.mp4 reference.png x.mp4 --pose-cache poses.npy --pose-seule
../.venv/bin/python ../emb.py            # adapter prompt/neg dans emb.py ET genere.py au personnage
../tout.sh .
../.venv/bin/python ../assemble.py    # fondu entre morceaux, 720x1280 24 i/s, son de reel.mp4
```

Le prompt décrit le personnage de référence (habits, coiffure) : il est à modifier pour chaque personnage.

## Coût réel mesuré (4 cœurs Xeon, 15 Go, sans GPU)

- float32 obligatoire : ce processeur fait 320 GFLOPS en float32 contre 81 en bf16.
- ~370 s par étape pour 17 images ; masque SAM2 ~20 min et squelette ~15 min pour 15 s de vidéo.
- Une vidéo de 15 s prend donc plusieurs heures. Avec une carte graphique, ce serait quelques minutes.
