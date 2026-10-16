# Musique (mesurée sur 14 vidéos de pros, séparation voix/reste avec demucs)

## Niveaux
- Présente **70–100 % du temps**.
- **12 à 25 dB sous la voix** (médiane ~17 dB).
- Long format = plus bas (Loucash 2 min 26 : 29 dB sous la voix, mélodie douce).
- Exception : DA « poster » rapide ~6 dB sous la voix.

## Deux façons d'ouvrir, selon le type
- **Tuto / outil** (Med, Loucash) : **hook presque sec** (voix + petits pops), puis un **riser de 1–1,5 s**
  qui mène à une coupe, et la musique démarre sur cette coupe, hook fini.
- **Vulgarisation / histoire** (Faro) : **musique épique forte sous le hook** (presque au niveau de la voix
  pendant les promesses), puis elle baisse de ~12 dB pour le corps.

## Ponctuation musicale (c'est ce qui fait « pro »)
- Juste après avoir nommé le concept clé : **2–4 s de musique seule** (montée/drop) sur la carte-titre.
- **Couper net la musique 1,5–2 s sur la punchline** : le silence met la phrase en valeur (Wu).
- Changer de musique/texture au changement de chapitre ou d'étape.
- Musique qui remonte (~6 dB) quand la voix s'arrête (démo).
- Fin : la musique s'arrête sur un carillon.
- Couper la musique pendant une phrase sérieuse/intime (« je ne peux pas entendre le son »).

## Ducking
La musique baisse automatiquement sous la voix (enveloppe de la voix) — voir `04-outils/python/son_pro.py`.

## Source
- **Vraie musique enregistrée** d'une bibliothèque dont la licence couvre l'usage. Mixkit « Stock Music Free
  License » : réseaux sociaux + publicités en ligne autorisés, pas TV/radio, pas de remix en morceau seul.
  (Le site est derrière Cloudflare : passer par Playwright/Chromium ; ne garder que les fichiers
  `assets.mixkit.co`, les « audio-previews.elements.envatousercontent.com » sont PAYANTS.)
- Choisir pour la marque et le public (afro pour une boutique de Yaoundé, guitare chaleureuse pour des cadeaux),
  vérifier avec demucs qu'il n'y a **pas de chant** si une voix parle dessus.
- **Monter la musique comme un humain** : coupes des plans sur les temps du morceau (`librosa` beat_track →
  `caler()`), 1er temps du morceau sur la coupe après le hook, **vraie fin du morceau raccordée sur l'écran
  final** (saut au temps le plus proche du début de l'outro), pas de fondu de sortie.
- **Jamais de musique synthétisée par nous** (sinusoïdes en boucle = son « IA »). Jamais de morceau commercial.
