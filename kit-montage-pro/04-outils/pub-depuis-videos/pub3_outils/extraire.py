"""Extrait l'audio (WAV/MP3 base64) d'une réponse treg sauvegardée → fichier."""
import json, base64, sys
r = json.load(open(sys.argv[1]))
print('cout', r.get('cost_usd'), 'statut', r.get('status'))
b = r['body']
parts = b['candidates'][0]['content']['parts']
for p in parts:
    if 'text' in p: print('texte:', p['text'][:400])
    if 'inlineData' in p:
        open(sys.argv[2], 'wb').write(base64.b64decode(p['inlineData']['data'])); print('->', sys.argv[2], p['inlineData']['mimeType'])
print(b.get('usageMetadata'))
