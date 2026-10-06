#!/bin/bash
# Voix FR "améliorée" (EQ + compression + présence) + musique/bruitages d'origine sans la voix anglaise -> -14 LUFS
cd "$(dirname "$0")"
ffmpeg -v error -y -i voix/voix_fr.wav -af "highpass=f=75,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.0:g=2.5,highshelf=f=9000:g=2,deesser=i=0.35,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,aecho=0.9:0.9:28:0.05" -ar 44100 voix/voix_fr_pro.wav
# niveau : voix FR au niveau de la voix anglaise d'origine (-14,3 LUFS)
ffmpeg -v error -y -i voix/voix_fr_pro.wav -af loudnorm=I=-14.3:TP=-1.5:LRA=7 -ar 44100 voix/voix_fr_n.wav
ffmpeg -v error -y -i voix/voix_fr_n.wav -i src/sep/htdemucs/audio/no_vocals.wav \
  -filter_complex "[0:a]aformat=channel_layouts=stereo,apad[v];[1:a]aformat=channel_layouts=stereo[m];[v][m]amix=inputs=2:duration=shortest:normalize=0,loudnorm=I=-14:TP=-1:LRA=9[o]" \
  -map "[o]" -ar 44100 -t 50.04 rendu/mix_fr.wav
ffmpeg -nostats -i rendu/mix_fr.wav -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1
