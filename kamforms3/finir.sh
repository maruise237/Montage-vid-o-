#!/bin/sh
# Rendu image (4 segments en parallèle, 60 i/s) + son, -14 LUFS → ../reel_kamforms_apkpure.mp4 (+ copie légère)
cd "$(dirname "$0")"
node rendu.mjs sons && python3 son.py || exit 1
N=$(python3 -c "import json;print(round(json.load(open('timeline.json'))['duree']*60))"); Q=$(( (N+3)/4 ))
for i in 0 1 2 3; do node rendu.mjs seg $((i*Q)) $(( (i+1)*Q < N ? (i+1)*Q : N )) seg$i.mp4 & done; wait
printf "file seg0.mp4\nfile seg1.mp4\nfile seg2.mp4\nfile seg3.mp4\n" > segs.txt
ffmpeg -v error -y -f concat -i segs.txt -c copy muet.mp4 && \
ffmpeg -v error -y -i muet.mp4 -i son.wav -map 0:v -map 1:a -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest ../reel_kamforms_apkpure.mp4 && \
ffmpeg -v error -y -i ../reel_kamforms_apkpure.mp4 -vf "scale=720:1280,fps=30" -c:v libx264 -crf 22 -preset medium -c:a copy ../reel_kamforms_apkpure_partage.mp4 && \
rm -f seg?.mp4 segs.txt && \
ffmpeg -i ../reel_kamforms_apkpure.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness" | tail -1
