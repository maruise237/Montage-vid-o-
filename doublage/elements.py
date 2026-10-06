# Textes anglais incrustés -> français. box = zone (x0,y0,x1,y1) en 1080x1920 où le texte anglais est effacé.
# en = texte anglais (sert à calibrer la taille de police), fr = segments (texte, police, couleur|None=auto|'arc')
S, SI, SA, SB, M = 'serif', 'serif-i', 'sans', 'sans-b', 'mono'
BLEU = (40, 100, 235)
E = [
 # --- 1. They look the same ---
 dict(t=(0.0, 2.97), box=(20, 185, 1060, 345), en=[("They look ", S), ("the same.", SI)],
      fr=[("Ils se ", S, None), ("ressemblent.", SI, None)], align='c'),
 # --- 2. They're not / Three completely different / kinds of work ---
 dict(t=(2.9, 6.45), box=(150, 225, 930, 395), en=[("They're not.", S)], fr=[("Faux.", S, None)], align='c'),
 dict(t=(2.9, 6.45), box=(100, 405, 980, 520), en=[("Three completely different", S)],
      fr=[("Trois types de travail", S, None)], align='c'),
 dict(t=(2.9, 6.45), box=(100, 525, 980, 665), en=[("kinds of work.", SI)],
      fr=[("très différents.", SI, None)], align='c'),
 # --- 3. Dots ---
 dict(t=(7.0, 10.3), box=(55, 1232, 760, 1340), en=[("An ", S), ("always-on", SI), (" worker", S)],
      fr=[("Un employé ", S, None), ("toujours actif", SI, None)], align='l'),
 dict(t=(9.0, 10.3), box=(140, 1372, 390, 1416), en=[("inside ChatGPT", SA)], fr=[("dans ChatGPT", SA, None)], align='c', k=31, couleur='live'),
 dict(t=(10.2, 14.35), box=(85, 335, 330, 380), en=[("ONGOING GOAL", M)], fr=[("OBJECTIF EN COURS", M, None)],
      align='l', esp=4),
 dict(t=(10.2, 14.35), box=(853, 342, 984, 374), en=[("REPEATS", M)], fr=[("RÉPÉTÉ", M, None)], align="l", esp=2,
      couleur='live', k=13, aplat=(853, 347, 979, 370)),
 dict(t=(10.2, 14.35), box=(200, 405, 1010, 505), en=[("Keep my launch on track", S)],
      fr=[("Garder mon lancement au cap", S, None)], align='l', frappe=True, tref=13.2, maxw=700),
 # --- 4. Muse ---
 dict(t=(14.75, 21.3), box=(95, 268, 990, 425), en=[("Built for ", S), ("everyday", SI), (" tasks", S)],
      fr=[("Pensé pour le ", S, None), ("quotidien", SI, BLEU)], align='c'),
 dict(t=(16.5, 17.55), box=(170, 765, 830, 840), en=[("Help me stay on top of school em", 'sans-m')], taille=44.8,
      fr=[("Aide-moi à gérer mes mails", 'sans-m', None)], align='l', frappe=True, k=41, tref=17.4, maxw=640),
 dict(t=(14.75, 21.3), puces=[[(145, 1180, 337, 1248), (353, 1180, 547, 1248), (563, 1180, 705, 1248), (713, 1180, 943, 1248)], [(390, 1262, 690, 1328)]],
      labels=[["Réservations", "Achats", "Formulaires", "Rappels"], ["Objectifs à long terme"]], police=SA, taille=29),
 # --- 5. Grok Bot ---
 dict(t=(21.7, 24.55), box=(25, 1245, 760, 1335), en=[("A team of ", S), ("AI coworkers", SI)],
      fr=[("Une équipe de ", S, None), ("collègues IA", SI, None)], align='l'),
 dict(t=(24.55, 29.85), box=(230, 280, 850, 396), en=[("Different bots,", S)], fr=[("Des bots différents,", S, None)], align='c'),
 dict(t=(24.55, 29.85), box=(230, 397, 850, 500), en=[("different roles", SI)], fr=[("des rôles différents", SI, None)], align='c'),
 dict(t=(24.55, 29.85), box=(500, 722, 580, 750), en=[("YOU", M)], fr=[("TOI", M, None)], align='c', esp=3, k=31),
 dict(t=(24.55, 29.85), box=(0, 1068, 1080, 1122), rangee=["Recherche", "Ventes", "Marketing", "Opérations"],
      en=[("Marketing", SA)], police=SA),
 # --- 6. So basically ---
 dict(t=(29.85, 36.3), box=(200, 200, 880, 365), en=[("So ", S), ("basically", SI)], fr=[("En ", S, None), ("gros", SI, None)], align='c'),
 dict(t=(29.85, 36.3), box=(300, 535, 1005, 655), en=[("Ongoing work", S)], fr=[("Travail continu", S, 'arc')], align='l'),
 dict(t=(29.85, 36.3), box=(300, 862, 1005, 985), en=[("Personal life tasks", S)], fr=[("Tâches perso", S, None)], align='l'),
 dict(t=(29.85, 36.3), box=(300, 1180, 1005, 1305), en=[("AI teams", S)], fr=[("Équipes d'IA", S, None)], align='l'),
 # --- 7. Very different where it counts + tableau ---
 dict(t=(36.3, 41.0), box=(180, 205, 900, 330), en=[("Very ", S), ("different", SI)], fr=[("Très ", S, None), ("différents", SI, None)], align='c'),
 dict(t=(36.3, 41.0), box=(180, 331, 900, 455), en=[("where it counts", S)], fr=[("là où ça compte", S, None)], align='c'),
 dict(t=(36.3, 41.0), box=(80, 722, 335, 795), en=[("Pricing", S)], fr=[("Prix", S, None)], align='l', couleur='live', k=41),
 dict(t=(36.3, 41.0), box=(80, 882, 335, 955), en=[("Privacy", S)], fr=[("Confidentialité", S, None)], align='l', couleur='live', k=41, maxw=250),
 dict(t=(36.3, 41.0), box=(80, 1042, 335, 1118), en=[("Strengths", S)], fr=[("Points forts", S, None)], align='l', couleur='live', k=41, maxw=250),
 dict(t=(36.3, 41.0), box=(80, 1200, 335, 1276), en=[("Limitations", S)], fr=[("Limites", S, None)], align='l', couleur='live', k=41),
 dict(t=(36.3, 41.0), box=(355, 728, 515, 760), couleur='live', en=[("Pro tier", SB)], fr=[("Offre Pro", SB, None)], align='c', k=31),
 dict(t=(36.3, 41.0), box=(355, 764, 515, 794), couleur='live', en=[("from $100/mo", 'sans-m')], fr=[("dès 100 $/mois", 'sans-m', None)], align='c', k=31),
 dict(t=(36.3, 41.0), box=(575, 728, 740, 760), couleur='live', en=[("Free tier", SB)], fr=[("Gratuit", SB, None)], align='c', k=31),
 dict(t=(36.3, 41.0), box=(565, 764, 750, 794), couleur='live', en=[("paid plans exist", 'sans-m')], fr=[("+ offres payantes", 'sans-m', None)], align='c', k=31),
 dict(t=(36.3, 41.0), box=(800, 764, 960, 794), couleur='live', en=[("$30/mo", 'sans-m')], fr=[("30 $/mois", 'sans-m', None)], align='c', k=31),
 # --- 8. The full comparison ---
 dict(t=(41.0, 46.3), box=(100, 200, 985, 350), en=[("The full ", S), ("comparison", SI)], fr=[("Le comparatif ", S, None), ("complet", SI, None)], align='c'),
 dict(t=(41.0, 46.3), puces=[[(60, 1300, 222, 1358), (238, 1300, 377, 1358), (389, 1300, 532, 1358), (548, 1300, 750, 1358), (762, 1300, 992, 1358)]],
      labels=[["10 pages", "Prix", "Vie privée", "Pour & contre", "3 alternatives"]], police='sans-m', taille=29),
 # --- 9. CTA ---
 dict(t=(46.3, 50.1), box=(300, 225, 790, 362), en=[("Comment", S)], fr=[("Commente", S, None)], align='c'),
 dict(t=(46.3, 50.1), box=(850, 745, 960, 795), en=[("Post", SB)], fr=[("Publier", SB, None)], align='r', k=31),
 dict(t=(46.3, 50.1), box=(210, 955, 560, 985), en=[("sent you a message · now", 'sans-m')], fr=[("t'a envoyé un message · à l'instant", 'sans-m', None)], align='l', k=31, maxw=420),
 dict(t=(46.3, 50.1), box=(140, 1040, 620, 1090), en=[("Here's your AI agent guide", SA)], fr=[("Voici ton guide des agents IA", SA, None)], align='l', k=31),
 dict(t=(46.3, 50.1), box=(295, 1142, 640, 1190), en=[("The New AI Agents", SB)], fr=[("Les nouveaux agents IA", SB, None)], align='l', k=31),
]
