#!/usr/bin/env bash
# Génère toute la vidéo par morceaux de 33 images (16 i/s), 4 images de recouvrement pour la continuité.
# Usage : tout.sh DOSSIER  (DOSSIER contient src16.mp4, mask16.mp4, poses.npy, reference.png)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; PY="${PY:-$HERE/.venv/bin/python}"
cd "$1"
N=$(ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 src16.mp4)
L=33; R=4; STEP=$((L-R)); prev=""; k=0
for ((d=0; d+R<N; d+=STEP)); do
  out=$(printf "morceau_%02d.mp4" $k)
  if [ ! -s "$out" ]; then
    echo "=== morceau $k (images $d..$((d+L-1))) $(date +%H:%M)"
    "$PY" -W ignore "$HERE/genere.py" src16.mp4 mask16.mp4 reference.png "$out" --debut $d --frames $L \
      --steps 4 --cond 0.75 --amincir 1 --pose-cache poses.npy ${prev:+--suite $prev --recouvre $R} 2>&1 \
      | tr '\r' '\n' | grep -i "étape\|génération\|^ok\|error\|trace\|killed"
    [ -s "$out" ] || { echo "ÉCHEC morceau $k"; exit 1; }
  fi
  prev=$out; k=$((k+1))
done
echo "TOUT FINI $(date +%H:%M)"
