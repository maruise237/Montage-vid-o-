import sys, json, subprocess, os, re
sys.path.insert(0, '.')
from script_fr import PHRASES
V = sys.argv[1] if len(sys.argv) > 1 else 'fr-FR-RemyMultilingualNeural'
RATE = sys.argv[2] if len(sys.argv) > 2 else '+6%'
for i, ph in enumerate(PHRASES):
    txt = ' '.join(c for _, c in ph)
    dit = re.sub(r"\bIA\b", 'I.A.', txt)
    subprocess.run(['python3', 'outils_d/tts_edge.py', V, dit, f'voix/p{i}.mp3', RATE], check=True)
    m = json.load(open(f'voix/p{i}.json'))
    print(i, round(m[-1][2], 2), 's |', txt)
