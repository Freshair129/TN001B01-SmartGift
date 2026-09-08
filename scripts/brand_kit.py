#!/usr/bin/env python3
"""ชุดแบรนด์ SmartGift Thailand — โลโก้ + CSS ที่ generate จาก design tokens

สีทั้งหมดมาจาก tokens/smartgift-color.tokens.json (W3C Design Tokens format)
ซึ่ง sample จากไฟล์โลโก้จริง ไม่มีการ hardcode สีแบรนด์ในไฟล์นี้

emit ออกมาเป็น CSS custom properties 3 ชั้น
  1. scale        --orange-500, --cocoa-600, --neutral-200 ...
  2. alias ใช้งาน --brand, --ink, --line, --action-bg ... (ชื่อสั้นที่หน้าเว็บอ้างถึง)
  3. ธีมสำรอง B/C จากภาพเปรียบเทียบ — ไม่ได้อยู่ในไฟล์ token
     มีแค่ธีม A เท่านั้นที่เป็นสีแบรนด์จริงที่ sample มา
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "tokens" / "smartgift-color.tokens.json"

# ปุ่ม "ขอใบเสนอราคา" ต้องมีปลายทางจริง เติมค่าที่นี่แล้ว rebuild
# ปล่อยว่าง = ปุ่มจะใช้ "คัดลอกรายการ" ซึ่งทำงานได้จริงอยู่แล้ว
CONTACT = {
    "email": "",
    "line": "",
    "tel": "",
}

_DOC = json.loads(TOKENS.read_text(encoding="utf-8"))
_ALIAS = re.compile(r"^\{([^}]+)\}$")


def _walk(path: str):
    node = _DOC
    for part in path.split("."):
        node = node[part]
    return node


def tok(path: str) -> str:
    """resolve token path เช่น 'color.orange.500' หรือ 'semantic.text.brand' เป็นค่า hex"""
    node = _walk(path)
    value = node["$value"] if isinstance(node, dict) and "$value" in node else node
    m = _ALIAS.match(value) if isinstance(value, str) else None
    return tok(m.group(1)) if m else value


def _gradient(name: str, angle: str = "135deg") -> str:
    stops = _walk("gradient." + name)["$value"]
    parts = []
    for s in stops:
        m = _ALIAS.match(s["color"])
        parts.append(f"{tok(m.group(1)) if m else s['color']} {round(s['position'] * 100)}%")
    return f"linear-gradient({angle}, " + ", ".join(parts) + ")"


def _rgba(path: str, alpha: float) -> str:
    h = tok(path).lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alpha})"


SCALES = ["orange", "gold", "cocoa", "neutral"]

# alias ที่หน้าเว็บใช้ -> token path (โหมดสว่าง)
LIGHT = {
    "paper": "color.neutral.0",
    "ground": "semantic.background.canvas",
    "surface": "semantic.background.surface",
    "sunk": "semantic.background.subtle",
    "stage": "color.cocoa.900",          # พื้นหลังเข้มรอบ flipbook
    "ink": "semantic.text.primary",
    "muted": "semantic.text.muted",
    "line": "semantic.border.subtle",
    "line-strong": "semantic.border.default",
    "brand": "semantic.brand.primary",
    "brand-deep": "semantic.text.brand",
    "brand-wash": "semantic.background.brand-subtle",
    "brown": "semantic.brand.signature-dark",
    "brown-deep": "color.cocoa.900",
    "gold": "semantic.brand.accent",
    "gold-deep": "semantic.brand.accent-strong",
    "gold-wash": "color.gold.50",
    "bar": "color.orange.200",
    "bar-lead": "color.orange.500",
    "flag-ink": "color.gold.700",
    "flag-wash": "color.gold.100",
    "action-bg": "semantic.action.primary-background",
    "action-bg-hover": "semantic.action.primary-background-hover",
    "on-brand": "semantic.action.primary-foreground",
    "focus": "semantic.border.focus",
}

# โหมดมืด — เลื่อนขั้นบน scale เดียวกัน ไม่ได้คิดสีใหม่นอกไฟล์ token
DARK = {
    "ground": "color.neutral.950",
    "surface": "color.cocoa.950",
    "sunk": "color.cocoa.900",
    "stage": "color.neutral.950",
    "ink": "color.neutral.100",
    "muted": "color.cocoa.300",
    "line": "color.cocoa.800",
    "line-strong": "color.cocoa.700",
    "brand": "color.orange.400",
    "brand-deep": "color.orange.300",
    "brand-wash": "color.orange.950",
    "brown": "color.cocoa.300",
    "brown-deep": "color.cocoa.100",
    "gold": "color.gold.300",
    "gold-deep": "color.gold.200",
    "gold-wash": "color.gold.950",
    "bar": "color.orange.800",
    "bar-lead": "color.orange.400",
    "flag-ink": "color.gold.200",
    "flag-wash": "color.gold.950",
    "action-bg-hover": "color.orange.600",
    "focus": "color.orange.400",
}

FONTS = """    --display: "IBM Plex Sans Thai", "Noto Sans Thai", system-ui, sans-serif;
    --body: "Noto Sans Thai", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Consolas, monospace;"""

ALT_THEMES = """
  /* B · Warm Festive — แดงเทศกาล + ทอง (ธีมแคมเปญ ไม่ใช่สีแบรนด์ที่ sample มา) */
  :root[data-palette="b"] {
    --ground: #fdfaf8; --sunk: #f8efea; --ink: #2d1a19; --muted: #7d605c;
    --line: #eeddd7; --line-strong: #ddc5bd; --stage: #35201d;
    --brand: #c0392f; --brand-deep: #8e2119; --brand-wash: #fceeec;
    --brown: #6b4038; --brown-deep: #35201d;
    --gold: #d4af37; --gold-deep: #96761a; --gold-wash: #fbf3d8;
    --bar: #eab9b3; --bar-lead: #c0392f;
    --flag-ink: #875016; --flag-wash: #f7edc8;
    --action-bg: #8e2119; --action-bg-hover: #6f180f; --focus: #8e2119;
  }

  /* C · Modern Teal — teal + เทาฟ้า (ธีมแคมเปญ ไม่ใช่สีแบรนด์ที่ sample มา) */
  :root[data-palette="c"] {
    --ground: #f8fbfa; --sunk: #eaf3f1; --ink: #16292b; --muted: #5f7b7c;
    --line: #dcebe8; --line-strong: #bfd6d2; --stage: #1d3335;
    --brand: #17857f; --brand-deep: #0b5b56; --brand-wash: #e3f3f0;
    --brown: #40595a; --brown-deep: #1d3335;
    --gold: #d0a54e; --gold-deep: #9c762c; --gold-wash: #f8f0dd;
    --bar: #96c8c2; --bar-lead: #17857f;
    --flag-ink: #875016; --flag-wash: #f7edc8;
    --action-bg: #0b5b56; --action-bg-hover: #084441; --focus: #0b5b56;
  }
"""

# ---- โลโก้ ---------------------------------------------------------------
# กล่องไอโซเมตริก หน้าซ้ายส้มเจาะตัว S หน้าขวาน้ำตาลเจาะตัว G ฝาบนแบ่งสี่ช่องด้วยกากบาทขาว
# โบว์ทองวาดด้วย stroke เพื่อให้เกิดช่องว่างกลางห่วงเหมือนต้นฉบับ
# แต่ละหน้า map ด้วย matrix ให้กรอบพิกัด 40x40 ตกลงบนหน้ากล่องพอดี ตัวอักษรจึงเอียงตามหน้า
LOGO_SVG = """<svg class="sg-mark" viewBox="0 -20 120 120" role="img" aria-label="SmartGift Thailand">
  <g class="sg-bow" fill="none" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <path d="M60 14C46 0 28-6 24 2c-4 8 14 14 36 12Z"/>
    <path d="M60 14c14-14 32-20 36-12 4 8-14 14-36 12Z"/>
  </g>
  <rect class="sg-knot" x="54" y="6" width="12" height="15" rx="2.5"/>
  <path class="sg-top" d="M60 16 100 36 60 56 20 36Z"/>
  <path class="sg-left" d="M20 36 60 56v40L20 76Z"/>
  <path class="sg-right" d="M100 36 60 56v40l40-20Z"/>
  <path class="sg-cross" d="M40 26 80 46M80 26 40 46" stroke-width="5.5"/>
  <text class="sg-letter" transform="matrix(1 .5 0 1 20 36)" x="20" y="30" text-anchor="middle" font-size="40">S</text>
  <text class="sg-letter" transform="matrix(1 -.5 0 1 60 56)" x="20" y="30" text-anchor="middle" font-size="40">G</text>
</svg>
<span class="sg-bar" aria-hidden="true"></span>
<span class="sg-word">
  <span class="sg-w1">SMART</span>
  <span class="sg-w2">GIFT</span>
  <span class="sg-w3"><i></i>THAILAND<i></i></span>
</span>"""

LOGO_CSS = """
  .sg-lockup { display: inline-flex; align-items: center; gap: 12px; text-decoration: none; }
  .sg-mark { width: 58px; height: auto; flex: none; }
  .sg-bow { stroke: var(--gold); }
  .sg-knot { fill: var(--gold-deep); }
  .sg-top, .sg-left { fill: var(--brand); }
  .sg-right { fill: var(--brown); }
  .sg-cross { stroke: var(--surface); }
  .sg-letter { font-family: var(--display); font-weight: 800; fill: var(--surface); }
  .sg-bar { width: 1.5px; align-self: stretch; min-height: 46px; background: var(--gold); flex: none; }
  .sg-word { display: grid; gap: 3px; line-height: 1; }
  .sg-w1 { font-family: var(--display); font-weight: 600; font-size: 14px; letter-spacing: .3em; color: var(--brown); }
  .sg-w2 { font-family: var(--display); font-weight: 700; font-size: 22px; letter-spacing: .13em; color: var(--brand); }
  .sg-w3 { display: flex; align-items: center; gap: 7px; font-family: var(--display); font-weight: 600; font-size: 8px; letter-spacing: .34em; color: var(--gold-deep); margin-top: 2px; }
  .sg-w3 i { flex: 1; min-width: 9px; height: 1px; background: var(--grad-gold); }
  .sg-tagline { font-size: 12.5px; color: var(--brown); letter-spacing: .01em; }
  .sg-tagline b { color: var(--brand-deep); font-weight: 600; }
"""


def _alias_block(mapping: dict, indent: str) -> str:
    return "".join(f"{indent}--{k}: {tok(v)};\n" for k, v in mapping.items())


def theme_css() -> str:
    """CSS ทั้งหมด: scale + alias + ธีมสำรอง + โหมดมืดครบสามสถานะของ viewer + โลโก้"""
    out = ["  :root {"]
    for scale in SCALES:
        for step in _DOC["color"][scale]:
            if step != "$type":
                out.append(f"    --{scale}-{step}: {tok('color.' + scale + '.' + step)};")
    out.append("")
    out.append(_alias_block(LIGHT, "    ").rstrip("\n"))
    out.append(f"    --grad-orange: {_gradient('brand-orange')};")
    out.append(f"    --grad-gold: {_gradient('brand-gold', '90deg')};")
    out.append(f"    --shadow: 0 1px 2px {_rgba('color.cocoa.950', 0.08)};")
    out.append(f"    --shadow-lift: 0 10px 30px {_rgba('color.cocoa.950', 0.14)};")
    out.append(FONTS)
    out.append("  }\n")
    out.append(ALT_THEMES)

    dark = (_alias_block(DARK, "      ")
            + f"      --shadow: 0 1px 2px {_rgba('color.neutral.950', 0.5)};\n"
            + f"      --shadow-lift: 0 10px 30px {_rgba('color.neutral.950', 0.6)};\n")
    out.append('  @media (prefers-color-scheme: dark) {\n    :root:not([data-theme="light"]) {\n'
               + dark + "    }\n  }")
    out.append('  :root[data-theme="dark"] {\n' + dark.replace("      ", "    ") + "  }")
    out.append(LOGO_CSS)
    return "\n".join(out)


FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Thai:wght@500;600;700;800&"
    'family=Noto+Sans+Thai:wght@400;500;600&display=swap">'
)
