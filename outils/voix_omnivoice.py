"""Voix off locale et gratuite avec OmniVoice (moteur de VoiceStudio), sur CPU.

Installation : pip install torch torchaudio (index CPU) "transformers>=5.10" soundfile,
plus le dépôt github.com/debpalash/VoiceStudio dans PYTHONPATH.
Usage : python voix_omnivoice.py REF_AUDIO REF_TEXT PREFIXE_SORTIE "texte 1" ["texte 2" ...]
"""
import sys

import soundfile as sf
import torch

from omnivoice.models.omnivoice import OmniVoice

ref_audio, ref_text, out_prefix, *texts = sys.argv[1:]

model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
for i, text in enumerate(texts, 1):
    audio = model.generate(text=text, language="fr", ref_audio=ref_audio, ref_text=ref_text)[0]
    out = f"{out_prefix}_{i}.wav"
    sf.write(out, audio.squeeze(0).cpu().numpy(), model.sampling_rate)
    print("saved", out, flush=True)
