"""Encode full volumetric renders; normalize only the fully concealed prefix."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parents[1]/'outputs/v5'
FF=imageio_ffmpeg.get_ffmpeg_exe()
NAMES={'A':'hero_west_receive.mp4','B':'hero_east_discover.mp4'}


def call(args):
    result=subprocess.run([FF,'-hide_banner','-y',*map(str,args)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
    return result.stderr


def finish():
    for v in NAMES:
        assert len(list((OUT/'frames'/v).glob('*.png')))==120
    poses=json.loads((OUT/'scene_contract.json').read_text())['frames']
    assert np.allclose([p['lid_degrees'] for p in poses],np.linspace(0,105,120),atol=1e-10)
    for field in ['camera_location','camera_rotation','hinge_location','base_location']:
        assert len({tuple(p[field]) for p in poses})==1,field
    assert {p['camera_elevation'] for p in poses}=={50}
    assert len({p['ortho_width'] for p in poses})==1
    bounds=json.loads((OUT/'projection_bounds.json').read_text())
    margins=[min(b[1] for b in bounds),min(b[2] for b in bounds),1920-max(b[3] for b in bounds),1080-max(b[4] for b in bounds)]
    assert min(margins)>32,margins
    masks={v:[int(np.count_nonzero(np.asarray(Image.open(OUT/f'masks/{v}/{i:04}.png')))) for i in range(120)] for v in NAMES}
    first_visible=next(i for i in range(120) if any(masks[v][i] for v in NAMES))
    assert first_visible>18,first_visible
    # Different hidden meshes can perturb a few stochastic GI samples. Reuse the
    # common master only while both depth-tested variant visibility masks are zero.
    # After reveal, preserve entire rendered images, including real bounced light.
    common=OUT/'concealed_B_originals'
    common.mkdir(exist_ok=True)
    for i in range(first_visible):
        src=OUT/f'frames/A/{i:04}.png'
        dest=OUT/f'frames/B/{i:04}.png'
        if not (common/dest.name).exists():shutil.copy2(dest,common/dest.name)
        shutil.copy2(src,dest)
    shutil.copy2(OUT/'frames/A/0000.png',OUT/'frame0_closed_master.png')
    for v,name in NAMES.items():
        log=call(['-framerate','30','-i',OUT/f'frames/{v}/%04d.png','-vf','format=yuv420p',
                  '-frames:v','120','-an','-c:v','libx264','-profile:v','high','-preset','medium',
                  '-qp','18','-g','15','-keyint_min','15','-sc_threshold','0','-bf','0','-threads','1',
                  '-x264-params','rc-lookahead=0:sync-lookahead=0:aq-mode=0:mbtree=0:ref=1',
                  '-fps_mode','cfr','-r','30','-movflags','+faststart',OUT/name])
        (OUT/f'encode_{v}.log').write_text(log,encoding='utf-8')
        print('ENCODED',v,flush=True)
    decoders=[imageio_ffmpeg.read_frames(str(OUT/NAMES[v]),pix_fmt='rgb24') for v in NAMES]
    metadata=[next(d) for d in decoders]
    same=[]
    for i,(a,b) in enumerate(zip(*decoders)):
        same.append(a==b)
        if i<first_visible:assert a==b,('prefix mismatch',i)
    assert len(same)==120 and not same[-1]
    report={'status':'PASS','camera_elevation':50,'camera_and_scale_constant':True,'linear_lid_degrees':[0,105],
            'products':'volumetric reference reconstructions with approximate dimensions',
            'compositing':'common concealed prefix only; full independent GI renders after visibility',
            'first_visible_variant_frame':first_visible,'variant_visible_pixels':masks,
            'decoded_frame0_pixel_identical':same[0],'decoded_equal_frames':[i for i,x in enumerate(same) if x],
            'minimum_geometry_margins_ltrb':margins,'videos':{}}
    for v,meta in zip(NAMES,metadata):
        path=OUT/NAMES[v]
        assert meta['size']==(1920,1080) and meta['fps']==30 and abs(meta['duration']-4)<.001
        log=call(['-i',path,'-vf','showinfo','-f','null','-'])
        keyframes=[int(re.search(r'\bn:\s*(\d+)',line).group(1)) for line in log.splitlines() if 'iskey:1' in line]
        assert keyframes==list(range(0,120,15))
        assert 'Audio:' not in log and 'High' in log and 'yuv420p' in log
        data=path.read_bytes()
        assert data.find(b'moov')<data.find(b'mdat')
        call(['-i',path,'-vf',"select='eq(n,0)+eq(n,15)+eq(n,30)+eq(n,45)+eq(n,60)+eq(n,75)+eq(n,90)+eq(n,105)+eq(n,119)',scale=480:270,tile=3x3",'-frames:v','1',OUT/f'contact_{v}.jpg'])
        for i in [0,18,60,119]:
            call(['-i',path,'-vf',f'select=eq(n\\,{i})','-frames:v','1',OUT/f'decoded_{v}_{i:04}.png'])
        report['videos'][v]={'file':path.name,'size':meta['size'],'fps':30,'duration':4,'frames':120,
            'keyframes':keyframes,'audio':False,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'faststart':True}
    call(['-i',OUT/NAMES['A'],'-frames:v','1','-q:v','2',OUT/'hero_frame0_poster.jpg'])
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='variant_visible_pixels'},indent=2))


if __name__=='__main__':finish()
