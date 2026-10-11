#!/bin/sh
# Image + son, -14 LUFS → video_avatar_1.mp4 (+ copie 720p à partager)
cd "$(dirname "$0")"
python3 son.py && \
ffmpeg -v error -y -i muet.mp4 -i son.wav -map 0:v -map 1:a -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest ../video_avatar_1.mp4 && \
ffmpeg -v error -y -i ../video_avatar_1.mp4 -vf scale=720:1280 -c:v libx264 -crf 22 -preset medium -c:a copy ../video_avatar_1_partage.mp4 && \
ffmpeg -i ../video_avatar_1.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness" | tail -1
