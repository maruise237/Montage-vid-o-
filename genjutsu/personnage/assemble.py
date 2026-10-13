"""Colle les morceaux en fondant les 4 images communes, puis 720x1280, 24 i/s, son d'origine."""
import glob, subprocess, numpy as np, imageio.v3 as iio

R = 4
chunks = [iio.imread(f, plugin='pyav') for f in sorted(glob.glob('morceau_[0-9][0-9].mp4'))]
out = list(chunks[0])
for c in chunks[1:]:
    for i in range(R):  # fondu linéaire sur le recouvrement
        w = (i + 1) / (R + 1)
        out[-R + i] = ((1 - w) * out[-R + i] + w * c[i]).astype(np.uint8)
    out.extend(c[R:])
iio.imwrite('genere16.mp4', np.stack(out), fps=16, codec='libx264', plugin='pyav', out_pixel_format='yuv420p')
print(len(out), 'images')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'genere16.mp4', '-i', 'reel.mp4', '-map', '0:v', '-map', '1:a',
                '-vf', 'scale=720:1280:flags=lanczos,fps=24,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow',
                '-crf', '18', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', 'reel_kelvin.mp4'], check=True)
