#!/usr/bin/env python3
"""แปลง public/data/catalog_listing.json เป็นเอกสารรายการอ่านง่าย (Markdown)

รัน build_catalog_listing.py ก่อน แล้วค่อยรันไฟล์นี้
ผลลัพธ์: docs/business/<YYYY-MM-DD>-catalog-listing.md
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / "public" / "data" / "catalog_listing.json"

CAT_TH = {
    "eco-friendly": "รักษ์โลก",
    "executive-smart-tech": "เทคโนโลยีและการทำงาน",
    "classic-oriental": "ศิลปะและวัฒนธรรม",
    "novelty-self-care": "ไลฟ์สไตล์และการดูแลตัวเอง",
}
IMG_TH = {
    "source_photo": "ภาพต้นฉบับ",
    "creative_proof": "ภาพสร้างจากต้นฉบับ",
    "placeholder": "ยังไม่มีภาพสินค้า",
    "unverified": "ยังไม่มีภาพสินค้า",
    "none": "ยังไม่มีภาพสินค้า",
}


def money(v) -> str:
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"


def price_cell(rec) -> str:
    if rec["price_status"] != "confirmed_tiers":
        return "สอบถามราคา"
    t = rec["price_tiers"]
    lo, hi = t[0], t[-1]
    if lo["min_qty"] == hi["min_qty"]:
        return f"{money(lo['unit_price'])} ฿ @{lo['min_qty']}+"
    return f"{money(hi['unit_price'])}–{money(lo['unit_price'])} ฿ ({hi['min_qty']}+ → {lo['min_qty']}+)"


def img_th(rec) -> str:
    return IMG_TH.get(rec.get("image_evidence"), "ยังไม่มีภาพสินค้า")


def esc(s) -> str:
    return (s or "—").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    d = json.loads(LISTING.read_text(encoding="utf-8"))
    gen = d["generated_at"]
    out = ROOT / "docs" / "business" / f"{gen}-catalog-listing.md"
    L: list[str] = []
    a = L.append

    a("---")
    a('version: "0.1.0b"')
    a(f'created_at: "{gen}T00:00:00+07:00,CLAUDE"')
    a(f'last_update: "{gen}T00:00:00+07:00,CLAUDE"')
    a('status: "beta"')
    a("attributes:")
    a('  scope: "catalog listing — แยกสินค้าเดี่ยว / ชุดของขวัญ"')
    a('  language: "th"')
    a("---")
    a("")
    a("# รายการ Catalog สินค้า — แยกเดี่ยว / ชุด")
    a("")
    a(f"อ้างอิง PM `{d['source']['product_manifest_version']}` · pricelist schema `{d['source']['pricelist_schema']}`")
    a("")
    a(f"> {d['disclaimer_th']}")
    a("")

    s, st = d["summary"]["singles"], d["summary"]["sets"]
    a("## สรุปจำนวน")
    a("")
    a("| | สินค้าเดี่ยว | ชุดของขวัญ | รวม |")
    a("|---|---:|---:|---:|")
    a(f"| **รวมทั้งหมด** | {s['total']} | {st['total']} | {s['total'] + st['total']} |")
    a(f"| ชั้น Core (PM ยืนยันแล้ว) | {s['core']} | {st['core']} | {s['core'] + st['core']} |")
    a(f"| ชั้น Supplier catalog | {s['supplier']} | {st['supplier']} | {s['supplier'] + st['supplier']} |")
    a(f"| มีราคาพร้อมขั้นจำนวน | {s['priced']} | {st['priced']} | {s['priced'] + st['priced']} |")
    a(f"| ต้องสอบถามราคา | {s['ask_for_quote']} | {st['ask_for_quote']} | {s['ask_for_quote'] + st['ask_for_quote']} |")
    a(f"| ภาพต้นฉบับที่ตรวจรหัสแล้ว | {s['source_photo']} | {st['source_photo']} | {s['source_photo'] + st['source_photo']} |")
    a(f"| ภาพสร้างจากต้นฉบับ (ไม่ใช่ภาพสินค้าจริง) | {s['creative_proof']} | {st['creative_proof']} | {s['creative_proof'] + st['creative_proof']} |")
    a(f"| ยังไม่มีภาพสินค้า | {s['no_usable_image']} | {st['no_usable_image']} | {s['no_usable_image'] + st['no_usable_image']} |")
    a("")

    # ---------------- เดี่ยว: core ----------------
    a("---")
    a("")
    a("# ส่วนที่ 1 — สินค้าเดี่ยว")
    a("")
    a(f"## 1.1 Core / PM canonical ({s['core']} รายการ)")
    a("")
    a("ราคายืนยันครบ 8 ขั้นจำนวน (1/10/20/50/100/300/500/1000) ใช้เสนอลูกค้าได้ทันที")
    a("")
    core_singles = [r for r in d["singles"] if r["tier"] == "core"]
    for slug in ["eco-friendly", "executive-smart-tech", "classic-oriental", "novelty-self-care"]:
        rows = [r for r in core_singles if r["category_slug"] == slug]
        if not rows:
            continue
        a(f"### {CAT_TH[slug]} ({slug}) — {len(rows)} รายการ")
        a("")
        a("| รหัส | ชื่อสินค้า | กลุ่ม | ขนาด (ก×ย×ส ซม.) | นน. (กก.) | SRP @1 | ราคา @1000 | ภาพ |")
        a("|---|---|---|---|---:|---:|---:|---|")
        for r in rows:
            dm = r.get("dimensions_cm") or {}
            dim = f"{dm.get('length','—')}×{dm.get('width','—')}×{dm.get('height','—')}" if dm else "—"
            last = r["price_tiers"][-1]["unit_price"] if r["price_tiers"] else None
            a(f"| `{r['code']}` | {esc(r['name_th'])} | {esc(r['product_family'])} | {dim} | "
              f"{r.get('unit_weight_kg') or '—'} | {money(r['srp_price'])} | "
              f"{money(last) if last else 'สอบถามราคา'} | {img_th(r)} |")
        a("")

    # ---------------- เดี่ยว: supplier ----------------
    sup_singles = sorted((r for r in d["singles"] if r["tier"] == "supplier"), key=lambda r: r["code"])
    a(f"## 1.2 Supplier catalog — เดี่ยว ({len(sup_singles)} รายการ)")
    a("")
    a("มาจาก catalog ผู้ผลิต ยังไม่ผ่านการยืนยันเป็น PM canonical")
    a("")
    a("| รหัส | ชื่อ | รายละเอียดตามต้นฉบับ | ราคา | สถานะจัดหมวด | ภาพ |")
    a("|---|---|---|---|---|---|")
    for r in sup_singles:
        a(f"| `{r['code']}` | {esc(r['name_th'] or r['name_en'])} | {esc(r.get('description'))} | "
          f"{price_cell(r)} | {r['classification_status']} | {img_th(r)} |")
    a("")

    # ---------------- ชุด: core ----------------
    a("---")
    a("")
    a("# ส่วนที่ 2 — ชุดของขวัญ")
    a("")
    core_sets = [r for r in d["sets"] if r["tier"] == "core"]
    a(f"## 2.1 Core / ชุดที่ยืนยันส่วนประกอบแล้ว ({len(core_sets)} ชุด)")
    a("")
    for r in core_sets:
        a(f"### `{r['code']}` — {r['name_th']}")
        a("")
        a(f"- หมวด: {CAT_TH.get(r['category_slug'], r['category_slug'])} · ระดับ: **{r.get('gift_tier') or '—'}**")
        if r.get("unboxing_experience"):
            a(f"- ประสบการณ์เปิดกล่อง: {r['unboxing_experience']}")
        a(f"- ภาพ: {img_th(r)}")
        a(f"- ราคา: {price_cell(r)}")
        if r["price_tiers"]:
            a("  - " + " · ".join(f"{t['min_qty']}+ = {money(t['unit_price'])} ฿" for t in r["price_tiers"]))
        a(f"- ในชุดประกอบด้วย ({r['component_count']} รายการ, {('ยืนยันแล้ว' if r['components_status'] == 'confirmed_bom' else 'อยู่ระหว่างยืนยัน')}):")
        for c in r["components"]:
            srp = f" — SRP {money(c['unit_srp_qty1'])} ฿" if c.get("unit_srp_qty1") else ""
            a(f"  - `{c['product_code']}` × {c.get('qty')} — {c.get('name_th') or '—'}{srp}")
        a("")

    # ---------------- ชุด: supplier ----------------
    sup_sets = [r for r in d["sets"] if r["tier"] == "supplier"]
    priced = sorted((r for r in sup_sets if r["price_status"] == "confirmed_tiers"), key=lambda r: r["code"])
    quote = sorted((r for r in sup_sets if r["price_status"] != "confirmed_tiers"), key=lambda r: r["code"])

    a(f"## 2.2 Supplier catalog — ชุด ({len(sup_sets)} รายการ)")
    a("")
    a(f"แยกเป็น มีราคาพร้อมขั้นจำนวน {len(priced)} รายการ · ต้องสอบถามราคา {len(quote)} รายการ")
    a("")
    a(f"### 2.2.1 มีราคาพร้อมขั้นจำนวน ({len(priced)} รายการ)")
    a("")
    a("| รหัส | ชื่อ | รายละเอียดตามต้นฉบับ | ช่วงราคา | ภาพ |")
    a("|---|---|---|---|---|")
    for r in priced:
        a(f"| `{r['code']}` | {esc(r['name_th'] or r['name_en'])} | {esc(r.get('description'))} | "
          f"{price_cell(r)} | {img_th(r)} |")
    a("")
    a(f"### 2.2.2 ต้องสอบถามราคา ({len(quote)} รายการ)")
    a("")
    a("| รหัส | ชื่อ | รายละเอียดตามต้นฉบับ | สถานะจัดหมวด | ภาพ |")
    a("|---|---|---|---|---|")
    for r in quote:
        a(f"| `{r['code']}` | {esc(r['name_th'] or r['name_en'])} | {esc(r.get('description'))} | "
          f"{r['classification_status']} | {img_th(r)} |")
    a("")

    a("---")
    a("")
    a("## ช่องว่างข้อมูลที่ต้องปิดก่อนขึ้นหน้า catalog ลูกค้า")
    a("")
    cls = Counter(r["classification_status"] for r in sup_sets + sup_singles)
    a(f"1. **ราคา** — ชุด supplier {len(quote)} จาก {len(sup_sets)} รายการยังไม่มีราคาผูกกับขั้นจำนวน ต้องแสดง \"สอบถามราคา\" ตาม SPEC ห้ามใส่ 0 บาท")
    a(f"2. **ภาพ** — {st['no_usable_image'] + s['no_usable_image']} รายการยังไม่มีภาพสินค้าที่ใช้ได้ (path `/assets/products/catalog-2026/*.webp` ยังไม่มีไฟล์เลย และ PM canonical 16 รายการชี้ไปที่ `hero-fxd66-3-generated.webp` ซึ่งเป็น `fallback-placeholder`) ต้องแสดง \"ยังไม่มีภาพสินค้า\" ไม่ใช่ภาพแทน")
    a(f"3. **การจัดหมวด** — สถานะ supplier: " + ", ".join(f"{k}={v}" for k, v in cls.most_common()) + " ; รายการที่ไม่ใช่ `auto` ยังไม่ควรถือว่าพร้อมเสนอ")
    a("4. **ส่วนประกอบชุด** — ชุด supplier ยังไม่มี BOM ยืนยัน ต้องขึ้นข้อความ \"รายละเอียดชุดอยู่ระหว่างยืนยัน\" ไม่แตกรายการจากชื่อชุด")
    a("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote " + str(out.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
