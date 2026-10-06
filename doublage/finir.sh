#!/bin/bash
# vidéo FR + mix FR -> livrables (HD 60 i/s + version légère à partager)
cd "$(dirname "$0")"
ffmpeg -v error -y -i rendu/video_fr.mp4 -i rendu/mix_fr.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest ../reel_doublage_fr.mp4
ffmpeg -v error -y -i ../reel_doublage_fr.mp4 -vf fps=30 -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 128k ../reel_doublage_fr_partage.mp4
ls -la ../reel_doublage_fr*.mp4
