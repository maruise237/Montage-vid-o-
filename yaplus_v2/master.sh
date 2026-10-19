#!/bin/sh
# Mastering du mix (≈ -14 LUFS) puis encodage final + version partage 720p
set -e
ffmpeg -v error -y -i mix_brut.wav -af "acompressor=threshold=0.1:ratio=2.5:attack=1:release=120:knee=6,volume=12.2dB,alimiter=limit=0.84:attack=1:release=70:level=false" -ar 48000 mix.wav
ffmpeg -hide_banner -i mix.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
ffmpeg -v error -y -framerate 30 -i frames/%05d.jpg -i mix.wav -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart Yaplus_v2.mp4
ffmpeg -v error -y -i Yaplus_v2.mp4 -c:v libx264 -preset slow -crf 25 -vf scale=720:-2 -c:a aac -b:a 128k -movflags +faststart Yaplus_v2_partage.mp4
ls -la *.mp4
