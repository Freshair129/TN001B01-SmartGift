#!/usr/bin/env python3
"""ย้อม public/internal.html ให้ใช้สีแบรนด์จาก tokens/smartgift-color.tokens.json

แดชบอร์ดภายในเขียนด้วยมือ ไม่ได้ generate ทั้งไฟล์ สคริปต์นี้จึงทำสองอย่าง
  1. เขียนบล็อก :root ใหม่ โดยคงชื่อตัวแปรเดิมทุกตัว (--accent, --good, --warn, ...)
     ของเดิมอ้างชื่อพวกนี้อยู่ทั่วไฟล์ เปลี่ยนแค่ค่าเลยไม่กระทบ layout
  2. แทน hex ที่ hardcode ไว้นอกบล็อก token (แผงมืด 2.5D, glass orbs, ป้าย expo)

รันซ้ำได้ ค่าใหม่ไม่อยู่ในตารางแปลง จึงไม่ถูกแปลงซ้ำ
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_kit import tok  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "public" / "internal.html"
# แผงลูกค้าที่ internal.html เรียกใช้ตอนอยู่ route #/catalog ต้องย้อมด้วย ไม่งั้นสีไม่ตรงกัน
CSS_TARGET = ROOT / "public" / "customer-catalog.css"

# hex ใน customer-catalog.css -> token path
CSS_MAP = {
    "#163038": "semantic.text.primary",
    "#52626a": "semantic.text.muted",
    "#344c56": "color.cocoa.700",
    "#08798a": "semantic.text.brand",       # พื้นปุ่มที่เลือก + เส้นโฟกัส ต้องผ่าน AA
    "#086679": "semantic.text.brand",
    "#e3f5f7": "semantic.background.brand-subtle",
    "#dce4e7": "semantic.border.subtle",
    "#cbd6da": "semantic.border.default",
    "#fafafa": "semantic.background.subtle",
    "#f1f5f6": "color.cocoa.50",
    "#edf1f2": "semantic.border.subtle",
}
CSS_RGBA_OLD = re.compile(r"rgba\(\s*16\s*,\s*35\s*,\s*42\s*,\s*([0-9.]+)\s*\)")

# ชื่อตัวแปรเดิม -> token path
# --accent ถูกใช้เป็นสีตัวอักษรลิงก์ จึงต้องเป็น orange.700 ที่ผ่าน AA ไม่ใช่ orange.500
ROOT_VARS = [
    ("bg", "semantic.background.subtle"),
    ("panel", "semantic.background.surface"),
    ("soft", "color.cocoa.50"),
    ("ink", "semantic.text.primary"),
    ("muted", "semantic.text.muted"),
    ("line", "semantic.border.subtle"),
    ("strong", "semantic.border.default"),
    ("accent", "semantic.text.brand"),
    ("accent-visual", "semantic.brand.primary"),
    ("accent-soft", "semantic.background.brand-subtle"),
    ("good", None, "#186B45"),
    ("good-bg", None, "#E6F4EC"),
    ("warn", "color.gold.700"),
    ("warn-bg", "color.gold.100"),
    ("bad", None, "#A8323D"),
    ("bad-bg", None, "#FBE9EA"),
    ("gold", "semantic.brand.accent-strong"),
    ("gold-bg", "color.gold.50"),
]

# hex ที่ hardcode ไว้นอกบล็อก token -> token path
HEX_MAP = {
    "#78b9cb": "semantic.border.focus",     # เส้นโฟกัส
    "#08798a": "semantic.text.brand",       # glass orb + เงา
    "#0ea5b7": "semantic.brand.primary",
    "#d4af37": "semantic.brand.accent",     # glass orb ทอง
    "#3b82f6": "semantic.brand.signature-dark",  # glass orb ที่สาม
    "#38d6df": "color.orange.400",          # ไฮไลต์บนแผงมืด
    "#1e293b": "color.cocoa.900",           # ไล่สีแผงมืด
    "#0a0f16": "color.neutral.950",
    "#e2e8f0": "color.neutral.100",
    "#cbd5e1": "color.cocoa.200",
    "#94a3b8": "color.cocoa.300",
    "#edf1f3": "semantic.border.subtle",
    "#194d56": "color.cocoa.700",           # ป้าย expo ใบแรก
    "#0b1824": "color.cocoa.950",
    "#3a3b63": "color.gold.800",            # ป้าย expo ปีใหม่ — เปลี่ยนเป็นโทนทอง
    "#10182d": "color.gold.950",
}

# rgba ของสี accent เดิม (เงา ออร่า พื้นโปร่ง) — จับได้ทุกค่า alpha
RGBA_OLD = re.compile(r"rgba\(\s*8\s*,\s*121\s*,\s*138\s*,\s*([0-9.]+)\s*\)")
RGBA_TOKEN = "semantic.text.brand"


def rgba(path: str, alpha: float) -> str:
    h = tok(path).lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alpha})"


def main() -> int:
    html = TARGET.read_text(encoding="utf-8")
    original = html

    lines = ["    :root {", "      color-scheme: light;"]
    for entry in ROOT_VARS:
        name = entry[0]
        value = entry[2] if len(entry) == 3 else tok(entry[1])
        lines.append(f"      --{name}: {value};")
    lines.append("    }")
    block = "\n".join(lines)

    html, n = re.subn(r"    :root \{.*?\n    \}", block, html, count=1, flags=re.S)
    if n != 1:
        print("ERROR: หาบล็อก :root ไม่เจอ ไม่ได้แก้ไฟล์", file=sys.stderr)
        return 1

    swapped = 0
    for old, path in HEX_MAP.items():
        new = tok(path)
        for variant in (old, old.upper()):
            if variant in html:
                swapped += html.count(variant)
                html = html.replace(variant, new)
    hits = RGBA_OLD.findall(html)
    if hits:
        swapped += len(hits)
        html = RGBA_OLD.sub(lambda m: rgba(RGBA_TOKEN, float(m.group(1))), html)

    if html == original:
        print("internal.html — ย้อมไปแล้ว")
    else:
        TARGET.write_text(html, encoding="utf-8")
        print(f"ย้อม public/internal.html แล้ว — :root {len(ROOT_VARS)} ตัวแปร + hex นอกบล็อก {swapped} จุด")
    _css()
    return 0


def _css() -> None:
    css = CSS_TARGET.read_text(encoding="utf-8")
    before = css
    n = 0
    for old, path in CSS_MAP.items():
        new = tok(path)
        for variant in (old, old.upper()):
            if variant in css:
                n += css.count(variant)
                css = css.replace(variant, new)
    hits = CSS_RGBA_OLD.findall(css)
    if hits:
        n += len(hits)
        css = CSS_RGBA_OLD.sub(lambda m: rgba("color.cocoa.950", float(m.group(1))), css)
    if css == before:
        print("customer-catalog.css — ย้อมไปแล้ว")
        return
    CSS_TARGET.write_text(css, encoding="utf-8")
    print(f"ย้อม public/customer-catalog.css แล้ว — {n} จุด")


if __name__ == "__main__":
    sys.exit(main())
