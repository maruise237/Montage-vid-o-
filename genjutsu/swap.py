"""Remplace le visage d'une vidéo par celui d'une image de référence, en local sur processeur.

  python3 swap.py SOURCE.mp4 REFERENCE.jpg [REFERENCE2.jpg ...] [--sans-enhancer] [--tous-les-visages]

Modèles : hyperswap_1a_256 (remplacement) + gfpgan_1.4 (netteté du visage), via FaceFusion.
Sortie dans runs/<date>/ : final.mp4 (son d'origine complet), comparaison.jpg.
"""
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FF = ROOT / 'facefusion'


def duree(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)['format']['duration'])


def a_du_son(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0',
                          str(path)], capture_output=True, text=True).stdout
    return bool(out.strip())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('source'); p.add_argument('references', nargs='+', help='une ou plusieurs photos du même visage')
    p.add_argument('--sans-enhancer', action='store_true', help='3x plus rapide, visage moins net')
    p.add_argument('--tous-les-visages', action='store_true', help='par défaut seul le plus grand visage de chaque image change')
    args = p.parse_args()
    if not (FF / '.venv').exists():
        subprocess.run(['bash', str(ROOT / 'setup.sh')], check=True)

    source = Path(args.source).resolve()
    references = [Path(r).resolve() for r in args.references]
    reference = references[0]
    job = ROOT / 'runs' / time.strftime('%Y%m%d-%H%M%S')
    job.mkdir(parents=True)
    swapped = job / 'visage_remplace.mp4'
    processors = ['face_swapper'] + ([] if args.sans_enhancer else ['face_enhancer'])
    subprocess.run([str(FF / '.venv/bin/python'), 'facefusion.py', 'headless-run',
                    '--source-paths', *map(str, references),
                    '--face-selector-mode', 'many' if args.tous_les_visages else 'one', '--target-path', str(source), '--output-path', str(swapped),
                    '--processors', *processors, '--face-swapper-model', 'hyperswap_1a_256',
                    '--face-enhancer-model', 'gfpgan_1.4', '--output-video-quality', '90',
                    '--execution-providers', 'cpu', '--execution-thread-count', '4',
                    '--download-providers', 'huggingface', '--log-level', 'warn'], cwd=FF, check=True)

    # Vidéo générée + piste son de la source, copiée telle quelle.
    final = job / 'final.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(swapped), '-i', str(source), '-map', '0:v:0']
    if a_du_son(source):
        cmd += ['-map', '1:a:0', '-c:a', 'copy']
    subprocess.run(cmd + ['-c:v', 'copy', '-movflags', '+faststart', str(final)], check=True)

    # Comparaison : référence | source | résultat, à 3 instants.
    d = duree(final)
    rows = []
    for i, t in enumerate([d * 0.2, d * 0.5, d * 0.8]):
        row = job / f'.row{i}.jpg'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(reference), '-ss', f'{t:.2f}', '-i', str(source),
                        '-ss', f'{t:.2f}', '-i', str(final), '-filter_complex',
                        '[0]scale=-2:480,setsar=1[a];[1]scale=-2:480,setsar=1[b];[2]scale=-2:480,setsar=1[c];[a][b][c]hstack=3',
                        '-frames:v', '1', str(row)], check=True)
        rows.append(row)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *sum([['-i', str(r)] for r in rows], []), '-filter_complex',
                    '[0][1][2]vstack=3', str(job / 'comparaison.jpg')], check=True)
    for r in rows:
        r.unlink()
    for i, r in enumerate(references, 1):
        shutil.copy(r, job / f'reference{i}{r.suffix.lower()}')
    print(f'Terminé : {final}\nComparaison : {job / "comparaison.jpg"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
