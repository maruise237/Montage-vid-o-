# Genjutsu gratuit : remplacer une personne dans une vidéo sans clé payante

Inspiré de [Genjustsu Open Source Workflow](https://github.com/sirioberati/Genjustsu-Open-Source-Workflow) (MIT, Sirio Berati).
L'original génère avec Seedance via Enhancor et sépare la voix avec Replicate : deux API payantes.
Ici, la génération passe par **Wan2.2-Animate** (modèle open source d'Alibaba, mode *Character Swap*),
hébergé gratuitement sur le Space Hugging Face [`alexnasa/Wan2.2-Animate-ZEROGPU`](https://huggingface.co/spaces/alexnasa/Wan2.2-Animate-ZEROGPU).

## Ce que ça fait

1. Envoie ta vidéo source et ton image de référence au Space (mode Character Swap).
2. Le Space détecte la personne, calcule pose, visage, masque et fond, puis génère la nouvelle personne
   dans la même scène, avec les mêmes mouvements et expressions.
3. En local : remet la vidéo à la résolution de la source, recolle **tout le son d'origine**
   et fabrique `planche.jpg` (source | masque | résultat sur 4 instants) pour vérifier avant publication.

Tout est rangé dans `runs/<date>/` : `final.mp4`, `resultat_brut.mp4`, `masque.mp4`, `pose.mp4`, `visage.mp4`, `fond.mp4`, `job.json`.

## Installation

```bash
bash setup.sh               # ffmpeg requis ; AVEC_ORIGINAL=1 bash setup.sh clone aussi l'original dans upstream/
```

Mets ton jeton Hugging Face (gratuit, droit *read*) dans `.env` : `HF_TOKEN=hf_...`
Sans jeton, le quota anonyme est presque toujours à zéro.

## Utilisation

```bash
.venv/bin/python gratuit.py check
.venv/bin/python gratuit.py swap source.mp4 reference.png --secondes 4 --res low
.venv/bin/python gratuit.py finalise runs/<date>     # refaire seulement la finition
```

## Limites (à connaître avant de promettre quoi que ce soit)

| | |
|---|---|
| Durée | 2 à 20 s par génération |
| Résolution générée | Low 640×360 / Medium 832×480 (agrandie ensuite à la taille source, donc moins nette qu'un vrai 1080p) |
| Quota ZeroGPU | 4 s en Low ≈ 75 s de GPU, 10 s ≈ 135 s ; Medium = x2. Le quota gratuit du compte est de quelques minutes par jour |
| Meilleurs résultats | une seule personne bien visible, cadrage proche entre la vidéo et l'image de référence (même posture, corps entier si la vidéo montre le corps) |
| Dépendance | un Space communautaire : il peut tomber en pause ou changer son API (`GENJUTSU_SPACE=owner/nom` pour viser une copie) |

N'utilise que des personnes qui ont donné leur accord (toi, tes clients, des personnages fictifs).
