"""Cherche des photos sous licence libre (Openverse : Flickr CC, Wikimedia) et fait une planche par sujet."""
import json, sys, urllib.request, urllib.parse, io, os
from PIL import Image, ImageDraw
UA = {'User-Agent': 'Mozilla/5.0 (montage Yaplus)'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
sujet, *qs = sys.argv[1:]
res = []
for q in qs:
    u = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode({'q': q, 'license_type': 'commercial', 'page_size': 12, 'mature': 'false'})
    try: res += json.loads(get(u))['results']
    except Exception as e: print('err', q, e)
vus, ims = set(), []
for r in res:
    if r['url'] in vus: continue
    vus.add(r['url'])
    try:
        im = Image.open(io.BytesIO(get(r.get('thumbnail') or r['url']))).convert('RGB'); im.thumbnail((300, 300))
        ims.append((im, r))
    except Exception: pass
    if len(ims) >= 24: break
W = Image.new('RGB', (300 * 6, 330 * ((len(ims) + 5) // 6)), 'white'); d = ImageDraw.Draw(W)
meta = []
for i, (im, r) in enumerate(ims):
    x, y = (i % 6) * 300, (i // 6) * 330; W.paste(im, (x, y)); d.text((x + 4, y + 304), f"{i} {r['license']} {r['source']}", fill='black')
    meta.append({'i': i, 'url': r['url'], 'license': r['license'], 'version': r.get('license_version'), 'creator': r.get('creator'), 'titre': r['title'], 'page': r.get('foreign_landing_url')})
W.save(f'cand/{sujet}.jpg', quality=80); json.dump(meta, open(f'cand/{sujet}.json', 'w'), ensure_ascii=False, indent=1)
print(sujet, len(ims))
