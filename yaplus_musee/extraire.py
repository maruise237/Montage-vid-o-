"""Décode une réponse treg (TTS Gemini en base64 ou musique) sauvegardée dans tool-results → fichier audio."""
import json, sys, base64
src, dst = sys.argv[1:3]
d = json.load(open(src))
for p in d['body']['candidates'][0]['content']['parts']:
    if 'inlineData' in p:
        open(dst, 'wb').write(base64.b64decode(p['inlineData']['data'])); break
print(dst, 'coût', d.get('cost_usd'))
