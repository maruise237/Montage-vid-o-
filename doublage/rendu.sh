#!/bin/bash
# rendu parallèle en 4 segments puis concaténation
cd "$(dirname "$0")"
D=50.0; N=4; S=$(python3 -c "print($D/$N)")
for i in $(seq 0 $((N-1))); do
  T0=$(python3 -c "print($i*$S)")
  python3 doubler.py segment $T0 $S rendu/seg$i.mp4 2>rendu/seg$i.log &
done
wait
for i in $(seq 0 $((N-1))); do echo "file 'seg$i.mp4'"; done > rendu/liste.txt
ffmpeg -v error -y -f concat -safe 0 -i rendu/liste.txt -c copy rendu/video_fr.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 rendu/video_fr.mp4
