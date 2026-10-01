# Valex L'infographiste — vidéo motion design (9:16, 36 s)

- `valex_motion_design.mp4` : vidéo finale 1080×1920, 30 fps, son stéréo (-14 LUFS)
- `index.html` : animation (timeline déterministe, textes modifiables)
- `make_audio.py` : beat + bruitages synthétisés
- `render.js` : rendu image par image (Playwright) ; assemblage : voir commande ffmpeg ci-dessous

```
npm i && python3 make_audio.py && node render.js
ffmpeg -framerate 30 -i build/frames/f%05d.jpg -i build/audio.wav -af loudnorm=I=-14:TP=-1.5 \
  -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -shortest valex_motion_design.mp4
```
