import json,os,sys,base64,urllib.request
VOIX=sys.argv[2] if len(sys.argv)>2 else 'nbiTBaMRdSobTQJDzIWm'
k=sys.argv[1]; txt=json.load(open('reponses.json'))[k]
body=json.dumps({"text":txt,"model_id":"eleven_multilingual_v2",
 "voice_settings":{"stability":0.42,"similarity_boost":0.8,"style":0.35,"use_speaker_boost":True}}).encode()
req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOIX}/with-timestamps?output_format=mp3_44100_128",
 data=body,headers={"xi-api-key":os.environ["ELEVENLABS"],"Content-Type":"application/json"})
try: d=json.load(urllib.request.urlopen(req))
except urllib.error.HTTPError as e: print(e.code,e.read()[:400]);sys.exit(1)
open(f'voix/{k}.mp3','wb').write(base64.b64decode(d['audio_base64']))
a=d['alignment'];ch,st,en=a['characters'],a['character_start_times_seconds'],a['character_end_times_seconds']
mots=[];cur='';s=None
for c,a0,a1 in zip(ch,st,en):
  if c.isspace():
    if cur: mots.append([cur,s,e]);cur=''
    continue
  if not cur: s=a0
  cur+=c;e=a1
if cur: mots.append([cur,s,e])
json.dump(mots,open(f'voix/{k}.json','w'),ensure_ascii=False)
print(k,len(mots),'mots',round(mots[-1][2],2),'s')
