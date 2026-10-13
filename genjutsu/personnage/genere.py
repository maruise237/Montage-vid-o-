"""Remplace le personnage entier avec Wan2.1-VACE-1.3B (CPU).

Le masque (dilaté) indique la zone à redessiner ; dans cette zone on met le squelette OpenPose du
personnage d'origine, hors zone la vidéo d'origine est gardée. La référence donne l'identité et les habits.

  python genere.py SRC16.mp4 MASK16.mp4 REF.png OUT.mp4 --debut 0 --frames 81 --steps 6 [--suite PREV.mp4]
"""
import argparse, time, numpy as np, torch, cv2, imageio.v3 as iio
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('src'); p.add_argument('mask'); p.add_argument('ref'); p.add_argument('out')
p.add_argument('--debut', type=int, default=0); p.add_argument('--frames', type=int, default=81)
p.add_argument('--steps', type=int, default=6); p.add_argument('--dilate', type=int, default=21)
p.add_argument('--suite', help='clip précédent généré : ses dernières images servent de départ')
p.add_argument('--recouvre', type=int, default=8)
p.add_argument('--cond', type=float, default=1.0)
p.add_argument('--amincir', type=int, default=0)
p.add_argument('--lora', type=float, default=0.7)
p.add_argument('--pose-cache', default=None)
p.add_argument('--pose-seule', action='store_true')
a = p.parse_args()
W, H = 480, 832
torch.set_num_threads(4)

src = iio.imread(a.src, plugin='pyav')[a.debut:a.debut + a.frames]
msk = iio.imread(a.mask, plugin='pyav')[a.debut:a.debut + a.frames]
n = len(src)
n = (n - 1) // 4 * 4 + 1  # VACE : 4k+1 images
src, msk = src[:n], msk[:n]
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (a.dilate, a.dilate))
masks = [cv2.dilate((m[..., 0] > 127).astype(np.uint8), kernel) for m in msk]

# Squelette du seul personnage principal : OpenPose sur l'image où tout le reste est noirci.
import os
cache = a.pose_cache
if cache and os.path.exists(cache):
    poses = list(np.load(cache)[a.debut:a.debut + n])
else:
    from controlnet_aux import OpenposeDetector
    det = OpenposeDetector.from_pretrained('lllyasviel/Annotators')
    allsrc = iio.imread(a.src, plugin='pyav'); allmsk = iio.imread(a.mask, plugin='pyav')
    poses = []
    t0 = time.time()
    for f, mm in zip(allsrc, allmsk):
        m = cv2.dilate((mm[..., 0] > 127).astype(np.uint8), kernel)
        iso = (f * m[..., None]).astype(np.uint8)
        pose = det(Image.fromarray(iso), detect_resolution=512, image_resolution=max(W, H), include_hand=False, include_face=False)
        poses.append(np.array(pose.resize((W, H))))
    print(f'pose {len(poses)} images en {time.time() - t0:.0f} s', flush=True)
    if cache:
        np.save(cache, np.stack(poses))
    poses = poses[a.debut:a.debut + n]
if a.pose_seule:
    raise SystemExit(0)
if a.amincir:  # traits du squelette plus fins : moins de couleur qui déteint sur les habits
    k3 = np.ones((3, 3), np.uint8)
    poses = [cv2.erode(po, k3, iterations=a.amincir) for po in poses]

video, mask_out = [], []
for f, m, po in zip(src, masks, poses):
    m3 = m[..., None].astype(bool)
    video.append(Image.fromarray(np.where(m3, po, f).astype(np.uint8)))
    mask_out.append(Image.fromarray((m * 255).astype(np.uint8)))

if a.suite:  # continuité : les premières images = fin du clip précédent, à ne pas redessiner
    prev = iio.imread(a.suite, plugin='pyav')[-a.recouvre:]
    for i, pf in enumerate(prev):
        video[i] = Image.fromarray(pf)
        mask_out[i] = Image.new('L', (W, H), 0)

ref = Image.open(a.ref).convert('RGB')
canvas = Image.new('RGB', (W, H), 'white')
ref.thumbnail((W, H))
canvas.paste(ref, ((W - ref.width) // 2, (H - ref.height) // 2))

prompt = ('A young African man, slim athletic build, very short clean fade haircut, wearing a black graphic t-shirt '
          'with blue and white abstract design and small logo, brown chino pants, black crossbody bag, black and gray sneakers, '
          'playing football on a stadium pitch at night, dynamic motion, realistic, sharp details')
neg = 'robe, gown, hat, cap, sunglasses, blurry, deformed, extra limbs, low quality, cartoon, text, watermark'
from diffusers import WanVACEPipeline, AutoencoderKLWan
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler
M = os.environ.get('GENJUTSU_MODELS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')) + '/vace13'
vae = AutoencoderKLWan.from_pretrained(M, subfolder='vae', torch_dtype=torch.float32)
emb = M + '/../prompt_embeds.pt'
if not os.path.exists(emb):
    from transformers import UMT5EncoderModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(M, subfolder='tokenizer')
    te = UMT5EncoderModel.from_pretrained(M, subfolder='text_encoder', torch_dtype=torch.bfloat16, low_cpu_mem_usage=True)
    def enc(t):
        ids = tok([t], padding='max_length', max_length=512, truncation=True, return_tensors='pt')
        with torch.inference_mode():
            h = te(ids.input_ids, ids.attention_mask).last_hidden_state.clone()
            L = int(ids.attention_mask.sum()); h[:, L:] = 0
        return h
    torch.save({'p': enc(prompt), 'n': enc(neg)}, emb)
    del te
    raise SystemExit('embeddings prêts, relance')
E = torch.load(emb)
pipe = WanVACEPipeline.from_pretrained(M, vae=vae, text_encoder=None, tokenizer=None, torch_dtype=torch.float32)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=3.0)
pipe.load_lora_weights(os.environ.get('GENJUTSU_MODELS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')) + '/lora/causvid_1_3b.safetensors', adapter_name='causvid')
pipe.set_adapters(['causvid'], [a.lora])

t0 = time.time()
step_t = [time.time()]
def cb(pipe_, i, t, kw):
    step_t.append(time.time()); print(f'étape {i + 1}/{a.steps} {step_t[-1] - step_t[-2]:.0f} s', flush=True); return kw
with torch.inference_mode():
    out = pipe(video=video, mask=mask_out, reference_images=[canvas], prompt_embeds=E['p'].float(), negative_prompt_embeds=E['n'].float(),
               height=H, width=W, num_frames=n, num_inference_steps=a.steps, guidance_scale=1.0,
               conditioning_scale=a.cond, generator=torch.Generator().manual_seed(42),
               callback_on_step_end=cb, output_type='np').frames[0]
print(f'génération {time.time() - t0:.0f} s', flush=True)
iio.imwrite(a.out, (out * 255).clip(0, 255).astype(np.uint8), fps=16, codec='libx264', plugin='pyav', out_pixel_format='yuv420p')
iio.imwrite(a.out.replace('.mp4', '_guide.mp4'), np.stack([np.array(v) for v in video]), fps=16, codec='libx264', plugin='pyav', out_pixel_format='yuv420p')
print('ok', a.out)
