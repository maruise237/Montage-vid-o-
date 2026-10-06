"""TTS Edge (gratuit) avec horodatage des mots. usage: tts_edge.py VOIX "texte" sortie.mp3 [rate] [pitch]"""
import sys, json, asyncio, certifi
certifi.where = lambda: '/root/.ccr/ca-bundle.crt'
import edge_tts
v, txt, out = sys.argv[1:4]
rate = sys.argv[4] if len(sys.argv) > 4 else '+0%'
pitch = sys.argv[5] if len(sys.argv) > 5 else '+0Hz'
async def main():
    c = edge_tts.Communicate(txt, v, rate=rate, pitch=pitch, boundary='WordBoundary')
    mots = []
    with open(out, 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio': f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                mots.append([ch['text'], ch['offset']/1e7, (ch['offset']+ch['duration'])/1e7])
    json.dump(mots, open(out.rsplit('.',1)[0]+'.json','w'), ensure_ascii=False)
asyncio.run(main())
