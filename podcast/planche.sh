#!/bin/bash
# ./planche.sh t1 t2 ... -> planche/planche.jpg (étiquette de temps sur chaque vignette)
cd "$(dirname "$0")"; rm -rf planche; node rendu.mjs "$@" || exit 1
n=$#; cols=$(( n<=8 ? 4 : 5 )); in=(); f=""; i=0
for t in "$@"; do p=$(printf 'planche/p%02d.jpg' $i); in+=(-i $p)
 f+="[$i:v]scale=270:480,drawtext=text='$t':x=8:y=8:fontsize=26:fontcolor=yellow:box=1:boxcolor=black@0.7[v$i];"; i=$((i+1)); done
lay=""; for ((k=0;k<n;k++)); do lay+="$(( (k%cols)*270 ))_$(( (k/cols)*480 ))|"; done
s=""; for ((k=0;k<n;k++)); do s+="[v$k]"; done
ffmpeg -v error -y "${in[@]}" -filter_complex "${f}${s}xstack=inputs=$n:layout=${lay%|}:fill=black" planche/planche.jpg && echo planche/planche.jpg
