---
name: montage-pro
description: Savoir-faire de montage vidéo short-form (Reels, TikTok, Shorts) de Mariuse / KAMTECH, construit à partir de ses vidéos d'inspiration et de nos projets. À lire AVANT tout montage, motion design, podcast, pub ou sous-titrage, et à METTRE À JOUR à la fin de chaque projet (nouvelles inspirations, retours de Mariuse, erreurs). Déclencher sur : montage, vidéo, reel, short, motion design, sous-titres, typographie vidéo, hook, inspiration, "fais comme les pros", "pas de slop IA".
---

# Montage pro — compétence vivante

Objectif de Mariuse : des vidéos qui ressemblent à celles de vrais créateurs pros, **jamais du « slop IA »**
(gabarit répété, animations génériques, tout centré, tout pareil du début à la fin).

Ce fichier grandit à chaque projet. Ordre de lecture :
1. Ce fichier (règles).
2. `references/inspirations.md` : décorticage plan par plan des vidéos que Mariuse adore.
3. `references/journal.md` : ce qu'on a livré, les retours de Mariuse, ce qu'on a appris.

## 1. Les 10 règles qui séparent le pro du slop

1. **Une idée = un écran.** Chaque phrase clé a sa propre composition. Jamais le même layout plus de ~4 s.
   Les pros changent de plan/visuel toutes les **1,5 à 4 s** (mesuré : 1,6 s à 4,8 s sur les 8 inspirations).
2. **La typo EST le visuel.** Le mot fort est énorme (50–90 % de la largeur), le reste est petit.
   Hiérarchie = 1 mot géant + 1–3 mots d'accompagnement en petit. Pas de paragraphe à l'écran.
3. **Mélange de polices avec intention** : un sans-serif gras/serré (Helvetica/Inter/Neue Haas) +
   un serif italique pour le mot émotionnel (« tes *créateurs* préférés », « plus c'est *mémorable* »).
   Ou une seule famille serif éditoriale pour tout (style Loucash). Jamais 3 polices au hasard.
4. **Profondeur : le texte DERRIÈRE le sujet.** Gros titre posé derrière la tête (détourage de la personne)
   = effet magazine immédiat. C'est le marqueur n°1 du « pro » vs « template ».
5. **Sous-titres : 1 à 3 mots, pas de karaoké coloré criard.** Blanc, propre, position fixe basse/centre.
   Le mot clé occasionnel monte en taille ou passe en italique serif. Majuscules condensées jaunes
   (style Bebas/Anton) seulement si la DA de la vidéo est « jaune/poster ».
6. **Alterner les ambiances.** Facecam sombre ↔ plein écran clair (papier blanc/crème, formes organiques,
   branches, objets 3D isolés) ↔ capture d'écran. Le contraste clair/sombre relance l'attention.
7. **Montrer, pas illustrer.** Vraies captures (Google, CapCut, GitHub, sites, tarifs) avec curseur visible,
   **cercle loupe** sur le réglage dont on parle, valeurs qui changent (100 % → 85 %). Pas d'icônes génériques.
8. **Illustrations avec une DA.** Ex. Loucash : aplats corail #E07A5F + crème + traits noirs dessinés main,
   mêmes couleurs partout. Une seule DA par vidéo. Mèmes/GIF pour les punchlines humour (« késtufé louca ? »).
9. **Structure en 4 temps** (Hook → Build-up → Valeur → CTA), voir §3. Hook = règle des 3 :
   parole + visuel + texte frappent ensemble dans les 3 premières secondes.
10. **CTA dans la continuité** : « abonne-toi, commente MOT et je te l'envoie ». À l'écran : icône dossier
    + MOT en jaune gras. Pas d'écran de fin générique.

## 2. Boîte à outils technique (notre pipeline HTML → Playwright → ffmpeg)

Pipeline de référence : `podcast/` (render(t) déterministe, rendu Playwright parallèle, mix numpy, loudnorm).

| Technique pro | Comment la faire chez nous |
|---|---|
| Texte derrière le sujet | **Construit.** `outils/detourage.py` (RVM resnet50, ~0,1 s/image, cohérent dans le temps) + exemple complet `outils/demo_derriere.py` → `demo_texte_derriere.mp4`. Calques : fond flouté ×0,30 + vignette → TITRE (45 % du mot géant sous le haut de la tête, mesuré sur l'alpha au début du beat) → personne → sous-titres. Pour une image fixe : remplissage depuis les bords (pub Valex v2). |
| Typo mixte | Dans `fonts/` : `InterTight-ExtraBold.ttf` (sans serré) + `InstrumentSerif-Italic/Regular.ttf` (accent). À ajouter au besoin : Anton/Bebas Neue (poster jaune), via `fonts.googleapis.com/css2?family=…` avec un vieux User-Agent pour obtenir le .ttf. |
| Texte « glow » sur fond sombre | `text-shadow: 0 0 20px rgba(255,255,255,.6)` + serif italique + capitales condensées (cf. « C'EST TOUT UN ART »). |
| Texture vintage | Grain (bruit canvas animé), aberration chromatique (décalage RGB 2–4 px), légère pixellisation, opacité texte 85 %. |
| Letterbox Loucash | Vidéo dans une bande centrale ~16:9, bandes noires haut/bas ; visuel/titre dans la bande du haut, sous-titre serif dans celle du bas. |
| Screen-record pédagogique | Capture → zoom progressif (scale 1→1.3) + cercle loupe blanc 2 px sur la zone + curseur. |
| Encadré « sélection » | Rectangle pointillé avec poignées aux coins (look Figma/Canva) autour d'un mot (« PAROLE / VISUEL », « FOMO »). |
| Sous-titre négatif | Texte en masque qui inverse la vidéo dessous (`mix-blend-mode: difference`). |
| Punch-in | Zoom 100 → 115 % sur la facecam sur les mots forts (coupe sèche, pas de fondu). |
| Audio | Voix devant, musique discrète, **-14 LUFS intégré** (mesuré sur les inspirations : -14,4/-14,5). Whoosh sur les changements d'écran, pop sur les mots géants. |

**Règle d'attitude : ne jamais dire « impossible » ou « pas encore construit » sans avoir essayé
au moins 3 méthodes.** Vérifier d'abord le journal : on l'a peut-être déjà fait.

## 3. Structure de script (formule virale en 4 étapes, d'après MedTheDesigner)

1. **Hook (0–3 s)** : rupture mentale. « Est-ce que tu savais… », « Il faut absolument que tu le saches »,
   « J'aurais aimé qu'on me dise ça plus tôt », « Au cas où tu vis sous un caillou… ». Parfois on montre
   le RÉSULTAT d'abord (vidéo 6 : « Excellent, ça fonctionne » puis on explique).
2. **Build-up** : faire monter la tension, ne pas donner la réponse trop vite (twist à la fin).
   Opposition « le problème c'est jamais X, c'est Y ». Ennemi commun (le prix, les abonnements…).
3. **Valeur** : une idée = une phrase. Étapes numérotées. Digeste > exhaustif.
4. **CTA** : FOMO + mot-clé à commenter + promesse d'envoi en message.

Débit de parole des pros : **3,5 à 4,5 mots/s**. Durée : 26–65 s, jusqu'à 2 min 30 si le sujet le mérite.

## 4. Checklist anti-slop (à passer AVANT de livrer)

Sortir une planche contact (`planche.sh`, 1 image / 1–2 s) et vérifier :
- [ ] Aucune séquence de >4 s sans changement visuel (plan, zoom, typo, visuel).
- [ ] Au moins 3 ambiances différentes (sombre / clair / capture / illustration).
- [ ] Les 3 premières secondes : parole + texte + visuel forts en même temps.
- [ ] Le mot fort de chaque phrase clé est géant, le reste petit.
- [ ] 2 polices max (+1 condensée si DA poster), une seule DA couleur.
- [ ] Sous-titres 1–3 mots, jamais par-dessus un visuel important.
- [ ] Rien n'est centré « par défaut » : chaque position est un choix.
- [ ] Faits personnels vérifiés (ville = **Yaoundé**, nom de marque, chiffres).
- [ ] -14 LUFS, voix intelligible sous la musique.
- [ ] Je me demande : « Est-ce que MedTheDesigner ou Loucash posterait ça ? » Si non, itérer.

## 5. Comment faire grandir ce skill

À la fin de CHAQUE projet vidéo :
- Ajouter une entrée dans `references/journal.md` (livré, retour de Mariuse, leçon).
- Nouvelle vidéo d'inspiration → télécharger (`yt-dlp`), transcrire (ElevenLabs Scribe), planche contact,
  mesurer coupes/mots par s/LUFS, ajouter une fiche dans `references/inspirations.md`.
- Si une leçon devient une règle générale → la promouvoir dans §1 ou §2 ci-dessus.
- Si une technique de §2 est construite → noter le fichier/fonction réutilisable.
- Commit + push sur la branche de travail.
