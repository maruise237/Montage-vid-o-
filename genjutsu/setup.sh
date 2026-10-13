#!/usr/bin/env bash
# Installe le flux gratuit, et optionnellement le Genjustsu d'origine (payant : Enhancor + Replicate) dans upstream/.
set -euo pipefail
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || { echo "Installe ffmpeg (brew install ffmpeg / sudo apt install ffmpeg)"; exit 1; }
[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip install -q gradio_client==2.7.2
if [ "${AVEC_ORIGINAL:-0}" = "1" ] && [ ! -d upstream ]; then
  git clone --depth 1 https://github.com/sirioberati/Genjustsu-Open-Source-Workflow.git upstream
fi
[ -f .env ] || { printf 'HF_TOKEN=\n' > .env; chmod 600 .env; }
.venv/bin/python gratuit.py check
