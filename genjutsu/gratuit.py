"""Flux Genjutsu sans clé payante : remplacement de personnage via Wan2.2-Animate (Hugging Face ZeroGPU).

  python gratuit.py check
  python gratuit.py swap SOURCE.mp4 REFERENCE.png --secondes 4 --res low
  python gratuit.py finalise runs/<id>

Rien n'est payant. Le seul quota consommé est le quota ZeroGPU gratuit du compte
Hugging Face dont le jeton est dans HF_TOKEN (sans jeton, le quota anonyme est souvent à 0).
"""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / 'runs'
# Seul Space Wan2.2-Animate gratuit sur GPU en ligne au 13/10/2026. Autre copie : GENJUTSU_SPACE=owner/nom
SPACES = [os.getenv('GENJUTSU_SPACE', 'alexnasa/Wan2.2-Animate-ZEROGPU')]
# Secondes de GPU demandées par le Space (table calculate_time_required, x0,5 en Low Res)
GPU_S = {2: 110, 3: 150, 4: 150, 5: 150, 6: 210, 7: 220, 8: 260, 9: 270, 10: 270, 11: 320, 12: 340,
         13: 360, 14: 390, 15: 390, 16: 450, 17: 460, 18: 470, 19: 480, 20: 500}
OUTPUTS = ['resultat_brut', 'pose', 'fond', 'masque', 'visage']


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate:format=duration',
                          '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    video = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
    if not video:
        raise SystemExit(f'{path} : aucune piste vidéo')
    return {'width': video['width'], 'height': video['height'], 'duration': float(data['format']['duration']),
            'audio': any(s['codec_type'] == 'audio' for s in data['streams'])}


def gpu_seconds(secondes, res):
    return int(GPU_S[secondes] * (1.0 if res == 'medium' else 0.5))


def token():
    value = os.getenv('HF_TOKEN', '').strip()
    if not value:
        env = ROOT / '.env'
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith('HF_TOKEN='):
                    value = line.split('=', 1)[1].strip()
    return value or None


def check(_args):
    ok = True
    for tool in ['ffmpeg', 'ffprobe']:
        found = shutil.which(tool)
        print(f'{tool}: ' + ('OK' if found else 'MANQUANT'))
        ok = ok and bool(found)
    try:
        import gradio_client  # noqa: F401
        print('gradio_client: OK')
    except ImportError:
        print('gradio_client: MANQUANT (bash setup.sh)'); ok = False
    print('HF_TOKEN: ' + ('présent (non affiché)' if token() else 'ABSENT — quota ZeroGPU anonyme, souvent épuisé'))
    if ok:
        from gradio_client import Client
        for space in SPACES:
            try:
                api = Client(space, token=token(), verbose=False).view_api(print_info=False, return_format='dict')
                print(f'{space}: en ligne, endpoints {list(api["named_endpoints"])}')
            except Exception as exc:
                print(f'{space}: indisponible ({type(exc).__name__})')
    return 0 if ok else 1


def swap(args):
    source, reference = Path(args.source).resolve(), Path(args.reference).resolve()
    info = probe(source)
    secondes = max(2, min(20, args.secondes or int(info['duration'])))
    if secondes > info['duration'] + 0.5:
        raise SystemExit(f'La source dure {info["duration"]:.1f} s, impossible d\'en générer {secondes} s')
    job = RUNS / time.strftime('%Y%m%d-%H%M%S')
    job.mkdir(parents=True)
    shutil.copy(source, job / ('source' + source.suffix.lower()))
    shutil.copy(reference, job / ('reference' + reference.suffix.lower()))
    meta = {'source': source.name, 'reference': reference.name, 'source_info': info, 'secondes': secondes,
            'res': args.res, 'mode': 'Character Swap', 'gpu_s_demandees': gpu_seconds(secondes, args.res)}
    (job / 'job.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f'Job {job.name} : {secondes} s, {args.res}, ~{meta["gpu_s_demandees"]} s de quota ZeroGPU')

    from gradio_client import Client, handle_file
    errors = []
    for space in SPACES:
        try:
            print(f'Envoi à {space} (file d\'attente possible)…', flush=True)
            client = Client(space, token=token(), verbose=False)
            result = client.predict(handle_file(str(job / ('source' + source.suffix.lower()))), secondes,
                                    handle_file(str(job / ('reference' + reference.suffix.lower()))), 'Character Swap',
                                    'Medium Res' if args.res == 'medium' else 'Low Res', api_name='/animate_scene')
            break
        except Exception as exc:
            errors.append(f'{space}: {exc}')
            print(f'Échec sur {space} : {exc}', flush=True)
            if 'quota' in str(exc).lower():
                break
    else:
        result = None
    if result is None:
        meta['erreurs'] = errors
        (job / 'job.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        raise SystemExit('Génération impossible : ' + ' | '.join(errors) +
                         '\nCause la plus fréquente : quota ZeroGPU épuisé ou HF_TOKEN absent. Réessaie plus tard ou ajoute ton jeton.')

    for name, item in zip(OUTPUTS, result):
        path = item.get('video') if isinstance(item, dict) else item
        if path:
            shutil.copy(path, job / f'{name}.mp4')
    meta['space'] = space
    (job / 'job.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    args.job = str(job)
    return finalise(args)


def finalise(args):
    job = Path(args.job).resolve()
    meta = json.loads((job / 'job.json').read_text())
    source = next(job.glob('source.*'))
    raw = job / 'resultat_brut.mp4'
    out = probe(raw)
    src = meta['source_info']
    # Remet la résolution de la source et TOUT le son d'origine, sans le son généré.
    scale = f'scale={src["width"]}:{src["height"]}:flags=lanczos'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-i', str(source), '-map', '0:v:0']
    if src['audio']:
        cmd += ['-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k']
    cmd += ['-vf', scale + ',format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
            '-t', f'{out["duration"]:.3f}', '-movflags', '+faststart', str(job / 'final.mp4')]
    run(cmd)
    # Planche de contrôle : source | masque | résultat, 4 instants
    sheet = job / 'planche.jpg'
    d = out['duration']
    frames = []
    for i, t in enumerate([d * k / 5 for k in range(1, 5)]):
        row = job / f'.row{i}.jpg'
        clips = [f for f in [source, job / 'masque.mp4', job / 'final.mp4'] if f.exists()]
        inputs = sum([['-ss', f'{t:.2f}', '-i', str(f)] for f in clips], [])
        filt = ';'.join(f'[{k}:v]scale=-2:360,setsar=1[v{k}]' for k in range(len(clips)))
        filt += ';' + ''.join(f'[v{k}]' for k in range(len(clips))) + f'hstack=inputs={len(clips)}'
        run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', filt, '-frames:v', '1', str(row)])
        frames.append(row)
    run(['ffmpeg', '-v', 'error', '-y', *sum([['-i', str(f)] for f in frames], []), '-filter_complex',
         ''.join(f'[{k}:v]' for k in range(len(frames))) + f'vstack=inputs={len(frames)}', str(sheet)])
    for f in frames:
        f.unlink()
    meta['final'] = 'final.mp4'
    meta['final_info'] = probe(job / 'final.mp4')
    (job / 'job.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f'Terminé : {job / "final.mp4"}\nPlanche de contrôle : {sheet}')
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('check').set_defaults(fn=check)
    s = sub.add_parser('swap'); s.add_argument('source'); s.add_argument('reference')
    s.add_argument('--secondes', type=int, help='2 à 20 (défaut : durée de la source, plafonnée à 20)')
    s.add_argument('--res', choices=['low', 'medium'], default='low', help='low = 640x360, medium = 832x480 (2x plus de quota)')
    s.set_defaults(fn=swap)
    f = sub.add_parser('finalise'); f.add_argument('job'); f.set_defaults(fn=finalise)
    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == '__main__':
    main()
