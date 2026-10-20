#!/usr/bin/env bash
# Environnement CPU + poids (~19 Go) : Wan2.1-VACE-1.3B, LoRA CausVid 1.3B. Aucune clé.
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || python3.12 -m venv .venv
.venv/bin/pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -q diffusers transformers accelerate sentencepiece ftfy imageio imageio-ffmpeg av \
  opencv-python-headless peft huggingface_hub controlnet_aux matplotlib
.venv/bin/python -c "from huggingface_hub import snapshot_download as s; s('Wan-AI/Wan2.1-VACE-1.3B-diffusers', local_dir='models/vace13', allow_patterns=['*.json','*.safetensors','tokenizer/*','scheduler/*'])"
mkdir -p models/lora
[ -s models/lora/causvid_1_3b.safetensors ] || curl -sL -o models/lora/causvid_1_3b.safetensors \
  https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan21_CausVid_bidirect2_T2V_1_3B_lora_rank32.safetensors
