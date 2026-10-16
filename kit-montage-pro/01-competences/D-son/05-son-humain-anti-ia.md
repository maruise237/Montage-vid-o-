# Son humain : enlever le pattern « monté par une IA »

Retour de Mariuse (pubs NGUELEK PRINT, oct. 2026) : « les bruitages, effets d'apparition, tchou-tchou… sont trop
génériques, on arrive à détecter que la vidéo a été montée par Claude ».

## Ce qui trahit l'IA
| Signe | Exemple v1 |
|---|---|
| Timbre synthétique | « pop » = sinus qui descend, « whoosh » = bruit blanc filtré, « riser », « impact » |
| Un son sur TOUT | chaque étiquette, chaque morceau du logo, chaque coupe |
| Régularité mécanique | même échantillon, même gain, calé à l'image près |
| Clichés | riser → impact avant le logo, carillon final |
| Musique synthétisée | boucle sans structure, coupée par un fondu |

## Ce qu'on fait (dans l'ordre de priorité)
1. **Son direct** : le vrai bruit de ce qu'on voit (CNC, brodeuse, laser, imprimante, rue), tiré des vidéos
   sources, synchrone. Vérifier d'abord qu'il n'y a pas de chanson dessus (demucs 4 pistes : basse/batterie
   fortes = musique ; transcription qui « entend des paroles » = chanson).
2. **Vraie musique** montée sur ses temps, avec sa vraie fin (fiche `01-musique.md`).
3. **Quelques bruitages enregistrés qui ont du sens pour la marque** :
   | Marque / scène | Sons qui racontent quelque chose |
   |---|---|
   | Imprimerie | feuille qui glisse, page tournée, imprimante matricielle, frappe de machine à écrire, agrafeuse |
   | Enseigne lumineuse | interrupteur + bourdonnement électrique |
   | Cadeau | interrupteur de veilleuse, trousseau de clés, papier |
   | Rafale de produits | vrais déclencheurs d'appareil photo, un sur deux |
4. **Rare** : pas de son sur les étiquettes de texte ni sur chaque morceau du logo. Le silence est un choix.
5. **Varié** : jamais deux fois le même échantillon de suite, hauteur ± 3 %, gain ± 2 dB, décalage 10–20 ms.
6. **Voix** : son d'origine de la caméra (vrai ambiant) ; demucs sert à mesurer, pas à diffuser.

## Contrôle avant livraison
- Retranscrire la bande son finale : chaque phrase finit entière.
- Compter : moins de bruitages que d'éléments à l'écran. Si chaque apparition a son son → trop.
- Se demander : « est-ce qu'un monteur aurait trouvé ce son en fouillant une banque, ou est-ce un son de logiciel ? »
