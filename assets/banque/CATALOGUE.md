# Banque d'images — piocher ici AVANT de générer

Aperçu de tout en une image : `apercu.jpg`. Tout est PNG transparent sauf les décors (9:16, 768x1344).
Nom = `humeur_action` (poses) ou `lieu_détail` (décors). Ajouter chaque nouvelle image ici (1 ligne).

## avatar_poses/ — Mariuse en 3D (t-shirt KAMTECH, jean, baskets), corps entier, détouré
| Fichier | Humeur | Pour une phrase qui… |
|---|---|---|
| neutre_face_bras_le_long | neutre, souriant | présente, pose le sujet |
| content_pouce_clin_doeil | content | valide, « c'est gratuit », « ça marche » |
| choque_mains_sur_joues | choqué | surprise, chiffre fou, « tu savais pas ? » |
| pensif_main_menton | pensif | question, doute, « réfléchis » |
| confiant_bras_croises | sûr de lui | affirmation, défi, preuve |
| explique_mains_ouvertes | calme, pédagogue | explique, liste |
| perplexe_haussement_epaules | perplexe | « ce n'est pas… », comparaison, mauvais choix |
| enthousiaste_pointe_haut_gauche | enthousiaste | montre une carte/logo en haut à gauche |
| victoire_poing_leve | fier | nouveau cap, réussite, annonce |
| concentre_ordinateur | concentré | travail, code, outil sur PC |
| amuse_telephone | amusé | appli mobile, vocal, WhatsApp, message |
| cool_marche_lunettes_soleil | décontracté | balade, déplacement, se tourne vers la droite |

Avatar maître (référence pour générer une nouvelle pose) : `assets/avatar/maitre.png`.

## personnages/
| Fichier | Contenu |
|---|---|
| mascotte_claude_marche_lunettes | mascotte orange « Claude » (soleil, lunettes noires) qui marche vers la droite |

## decors/ — fonds 3D style Pixar, sans personnage, sol dans le tiers bas
| Fichier | Lieu / ambiance |
|---|---|
| ciel_nuages_jour | ciel bleu, gros nuages, herbe en bas : rêve, liberté, « change d'arrière-plan » |
| ville_yaounde_rue_taxis | rue de Yaoundé, maisons colorées, taxis jaunes : ville, Cameroun, terrain |
| bureau_kamtech_logo_mur | bureau moderne + vrai logo KAMTECH au mur : l'agence, travail, pro |
| bureau_moderne_panneau_noir_vide | même bureau, panneau noir vide (y poser un logo/texte : x 314–704, y 254–583) |
| plage_kribi_palmiers | plage de Kribi, palmiers, mer turquoise : vacances, détente, liberté |

## illustrations/ — cartes néo-brutalistes et tampons (fabriqués par le code, `avatar1/montage.py`)
| Fichier | Sert à |
|---|---|
| carte_fenetre_code_python | « fait avec du code », technique |
| carte_facture_total_0_euro | gratuit, coût zéro |
| carte_message_vocal_envoye | vocal / WhatsApp envoyé |
| carte_onde_vocal_hesitations_coupees | montage audio, nettoyage de la voix |
| carte_prompt_a_claude | demande faite à une IA (texte à changer dans le code) |
| croix_rouge_barre | « pas ça », mauvais choix, à barrer |
| tampon_100_pourcent_gratuit, tampon_cest_fait, tampon_bien_fait, tampon_banque_de_poses | ponctuer une phrase |

Pour un texte différent sur une carte ou un tampon : fonctions `carte()`, `tampon()`, `facture()`… dans
`avatar1/montage.py` (gratuit, pas besoin de générer).

## Ailleurs
- Logos officiels : `assets/logos/` (claude, chatgpt, kamtech, veo, kling, seedance, cloudflare, whatsapp, google…).
- Essais ratés / anciennes versions : `assets/avatar/essais/` (ne pas utiliser).
- Photos réelles de Mariuse : `assets/avatar/photos/`, privées, jamais sur GitHub.
