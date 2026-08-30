"""Build the task-owned SmartGift creative PDF proof; never mutate catalog data."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'python-deps'))
import json
import hashlib
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, shapeStr
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT = HERE.parent.parent
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((HERE / 'production-manifest.json').read_text(encoding='utf-8'))
SETS = DATA['sets']
PRODUCTS = DATA['products']
W, H = 297 * mm, 210 * mm
PAPER = HexColor('#F7F5EF')
INK = HexColor('#182B30')
MUTED = HexColor('#52676C')
TEAL = HexColor('#08798A')
LINE = HexColor('#CCD5D1')
WHITE = HexColor('#FFFFFF')
pdfmetrics.registerFont(TTFont('SG', r'C:\Windows\Fonts\LeelawUI.ttf', shapable=True))
pdfmetrics.registerFont(TTFont('SGB', r'C:\Windows\Fonts\LeelaUIb.ttf', shapable=True))
assert pdfmetrics.getFont('SG').shapable
layout_checks = []
embedded_images = {}


def width(text, size=11, bold=False):
    font = 'SGB' if bold else 'SG'
    value = shapeStr(text, font, size)
    return sum(g.x_advance for g in value.__shapeData__) * size / 1000 if hasattr(value, '__shapeData__') else pdfmetrics.stringWidth(text, font, size)


def line(c, text, x, y, size=11, color=INK, bold=False, maxw=None, align='left'):
    actual = width(text, size, bold)
    if maxw is not None and actual > maxw + 0.5:
        raise ValueError(f'Text exceeds width: {text!r} ({actual:.1f}>{maxw:.1f})')
    c.setFont('SGB' if bold else 'SG', size)
    c.setFillColor(color)
    method = c.drawRightString if align == 'right' else c.drawCentredString if align == 'center' else c.drawString
    method(x, y, text, shaping=True)
    layout_checks.append({'text': text, 'x': round(x, 2), 'y': round(y, 2), 'size': size, 'width': round(actual, 2)})


def lines(c, values, x, y, size=11, leading=18, color=INK, bold=False, maxw=None):
    for value in values:
        line(c, value, x, y, size, color, bold, maxw)
        y -= leading
    return y


def image_fit(c, filename, x, y, w, h):
    path = HERE / filename
    with Image.open(path) as im:
        iw, ih = im.size
        if filename.startswith('artwork/'):
            embed_path = HERE / 'embed' / f'{path.stem}.jpg'
            if filename not in embedded_images:
                embed_path.parent.mkdir(parents=True, exist_ok=True)
                im.convert('RGB').save(embed_path, 'JPEG', quality=95, subsampling=0, optimize=True)
                embedded_images[filename] = {'pixels': [iw, ih], 'jpeg_quality': 95, 'resized': False, 'source_bytes': path.stat().st_size, 'embedded_bytes': embed_path.stat().st_size}
            path = embed_path
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask='auto')
    return min(iw / (dw / 72), ih / (dh / 72))


def start(c, number, label, background=PAPER, title=None):
    c.setFillColor(background)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    line(c, 'SmartGift', 15 * mm, H - 16 * mm, 18, bold=True)
    line(c, label, W - 15 * mm, H - 15 * mm, 8.5, MUTED, align='right')
    c.setStrokeColor(LINE)
    c.setLineWidth(.6)
    c.line(15 * mm, H - 21 * mm, W - 15 * mm, H - 21 * mm)
    line(c, 'CREATIVE PROOF  /  2026', 15 * mm, 10 * mm, 7.5, MUTED)
    line(c, f'{number:02d}', W - 15 * mm, 10 * mm, 9, MUTED, align='right')
    if title:
        c.bookmarkPage(f'p{number}')
        c.addOutlineEntry(title, f'p{number}', 0)


def finish(c):
    c.showPage()


def cover(c):
    start(c, 1, 'CORPORATE GIFT PORTFOLIO', title='SmartGift: ของขวัญที่เริ่มจากผู้รับ')
    image_fit(c, SETS[0]['artwork'], 91 * mm, 28 * mm, 197 * mm, 153 * mm)
    line(c, 'THE RECIPIENT-FIRST EDIT', 18 * mm, 166 * mm, 9, TEAL)
    lines(c, ['ของขวัญที่', 'เริ่มจากผู้รับ'], 18 * mm, 142 * mm, 29, 43, bold=True, maxw=111 * mm)
    lines(c, ['คัดสรรสิ่งของและรายละเอียด', 'ให้เหมาะกับคน โอกาส', 'และความรู้สึกที่อยากส่งต่อ'], 18 * mm, 94 * mm, 12, 21, MUTED, maxw=105 * mm)
    line(c, '4 GIFT SETS  /  6 SINGLE PRODUCTS', 18 * mm, 38 * mm, 9, TEAL)
    line(c, 'ภาพสร้างสรรค์จากภาพสินค้าอ้างอิง', 18 * mm, 23 * mm, 8.5, MUTED)
    finish(c)


def philosophy(c):
    start(c, 2, 'A THOUGHTFUL START', title='เริ่มจากคนและโอกาส')
    line(c, 'ให้ใคร เพื่ออะไร ในโอกาสใด', 18 * mm, 167 * mm, 27, bold=True, maxw=265 * mm)
    lines(c, ['หนึ่งแคมเปญอาจมีหลายกลุ่มผู้รับ เลือกสิ่งของและวิธีนำเสนอให้เหมาะกัน',
              'โดยยังสื่อสารเรื่องราวของแบรนด์เดียวกัน'], 18 * mm, 149 * mm, 12, 21, MUTED, maxw=260 * mm)
    tiers = [('Reach', 'เข้าถึงผู้รับในวงกว้าง'), ('Select', 'คัดให้เหมาะกับกลุ่ม'), ('Signature', 'ใส่ใจในรายละเอียด'), ('Bespoke', 'ออกแบบตามบริบท')]
    colw = 60 * mm
    for i, (name, desc) in enumerate(tiers):
        x = 18 * mm + i * 67 * mm
        line(c, f'0{i+1}', x, 119 * mm, 10, TEAL)
        c.setStrokeColor(LINE)
        c.line(x, 112 * mm, x + colw, 112 * mm)
        line(c, name, x, 98 * mm, 21, bold=True)
        line(c, desc, x, 84 * mm, 11, MUTED, maxw=colw)
    lines(c, ['ระดับการดูแลเป็นทางเลือกในการนำเสนอ ไม่ใช่การจัดลำดับคุณค่าของผู้รับ',
              'ความเหมาะสมของสินค้า การปรับแต่ง และจำนวนสั่งซื้อ ต้องยืนยันเป็นรายชุด'],
          18 * mm, 55 * mm, 11, 19, MUTED, maxw=260 * mm)
    finish(c)


def contents(c):
    start(c, 3, 'THE SELECTED SETS', title='ชุดของขวัญในเล่ม')
    line(c, 'สี่ชุด สี่บรรยากาศการให้', 18 * mm, 169 * mm, 26, bold=True)
    positions = [(18, 94), (154, 94), (18, 25), (154, 25)]
    for i, (s, (xx, yy)) in enumerate(zip(SETS, positions)):
        x, y = xx * mm, yy * mm
        image_fit(c, s['artwork'], x, y + 14 * mm, 63 * mm, 43 * mm)
        line(c, s['code'], x + 69 * mm, y + 48 * mm, 10, TEAL)
        lines(c, s['short_title_lines'], x + 69 * mm, y + 34 * mm, 15, 21, bold=True, maxw=58 * mm)
        line(c, f'ดูชุดนี้  /  0{i+4}', x + 69 * mm, y + 9 * mm, 9, MUTED)
        c.linkRect('', f'p{i+4}', (x, y, x + 124 * mm, y + 62 * mm), relative=0, thickness=0)
    finish(c)


def set_page(c, s, number):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    image_fit(c, s['artwork'], 0, 12 * mm, W, 198 * mm)
    dark = s.get('dark', False)
    main = WHITE if dark else INK
    secondary = HexColor('#E3E7E4') if dark else INK
    accent = HexColor('#E4CC96') if dark else TEAL
    c.bookmarkPage(f'p{number}')
    c.addOutlineEntry(f"{s['code']} - {s['title']}", f'p{number}', 0)
    line(c, 'SmartGift', 15 * mm, H - 16 * mm, 18, main, bold=True)
    line(c, f"GIFT SET / {s['code']}", W-15*mm, H-15*mm, 8.5, main, align='right')
    line(c, s['eyebrow'], 18 * mm, 166 * mm, 8.5, accent)
    lines(c, s['headline_lines'], 18 * mm, 148 * mm, 24, 35, main, bold=True, maxw=80 * mm)
    lines(c, s['copy_lines'], 18 * mm, 112 * mm, 11, 18, secondary, maxw=73 * mm)
    line(c, 'ในชุดประกอบด้วย', 18 * mm, 76 * mm, 11, main, bold=True)
    lines(c, s['components'], 18 * mm, 66 * mm, 10.5, 17, secondary, maxw=73 * mm)
    line(c, 'สอบถามราคา', 18 * mm, 31 * mm, 11, accent)
    line(c, 'ภาพสร้างสรรค์จากภาพสินค้าอ้างอิง • โปรดยืนยันรายละเอียดก่อนสั่งผลิต', 15 * mm, 6 * mm, 8, MUTED)
    line(c, f'{number:02d}', W-15*mm, 6*mm, 9, MUTED, align='right')
    finish(c)


def singles(c, products, number, heading):
    assert 2 <= len(products) <= 3
    start(c, number, 'SINGLE PRODUCTS', WHITE, title=heading)
    line(c, heading, 18 * mm, 169 * mm, 26, bold=True)
    line(c, 'เลือกเป็นชิ้นเดี่ยว หรือใช้เป็นจุดเริ่มต้นในการจัดชุด', 18 * mm, 155 * mm, 11, MUTED)
    usable = 261 * mm
    gap = 10 * mm
    colw = (usable - gap * (len(products) - 1)) / len(products)
    for i, p in enumerate(products):
        x = 18 * mm + i * (colw + gap)
        image_fit(c, p['image'], x, 71 * mm, colw, 72 * mm)
        line(c, p['code'], x, 63 * mm, 10, TEAL)
        lines(c, p['title_lines'], x, 51 * mm, 14, 19, bold=True, maxw=colw)
        line(c, 'สอบถามราคาและตัวเลือก', x, 28 * mm, 10, MUTED, maxw=colw)
    note = 'ภาพสินค้าอ้างอิงจาก catalog • ภาพหลายมุมคือสินค้ารุ่นเดียวกัน • โปรดยืนยันรายละเอียดก่อนสั่งผลิต' if number == 8 else 'ภาพจาก catalog; UT3056 / S1033 ปรับภาพด้วย AI • ภาพหลายมุมคือสินค้ารุ่นเดียวกัน'
    line(c, note, 18 * mm, 18 * mm, 8, MUTED)
    finish(c)


def unboxing(c):
    start(c, 10, 'THE ART OF UNBOXING', title='รายละเอียดของการเปิดกล่อง')
    line(c, 'ก่อนเห็นของ ก็เริ่มรู้สึกแล้ว', 18 * mm, 168 * mm, 26, bold=True)
    image_fit(c, SETS[2]['artwork'], 122 * mm, 35 * mm, 164 * mm, 120 * mm)
    for i, (title, detail) in enumerate([
        ('มองเห็น', 'รูปทรง สี และรายละเอียดภายนอก'),
        ('เปิดสัมผัส', 'วัสดุและจังหวะการเปิดกล่อง'),
        ('ค้นพบ', 'การจัดวางสิ่งของและข้อความ')]):
        y = (140 - i * 32) * mm
        line(c, f'0{i+1}', 18 * mm, y, 11, TEAL)
        line(c, title, 32 * mm, y, 18, bold=True)
        line(c, detail, 32 * mm, y - 11 * mm, 11, MUTED, maxw=100 * mm)
    lines(c, ['แนวทางการนำเสนอขึ้นกับแพ็กเกจของแต่ละชุด', 'ภาพประกอบเป็น ad creative จากภาพสินค้าอ้างอิง'], 18 * mm, 35 * mm, 9.5, 16, MUTED)
    finish(c)


def brief(c):
    start(c, 11, 'START YOUR GIFTING BRIEF', title='เตรียมโจทย์ของขวัญ')
    line(c, 'เริ่มคุยจากโจทย์ที่สำคัญ', 18 * mm, 168 * mm, 27, bold=True)
    for i, (question, hint) in enumerate([
        ('ให้ใคร', 'กลุ่มผู้รับและบริบทการให้'),
        ('เพื่ออะไร', 'โอกาสและความรู้สึกที่อยากส่งต่อ'),
        ('จำนวนเท่าไร', 'จำนวนโดยประมาณและงบต่อชุด'),
        ('ใช้เมื่อไร', 'วันใช้งานและรายละเอียดการส่งมอบ')]):
        x = (18 + (i % 2) * 139) * mm
        y = (138 - (i // 2) * 43) * mm
        line(c, f'0{i+1}', x, y, 10, TEAL)
        line(c, question, x + 15 * mm, y, 22, bold=True)
        line(c, hint, x + 15 * mm, y - 13 * mm, 11, MUTED, maxw=104 * mm)
    c.setStrokeColor(LINE)
    c.line(18 * mm, 53 * mm, 279 * mm, 53 * mm)
    lines(c, ['ฉบับนี้เป็น creative proof ของ 4 ชุดและสินค้าเดี่ยว 6 รายการที่คัดจาก catalog',
              'ภาพ ad creative สร้างใหม่จากภาพสินค้าอ้างอิง ไม่ใช่ภาพถ่ายสินค้ารอบผลิตใหม่',
              'ราคา สต็อก รายละเอียด การปรับแต่ง และสิทธิ์เผยแพร่ต้องยืนยันก่อนใช้งานจริง'],
          18 * mm, 43 * mm, 10, 17, MUTED, maxw=260 * mm)
    finish(c)


def back(c):
    start(c, 12, 'THOUGHTFUL AT EVERY LAYER', title='SmartGift')
    for i, s in enumerate(SETS):
        image_fit(c, s['artwork'], (18 + i * 67) * mm, 93 * mm, 60 * mm, 57 * mm)
    line(c, 'SmartGift', W/2, 76 * mm, 33, bold=True, align='center')
    line(c, 'ของขวัญที่เริ่มจากผู้รับ', W/2, 58 * mm, 18, MUTED, align='center')
    line(c, 'RECIPIENT-FIRST  /  CONSIDERED PRESENTATION', W/2, 37 * mm, 9, TEAL, align='center')
    finish(c)


target = OUT / 'smartgift-catalog-adcreative-proof-v0.2.pdf'
c = canvas.Canvas(str(target), pagesize=(W,H), pageCompression=1, pdfVersion=(1,7), initialFontName='SG')
c.setTitle('SmartGift - Recipient-first Catalog Creative Proof')
c.setAuthor('SmartGift')
c.setSubject('A4 landscape creative proof - 4 gift sets and 6 individual products')
c.setCreator('SmartGift Catalog Studio')
c.setViewerPreference('DisplayDocTitle', 'true')
cover(c)
philosophy(c)
contents(c)
for i, s in enumerate(SETS):
    set_page(c, s, 4+i)
singles(c, PRODUCTS[:3], 8, 'สินค้าเดี่ยวสำหรับวันทำงาน')
singles(c, PRODUCTS[3:6], 9, 'เติมความสะดวกในแต่ละวัน')
unboxing(c)
brief(c)
back(c)
c.save()
r = PdfReader(target)
assert len(r.pages) == 12
assert all(abs(float(p.mediabox.width)-W)<.05 and abs(float(p.mediabox.height)-H)<.05 for p in r.pages)
text = '\n'.join(p.extract_text() or '' for p in r.pages)
blocked = ['O:\\', 'C:\\', 'SHA-256', 'source_file', 'factory_cost', 'gross_margin', 'PII', 'CRM']
assert not any(term in text for term in blocked)
assert not r.attachments
report = {'pdf':str(target), 'pages':len(r.pages), 'page_mm':[297,210], 'set_count':len(SETS), 'single_product_pages':{'8':3,'9':3}, 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes':target.stat().st_size, 'font_shaping':True, 'pdfx_preflight':'NOT_PERFORMED', 'status':'creative-proof', 'attachments':0, 'text_chars':len(text), 'embedded_images':embedded_images}
(HERE/'pdf-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'layout-checks.json').write_text(json.dumps(layout_checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
