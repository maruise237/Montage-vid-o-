"""Masque du personnage principal sur toute la vidéo (SAM2 video, CPU)."""
import sys, numpy as np, torch, imageio.v3 as iio
from transformers import Sam2VideoModel, Sam2VideoProcessor

src, out, box = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
frames = iio.imread(src, plugin='pyav')
model_id = 'facebook/sam2.1-hiera-small'
model = Sam2VideoModel.from_pretrained(model_id).eval()
proc = Sam2VideoProcessor.from_pretrained(model_id)
session = proc.init_video_session(video=list(frames), inference_device='cpu', dtype=torch.float32)
proc.add_inputs_to_inference_session(inference_session=session, frame_idx=0, obj_ids=1, input_boxes=[[box]])
masks = {}
with torch.inference_mode():
    model(inference_session=session, frame_idx=0)
    for o in model.propagate_in_video_iterator(session):
        m = proc.post_process_masks([o.pred_masks], original_sizes=[[session.video_height, session.video_width]], binarize=True)[0]
        masks[o.frame_idx] = (m[0, 0].numpy() * 255).astype(np.uint8)
        if o.frame_idx % 40 == 0:
            print('frame', o.frame_idx, flush=True)
arr = np.stack([masks[i] for i in range(len(frames))])
np.save(out.replace('.mp4', '.npy'), arr)
iio.imwrite(out, np.repeat(arr[..., None], 3, axis=-1), fps=16, codec='libx264', plugin='pyav',
            out_pixel_format='yuv420p')
print('ok', len(masks))
