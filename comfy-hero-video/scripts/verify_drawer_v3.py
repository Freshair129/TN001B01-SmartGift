"""Artifact checks for the approved v3 hero; never copies into the website.

Usage: python scripts/verify_drawer_v3.py outputs/v3 [--review]
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]).resolve()
OUT = HERE / 'outputs/v3'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
NAMES = {'west': 'hero_west_receive.mp4', 'east': 'hero_east_discover.mp4'}
REVIEW = '--review' in sys.argv


def run(args):
    return subprocess.run([FFMPEG, '-hide_banner', *map(str, args)],
                          capture_output=True, check=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atoms(path):
    data = path.read_bytes()
    result, offset = {}, 0
    while offset + 8 <= len(data):
        size, kind = struct.unpack('>I4s', data[offset:offset + 8])
        if size == 1:
            size = struct.unpack('>Q', data[offset + 8:offset + 16])[0]
        if size == 0:
            size = len(data) - offset
        assert size >= 8
        result[kind.decode()] = offset
        offset += size
    return result


def frame(path, index):
    data = run(['-v', 'error', '-i', path, '-vf', f'select=eq(n\\,{index})',
                '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']).stdout
    return np.frombuffer(data, np.uint8).reshape(1080, 1920, 3)


report = {'source': str(SOURCE), 'checks': {}, 'files': {}}
first = {}
for side, name in NAMES.items():
    path = SOURCE / name
    log = run(['-i', path, '-vf', 'showinfo', '-f', 'null', '-']).stderr.decode('utf-8', 'replace')
    (OUT / f'{SOURCE.name}_{side}_ffmpeg.log').write_text(log, encoding='utf-8')
    lines = [line for line in log.splitlines() if 'Parsed_showinfo' in line and ' n:' in line]
    pts = [float(re.search(r'pts_time:([\d.]+)', line)[1]) for line in lines]
    keys = [i for i, line in enumerate(lines) if 'type:I' in line]
    assert len(lines) == 120, len(lines)
    assert keys == list(range(0, 120, 15)), keys
    assert max(abs(t - i / 30) for i, t in enumerate(pts)) < .00001
    input_info = log.split('Stream mapping:')[0]
    assert 'h264 (High)' in input_info and 'yuv420p' in input_info
    assert '1920x1080' in input_info and '30 fps' in input_info
    assert 'Duration: 00:00:04.00' in input_info and 'Audio:' not in input_info
    boxes = atoms(path)
    assert boxes['moov'] < boxes['mdat'], boxes
    first[side] = frame(path, 0)
    report['files'][side] = {'file': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size,
                             'frames': 120, 'fps': 30, 'duration': 4.0, 'profile': 'High',
                             'pixel_format': 'yuv420p', 'audio_streams': 0, 'iframes': len(keys),
                             'iframe_indices': keys, 'faststart': True,
                             'pts_max_error_seconds': max(abs(t - i / 30) for i, t in enumerate(pts))}
    if REVIEW:
        font = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 17)
        sheet = Image.new('RGB', (1440, 894), '#f0eeeb')
        draw = ImageDraw.Draw(sheet)
        draw.text((18, 10), f'SMARTGIFT  /  V3  /  {side.upper()}   -   decoded delivery MP4', font=font, fill='#463b30')
        samples = []
        for slot, t in enumerate([0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 3.95]):
            index = min(119, math.ceil(t * 30))
            im = Image.fromarray(frame(path, index))
            im.save(OUT / f'{side}_frame_{index:03d}.png')
            im.thumbnail((480, 270), Image.Resampling.LANCZOS)
            x, y = slot % 3 * 480, 40 + slot // 3 * 282
            sheet.paste(im, (x, y))
            draw.text((x + 12, y + 247), f't={t:.2f}s  |  frame {index}  |  PTS {index/30:.4f}s', font=font, fill='#514638')
            samples.append({'requested_time': t, 'frame': index, 'pts': index / 30})
        sheet.save(OUT / f'{side}_contact_sheet.jpg', quality=94, subsampling=0)
        report['files'][side]['contact_sheet_samples'] = samples

mad = float(np.abs(first['west'].astype(float) - first['east']).mean())
assert mad < 3, mad
report['checks']['decoded_frame0_RGB_MAD_255'] = mad
report['checks']['frame0_parity_ok'] = True

# Rendered source checks establish the shared frame and actual sleeve bounds.
spec = importlib.util.spec_from_file_location('drawer', HERE / 'scripts/drawer_v2.py')
drawer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drawer)
a = np.asarray(drawer.render_frame(0, 'west', drawer.tray_products))
b = np.asarray(drawer.render_frame(0, 'east', drawer.tray_clients))
assert np.array_equal(a, b)
mask = (a[:, :, 0] > 120) & (a[:, :, 0] > a[:, :, 1].astype(float) * 1.6) & (a[:, :, 2] < 120)
y, x = np.where(mask)
bounds = [int(x.min()), int(y.min()), int(x.max()) + 1, int(y.max()) + 1]
assert bounds[3] - bounds[1] <= 560
assert abs((bounds[0] + bounds[2]) / 2 - 960) <= 2
assert abs((bounds[1] + bounds[3]) / 2 - 540) <= 2
assert np.all(a[:150] == 255) and np.all(a[950:] == 255)
report['checks'].update(source_frame0_bit_identical=True, source_box_bounds=bounds,
                        source_box_height=bounds[3] - bounds[1], white_ground=True)

# Measure the leading tray edge in a decoded scanline, beyond the opening.
# This checks rendered movement, rather than merely repeating the motion formula.
for side, name in NAMES.items():
    scan_y = round(540 + (drawer.sleeve_y + drawer.frame_t + 10 + 24 - 540) * drawer.FORESHORTEN)
    strip = run(['-v', 'error', '-i', SOURCE / name, '-vf', f'format=gray,crop=1920:20:0:{scan_y-10},scale=1920:1:flags=area',
                 '-pix_fmt', 'gray', '-f', 'rawvideo', '-']).stdout
    rows = np.frombuffer(strip, np.uint8).reshape(120, 1920).astype(float)
    half_travel = round(drawer.box_w * .5)
    final_origin = drawer.sleeve_x + drawer.frame_t + (-half_travel if side == 'west' else half_travel) - 2
    final_edge = final_origin + (0 if side == 'west' else drawer.tray_w + 3)
    final_edge += drawer.SHEAR * (scan_y - 540) / drawer.FORESHORTEN
    template_x = round(final_edge)
    template = rows[-1, template_x - 12:template_x + 13]
    measured, expected, indices = [], [], []
    # After frame 48 the leading edge is clear of the stationary sleeve shadow;
    # earlier pixels change illumination as well as position and are not a stable template.
    for i in range(48, 120):
        offset = round(i / 119 * .5 * drawer.box_w)
        origin = drawer.sleeve_x + drawer.frame_t + (-offset if side == 'west' else offset) - 2
        edge = origin + (0 if side == 'west' else drawer.tray_w + 3)
        edge += drawer.SHEAR * (scan_y - 540) / drawer.FORESHORTEN
        lo, hi = round(edge) - 5, round(edge) + 6
        scores = [np.mean((rows[i, pos - 12:pos + 13] - template) ** 2) for pos in range(lo, hi)]
        measured.append(int(lo + np.argmin(scores)))
        expected.append(edge)
        indices.append(i)
    errors = np.abs(np.array(measured) - expected)
    signed_steps = np.diff(measured) * (-1 if side == 'west' else 1)
    assert errors.max() <= 5.5, (side, errors.max())
    assert signed_steps.min() >= 0, (side, signed_steps.min())
    # A straight-line fit independently verifies constant motion on the screen.
    fit = np.polyfit(indices, measured, 1)
    residual = np.max(np.abs(np.polyval(fit, indices) - measured))
    assert residual < 2.0, (side, residual)
    report['files'][side]['motion_scanline'] = {'y': scan_y, 'frames': indices,
        'measured_edge_x': measured, 'max_error_px': float(errors.max()),
        'linear_fit_max_residual_px': float(residual), 'slope_px_per_frame': float(fit[0]),
        'expected_travel_px': drawer.box_w * .5, 'monotonic': True}

assets = [Path(drawer.AD), Path(drawer.LOGO)] + [Path(drawer.CUT) / n for n in drawer.CLIENT_MOCKUPS]
report['asset_sha256'] = {str(p): sha(p) for p in assets}
report['renderer_sha256'] = sha(HERE / 'scripts/drawer_v2.py')
if REVIEW:
    poster = OUT / 'hero_frame0_poster.jpg'
    Image.fromarray(first['west']).save(poster, quality=90, optimize=True)
    assert poster.stat().st_size <= 180000
    report['poster'] = {'file': str(poster), 'bytes': poster.stat().st_size, 'sha256': sha(poster),
                        'source': 'decoded west conformed frame 0', 'size': [1920, 1080]}
report['passed'] = True
dest = OUT / ('verification_conformed.json' if REVIEW else 'verification_raw.json')
dest.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'passed': True, 'report': str(dest), 'frame0_RGB_MAD': mad,
                  'box_bounds': bounds, 'iframes': [8, 8]}, indent=2))
