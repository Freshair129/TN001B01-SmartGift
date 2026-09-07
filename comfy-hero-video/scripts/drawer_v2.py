"""SG-1 v3 — refinement of the v2 deterministic drawer compositor.

White studio background, the SmartGift orange box centred. Both clips start from the same closed box:
  west  (mouse left)  : the tray slides out to the LEFT, at most half the box, revealing the real FXD66-3 products
  east  (mouse right) : the tray slides out to the RIGHT, revealing client-branded mockups (GMMTV, True, UD Trucks)
Motion is linear (progress 0 → 1 == tray 0 → 50 % out) so the mouse scrubber maps 1:1.

Sources
  box + product tray : output/catalog-internal/artwork/FXD66-3-adcreative-v1.png (approved ad creative, real products)
  client mockups     : web-ui-smg/public/assets/smartgift/mockups/*.jpg cut out with rembg → assets/mockups_cut/*.png
Outputs (spec: 1920x1080, 30 fps, 4.0 s, H.264 high, -g 15, no audio, faststart)
  outputs/v3/hero_west_receive.mp4, outputs/v3/hero_east_discover.mp4, outputs/v3/hero_frame0_poster.jpg
"""
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AD = r'C:\Users\pc\workspace\business-01-smart-gift\output\catalog-internal\artwork\FXD66-3-adcreative-v1.png'
CUT = os.path.join(HERE, 'assets', 'mockups_cut')
OUT = os.path.join(HERE, 'outputs', 'v3')
LOGO = r'C:\Users\pc\workspace\web-ui-smg\public\logo-smg.jpg'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1920, 1080
FPS, SECONDS = 30, 4.0
FRAMES = int(FPS * SECONDS)
BOX_H = 420                      # top + 28 px wall, 442 px projected; clears the 1366px ledger
DEPTH = 28
SHEAR, FORESHORTEN = 0.045, 0.985  # fixed near-top-down orthographic view; horizontal motion stays linear
BG = (255, 255, 255)
# Four cells; only the right half emerges, so the two on the right are the ones a visitor actually sees.
CLIENT_MOCKUPS = ['udtrucks.png', 'gmmtv_pb.png', 'gmmtv_tmb.png', 'truepride.png']   # brands with a documented relationship


# ---------------------------------------------------------------------------
# 1. Measure the box in the ad creative and lift the tray (inner inset) out of it
# ---------------------------------------------------------------------------
def measure_box(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    orange = (a[:, :, 0] > 200) & (a[:, :, 1] < 130) & (a[:, :, 2] < 70)
    cols = orange.mean(axis=0)
    rows = orange.mean(axis=1)
    xs = np.where(cols > 0.02)[0]
    ys = np.where(rows > 0.02)[0]
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    # inner inset = the white tray surface: first/last bright columns (rows) inside the frame,
    # measured across the middle band so the products do not disturb the edge detection
    bright = a.min(axis=2) > 205
    sub = bright[y0:y1 + 1, x0:x1 + 1]
    h, w = sub.shape
    col_frac = sub[int(h * 0.3):int(h * 0.7), :].mean(axis=0)
    row_frac = sub[:, int(w * 0.3):int(w * 0.7)].mean(axis=1)
    inner_cols = np.where(col_frac > 0.5)[0]
    inner_rows = np.where(row_frac > 0.5)[0]
    ix0, ix1 = x0 + int(inner_cols.min()), x0 + int(inner_cols.max())
    iy0, iy1 = y0 + int(inner_rows.min()), y0 + int(inner_rows.max())
    sel = a[orange]
    color = tuple(int(v) for v in np.median(sel, axis=0))
    return (x0, y0, x1, y1), (ix0, iy0, ix1, iy1), color


ad = Image.open(AD).convert('RGB')
outer, inner, ORANGE = measure_box(ad)
print('outer box', outer, 'inner tray', inner, 'orange', ORANGE)

scale = BOX_H / (outer[3] - outer[1])
box_w = int(round((outer[2] - outer[0]) * scale))
box_h = BOX_H
sleeve_x = (W - box_w) // 2
sleeve_y = (H - box_h - DEPTH) // 2
frame_t = int(round(min(inner[0] - outer[0], inner[1] - outer[1], outer[2] - inner[2], outer[3] - inner[3]) * scale))
assert 20 <= frame_t <= 80, f'unexpected frame thickness {frame_t}px — check measure_box()'
tray_w = box_w - 2 * frame_t
tray_h = box_h - 2 * frame_t
print(f'canvas box {box_w}x{box_h} at ({sleeve_x},{sleeve_y}), frame {frame_t}px, tray {tray_w}x{tray_h}')

# real product tray = the inner inset of the photo, resized to the canvas tray
tray_products = ad.crop(inner).resize((tray_w, tray_h), Image.LANCZOS)
tray_bg = tuple(int(v) for v in np.median(np.asarray(tray_products)[10:40, 10:40].reshape(-1, 3), axis=0))
print('tray surface colour', tray_bg)


# ---------------------------------------------------------------------------
# 2. Client tray: four original cutouts on the same ivory surface
# ---------------------------------------------------------------------------
def soft_shadow(size, radius, opacity, offset=(0, 0)):
    """RGBA layer with a blurred dark rectangle."""
    pad = radius * 3
    layer = Image.new('RGBA', (size[0] + 2 * pad, size[1] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((pad + offset[0], pad + offset[1], pad + size[0] + offset[0], pad + size[1] + offset[1]), fill=(0, 0, 0, int(255 * opacity)))
    return layer.filter(ImageFilter.GaussianBlur(radius)), pad


def build_client_tray():
    tray = Image.new('RGBA', (tray_w, tray_h), tray_bg + (255,))
    cell = tray_w // len(CLIENT_MOCKUPS)
    max_h = int(tray_h * 0.74)
    max_w = int(cell * 0.86)
    for i, name in enumerate(CLIENT_MOCKUPS):
        cut = Image.open(os.path.join(CUT, name)).convert('RGBA')
        cut = cut.crop(cut.getbbox())
        r = min(max_w / cut.width, max_h / cut.height)
        cut = cut.resize((max(1, int(cut.width * r)), max(1, int(cut.height * r))), Image.LANCZOS)
        cx = i * cell + (cell - cut.width) // 2
        cy = (tray_h - cut.height) // 2
        # A silhouette shadow anchors the photographed mockup to the tray plane.
        sh = Image.new('RGBA', cut.size, (39, 29, 20, 0))
        sh.putalpha(cut.getchannel('A').point(lambda a: round(a * 0.20)))
        shadow_plane = Image.new('RGBA', tray.size)
        shadow_plane.alpha_composite(sh, (cx + 5, cy + 7))
        tray.alpha_composite(shadow_plane.filter(ImageFilter.GaussianBlur(5)))
        tray.alpha_composite(cut, (cx, cy))
    return tray.convert('RGB')


tray_clients = build_client_tray()


# ---------------------------------------------------------------------------
# 3. Sleeve (closed box top) — matte lacquer look built from the photo's orange
# ---------------------------------------------------------------------------
def build_sleeve():
    img = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
    base = np.zeros((box_h, box_w, 4), dtype=np.float32)
    yy = np.linspace(0, 1, box_h)[:, None]
    xx = np.linspace(0, 1, box_w)[None, :]
    light = 1.0 + 0.09 * (0.5 - yy) + 0.05 * (0.5 - xx)
    for c in range(3):
        base[:, :, c] = np.clip(ORANGE[c] * light, 0, 255)
    base[:, :, 3] = 255
    img = Image.fromarray(base.astype(np.uint8), 'RGBA')
    # rounded corners
    mask = Image.new('L', (box_w, box_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=10, fill=255)
    img.putalpha(mask)
    # Fine bevels retain a quiet matte face instead of heavy vector outlines.
    d = ImageDraw.Draw(img)
    dark = tuple(int(v * 0.72) for v in ORANGE) + (255,)
    d.rounded_rectangle((1, 1, box_w - 2, box_h - 2), radius=9, outline=dark, width=2)
    d.line((12, 3, box_w - 12, 3), fill=(255, 159, 82, 150), width=2)
    d.line((3, 12, 3, box_h - 12), fill=(255, 139, 69, 110), width=2)
    # subtle specular sheen band
    sheen = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
    ImageDraw.Draw(sheen).ellipse((-box_w // 2, -box_h, box_w, box_h), fill=(255, 218, 184, 19))
    sheen = sheen.filter(ImageFilter.GaussianBlur(95))
    img.alpha_composite(sheen)
    # matte lacquer grain + soft edge vignette so the lid stops reading as a flat vector
    rng = np.random.default_rng(7)
    grain = rng.normal(0, 0.65, (box_h, box_w, 1)).astype(np.float32)
    arr = np.asarray(img).astype(np.float32)
    yy = np.linspace(-1, 1, box_h)[:, None]
    xx = np.linspace(-1, 1, box_w)[None, :]
    vign = 1 - 0.025 * np.clip((np.abs(xx) ** 12 + np.abs(yy) ** 12), 0, 1)
    arr[:, :, :3] = np.clip(arr[:, :, :3] * vign[:, :, None] + grain, 0, 255)
    img = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    # Exact gift/SG/bow silhouette from the supplied logo, with white knocked out.
    # Crop excludes the separator, wordmark and tagline; no invented lettering.
    logo = np.asarray(Image.open(LOGO).convert('RGB').crop((112, 182, 590, 723))).astype(float)
    coverage = np.clip((245 - logo.min(axis=2)) / 70, 0, 1)
    mark = Image.fromarray((coverage * 255).astype(np.uint8))
    mark.thumbnail((int(box_w * .32), int(box_h * .43)), Image.Resampling.LANCZOS)
    relief = Image.new('L', img.size)
    relief.paste(mark, ((box_w - mark.width) // 2, (box_h - mark.height) // 2))
    blurred = relief.filter(ImageFilter.GaussianBlur(.6))
    lower = ImageChops.subtract(ImageChops.offset(blurred, 1, 2), blurred)
    upper = ImageChops.subtract(blurred, ImageChops.offset(blurred, 1, 2))
    for color, alpha in (((111, 37, 10), relief.point(lambda v: int(v * .20))),
                         ((91, 27, 7), upper.point(lambda v: int(v * .65))),
                         ((255, 185, 113), lower.point(lambda v: int(v * .80)))):
        layer = Image.new('RGBA', img.size, color + (0,))
        layer.putalpha(alpha)
        img.alpha_composite(layer)
    img.putalpha(mask)
    return img


top = build_sleeve()
sleeve = Image.new('RGBA', (box_w, box_h + DEPTH))
sd = ImageDraw.Draw(sleeve)
sd.rounded_rectangle((0, 15, box_w - 1, box_h + DEPTH - 1), radius=8,
                     fill=tuple(int(c * .67) for c in ORANGE) + (255,))
for y in range(box_h - 3, box_h + DEPTH - 2):
    shade = .78 - .13 * (y - box_h + 3) / (DEPTH + 1)
    sd.line((4, y, box_w - 5, y), fill=tuple(int(c * shade) for c in ORANGE) + (255,))
sd.line((10, box_h + 5, box_w - 11, box_h + 5), fill=(145, 44, 8, 255))
sd.line((10, box_h + 7, box_w - 11, box_h + 7), fill=(213, 69, 12, 255))
sleeve.alpha_composite(top)
box_shadow, box_pad = soft_shadow((box_w, box_h + DEPTH), 23, .19, offset=(12, 22))
contact_shadow, contact_pad = soft_shadow((box_w - 8, box_h + DEPTH - 8), 5, .23, offset=(4, 6))
tray_shadow, tray_pad = soft_shadow((tray_w, tray_h), 12, .15, offset=(8, 24))


EDGE_BAND = 56


def sleeve_edge_shadow(side):
    """Soft shadow the sleeve casts on the emerged tray, darkest right at the opening."""
    grad = np.zeros((tray_h + 4, EDGE_BAND, 4), dtype=np.uint8)
    ramp = (np.linspace(0, 1, EDGE_BAND) ** 1.6 * 78).astype(np.uint8)   # 0 → 78 alpha
    grad[:, :, 3] = ramp if side == 'west' else ramp[::-1]                 # west: darkest on the right (sleeve edge)
    return Image.fromarray(grad, 'RGBA')


edge_w = sleeve_edge_shadow('west')
edge_e = sleeve_edge_shadow('east')


# ---------------------------------------------------------------------------
# 4. Frame compositor
# ---------------------------------------------------------------------------
def render_frame(progress, side, tray_img):
    """progress 0..1 → tray out 0..50 % of the box width, to the given side."""
    canvas = Image.new('RGBA', (W, H), BG + (255,))
    offset = int(round(progress * 0.5 * box_w))
    dx = -offset if side == 'west' else offset
    tray_x = sleeve_x + frame_t + dx
    tray_y = sleeve_y + frame_t + 10
    # ambient shadow of the whole box
    canvas.alpha_composite(box_shadow, (sleeve_x - box_pad, sleeve_y - box_pad))
    canvas.alpha_composite(contact_shadow, (sleeve_x - contact_pad, sleeve_y - contact_pad))
    if offset > 0:
        # tray shadow (only the emerged part matters, the rest is under the sleeve anyway)
        canvas.alpha_composite(tray_shadow, (tray_x - tray_pad, tray_y - tray_pad))
        tray_layer = Image.new('RGBA', (tray_w + 4, tray_h + 18), (0, 0, 0, 0))
        td = ImageDraw.Draw(tray_layer)
        td.rounded_rectangle((0, 0, tray_w + 3, tray_h + 17), radius=5, fill=(182, 166, 144, 255))
        td.rounded_rectangle((0, 0, tray_w + 3, tray_h + 3), radius=4, fill=tray_bg + (255,))
        td.line((4, tray_h + 5, tray_w - 1, tray_h + 5), fill=(224, 213, 194, 255), width=2)
        tray_layer.paste(tray_img, (2, 2))
        # shadow band cast by the sleeve edge onto the tray, hugging the opening
        emerged = offset - frame_t            # tray pixels visible beyond the sleeve edge
        if emerged > 0:
            if side == 'west':
                tray_layer.alpha_composite(edge_w, (emerged - EDGE_BAND + 2, 0))
            else:
                tray_layer.alpha_composite(edge_e, (tray_w - emerged + 2, 0))
        canvas.alpha_composite(tray_layer, (tray_x - 2, tray_y - 2))
    canvas.alpha_composite(sleeve, (sleeve_x, sleeve_y))
    # A fixed affine camera keeps every image pixel tied to its physical plane.
    inv = (1, -SHEAR / FORESHORTEN, SHEAR * H / (2 * FORESHORTEN),
           0, 1 / FORESHORTEN, H / 2 * (1 - 1 / FORESHORTEN))
    return canvas.convert('RGB').transform((W, H), Image.Transform.AFFINE, inv,
                                          Image.Resampling.BICUBIC, fillcolor=BG)


def encode(side, tray_img, path):
    cmd = [FFMPEG, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '18',
           '-g', '15', '-keyint_min', '15', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        p.stdin.write(render_frame(t, side, tray_img).tobytes())
    p.stdin.close()
    err = p.stderr.read().decode('utf-8', 'replace')
    if p.wait() != 0:
        raise SystemExit(err[-1200:])
    print('encoded', path, f'{os.path.getsize(path)/1e6:.2f} MB')


def main():
    os.makedirs(OUT, exist_ok=True)
    poster = render_frame(0, 'west', tray_products)
    poster.save(os.path.join(OUT, 'hero_frame0_poster.jpg'), quality=90, optimize=True)
    # stills for review
    for side, tray in (('west', tray_products), ('east', tray_clients)):
        for p in (0.5, 1.0):
            render_frame(p, side, tray).save(os.path.join(OUT, f'still_{side}_{int(p*100)}.jpg'), quality=88)
    if '--stills' in sys.argv:
        return
    encode('west', tray_products, os.path.join(OUT, 'hero_west_receive.mp4'))
    encode('east', tray_clients, os.path.join(OUT, 'hero_east_discover.mp4'))
    print('done')


if __name__ == '__main__':
    main()
