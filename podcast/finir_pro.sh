#!/bin/sh
# Assemble image + son du remontage pro, normalisé à -14 LUFS.  Usage : V=_court sh podcast/finir_pro.sh
cd "$(dirname "$0")"
V=${V:-}
python3 son_pro.py && \
ffmpeg -v error -y -i pro${V}_muet.mp4 -i son_pro${V}.wav -map 0:v -map 1:a \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest \
  ../podcast_claude${V}_pro.mp4 && \
ffmpeg -i ../podcast_claude${V}_pro.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness" | tail -1
