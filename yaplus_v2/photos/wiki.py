"""Recherche Wikimedia Commons (photos, licence libre) → planche numérotée + méta (auteur, licence)."""
import json, sys, urllib.request, urllib.parse, io, time
from PIL import Image, ImageDraw
UA = {'User-Agent': 'MontageYaplus/1.0 (maruise237@gmail.com)'}
def get(u):
    for k in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        except Exception as e:
            if '429' in str(e): time.sleep(3 * (k + 1)); continue
            raise
sujet, *qs = sys.argv[1:]
pages = []
for q in qs:
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'generator': 'search', 'gsrsearch': q + ' filetype:bitmap', 'gsrnamespace': 6, 'gsrlimit': 15, 'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size', 'iiurlwidth': 300, 'format': 'json'})
    d = json.loads(get(u)); pages += sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))
    time.sleep(1)
vus, ims = set(), []
for p in pages:
    ii = p['imageinfo'][0]
    if ii['url'] in vus: continue
    vus.add(ii['url']); md = ii.get('extmetadata', {})
    lic = md.get('LicenseShortName', {}).get('value', '?')
    try: im = Image.open(io.BytesIO(get(ii['thumburl']))).convert('RGB'); im.thumbnail((300, 300)); time.sleep(.3)
    except Exception: continue
    ims.append((im, {'url': ii['url'], 'w': ii['width'], 'h': ii['height'], 'licence': lic, 'auteur': md.get('Artist', {}).get('value', '')[:200], 'page': ii['descriptionurl'], 'titre': p['title']}))
    if len(ims) >= 30: break
W = Image.new('RGB', (300 * 6, 330 * ((len(ims) + 5) // 6)), 'white'); d = ImageDraw.Draw(W)
for i, (im, m) in enumerate(ims):
    x, y = (i % 6) * 300, (i // 6) * 330; W.paste(im, (x, y)); d.text((x + 4, y + 304), f"{i} {m['licence']} {m['w']}px", fill='black')
W.save(f'cand/w_{sujet}.jpg', quality=80); json.dump([m for _, m in ims], open(f'cand/w_{sujet}.json', 'w'), ensure_ascii=False, indent=1)
print(sujet, len(ims))
