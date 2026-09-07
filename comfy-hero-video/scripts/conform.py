"""Conform the two raw Wan clips to the hero spec (docs/HERO-VIDEO-SPEC.md §3-4, BRAND-DIRECTION §5):
1920x1080, 30 fps CFR, exactly 4.0 s, H.264 high, -g 15, no audio, faststart; then verify first-frame parity
and keyframe count, and copy the results into the web app.

Usage: python scripts/conform.py <raw_west.mp4> <raw_east.mp4>
"""
import json
import os
import shutil
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding='utf-8')
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'outputs', 'conformed')
WEB = r'C:\Users\pc\workspace\web-ui-smg\public\assets\videos'
NAMES = {'west': 'hero_west_receive.mp4', 'east': 'hero_east_discover.mp4'}


def run(args):
    print('$', ' '.join(a if ' ' not in a else f'"{a}"' for a in args[:12]), '...', flush=True)
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit(f'ffmpeg failed ({r.returncode})')
    return r


def conform(src, dst):
    run([
        FFMPEG, '-y', '-i', src,
        '-t', '4',
        # FFmpeg 7.1 loses the final frame with scale before fps on these sources.
        '-vf', 'fps=30,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080',
        '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '20',
        '-g', '15', '-keyint_min', '15', '-sc_threshold', '0',
        '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart',
        dst,
    ])


def frame0(video, jpg):
    run([FFMPEG, '-y', '-i', video, '-vframes', '1', '-q:v', '2', jpg])


def keyframes(video):
    # imageio's binary ships ffmpeg only; count I-frames with the debug showinfo filter instead of ffprobe
    r = subprocess.run([FFMPEG, '-i', video, '-vf', 'showinfo', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    lines = [l for l in r.stderr.splitlines() if 'Parsed_showinfo' in l and ' n:' in l]
    iframes = sum(1 for l in lines if 'type:I' in l)
    return len(lines), iframes


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)
    report = {}
    for side, src in zip(('west', 'east'), sys.argv[1:3]):
        dst = os.path.join(OUT, NAMES[side])
        conform(src, dst)
        jpg = os.path.join(OUT, f'frame0_{side}.jpg')
        frame0(dst, jpg)
        frames, ifr = keyframes(dst)
        report[side] = {'file': dst, 'frames': frames, 'iframes': ifr, 'size_mb': round(os.path.getsize(dst) / 1e6, 2)}
    a = Image.open(os.path.join(OUT, 'frame0_west.jpg')).convert('L')
    b = Image.open(os.path.join(OUT, 'frame0_east.jpg')).convert('L')
    d = ImageChops.difference(a, b)
    h = d.histogram()
    mean_diff = sum(i * v for i, v in enumerate(h)) / max(1, sum(h))
    report['frame0_mean_abs_diff'] = round(mean_diff, 3)
    report['frame0_parity_ok'] = mean_diff < 3.0
    if not report['frame0_parity_ok'] or any(
        report[side]['frames'] != 120 or report[side]['iframes'] != 8 for side in ('west', 'east')
    ):
        print(json.dumps(report, indent=2, ensure_ascii=False))
        raise SystemExit('Conform checks failed; no files copied to the website.')
    for side in ('west', 'east'):
        shutil.copy(report[side]['file'], os.path.join(WEB, NAMES[side]))
    report['copied_to'] = WEB
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
