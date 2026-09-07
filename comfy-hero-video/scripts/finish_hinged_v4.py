"""Encode and verify the authorized four-second shared-scene hero videos."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/v4'
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAMES = {'A':'hero_west_receive.mp4', 'B':'hero_east_discover.mp4'}
parser = argparse.ArgumentParser()
parser.add_argument('--encode', choices=['A', 'B', 'both'])
parser.add_argument('--verify', action='store_true')
opts = parser.parse_args()


def call(args):
    result = subprocess.run([FF, '-hide_banner', '-y', *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stderr


def source(v):
    paths = sorted((OUT/'frames'/v).glob('*.png'))
    assert len(paths) == 120, (v, len(paths))
    return OUT/'frames'/v/'%04d.png'


def encode(v):
    source(v)
    inputs = ['-framerate','30','-i',source('A')]
    if v == 'B':
        inputs += ['-framerate','30','-i',source('B'), '-framerate','30','-i',OUT/'masks/B/%04d.png']
        # Same rendered exterior for both clips; only depth-visible insert pixels can differ.
        filters = ['-filter_complex','[0:v]format=gbrp[a];[1:v]format=gbrp[b];[2:v]format=gbrp[m];[a][b][m]maskedmerge,format=yuv420p[out]', '-map','[out]']
    else:
        filters = ['-vf', 'format=yuv420p']
    log = call(inputs+filters+['-frames:v','120','-an','-c:v','libx264','-profile:v','high',
        '-preset','medium','-qp','20','-g','15','-keyint_min','15','-sc_threshold','0','-bf','0',
        '-threads','1','-x264-params','rc-lookahead=0:sync-lookahead=0:aq-mode=0:mbtree=0:ref=1',
        '-fps_mode','cfr','-r','30','-movflags','+faststart',OUT/NAMES[v]])
    (OUT/f'encode_{v}.log').write_text(log, encoding='utf-8')
    print('ENCODED', v, (OUT/NAMES[v]).stat().st_size, flush=True)


def verify():
    contract = json.loads((OUT/'scene_contract.json').read_text(encoding='utf-8'))
    poses = contract['frames']
    angles = np.array([p['lid_degrees'] for p in poses])
    assert np.allclose(angles, np.linspace(0,105,120), atol=1e-10)
    assert poses[0]['camera_elevation'] == 80 and poses[-1]['camera_elevation'] == 50
    assert len({tuple(p['hinge_location']) for p in poses}) == 1
    assert len({tuple(p['base_location']) for p in poses}) == 1
    projection = json.loads((OUT/'projection_bounds.json').read_text())
    margins = [min(b[1] for b in projection), min(b[2] for b in projection),
               1920-max(b[3] for b in projection),1080-max(b[4] for b in projection)]
    assert min(margins) > 32, margins
    masks = []
    for i in range(120):
        mask = np.asarray(Image.open(OUT/f'masks/B/{i:04}.png'))
        masks.append(int(np.count_nonzero(mask)))
    first_visible = next((i for i,n in enumerate(masks) if n), None)
    assert first_visible is not None and first_visible > 18, first_visible
    report = {'scene':'PASS','linear_lid':[0,105],'camera_elevation':[80,50],
              'first_visible_insert_frame':first_visible,'visible_insert_pixels':masks,
              'minimum_geometry_margins_ltrb':margins,
              'source_compositing':'B uses common A render outside the depth-tested insert mask',
              'products':'reference-composited plates, not full volumetric product models','videos':{}}
    decoders = [imageio_ffmpeg.read_frames(str(OUT/NAMES[v]),pix_fmt='rgb24') for v in ['A','B']]
    metadata = [next(d) for d in decoders]
    same = []
    frame_count = 0
    for i,(a,b) in enumerate(zip(*decoders)):
        same.append(a == b)
        if i < first_visible:
            assert a == b, f'decoded shared frame mismatch {i}'
        frame_count += 1
    assert frame_count == 120
    assert not same[-1], 'Distinct sets are missing'
    for v, meta in zip(['A','B'],metadata):
        path = OUT/NAMES[v]
        assert meta['size'] == (1920,1080) and meta['fps'] == 30 and abs(meta['duration']-4) < .001
        log = call(['-i',path,'-vf','showinfo','-f','null','-'])
        lines = [line for line in log.splitlines() if 'iskey:1' in line]
        keyframes = [int(re.search(r'\bn:\s*(\d+)',line).group(1)) for line in lines]
        assert keyframes == list(range(0,120,15)), keyframes
        assert 'Audio:' not in log
        assert 'High' in log and 'yuv420p' in log
        raw = path.read_bytes()
        assert raw.find(b'moov') < raw.find(b'mdat')
        # Contact sheets and poster are video-derived review artifacts via FFmpeg.
        call(['-i',path,'-vf',"select='eq(n,0)+eq(n,15)+eq(n,30)+eq(n,45)+eq(n,60)+eq(n,75)+eq(n,90)+eq(n,105)+eq(n,119)',scale=480:270,tile=3x3",'-frames:v','1',OUT/f'contact_{v}.jpg'])
        for i in [0,18,60,119]:
            call(['-i',path,'-vf',f'select=eq(n\\,{i})','-frames:v','1',OUT/f'decoded_{v}_{i:04}.png'])
        report['videos'][v] = {'file':path.name,'size':meta['size'],'fps':meta['fps'],
            'duration':meta['duration'],'frames':frame_count,'keyframes':keyframes,'audio':False,
            'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'faststart':True}
    call(['-i',OUT/NAMES['A'],'-frames:v','1','-q:v','2',OUT/'hero_frame0_poster.jpg'])
    report['decoded_frame0_pixel_identical'] = same[0]
    report['decoded_equal_frames'] = [i for i,equal in enumerate(same) if equal]
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'visible_insert_pixels'},indent=2),flush=True)


if opts.encode:
    for variant in (['A','B'] if opts.encode == 'both' else [opts.encode]):
        encode(variant)
if opts.verify:
    verify()
