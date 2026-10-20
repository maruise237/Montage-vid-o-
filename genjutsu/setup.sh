#!/usr/bin/env bash
# Installe FaceFusion (open source, tourne sur processeur) à une version figée. Aucune clé, aucune interface.
set -euo pipefail
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || { echo "Installe ffmpeg"; exit 1; }
PY="${PYTHON:-python3.12}"
if [ ! -d facefusion ]; then
  git clone https://github.com/facefusion/facefusion.git facefusion
  git -C facefusion checkout -q 72470819a0373be3388b3929c8f8f311f418fc3c
fi
[ -d facefusion/.venv ] || "$PY" -m venv facefusion/.venv
facefusion/.venv/bin/pip install -q -r facefusion/requirements.txt
echo "Prêt. Les modèles (~1 Go) se téléchargent depuis Hugging Face au premier lancement."
