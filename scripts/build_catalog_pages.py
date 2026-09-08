#!/usr/bin/env python3
"""สร้างหน้า catalog สองแบบจาก catalog_listing.json (เฉพาะชั้น Core)

  public/index.html           CATALOG WEB     — ค้นหา / หมวด / การ์ด / รายละเอียด / เปรียบเทียบ / ขอใบเสนอราคา
  public/catalog-offline.html CATALOG OFFLINE — flipbook 12 หน้า เปิดได้โดยไม่ต้องใช้อินเทอร์เน็ต

แบรนด์และธีมอยู่ใน scripts/brand_kit.py (Smart Orange เป็นค่าเริ่มต้น)
ข้อมูลถูกฝังลงในไฟล์ ไม่ fetch ตอน runtime เพื่อให้หน้า offline ทำงานได้จริง

ยึด SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30:
  แยกรายชิ้น/ชุด · ไม่มีภาพยืนยัน = "ยังไม่มีภาพสินค้า" · ราคาผูกขั้นจำนวนเสมอ · ไม่โชว์ต้นทุน/รหัสภายใน
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_kit import CONTACT, FONT_LINK, LOGO_SVG, theme_css  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / "public" / "data" / "catalog_listing.json"
OUT_WEB = ROOT / "public" / "index.html"
OUT_OFF = ROOT / "public" / "catalog-offline.html"

UNSORTED = "unsorted"
CATEGORIES = [
    ("eco-friendly", "รักษ์โลก"),
    ("executive-smart-tech", "เทคโนโลยีและการทำงาน"),
    ("classic-oriental", "ศิลปะและวัฒนธรรม"),
    ("novelty-self-care", "ไลฟ์สไตล์และการดูแลตัวเอง"),
]
FAMILY_TH = {
    "PF-DRINKWARE": "แก้วและกระบอกน้ำ",
    "PF-OUTDOOR-LIFESTYLE": "ของใช้นอกบ้าน",
    "PF-ECO-LIFESTYLE": "ของใช้รักษ์โลก",
    "PF-SMART-OFFICE": "อุปกรณ์โต๊ะทำงาน",
    "PF-POWER-CHARGING": "พลังงานและการชาร์จ",
    "PF-AUDIO-TECH": "เครื่องเสียง",
    "PF-STORAGE-TECH": "อุปกรณ์เก็บข้อมูล",
    "PF-CRAFT-STATIONERY": "เครื่องเขียนงานคราฟต์",
    "PF-WELLNESS-HEALTH": "สุขภาพและการผ่อนคลาย",
}
TIER_TH = {
    "Reach": "Reach — ส่งถึงวงกว้าง",
    "Select": "Select — คัดสรร",
    "Signature": "Signature — ชูภาพลักษณ์",
    "Bespoke": "Bespoke — ออกแบบเฉพาะ",
}


def _photo_items(data):
    """รายการจาก catalog ผู้ผลิตที่มี "ภาพต้นฉบับตรวจรหัสแล้ว" อยู่จริงบนดิสก์

    ของพวกนี้ยังไม่ผ่านการยืนยันเป็น PM canonical จึงถูกทำเครื่องหมายเป็นชั้น supplier
    และไม่มี category_slug ติดมา เลยตกไปอยู่หมวด "ยังไม่จัดหมวด"
    """
    out = []
    for r in data["singles"] + data["sets"]:
        if r["tier"] != "supplier" or r["image_status"] != "verified_file":
            continue
        if r["image_evidence"] not in ("source_photo", "creative_proof"):
            continue
        out.append({
            "code": r["code"], "kind": r["kind"], "tier": "supplier",
            "name": r.get("name_th") or r.get("name_en") or r["code"],
            "nameEn": r.get("name_en"),
            "desc": r.get("description"),
            "cat": UNSORTED,
            "status": r.get("classification_status"),
            "tiers": r.get("price_tiers") or [],
            "img": r["image_url"],
            "proof": r["image_evidence"] == "creative_proof",
            "components": [],
        })
    out.sort(key=lambda r: (not r["tiers"], r["code"]))
    return out


def collect():
    data = json.loads(LISTING.read_text(encoding="utf-8"))
    items = []
    for r in (x for x in data["singles"] if x["tier"] == "core"):
        dm = r.get("dimensions_cm") or {}
        items.append({
            "code": r["code"], "kind": "single", "tier": "core", "name": r["name_th"],
            "nameEn": r.get("name_en"), "cat": r["category_slug"],
            "group": FAMILY_TH.get(r.get("product_family")),
            "dims": [dm.get("length"), dm.get("width"), dm.get("height")] if dm.get("length") else None,
            "weight": r.get("unit_weight_kg"), "tiers": r.get("price_tiers") or [],
            "img": None, "proof": False, "components": [],
        })
    for r in (x for x in data["sets"] if x["tier"] == "core"):
        items.append({
            "code": r["code"], "kind": "set", "tier": "core", "name": r["name_th"],
            "cat": r["category_slug"], "giftTier": r.get("gift_tier"),
            "giftTierTh": TIER_TH.get(r.get("gift_tier")),
            "unboxing": r.get("unboxing_experience"), "components": r.get("components") or [],
            "componentsConfirmed": r.get("components_status") == "confirmed_bom",
            "tiers": r.get("price_tiers") or [], "img": None, "proof": False,
        })
    photos = _photo_items(data)
    items += photos

    cats = [{"slug": s, "name": n} for s, n in CATEGORIES]
    if photos:
        cats.append({"slug": UNSORTED, "name": "ยังไม่จัดหมวด"})

    return {
        "catalogVersion": data["source"]["product_manifest_version"],
        "generatedAt": data["generated_at"],
        "totalAll": data["summary"]["singles"]["total"] + data["summary"]["sets"]["total"],
        "coreCount": len(items) - len(photos),
        "photoCount": len(photos),
        "categories": cats,
        "contact": CONTACT,
        "items": items,
    }


def embed_images(payload):
    """แปลง path รูปเป็น data URI เพื่อให้ไฟล์เดียวเปิดอ่านได้จริงตอนไม่มีเน็ต"""
    import base64
    import copy
    out = copy.deepcopy(payload)
    cache = {}
    for item in out["items"]:
        url = item.get("img")
        if not url:
            continue
        if url not in cache:
            path = ROOT / "public" / url.lstrip("/")
            mime = "image/webp" if path.suffix == ".webp" else "image/jpeg"
            cache[url] = ("data:" + mime + ";base64,"
                          + base64.b64encode(path.read_bytes()).decode("ascii"))
        item["img"] = cache[url]
    return out


def render(template: str, payload: dict) -> str:
    return (template
            .replace("__FONTS__", FONT_LINK)
            .replace("__TOKENS__", theme_css())
            .replace("__LOGO__", LOGO_SVG)
            .replace("__DATA__", json.dumps(payload, ensure_ascii=False)))


def main() -> int:
    payload = collect()
    # หน้าเว็บอ้างไฟล์รูปตามปกติ (เบราว์เซอร์แคชได้) หน้า offline ฝัง base64 ให้เป็นไฟล์เดียวจบ
    OUT_WEB.write_text(render(WEB, payload), encoding="utf-8")
    OUT_OFF.write_text(render(OFFLINE, embed_images(payload)), encoding="utf-8")
    # ตัวเลือกเสริม: หน้าเว็บฉบับฝังรูป สำหรับแชร์เป็นไฟล์เดียวที่ไม่มี /assets ให้อ้าง
    if "--embed-web" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--embed-web") + 1])
        dest.write_text(render(WEB, embed_images(payload)), encoding="utf-8")
        print(f"wrote {dest} ({dest.stat().st_size // 1024} KB, ฝังรูปในไฟล์)")

    n_s = sum(1 for i in payload["items"] if i["kind"] == "single")
    print(f"wrote public/index.html ({OUT_WEB.stat().st_size // 1024} KB) + "
          f"public/catalog-offline.html ({OUT_OFF.stat().st_size // 1024} KB)")
    print(f"  {n_s} รายชิ้น + {len(payload['items']) - n_s} ชุด "
          f"— ยืนยันแล้ว {payload['coreCount']} + มีภาพต้นฉบับ {payload['photoCount']}")
    if not any(CONTACT.values()):
        print("NOTE: CONTACT ใน scripts/brand_kit.py ยังว่าง — ปุ่มขอใบเสนอราคาจะใช้ 'คัดลอกรายการ' เป็นปลายทาง")
    return 0


# ===========================================================================
# CATALOG WEB
# ===========================================================================
WEB = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>SmartGift Thailand — สินค้าและชุดของขวัญองค์กร</title>
__FONTS__
<style>
__TOKENS__
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--ground); color: var(--ink); font: 400 16px/1.65 var(--body); -webkit-font-smoothing: antialiased; }
  h1, h2, h3 { font-family: var(--display); margin: 0; text-wrap: balance; }
  button, input { font: inherit; color: inherit; }
  button { cursor: pointer; }
  :focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; border-radius: 3px; }
  .wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

  /* header */
  .top { background: var(--surface); border-bottom: 1px solid var(--line); }
  .top-in { display: flex; align-items: center; justify-content: space-between; gap: 16px 28px; flex-wrap: wrap; padding-block: 18px; }
  .top-left { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
  .palette { display: flex; gap: 6px; align-items: center; }
  .palette-lab { font-size: 12px; color: var(--muted); margin-inline-end: 4px; }
  .sw { width: 40px; height: 30px; padding: 0; border: 1px solid var(--line-strong); border-radius: 6px; display: flex; overflow: hidden; }
  .sw i { flex: 1; }
  .sw[aria-pressed="true"] { border-color: var(--brand); box-shadow: 0 0 0 2px var(--brand-wash); }

  /* search */
  .searchbar { display: flex; align-items: center; gap: 10px; margin-top: 30px; background: var(--surface); border: 1px solid var(--line-strong); border-radius: 10px; padding: 0 16px; box-shadow: var(--shadow); }
  .searchbar svg { flex: none; color: var(--muted); }
  .searchbar input { flex: 1; min-width: 0; border: 0; background: none; padding: 15px 0; outline: none; }
  .searchbar input::placeholder { color: var(--muted); }

  .ftitle { font-size: 14px; font-weight: 600; color: var(--brown); margin: 24px 0 10px; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip { padding: 9px 16px; min-height: 44px; border: 1px solid var(--line-strong); border-radius: 999px; background: var(--surface); color: var(--muted); font-size: 14px; }
  .chip:hover { border-color: var(--brand); color: var(--brand-deep); }
  .chip[aria-pressed="true"] { background: var(--action-bg); border-color: var(--action-bg); color: var(--on-brand); font-weight: 600; }

  .tabs { display: flex; align-items: flex-end; justify-content: space-between; gap: 10px 24px; flex-wrap: wrap; border-bottom: 1px solid var(--line); margin-top: 26px; }
  .tabgroup { display: flex; gap: 26px; }
  .tab { padding: 10px 0 12px; min-height: 46px; background: none; border: 0; border-bottom: 3px solid transparent; color: var(--muted); font-size: 15px; }
  .tab[aria-pressed="true"] { color: var(--brand-deep); border-bottom-color: var(--brand); font-weight: 700; }
  .tab .n { font-family: var(--mono); font-size: 13px; margin-inline-start: 6px; }
  .count { font-size: 13px; color: var(--muted); padding-bottom: 12px; font-variant-numeric: tabular-nums; }

  /* carousel */
  .rail-wrap { position: relative; margin-top: 20px; }
  .rail { display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth; list-style: none; margin: 0; padding: 4px 2px 14px; }
  .rail::-webkit-scrollbar { height: 8px; }
  .rail::-webkit-scrollbar-thumb { background: var(--line-strong); border-radius: 4px; }
  .rail > li { flex: 0 0 268px; scroll-snap-align: start; display: flex; }
  .more-tile { display: flex; flex-direction: column; justify-content: center; gap: 8px; width: 100%; padding: 18px; border: 1px dashed var(--line-strong); border-radius: 12px; background: var(--sunk); color: var(--brand-deep); font-weight: 600; }
  .more-tile span { font-family: var(--body); font-size: 12px; font-weight: 400; color: var(--muted); }
  .more-tile:hover { border-color: var(--brand); }
  .rail-nav { position: absolute; top: calc(50% - 26px); width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--line-strong); background: var(--surface); color: var(--brand-deep); font-size: 20px; line-height: 1; display: grid; place-items: center; box-shadow: var(--shadow-lift); z-index: 2; }
  .rail-nav[disabled] { opacity: .35; cursor: default; }
  .rail-prev { inset-inline-start: -18px; }
  .rail-next { inset-inline-end: -18px; }

  .card { display: flex; flex-direction: column; width: 100%; text-align: start; gap: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 16px; box-shadow: var(--shadow); }
  .card:hover, .card[aria-pressed="true"] { border-color: var(--brand); }
  .card[aria-pressed="true"] { box-shadow: 0 0 0 2px var(--brand-wash), var(--shadow); }
  .plate { background: var(--sunk); border: 1px dashed var(--line-strong); border-radius: 8px; aspect-ratio: 4 / 3; display: grid; place-content: center; text-align: center; gap: 4px; padding: 12px; margin-bottom: 12px; }
  .plate b { font-family: var(--display); font-size: 13px; color: var(--brown); }
  .plate span { font-size: 11px; color: var(--muted); }
  .shot { background: var(--sunk); border: 1px solid var(--line); border-radius: 8px; aspect-ratio: 4 / 3; overflow: hidden; margin-bottom: 12px; display: grid; place-items: center; }
  .shot img { width: 100%; height: 100%; object-fit: contain; display: block; padding: 6px; }
  .badge-proof { background: var(--flag-wash); color: var(--flag-ink); }
  .card-desc { font-size: 12px; color: var(--muted); margin-top: 7px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .detail-shot { background: var(--sunk); border: 1px solid var(--line); border-radius: 10px; aspect-ratio: 1 / 1; overflow: hidden; display: grid; place-items: center; }
  .detail-shot img { width: 100%; height: 100%; object-fit: contain; padding: 10px; }
  .desc { font-size: 14px; line-height: 1.7; color: var(--muted); margin: 0; white-space: pre-line; }
  .card-code { font-family: var(--mono); font-size: 11.5px; color: var(--muted); overflow-wrap: anywhere; }
  .card-name { font-size: 15.5px; font-weight: 600; line-height: 1.45; margin-top: 6px; text-wrap: pretty; }
  .card-cat { font-size: 12.5px; color: var(--muted); margin-top: 5px; }
  .card-price { margin-top: auto; padding-top: 12px; font-family: var(--mono); font-size: 17px; font-variant-numeric: tabular-nums; }
  .card-price small { font-family: var(--body); font-size: 11.5px; color: var(--muted); margin-inline-start: 5px; }
  .card-price.quote { font-family: var(--body); font-size: 14px; font-weight: 600; color: var(--brand-deep); }
  .flag { display: inline-block; font-size: 10.5px; padding: 2px 7px; border-radius: 4px; background: var(--flag-wash); color: var(--flag-ink); margin-inline-start: 6px; }
  .flag-tier { background: var(--gold-wash); color: var(--gold-deep); font-weight: 600; }

  /* detail */
  .detail { margin-top: 8px; background: var(--surface); border: 1px solid var(--brand); border-radius: 12px; box-shadow: var(--shadow-lift); overflow: hidden; }
  .detail-in { display: grid; grid-template-columns: minmax(0, 300px) minmax(0, 1fr); gap: 26px; padding: 24px; }
  .detail-close { position: absolute; inset-block-start: 14px; inset-inline-end: 14px; width: 36px; height: 36px; border: 0; border-radius: 8px; background: var(--sunk); font-size: 17px; }
  .detail-head { position: relative; }
  .detail h3 { font-size: 21px; font-weight: 600; line-height: 1.4; padding-inline-end: 46px; }
  .detail-code { font-family: var(--mono); font-size: 12.5px; color: var(--muted); margin: 8px 0 0; }
  .sub-h { font-size: 13px; font-weight: 700; color: var(--brown); margin: 20px 0 10px; }
  .parts { display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch; list-style: none; margin: 0; padding: 0; }
  .parts li { display: flex; flex-direction: column; gap: 4px; width: 132px; background: var(--sunk); border-radius: 8px; padding: 10px; font-size: 12px; }
  .parts .q { font-family: var(--mono); font-size: 11.5px; color: var(--brand-deep); }
  .parts .pn { line-height: 1.45; }
  .plus { align-self: center; color: var(--muted); font-size: 18px; }
  .specs { display: flex; flex-wrap: wrap; gap: 10px; margin: 0; }
  .specs div { background: var(--sunk); border-radius: 8px; padding: 9px 13px; }
  .specs dt { font-size: 11.5px; color: var(--muted); }
  .specs dd { margin: 2px 0 0; font-family: var(--mono); font-size: 14px; font-variant-numeric: tabular-nums; }
  .note { background: var(--sunk); border-radius: 8px; padding: 12px 14px; font-size: 14px; color: var(--muted); margin: 0; }
  .actions { display: flex; flex-wrap: wrap; gap: 10px; padding: 0 24px 22px; }
  .btn { flex: 1 1 180px; min-height: 48px; padding: 12px 18px; border-radius: 8px; border: 1px solid transparent; font-weight: 600; font-size: 15px; text-align: center; }
  .btn-primary { background: var(--action-bg); color: var(--on-brand); }
  .btn-primary:hover { background: var(--action-bg-hover); }
  .btn-brown { background: var(--brown); color: var(--on-brand); }
  .btn-brown:hover { background: var(--brown-deep); }
  .btn-ghost { background: var(--surface); border-color: var(--brand); color: var(--brand-deep); }
  .btn-ghost:hover { background: var(--brand-wash); }

  /* ladder */
  .ladder { margin-top: 4px; }
  .bars { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: 4px; align-items: end; height: 46px; }
  .bar { background: var(--bar); border-radius: 3px 3px 0 0; min-height: 3px; }
  .bar.lead { background: var(--bar-lead); }
  .qtys { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: 4px; font-family: var(--mono); font-size: 10px; color: var(--muted); text-align: center; margin-top: 5px; font-variant-numeric: tabular-nums; }

  /* compare tray */
  .compare { margin-top: 28px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 18px 20px; }
  .compare h2 { font-size: 15px; font-weight: 700; margin-bottom: 12px; }
  .tray { display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch; }
  .tray-item { display: flex; align-items: center; gap: 10px; background: var(--sunk); border-radius: 8px; padding: 9px 10px 9px 13px; font-size: 13px; max-width: 260px; }
  .tray-item span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .tray-x { border: 0; background: none; color: var(--muted); font-size: 15px; padding: 4px 6px; border-radius: 6px; flex: none; }
  .tray-x:hover { background: var(--brand-wash); color: var(--brand-deep); }
  .tray-cta { min-height: 44px; padding: 10px 18px; border-radius: 8px; border: 1px solid var(--brand); background: var(--surface); color: var(--brand-deep); font-weight: 600; font-size: 14px; margin-inline-start: auto; }
  .tray-cta:hover { background: var(--brand-wash); }

  /* dialogs */
  dialog { padding: 0; border: 0; border-radius: 14px; background: var(--surface); color: var(--ink); width: min(880px, calc(100vw - 28px)); max-height: 88dvh; overflow: auto; box-shadow: 0 20px 60px rgba(40, 24, 14, .34); }
  dialog::backdrop { background: rgba(38, 24, 16, .6); }
  .d-bar { position: sticky; top: 0; display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 14px 22px; background: var(--surface); border-bottom: 1px solid var(--line); }
  .d-bar h2 { font-size: 16px; font-weight: 700; }
  .d-close { min-height: 44px; padding: 8px 15px; border: 0; border-radius: 8px; background: var(--sunk); }
  .d-body { padding: 22px; display: grid; gap: 18px; }
  .tbl-wrap { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
  th, td { padding: 10px 13px; border-bottom: 1px solid var(--line); text-align: start; font-size: 14px; vertical-align: top; }
  thead th { font-size: 12px; font-weight: 700; color: var(--brown); background: var(--sunk); }
  tbody th { font-weight: 500; color: var(--muted); font-size: 13px; white-space: nowrap; }
  td { font-family: var(--mono); }
  td.txt { font-family: var(--body); }
  .qty-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
  .qty-row label { font-size: 14px; color: var(--muted); }
  .qty-row input { width: 130px; padding: 11px 13px; border: 1px solid var(--line-strong); border-radius: 8px; background: var(--surface); font-family: var(--mono); font-variant-numeric: tabular-nums; }
  .quote-sum { background: var(--brand-wash); border-radius: 10px; padding: 16px 18px; display: grid; gap: 6px; }
  .quote-sum b { font-family: var(--mono); font-size: 22px; font-variant-numeric: tabular-nums; }
  .quote-sum span { font-size: 13px; color: var(--muted); }
  .ok { font-size: 13px; color: var(--brand-deep); min-height: 20px; }

  footer { border-top: 1px solid var(--line); margin-top: 44px; padding-block: 24px 36px; color: var(--muted); font-size: 13px; }
  footer p { margin: 0 0 7px; max-width: 78ch; }
  footer a { color: var(--brand-deep); }

  @media (max-width: 860px) { .detail-in { grid-template-columns: 1fr; gap: 18px; } }
  @media (max-width: 640px) {
    .wrap { padding: 0 16px; }
    .rail > li { flex-basis: 78vw; }
    .rail-prev, .rail-next { display: none; }
    .tray-cta { margin-inline-start: 0; width: 100%; }
  }
  @media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; scroll-behavior: auto !important; } }
</style>
</head>
<body>
<header class="top">
  <div class="wrap top-in">
    <div class="top-left">
      <span class="sg-lockup">__LOGO__</span>
      <p class="sg-tagline">The Right Gift. The Right <b>Impact.</b></p>
    </div>
    <div class="palette" role="group" aria-label="ธีมสี">
      <span class="palette-lab">ธีมสี</span>
      <button class="sw" type="button" data-p="a" title="A · Smart Orange" aria-label="ธีม A Smart Orange"><i style="background:#f26522"></i><i style="background:#5c5149"></i><i style="background:#d3ab63"></i></button>
      <button class="sw" type="button" data-p="b" title="B · Warm Festive" aria-label="ธีม B Warm Festive"><i style="background:#a52a32"></i><i style="background:#c9a227"></i><i style="background:#5a3b34"></i></button>
      <button class="sw" type="button" data-p="c" title="C · Modern Teal" aria-label="ธีม C Modern Teal"><i style="background:#12736e"></i><i style="background:#3f5b5c"></i><i style="background:#d0a54e"></i></button>
    </div>
  </div>
</header>

<main class="wrap">
  <h1 class="ftitle" style="font-size:26px;color:var(--ink);margin:30px 0 0;">สินค้าและชุดของขวัญองค์กร</h1>
  <p id="scope" class="note" style="margin-top:12px;max-width:70ch;"></p>

  <div class="searchbar">
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>
    <input id="q" type="search" placeholder="ค้นหาชื่อสินค้า ชุดของขวัญ หรือรหัส" aria-label="ค้นหา">
  </div>

  <h2 class="ftitle">หมวดสินค้า</h2>
  <div class="chips" role="group" aria-label="หมวดสินค้า" id="cats"></div>

  <div class="tabs">
    <div class="tabgroup" role="group" aria-label="ชนิดรายการ" id="kinds"></div>
    <p class="count" id="count"></p>
  </div>

  <div class="rail-wrap">
    <button class="rail-nav rail-prev" type="button" id="prev" aria-label="เลื่อนไปทางซ้าย">‹</button>
    <ul class="rail" id="rail"></ul>
    <button class="rail-nav rail-next" type="button" id="next" aria-label="เลื่อนไปทางขวา">›</button>
  </div>

  <section class="detail" id="detail" hidden aria-live="polite"></section>

  <section class="compare" id="compare" hidden>
    <h2 id="cmp-title"></h2>
    <div class="tray" id="tray"></div>
  </section>
</main>

<footer class="wrap">
  <p>ราคาต่อชิ้น/ต่อชุดผูกกับจำนวนสั่งซื้อขั้นต่ำเสมอ ราคาที่ 10 ชุดไม่ใช่ราคาสำหรับ 1 ชิ้น รายการที่ยังยืนยันราคาไม่ได้แสดง “สอบถามราคา”</p>
  <p>รายการในรอบนี้ยังไม่มีภาพสินค้าที่ตรวจรหัสกับต้นฉบับแล้ว จึงไม่แสดงภาพแทนหรือภาพที่สร้างขึ้น</p>
  <p><a href="./catalog-offline">เปิดแคตตาล็อกแบบออฟไลน์ (flipbook)</a> · <a href="./internal">แดชบอร์ดภายใน</a></p>
  <p id="foot-meta"></p>
</footer>

<dialog id="cmp-dlg" aria-labelledby="cmp-h">
  <div class="d-bar"><h2 id="cmp-h">เปรียบเทียบรายการ</h2><button class="d-close" type="button" data-close>ปิด</button></div>
  <div class="d-body"><div class="tbl-wrap" id="cmp-body"></div></div>
</dialog>

<dialog id="q-dlg" aria-labelledby="q-h">
  <div class="d-bar"><h2 id="q-h">ขอใบเสนอราคา</h2><button class="d-close" type="button" data-close>ปิด</button></div>
  <div class="d-body" id="q-body"></div>
</dialog>

<script>
(function () {
  'use strict';
  var DATA = __DATA__;
  var KINDS = [{ id: 'single', label: 'สินค้ารายชิ้น' }, { id: 'set', label: 'ชุดของขวัญ' }];
  var PAGE_STEP = 24;
  var state = { cat: 'all', kind: 'single', q: '', open: null, compare: [], limit: PAGE_STEP };
  var byCode = {};
  DATA.items.forEach(function (i) { byCode[i.code] = i; });

  var num = function (n) { return Number(n).toLocaleString('th-TH', { maximumFractionDigits: 0 }); };
  var qs = function (id) { return document.getElementById(id); };
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function catName(slug) {
    for (var i = 0; i < DATA.categories.length; i++) if (DATA.categories[i].slug === slug) return DATA.categories[i].name;
    return slug;
  }
  /* ราคาต่อหน่วยที่จำนวน qty — ใช้ขั้นสูงสุดที่ไม่เกิน qty */
  function priceAt(item, qty) {
    var hit = null;
    for (var i = 0; i < item.tiers.length; i++) if (qty >= item.tiers[i].min_qty) hit = item.tiers[i];
    return hit;
  }

  /* ---------- theme ---------- */
  var pal = document.querySelectorAll('.sw');
  function setPalette(p) {
    document.documentElement.setAttribute('data-palette', p);
    try { localStorage.setItem('sg-palette', p); } catch (e) {}
    Array.prototype.forEach.call(pal, function (b) { b.setAttribute('aria-pressed', String(b.dataset.p === p)); });
  }
  Array.prototype.forEach.call(pal, function (b) {
    b.addEventListener('click', function () { setPalette(b.dataset.p); });
  });
  var saved = 'a';
  try { saved = localStorage.getItem('sg-palette') || 'a'; } catch (e) {}
  setPalette(saved);

  /* ---------- header copy ---------- */
  var nS = DATA.items.filter(function (i) { return i.kind === 'single'; }).length;
  qs('scope').textContent = 'รอบนี้แสดง ' + DATA.items.length + ' รายการ — ยืนยันราคาและส่วนประกอบครบแล้ว '
    + DATA.coreCount + ' รายการ และมีภาพต้นฉบับที่ตรวจรหัสแล้วอีก ' + DATA.photoCount
    + ' รายการจากแคตตาล็อกผู้ผลิต (สินค้ารายชิ้น ' + nS + ' · ชุดของขวัญ ' + (DATA.items.length - nS)
    + ') จากทั้งแคตตาล็อก ' + num(DATA.totalAll) + ' รายการ';
  qs('foot-meta').textContent = 'อ้างอิงแคตตาล็อก ' + DATA.catalogVersion + ' · จัดทำรายการ ' + DATA.generatedAt;

  /* ---------- filters ---------- */
  var cats = qs('cats');
  [{ slug: 'all', name: 'ทุกหมวด' }].concat(DATA.categories).forEach(function (c) {
    var b = el('button', 'chip', c.name);
    b.type = 'button'; b.dataset.cat = c.slug;
    b.addEventListener('click', function () { state.cat = c.slug; state.open = null; state.limit = PAGE_STEP; render(); });
    cats.appendChild(b);
  });
  var kinds = qs('kinds');
  KINDS.forEach(function (k) {
    var b = el('button', 'tab');
    b.type = 'button'; b.dataset.kind = k.id;
    b.appendChild(document.createTextNode(k.label));
    b.appendChild(el('span', 'n'));
    b.addEventListener('click', function () { state.kind = k.id; state.open = null; state.limit = PAGE_STEP; render(); });
    kinds.appendChild(b);
  });
  qs('q').addEventListener('input', function (e) {
    state.q = e.target.value.trim().toLowerCase();
    state.limit = PAGE_STEP;
    render();
  });

  function match(i) {
    if (i.kind !== state.kind) return false;
    if (state.cat !== 'all' && i.cat !== state.cat) return false;
    if (!state.q) return true;
    return (i.name + ' ' + i.code + ' ' + (i.nameEn || '') + ' ' + (i.group || '')).toLowerCase().indexOf(state.q) >= 0;
  }

  /* ---------- ช่องรูป: มีภาพต้นฉบับก็แสดงจริง ไม่มีก็ขึ้นป้ายตามตรง ---------- */
  function shot(item, cls) {
    if (!item.img) {
      var plate = el('div', 'plate');
      if (cls === 'detail-shot') plate.style.aspectRatio = '1 / 1';
      plate.appendChild(el('b', null, 'ยังไม่มีภาพสินค้า'));
      plate.appendChild(el('span', null, cls === 'detail-shot'
        ? 'ยังไม่มีภาพที่ตรวจรหัสกับต้นฉบับแล้วสำหรับรายการนี้'
        : 'ขอภาพจริงได้จากทีมขาย'));
      return plate;
    }
    var box = el('div', cls);
    var img = document.createElement('img');
    img.src = item.img;
    img.alt = item.name;
    img.loading = 'lazy';
    img.decoding = 'async';
    // รูปโหลดไม่ขึ้น (เช่นเปิดไฟล์เดี่ยวนอกเซิร์ฟเวอร์) ให้ตกกลับไปป้ายตามตรง ไม่ทิ้งกรอบว่าง
    img.addEventListener('error', function () {
      var fb = el('div', 'plate');
      fb.style.margin = '0';
      fb.appendChild(el('b', null, 'ยังไม่มีภาพสินค้า'));
      box.replaceWith(fb);
    });
    box.appendChild(img);
    return box;
  }

  /* ---------- ladder ---------- */
  function ladder(item) {
    var box = el('div', 'ladder');
    if (item.tiers.length < 2) return box;
    var max = Math.max.apply(null, item.tiers.map(function (t) { return t.unit_price; }));
    var first = item.tiers[0], last = item.tiers[item.tiers.length - 1];
    var bars = el('div', 'bars');
    bars.setAttribute('role', 'img');
    bars.setAttribute('aria-label', 'ราคาต่อหน่วยลดจาก ' + num(first.unit_price) + ' บาทที่ ' + num(first.min_qty)
      + ' ชิ้น เหลือ ' + num(last.unit_price) + ' บาทที่ ' + num(last.min_qty) + ' ชิ้น');
    var qtys = el('div', 'qtys');
    qtys.setAttribute('aria-hidden', 'true');
    item.tiers.forEach(function (t, idx) {
      var b = el('div', 'bar' + (idx === item.tiers.length - 1 ? ' lead' : ''));
      b.style.height = Math.round(t.unit_price / max * 100) + '%';
      bars.appendChild(b);
      qtys.appendChild(el('div', null, t.min_qty >= 1000 ? (t.min_qty / 1000) + 'K' : String(t.min_qty)));
    });
    box.appendChild(bars); box.appendChild(qtys);
    return box;
  }

  /* ---------- cards ---------- */
  function card(item) {
    var li = el('li');
    var b = el('button', 'card');
    b.type = 'button';
    b.setAttribute('aria-pressed', String(state.open === item.code));

    b.appendChild(shot(item, 'shot'));

    var codeLine = el('p', 'card-code');
    codeLine.appendChild(document.createTextNode(item.code));
    if (item.giftTier) codeLine.appendChild(el('span', 'flag flag-tier', item.giftTier));
    if (item.proof) codeLine.appendChild(el('span', 'flag badge-proof', 'ภาพสร้างจากต้นฉบับ'));
    b.appendChild(codeLine);

    b.appendChild(el('h3', 'card-name', item.name));
    b.appendChild(el('p', 'card-cat', item.tier === 'core'
      ? catName(item.cat) + ' · ' + (item.kind === 'single' ? (item.group || 'สินค้ารายชิ้น')
                                     : item.components.length + ' ชิ้นในชุด')
      : 'จากแคตตาล็อกผู้ผลิต · ' + (item.kind === 'single' ? 'สินค้ารายชิ้น' : 'ชุดของขวัญ')));
    if (item.desc) b.appendChild(el('p', 'card-desc', item.desc));

    if (item.tiers.length) {
      var p = el('p', 'card-price', num(item.tiers[0].unit_price) + ' ฿');
      p.appendChild(el('small', null, item.tiers[0].min_qty === 1 ? 'ต่อชิ้น' : 'ที่ ' + num(item.tiers[0].min_qty) + '+'));
      b.appendChild(p);
    } else {
      b.appendChild(el('p', 'card-price quote', 'สอบถามราคา'));
    }

    b.addEventListener('click', function () {
      state.open = state.open === item.code ? null : item.code;
      render();
      if (state.open) qs('detail').scrollIntoView({ block: 'nearest' });
    });
    li.appendChild(b);
    return li;
  }

  /* ---------- detail ---------- */
  function detail(item) {
    var sec = qs('detail');
    sec.textContent = '';
    sec.hidden = false;

    var inner = el('div', 'detail-in');

    var left = el('div');
    left.appendChild(shot(item, 'detail-shot'));
    if (item.proof) left.appendChild(el('p', 'card-cat',
      'ภาพนี้สร้างจากต้นฉบับใน catalog ใช้ดูรูปทรง ไม่ใช่ภาพถ่ายสินค้าจริง'));
    if (item.tiers.length > 1) {
      left.appendChild(el('p', 'sub-h', 'ราคาต่อหน่วยตามจำนวน'));
      left.appendChild(ladder(item));
    }
    inner.appendChild(left);

    var right = el('div', 'detail-head');
    var x = el('button', 'detail-close', '✕');
    x.type = 'button';
    x.setAttribute('aria-label', 'ปิดรายละเอียด');
    x.addEventListener('click', function () { state.open = null; render(); });
    right.appendChild(x);
    right.appendChild(el('p', 'card-cat',
      (item.tier === 'core' ? catName(item.cat) : 'จากแคตตาล็อกผู้ผลิต')
      + (item.giftTierTh ? ' · ' + item.giftTierTh : '')));
    right.appendChild(el('h3', null, item.name));
    if (item.nameEn) right.appendChild(el('p', 'card-cat', item.nameEn));
    right.appendChild(el('p', 'detail-code', 'รหัสสำหรับคุยกับทีมขาย: ' + item.code));

    if (item.tier === 'supplier') {
      right.appendChild(el('p', 'sub-h', 'รายละเอียดตามต้นฉบับ'));
      right.appendChild(item.desc
        ? el('p', 'desc', item.desc.split(' • ').join('\n• '))
        : el('p', 'note', 'ต้นฉบับไม่ได้ระบุรายละเอียดไว้'));
      right.appendChild(el('p', 'note', 'รายการนี้มาจากแคตตาล็อกผู้ผลิต ยังไม่ผ่านการยืนยันเป็นสินค้าหลัก '
        + 'ส่วนประกอบและสเปกต้องให้ทีมขายยืนยันก่อนเสนอราคา'));
    } else if (item.kind === 'set') {
      right.appendChild(el('p', 'sub-h', 'ในชุดประกอบด้วย'));
      if (item.componentsConfirmed && item.components.length) {
        var ul = el('ul', 'parts');
        item.components.forEach(function (c, idx) {
          if (idx) { var pl = el('li', 'plus', '+'); pl.style.background = 'none'; pl.style.width = 'auto'; ul.appendChild(pl); }
          var li = el('li');
          li.appendChild(el('span', 'q', '×' + c.qty + ' · ' + c.product_code));
          li.appendChild(el('span', 'pn', c.name_th || c.product_code));
          ul.appendChild(li);
        });
        right.appendChild(ul);
      } else {
        right.appendChild(el('p', 'note', 'รายละเอียดชุดอยู่ระหว่างยืนยัน'));
      }
      if (item.unboxing) {
        right.appendChild(el('p', 'sub-h', 'ประสบการณ์เปิดกล่อง'));
        right.appendChild(el('p', 'note', item.unboxing));
      }
    } else {
      right.appendChild(el('p', 'sub-h', 'รายละเอียด'));
      var dl = el('dl', 'specs');
      var rows = [];
      if (item.group) rows.push(['กลุ่มสินค้า', item.group]);
      if (item.dims) rows.push(['ขนาด (ซม.)', item.dims.join(' × ')]);
      if (item.weight) rows.push(['น้ำหนักต่อชิ้น', item.weight + ' กก.']);
      rows.forEach(function (r) {
        var d = el('div');
        d.appendChild(el('dt', null, r[0]));
        d.appendChild(el('dd', null, r[1]));
        dl.appendChild(d);
      });
      right.appendChild(rows.length ? dl : el('p', 'note', 'ยังไม่มีสเปกที่ยืนยันเพิ่มเติม'));
    }
    inner.appendChild(right);
    sec.appendChild(inner);

    var acts = el('div', 'actions');
    var bDetail = el('button', 'btn btn-primary', item.tiers.length ? 'ดูตารางราคาทุกขั้น' : 'ดูรายละเอียดทั้งหมด');
    bDetail.type = 'button';
    bDetail.addEventListener('click', function () { openCompare([item.code]); });
    var inTray = state.compare.indexOf(item.code) >= 0;
    var bCmp = el('button', 'btn btn-brown', inTray ? 'อยู่ในรายการเปรียบเทียบแล้ว' : 'เปรียบเทียบ');
    bCmp.type = 'button';
    bCmp.disabled = inTray;
    if (inTray) bCmp.style.opacity = '.6';
    bCmp.addEventListener('click', function () {
      if (state.compare.length >= 4) { alert('เปรียบเทียบได้สูงสุด 4 รายการ'); return; }
      state.compare.push(item.code); render();
    });
    var bQ = el('button', 'btn btn-ghost', 'ขอใบเสนอราคา');
    bQ.type = 'button';
    bQ.addEventListener('click', function () { openQuote([item.code]); });
    acts.appendChild(bDetail); acts.appendChild(bCmp); acts.appendChild(bQ);
    sec.appendChild(acts);
  }

  /* ---------- compare ---------- */
  function renderTray() {
    var box = qs('compare'), tray = qs('tray');
    if (!state.compare.length) { box.hidden = true; return; }
    box.hidden = false;
    qs('cmp-title').textContent = 'เปรียบเทียบ (' + state.compare.length + ')';
    tray.textContent = '';
    state.compare.forEach(function (code) {
      var item = byCode[code];
      var chip = el('div', 'tray-item');
      var x = el('button', 'tray-x', '✕');
      x.type = 'button';
      x.setAttribute('aria-label', 'เอา ' + item.name + ' ออกจากการเปรียบเทียบ');
      x.addEventListener('click', function () {
        state.compare = state.compare.filter(function (c) { return c !== code; });
        render();
      });
      chip.appendChild(x);
      chip.appendChild(el('span', null, item.name));
      tray.appendChild(chip);
    });
    var cta = el('button', 'tray-cta', 'ดูรายละเอียดการเปรียบเทียบ');
    cta.type = 'button';
    cta.addEventListener('click', function () { openCompare(state.compare); });
    tray.appendChild(cta);
  }

  var QTY_LABELS = [1, 10, 20, 50, 100, 300, 500, 1000];
  function openCompare(codes) {
    var items = codes.map(function (c) { return byCode[c]; });
    var body = qs('cmp-body');
    body.textContent = '';
    var t = el('table');
    var thead = el('thead'), htr = el('tr');
    htr.appendChild(el('th', null, ''));
    items.forEach(function (i) { htr.appendChild(el('th', null, i.name)); });
    thead.appendChild(htr); t.appendChild(thead);
    var tb = el('tbody');
    function row(label, fn, cls) {
      var tr = el('tr');
      tr.appendChild(el('th', null, label));
      items.forEach(function (i) { tr.appendChild(el('td', cls || null, fn(i))); });
      tb.appendChild(tr);
    }
    row('รหัส', function (i) { return i.code; });
    row('หมวด', function (i) { return catName(i.cat); }, 'txt');
    row('ประเภท', function (i) { return i.kind === 'single' ? 'สินค้ารายชิ้น' : 'ชุดของขวัญ'; }, 'txt');
    row('ชั้นข้อมูล', function (i) {
      return i.tier === 'core' ? 'ยืนยันแล้ว' : 'แคตตาล็อกผู้ผลิต';
    }, 'txt');
    row('กลุ่ม / ในชุด', function (i) {
      if (i.tier === 'supplier') return i.desc || '—';
      return i.kind === 'single' ? (i.group || '—')
        : i.components.map(function (c) { return c.name_th || c.product_code; }).join(' + ');
    }, 'txt');
    row('ขนาด (ซม.)', function (i) { return i.dims ? i.dims.join(' × ') : '—'; });
    row('น้ำหนัก (กก.)', function (i) { return i.weight != null ? String(i.weight) : '—'; });
    QTY_LABELS.forEach(function (q) {
      var any = items.some(function (i) { return priceAt(i, q); });
      if (!any) return;
      row('ราคาที่ ' + num(q) + ' ชิ้น', function (i) {
        var hit = priceAt(i, q);
        return hit ? num(hit.unit_price) + ' ฿' : 'สอบถามราคา';
      });
    });
    t.appendChild(tb);
    var wrap = el('div', 'tbl-wrap');
    wrap.appendChild(t);
    body.appendChild(wrap);
    var n = el('p', 'note', 'ช่องที่ขึ้น “สอบถามราคา” คือขั้นจำนวนที่ยังไม่มีราคายืนยันสำหรับรายการนั้น ไม่ใช่ราคา 0 บาท');
    body.appendChild(n);
    qs('cmp-dlg').showModal();
  }

  /* ---------- quote ---------- */
  function openQuote(codes) {
    var items = codes.map(function (c) { return byCode[c]; });
    var body = qs('q-body');
    body.textContent = '';

    var qtyRow = el('div', 'qty-row');
    var lab = el('label', null, 'จำนวนที่ต้องการ (ชิ้น/ชุด)');
    lab.htmlFor = 'q-qty';
    var input = document.createElement('input');
    input.id = 'q-qty'; input.type = 'number'; input.min = '1'; input.step = '1'; input.value = '100';
    qtyRow.appendChild(lab); qtyRow.appendChild(input);
    body.appendChild(qtyRow);

    var sum = el('div', 'quote-sum');
    body.appendChild(sum);

    var listWrap = el('div', 'tbl-wrap');
    body.appendChild(listWrap);

    var ok = el('p', 'ok', '');
    var acts = el('div', 'actions');
    acts.style.padding = '0';

    function summary() {
      var qty = Math.max(1, parseInt(input.value, 10) || 1);
      sum.textContent = ''; listWrap.textContent = '';
      var total = 0, allPriced = true;
      var t = el('table'), thead = el('thead'), htr = el('tr');
      ['รายการ', 'รหัส', 'ราคาต่อหน่วย', 'รวม'].forEach(function (h) { htr.appendChild(el('th', null, h)); });
      thead.appendChild(htr); t.appendChild(thead);
      var tb = el('tbody');
      items.forEach(function (i) {
        var hit = priceAt(i, qty);
        var tr = el('tr');
        tr.appendChild(el('td', 'txt', i.name));
        tr.appendChild(el('td', null, i.code));
        tr.appendChild(el('td', null, hit ? num(hit.unit_price) + ' ฿ (ขั้น ' + num(hit.min_qty) + '+)' : 'สอบถามราคา'));
        tr.appendChild(el('td', null, hit ? num(hit.unit_price * qty) + ' ฿' : '—'));
        if (hit) total += hit.unit_price * qty; else allPriced = false;
        tb.appendChild(tr);
      });
      t.appendChild(tb); listWrap.appendChild(t);

      if (allPriced) {
        sum.appendChild(el('b', null, num(total) + ' ฿'));
        sum.appendChild(el('span', null, 'ประมาณการรวมที่ ' + num(qty) + ' ชิ้น/ชุด ตามขั้นราคาที่ยืนยันแล้ว ยังไม่รวมค่าสกรีนโลโก้ บรรจุภัณฑ์พิเศษ และค่าจัดส่ง'));
      } else {
        sum.appendChild(el('b', null, 'สอบถามราคา'));
        sum.appendChild(el('span', null, 'มีบางรายการที่ยังไม่มีราคาผูกกับขั้นจำนวน ทีมขายจะยืนยันกลับ'));
      }
      return { qty: qty, total: total, allPriced: allPriced };
    }

    function text() {
      var s = summary();
      var lines = ['ขอใบเสนอราคา SmartGift', 'จำนวน: ' + num(s.qty) + ' ชิ้น/ชุด', ''];
      items.forEach(function (i) {
        var hit = priceAt(i, s.qty);
        lines.push('- ' + i.code + ' ' + i.name + ' — ' + (hit ? num(hit.unit_price) + ' ฿/หน่วย' : 'สอบถามราคา'));
      });
      if (s.allPriced) lines.push('', 'ประมาณการรวม: ' + num(s.total) + ' ฿');
      lines.push('', 'อ้างอิงแคตตาล็อก ' + DATA.catalogVersion);
      return lines.join('\n');
    }

    var copy = el('button', 'btn btn-primary', 'คัดลอกรายการเพื่อส่งให้ทีมขาย');
    copy.type = 'button';
    copy.addEventListener('click', function () {
      var body = text();
      if (navigator.clipboard) {
        navigator.clipboard.writeText(body).then(function () { ok.textContent = 'คัดลอกแล้ว วางในอีเมลหรือแชตส่งทีมขายได้เลย'; },
          function () { ok.textContent = 'คัดลอกไม่สำเร็จ กดค้างที่ตารางด้านบนเพื่อเลือกข้อความแทน'; });
      } else { ok.textContent = 'เบราว์เซอร์นี้คัดลอกอัตโนมัติไม่ได้ กดค้างที่ตารางเพื่อเลือกข้อความ'; }
    });
    acts.appendChild(copy);

    if (DATA.contact.email) {
      var mail = document.createElement('a');
      mail.className = 'btn btn-ghost';
      mail.textContent = 'ส่งอีเมลหาทีมขาย';
      mail.addEventListener('click', function () {
        mail.href = 'mailto:' + DATA.contact.email + '?subject=' + encodeURIComponent('ขอใบเสนอราคา SmartGift')
          + '&body=' + encodeURIComponent(text());
      });
      mail.href = '#';
      acts.appendChild(mail);
    }
    if (DATA.contact.line) {
      var ln = document.createElement('a');
      ln.className = 'btn btn-ghost';
      ln.href = DATA.contact.line;
      ln.target = '_blank'; ln.rel = 'noopener';
      ln.textContent = 'ทักทีมขายทาง LINE';
      acts.appendChild(ln);
    }
    body.appendChild(acts);
    body.appendChild(ok);
    if (!DATA.contact.email && !DATA.contact.line) {
      body.appendChild(el('p', 'note', 'ยังไม่ได้ตั้งค่าอีเมล/LINE ของทีมขาย ปุ่มคัดลอกรายการใช้งานได้ทันที '
        + 'เมื่อใส่ช่องทางติดต่อใน scripts/brand_kit.py แล้ว ปุ่มส่งตรงจะขึ้นเพิ่ม'));
    }

    input.addEventListener('input', summary);
    summary();
    qs('q-dlg').showModal();
  }

  /* ---------- render ---------- */
  var rail = qs('rail');
  function render() {
    Array.prototype.forEach.call(cats.children, function (b) { b.setAttribute('aria-pressed', String(b.dataset.cat === state.cat)); });
    Array.prototype.forEach.call(kinds.children, function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.kind === state.kind));
      b.querySelector('.n').textContent = DATA.items.filter(function (i) {
        var k = state.kind; state.kind = b.dataset.kind;
        var m = match(i); state.kind = k; return m;
      }).length;
    });

    var visible = DATA.items.filter(match);
    qs('count').textContent = visible.length > state.limit
      ? 'แสดง ' + state.limit + ' จาก ' + visible.length + ' รายการ'
      : visible.length + ' รายการ';
    rail.textContent = '';
    if (!visible.length) {
      var li = el('li');
      li.style.flex = '1';
      li.appendChild(el('p', 'note', 'ไม่พบรายการที่ตรงกับเงื่อนไขนี้ ลองล้างคำค้นหรือเลือกหมวดอื่น'));
      rail.appendChild(li);
    } else {
      var shown = visible.slice(0, state.limit);
      shown.forEach(function (i) { rail.appendChild(card(i)); });
      if (visible.length > shown.length) {
        var li = el('li');
        var more = el('button', 'more-tile');
        more.type = 'button';
        var left = visible.length - shown.length;
        more.appendChild(document.createTextNode('แสดงเพิ่มอีก ' + Math.min(PAGE_STEP, left) + ' รายการ'));
        more.appendChild(el('span', null, 'เหลืออีก ' + left + ' รายการในเงื่อนไขนี้'));
        more.addEventListener('click', function () {
          var at = rail.querySelectorAll('.card').length;
          state.limit += PAGE_STEP;
          render();
          var next = rail.querySelectorAll('.card')[at];
          if (next) next.scrollIntoView({ block: 'nearest', inline: 'center' });
        });
        li.appendChild(more);
        rail.appendChild(li);
      }
    }

    if (state.open && visible.some(function (i) { return i.code === state.open; })) detail(byCode[state.open]);
    else { state.open = null; qs('detail').hidden = true; qs('detail').textContent = ''; }

    renderTray();
    updateNav();
  }

  /* ---------- rail nav ---------- */
  function updateNav() {
    var max = rail.scrollWidth - rail.clientWidth - 2;
    qs('prev').disabled = rail.scrollLeft <= 2;
    qs('next').disabled = rail.scrollLeft >= max;
  }
  qs('prev').addEventListener('click', function () { rail.scrollBy({ left: -rail.clientWidth * 0.8 }); });
  qs('next').addEventListener('click', function () { rail.scrollBy({ left: rail.clientWidth * 0.8 }); });
  rail.addEventListener('scroll', updateNav);
  window.addEventListener('resize', updateNav);

  Array.prototype.forEach.call(document.querySelectorAll('[data-close]'), function (b) {
    b.addEventListener('click', function () { b.closest('dialog').close(); });
  });
  Array.prototype.forEach.call(document.querySelectorAll('dialog'), function (d) {
    d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
  });

  render();
})();
</script>
</body>
</html>
"""

# ===========================================================================
# CATALOG OFFLINE — flipbook
# ===========================================================================
OFFLINE = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>แคตตาล็อกออฟไลน์ SmartGift Thailand</title>
__FONTS__
<style>
__TOKENS__
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--stage); color: var(--neutral-100); font: 400 16px/1.6 var(--body); -webkit-font-smoothing: antialiased; }
  h1, h2, h3 { font-family: var(--display); margin: 0; text-wrap: balance; }
  button { font: inherit; color: inherit; cursor: pointer; }
  :focus-visible { outline: 3px solid var(--gold); outline-offset: 3px; border-radius: 3px; }

  .app { max-width: 1220px; margin: 0 auto; padding: 18px 20px 28px; display: grid; gap: 16px; }
  .bar { display: flex; align-items: center; justify-content: space-between; gap: 14px 20px; flex-wrap: wrap; }
  .bar-title { font-family: var(--display); font-weight: 700; font-size: 19px; letter-spacing: .06em; color: var(--brand); }
  .bar .sg-lockup { background: var(--surface); border-radius: 10px; padding: 10px 16px; }

  .tools { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .tool { display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 9px 15px; border-radius: 9px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.07); color: #f4e9e1; font-size: 14px; }
  .tool:hover { background: rgba(255,255,255,.14); }
  .tool[aria-pressed="true"] { background: var(--action-bg); border-color: var(--action-bg); color: var(--on-brand); }
  .switch { display: inline-flex; align-items: center; gap: 10px; min-height: 44px; padding: 7px 14px; border-radius: 9px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.07); color: #f4e9e1; font-size: 14px; }
  .switch i { width: 40px; height: 22px; border-radius: 999px; background: rgba(255,255,255,.22); position: relative; transition: background .18s; flex: none; }
  .switch i::after { content: ""; position: absolute; top: 3px; inset-inline-start: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform .18s; }
  .switch[aria-pressed="true"] i { background: var(--brand); }
  .switch[aria-pressed="true"] i::after { transform: translateX(18px); }
  .offline-note { font-size: 12px; color: rgba(244,233,225,.72); max-width: 15ch; line-height: 1.35; }

  .stage { display: grid; grid-template-columns: 120px minmax(0, 1fr); gap: 16px; align-items: start; }
  .rail { display: grid; gap: 10px; max-height: 74vh; overflow-y: auto; padding: 2px; }
  .thumb { padding: 0; border: 2px solid transparent; border-radius: 8px; background: var(--surface); overflow: hidden; text-align: start; }
  .thumb[aria-current="true"] { border-color: var(--brand); }
  .thumb-in { padding: 9px 10px; display: grid; gap: 3px; aspect-ratio: 3 / 4; align-content: start; }
  .thumb-n { font-family: var(--mono); font-size: 10px; color: var(--muted); }
  .thumb-t { font-family: var(--display); font-size: 11px; font-weight: 600; line-height: 1.35; color: var(--ink); }

  .sheet { background: var(--surface); color: var(--ink); border-radius: 4px 14px 14px 4px; box-shadow: 0 22px 60px rgba(0,0,0,.42); min-height: 70vh; padding: 40px clamp(24px, 4vw, 56px); position: relative; overflow: hidden; }
  .sheet::after { content: ""; position: absolute; inset-block-end: 0; inset-inline-end: 0; border-width: 0 0 34px 34px; border-style: solid; border-color: transparent transparent var(--sunk) transparent; }
  .page { display: grid; gap: 22px; }
  .page-eyebrow { font-family: var(--display); font-size: 12px; font-weight: 600; letter-spacing: .22em; color: var(--gold-deep); }
  .page h2 { font-size: clamp(24px, 3vw, 34px); font-weight: 600; line-height: 1.3; color: var(--ink); }
  .page p { color: var(--muted); margin: 0; max-width: 66ch; }
  .cover { display: grid; gap: 20px; justify-items: start; align-content: center; min-height: 58vh; }
  .cover .sg-lockup { transform: scale(1.5); transform-origin: left center; margin-bottom: 18px; }
  .cover-rule { width: 96px; height: 4px; background: var(--grad-orange); border-radius: 2px; }

  .toc { display: grid; gap: 2px; margin: 0; padding: 0; list-style: none; max-width: 62ch; }
  .toc button { display: flex; width: 100%; gap: 14px; align-items: baseline; padding: 11px 4px; background: none; border: 0; border-bottom: 1px solid var(--line); text-align: start; }
  .toc button:hover { color: var(--brand-deep); }
  .toc .tn { font-family: var(--mono); font-size: 13px; color: var(--gold-deep); width: 2ch; flex: none; }
  .toc .tt { flex: 1; font-size: 15px; }
  .toc .tk { font-size: 12px; color: var(--muted); }

  .items { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; margin: 0; padding: 0; list-style: none; }
  .item { border: 1px solid var(--line); border-radius: 10px; padding: 15px; display: grid; gap: 6px; align-content: start; background: var(--surface); }
  .item figure { margin: 0 0 4px; background: var(--sunk); border-radius: 7px; aspect-ratio: 4 / 3; overflow: hidden; display: grid; place-items: center; }
  .item figure img { width: 100%; height: 100%; object-fit: contain; padding: 5px; display: block; }
  .item .noshot { font-size: 11px; color: var(--muted); text-align: center; padding: 8px; }
  .item .ic { font-family: var(--mono); font-size: 11.5px; color: var(--muted); overflow-wrap: anywhere; }
  .item .inm { font-family: var(--display); font-size: 15px; font-weight: 600; line-height: 1.45; color: var(--ink); }
  .item .imeta { font-size: 12.5px; color: var(--muted); }
  .item .ip { font-family: var(--mono); font-size: 15px; margin-top: 4px; font-variant-numeric: tabular-nums; color: var(--ink); }
  .item .ip small { font-family: var(--body); font-size: 11px; color: var(--muted); margin-inline-start: 4px; }
  .noimg { font-size: 10.5px; padding: 2px 7px; border-radius: 4px; background: var(--flag-wash); color: var(--flag-ink); justify-self: start; }
  .parts { margin: 6px 0 0; padding-inline-start: 18px; font-size: 12.5px; color: var(--muted); display: grid; gap: 3px; }

  .tbl-wrap { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
  th, td { padding: 9px 12px; border-bottom: 1px solid var(--line); text-align: end; font-family: var(--mono); font-size: 13.5px; white-space: nowrap; }
  th:first-child, td:first-child { text-align: start; font-family: var(--body); white-space: normal; min-width: 200px; }
  thead th { font-family: var(--body); font-size: 11.5px; font-weight: 700; color: var(--brown); background: var(--sunk); }

  .find { display: none; gap: 10px; align-items: center; background: var(--sunk); border-radius: 9px; padding: 10px 14px; }
  .find.on { display: flex; }
  .find input { flex: 1; min-width: 0; border: 1px solid var(--line-strong); border-radius: 7px; padding: 10px 12px; background: var(--surface); color: var(--ink); font: inherit; }
  .hits { display: grid; gap: 6px; margin: 0; padding: 0; list-style: none; }
  .hits button { width: 100%; text-align: start; padding: 10px 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); font-size: 14px; }
  .hits button:hover { border-color: var(--brand); }
  .hits .hn { font-family: var(--mono); font-size: 11.5px; color: var(--muted); }

  .pager { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .pgbtn { display: inline-flex; align-items: center; gap: 9px; min-height: 48px; padding: 12px 22px; border-radius: 10px; border: 0; background: var(--action-bg); color: var(--on-brand); font-weight: 600; }
  .pgbtn:hover { background: var(--action-bg-hover); }
  .pgbtn[disabled] { background: rgba(255,255,255,.12); color: rgba(244,233,225,.5); cursor: default; }
  .pgnum { font-family: var(--mono); font-size: 15px; color: #f4e9e1; background: rgba(255,255,255,.09); border-radius: 8px; padding: 11px 20px; font-variant-numeric: tabular-nums; }

  :fullscreen .app { max-width: none; height: 100%; }
  @media (max-width: 780px) {
    .stage { grid-template-columns: 1fr; }
    .rail { grid-auto-flow: column; grid-auto-columns: 92px; overflow-x: auto; overflow-y: hidden; max-height: none; }
    .offline-note { max-width: none; }
    .cover .sg-lockup { transform: scale(1.15); }
  }
  @media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; } }
</style>
</head>
<body>
<div class="app">
  <div class="bar">
    <span class="bar-title">CATALOG OFFLINE</span>
    <span class="sg-lockup">__LOGO__</span>
  </div>

  <div class="bar">
    <div class="tools">
      <button class="tool" type="button" id="t-toc" aria-pressed="false">☰ สารบัญ</button>
      <button class="tool" type="button" id="t-find" aria-pressed="false">🔍 ค้นหา</button>
      <button class="tool" type="button" id="t-full">⛶ เต็มจอ</button>
      <button class="tool" type="button" id="t-share">↗ แชร์ไฟล์</button>
    </div>
    <div class="tools">
      <button class="switch" type="button" id="t-auto" aria-pressed="false">Auto Flip <i aria-hidden="true"></i></button>
      <p class="offline-note">เปิดได้โดยไม่ต้องใช้อินเทอร์เน็ต</p>
    </div>
  </div>

  <div class="find" id="find">
    <input id="find-q" type="search" placeholder="ค้นหาชื่อสินค้าหรือรหัส แล้วกดผลลัพธ์เพื่อข้ามไปหน้านั้น" aria-label="ค้นหาในแคตตาล็อก">
  </div>
  <ul class="hits" id="hits"></ul>

  <div class="stage">
    <div class="rail" id="rail" role="tablist" aria-label="หน้าในแคตตาล็อก"></div>
    <div class="sheet"><div class="page" id="page" aria-live="polite"></div></div>
  </div>

  <div class="pager">
    <button class="pgbtn" type="button" id="prev">‹ ก่อนหน้า</button>
    <span class="pgnum" id="pgnum"></span>
    <button class="pgbtn" type="button" id="next">ถัดไป ›</button>
  </div>
</div>

<script>
(function () {
  'use strict';
  var DATA = __DATA__;
  var num = function (n) { return Number(n).toLocaleString('th-TH', { maximumFractionDigits: 0 }); };
  var qs = function (id) { return document.getElementById(id); };
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function catName(slug) {
    for (var i = 0; i < DATA.categories.length; i++) if (DATA.categories[i].slug === slug) return DATA.categories[i].name;
    return slug;
  }
  var singles = DATA.items.filter(function (i) { return i.kind === 'single'; });
  var sets = DATA.items.filter(function (i) { return i.kind === 'set'; });

  /* ---------- โครงหน้า: จำนวนหน้าคิดจากรายการจริง ไม่ได้ตรึงไว้ ---------- */
  var core = DATA.items.filter(function (i) { return i.tier === 'core'; });
  var shots = DATA.items.filter(function (i) { return i.tier === 'supplier'; });
  var PER_PAGE = 6;

  function chunk(list, n) {
    var out = [];
    for (var i = 0; i < list.length; i += n) out.push(list.slice(i, i + n));
    return out;
  }

  var PAGES = [{ t: 'ปก', k: 'ปก', build: coverPage }, { t: 'สารบัญ', k: 'นำทาง', build: tocPage }];
  DATA.categories.forEach(function (c) {
    var list = singles.filter(function (i) { return i.cat === c.slug && i.tier === 'core'; });
    if (!list.length) return;
    PAGES.push({
      t: 'สินค้ารายชิ้น · ' + c.name, k: 'สินค้ารายชิ้น',
      build: function (host) { itemsPage(host, 'สินค้ารายชิ้น', c.name, list); }
    });
  });
  var corePriced = sets.filter(function (x) { return x.tier === 'core' && x.tiers.length; });
  var coreQuote = sets.filter(function (x) { return x.tier === 'core' && !x.tiers.length; });
  if (corePriced.length) PAGES.push({ t: 'ชุดของขวัญ · ราคายืนยันแล้ว', k: 'ชุดของขวัญ',
    build: function (h) { setsPage(h, 'ชุดของขวัญที่ยืนยันราคาแล้ว', corePriced); } });
  if (coreQuote.length) PAGES.push({ t: 'ชุดของขวัญ · ตามฤดูกาล', k: 'ชุดของขวัญ',
    build: function (h) { setsPage(h, 'ชุดตามฤดูกาล — สอบถามราคา', coreQuote); } });

  // รายการจากแคตตาล็อกผู้ผลิตที่มีภาพต้นฉบับ — เรียงรายการที่มีราคายืนยันไว้ก่อน
  chunk(shots, PER_PAGE).forEach(function (group, idx, all) {
    PAGES.push({
      t: 'มีภาพต้นฉบับ ' + (idx + 1) + '/' + all.length, k: 'แคตตาล็อกผู้ผลิต',
      build: function (h) {
        head(h, 'แคตตาล็อกผู้ผลิต', 'รายการที่มีภาพต้นฉบับตรวจรหัสแล้ว',
          'ยังไม่ผ่านการยืนยันเป็นสินค้าหลัก ส่วนประกอบและสเปกให้ทีมขายยืนยันก่อนเสนอราคา');
        var ul = el('ul', 'items');
        group.forEach(function (i) { ul.appendChild(itemCard(i)); });
        h.appendChild(ul);
      }
    });
  });

  PAGES.push({ t: 'ตารางราคาสินค้ารายชิ้น', k: 'ราคา',
    build: function (h) { priceTable(h, 'สินค้ารายชิ้น', singles.filter(function (i) { return i.tier === 'core'; })); } });
  PAGES.push({ t: 'ตารางราคาชุดของขวัญ', k: 'ราคา',
    build: function (h) { priceTable(h, 'ชุดของขวัญ', sets.filter(function (i) { return i.tier === 'core'; })); } });
  var shotsPriced = shots.filter(function (i) { return i.tiers.length; });
  if (shotsPriced.length) PAGES.push({ t: 'ตารางราคา · แคตตาล็อกผู้ผลิต', k: 'ราคา',
    build: function (h) { priceTable(h, 'รายการจากแคตตาล็อกผู้ผลิตที่มีราคา', shotsPriced); } });
  PAGES.push({ t: 'เงื่อนไขราคาและภาพสินค้า', k: 'เงื่อนไข', build: termsPage });
  PAGES.push({ t: 'ติดต่อทีมขาย', k: 'ติดต่อ', build: contactPage });

  var page = 0;

  function head(host, eyebrow, title, lead) {
    host.appendChild(el('p', 'page-eyebrow', eyebrow));
    host.appendChild(el('h2', null, title));
    if (lead) host.appendChild(el('p', null, lead));
  }

  function coverPage(host) {
    var c = el('div', 'cover');
    var lock = el('span', 'sg-lockup');
    lock.innerHTML = document.querySelector('.bar .sg-lockup').innerHTML;
    c.appendChild(lock);
    c.appendChild(el('div', 'cover-rule'));
    c.appendChild(el('h2', null, 'แคตตาล็อกสินค้าและชุดของขวัญองค์กร'));
    c.appendChild(el('p', null, 'ยืนยันราคาและส่วนประกอบครบแล้ว ' + DATA.coreCount
      + ' รายการ และมีภาพต้นฉบับที่ตรวจรหัสแล้วอีก ' + DATA.photoCount
      + ' รายการ · รูปทั้งหมดฝังอยู่ในไฟล์นี้ เปิดอ่านได้โดยไม่ต้องต่ออินเทอร์เน็ต'));
    c.appendChild(el('p', 'page-eyebrow', 'อ้างอิงแคตตาล็อก ' + DATA.catalogVersion));
    host.appendChild(c);
  }

  function tocPage(host) {
    head(host, 'สารบัญ', 'ในเล่มนี้มีอะไรบ้าง');
    var ul = el('ul', 'toc');
    PAGES.forEach(function (p, idx) {
      if (!idx) return;
      var li = el('li');
      var b = el('button');
      b.type = 'button';
      b.appendChild(el('span', 'tn', String(idx + 1)));
      b.appendChild(el('span', 'tt', p.t));
      b.appendChild(el('span', 'tk', p.k));
      b.addEventListener('click', function () { go(idx); });
      li.appendChild(b);
      ul.appendChild(li);
    });
    host.appendChild(ul);
  }

  function itemCard(i) {
    var li = el('li', 'item');
    var fig = el('figure');
    if (i.img) {
      var img = document.createElement('img');
      img.src = i.img;
      img.alt = i.name;
      img.loading = 'lazy';
      fig.appendChild(img);
    } else {
      fig.appendChild(el('div', 'noshot', 'ยังไม่มีภาพสินค้า'));
    }
    li.appendChild(fig);
    li.appendChild(el('span', 'ic', i.code));
    li.appendChild(el('span', 'inm', i.name));
    li.appendChild(el('span', 'imeta', i.tier === 'supplier'
      ? 'จากแคตตาล็อกผู้ผลิต'
      : (i.kind === 'single'
        ? [i.group, i.dims ? i.dims.join('×') + ' ซม.' : null, i.weight ? i.weight + ' กก.' : null].filter(Boolean).join(' · ')
        : catName(i.cat) + ' · ' + i.components.length + ' ชิ้นในชุด')));
    if (i.kind === 'set' && i.componentsConfirmed) {
      var ul = el('ul', 'parts');
      i.components.forEach(function (c) { ul.appendChild(el('li', null, (c.name_th || c.product_code) + ' ×' + c.qty)); });
      li.appendChild(ul);
    }
    if (i.tiers.length) {
      var p = el('span', 'ip', num(i.tiers[0].unit_price) + ' ฿');
      p.appendChild(el('small', null, i.tiers[0].min_qty === 1 ? 'ต่อชิ้น' : 'ที่ ' + num(i.tiers[0].min_qty) + '+'));
      li.appendChild(p);
    } else {
      li.appendChild(el('span', 'ip', 'สอบถามราคา'));
    }
    if (i.proof) li.appendChild(el('span', 'noimg', 'ภาพสร้างจากต้นฉบับ'));
    return li;
  }

  function itemsPage(host, eyebrow, title, list) {
    head(host, eyebrow, title, list.length + ' รายการในหมวดนี้');
    var ul = el('ul', 'items');
    list.forEach(function (i) { ul.appendChild(itemCard(i)); });
    host.appendChild(list.length ? ul : el('p', null, 'ยังไม่มีรายการที่ยืนยันครบในหมวดนี้'));
  }

  function setsPage(host, title, list) {
    head(host, 'ชุดของขวัญ', title, list.length + ' ชุด');
    var ul = el('ul', 'items');
    list.forEach(function (i) { ul.appendChild(itemCard(i)); });
    host.appendChild(list.length ? ul : el('p', null, 'ยังไม่มีชุดในกลุ่มนี้'));
  }

  var QTY = [1, 10, 20, 50, 100, 300, 500, 1000];
  function priceAt(item, q) {
    var hit = null;
    for (var i = 0; i < item.tiers.length; i++) if (q >= item.tiers[i].min_qty) hit = item.tiers[i];
    return hit;
  }
  function priceTable(host, title, list) {
    head(host, 'ราคา', 'ตารางราคา — ' + title, 'ราคาต่อหน่วยเป็นบาท ผูกกับจำนวนสั่งซื้อขั้นต่ำในหัวคอลัมน์');
    var cols = QTY.filter(function (q) { return list.some(function (i) { return priceAt(i, q); }); });
    var t = el('table'), thead = el('thead'), htr = el('tr');
    htr.appendChild(el('th', null, 'รายการ'));
    cols.forEach(function (q) { htr.appendChild(el('th', null, num(q) + '+')); });
    thead.appendChild(htr); t.appendChild(thead);
    var tb = el('tbody');
    list.forEach(function (i) {
      var tr = el('tr');
      tr.appendChild(el('td', null, i.name + ' (' + i.code + ')'));
      cols.forEach(function (q) {
        var hit = priceAt(i, q);
        tr.appendChild(el('td', null, hit ? num(hit.unit_price) : '—'));
      });
      tb.appendChild(tr);
    });
    t.appendChild(tb);
    var w = el('div', 'tbl-wrap');
    w.appendChild(t);
    host.appendChild(w);
    host.appendChild(el('p', null, '“—” คือขั้นจำนวนที่ยังไม่มีราคายืนยันสำหรับรายการนั้น ไม่ใช่ราคา 0 บาท'));
  }

  function termsPage(host) {
    head(host, 'เงื่อนไข', 'ราคาและภาพสินค้าในเล่มนี้');
    var ul = el('ul');
    ul.style.display = 'grid'; ul.style.gap = '12px'; ul.style.paddingInlineStart = '20px'; ul.style.color = 'var(--muted)';
    [
      'ราคาทุกช่องผูกกับจำนวนสั่งซื้อขั้นต่ำที่ระบุกำกับเสมอ ราคาที่ 10 ชุดไม่ใช่ราคาสำหรับ 1 ชิ้น',
      'รายการที่ขึ้น “สอบถามราคา” คือยังไม่มีราคาที่ผูกกับขั้นจำนวน ไม่ใช่สินค้าราคา 0 บาท',
      'ราคายังไม่รวมค่าสกรีนโลโก้ บรรจุภัณฑ์พิเศษ และค่าจัดส่ง ทีมขายยืนยันอีกครั้งตามงานจริง',
      'รายการในรอบนี้ยังไม่มีภาพสินค้าที่ตรวจรหัสกับต้นฉบับแล้ว จึงไม่ใส่ภาพแทนหรือภาพที่สร้างขึ้น',
      'ชุดของขวัญแสดงเฉพาะส่วนประกอบที่ยืนยันแล้ว ชุดที่ยังไม่ยืนยันจะไม่แตกรายการจากชื่อชุด'
    ].forEach(function (s) { ul.appendChild(el('li', null, s)); });
    host.appendChild(ul);
  }

  function contactPage(host) {
    head(host, 'ติดต่อ', 'คุยรายละเอียดกับทีมขาย', 'แจ้งรหัสรายการที่สนใจกับจำนวนที่ต้องการ ทีมขายจะยืนยันราคา ระยะเวลาผลิต และการสกรีนโลโก้กลับไป');
    var box = el('div');
    box.style.display = 'grid'; box.style.gap = '10px';
    var rows = [];
    if (DATA.contact.email) rows.push(['อีเมล', DATA.contact.email]);
    if (DATA.contact.line) rows.push(['LINE', DATA.contact.line]);
    if (DATA.contact.tel) rows.push(['โทร', DATA.contact.tel]);
    if (!rows.length) {
      box.appendChild(el('p', null, 'ยังไม่ได้ตั้งค่าช่องทางติดต่อในเล่มนี้ — เติมค่าใน scripts/brand_kit.py แล้ว rebuild เพื่อให้หน้านี้แสดงอีเมล LINE และเบอร์โทรจริง'));
    } else {
      rows.forEach(function (r) {
        var p = el('p');
        p.appendChild(el('strong', null, r[0] + ': '));
        p.appendChild(document.createTextNode(r[1]));
        box.appendChild(p);
      });
    }
    box.appendChild(el('p', 'page-eyebrow', 'อ้างอิงแคตตาล็อก ' + DATA.catalogVersion + ' · จัดทำ ' + DATA.generatedAt));
    host.appendChild(box);
  }

  /* ---------- render ---------- */
  var rail = qs('rail');
  PAGES.forEach(function (p, idx) {
    var b = el('button', 'thumb');
    b.type = 'button';
    var inner = el('div', 'thumb-in');
    inner.appendChild(el('span', 'thumb-n', (idx + 1) + ' / ' + PAGES.length));
    inner.appendChild(el('span', 'thumb-t', p.t));
    b.appendChild(inner);
    b.addEventListener('click', function () { go(idx); });
    rail.appendChild(b);
  });

  function go(n) {
    page = (n + PAGES.length) % PAGES.length;
    var host = qs('page');
    host.textContent = '';
    PAGES[page].build(host);
    qs('pgnum').textContent = (page + 1) + ' / ' + PAGES.length;
    qs('prev').disabled = page === 0;
    qs('next').disabled = page === PAGES.length - 1;
    Array.prototype.forEach.call(rail.children, function (b, idx) {
      b.setAttribute('aria-current', String(idx === page));
      if (idx === page) b.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    });
  }
  qs('prev').addEventListener('click', function () { go(page - 1); });
  qs('next').addEventListener('click', function () { go(page + 1); });
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT') return;
    if (e.key === 'ArrowRight') go(page + 1);
    if (e.key === 'ArrowLeft') go(page - 1);
  });

  /* ---------- tools ---------- */
  qs('t-toc').addEventListener('click', function () { go(1); });
  var find = qs('find'), hits = qs('hits');
  qs('t-find').addEventListener('click', function () {
    var on = !find.classList.contains('on');
    find.classList.toggle('on', on);
    qs('t-find').setAttribute('aria-pressed', String(on));
    if (on) qs('find-q').focus(); else { hits.textContent = ''; qs('find-q').value = ''; }
  });
  qs('find-q').addEventListener('input', function (e) {
    var q = e.target.value.trim().toLowerCase();
    hits.textContent = '';
    if (q.length < 2) return;
    DATA.items.filter(function (i) {
      return (i.name + ' ' + i.code + ' ' + (i.nameEn || '')).toLowerCase().indexOf(q) >= 0;
    }).slice(0, 8).forEach(function (i) {
      var target = -1;
      if (i.tier === 'supplier') {
        var at = shots.indexOf(i);
        var nth = Math.floor(at / PER_PAGE);
        for (var q = 0; q < PAGES.length; q++) {
          if (PAGES[q].k === 'แคตตาล็อกผู้ผลิต') { target = q + nth; break; }
        }
      } else {
        for (var p = 0; p < PAGES.length; p++) {
          if (i.kind === 'single' && PAGES[p].t === 'สินค้ารายชิ้น · ' + catName(i.cat)) { target = p; break; }
          if (i.kind === 'set' && PAGES[p].k === 'ชุดของขวัญ'
            && ((i.tiers.length && PAGES[p].t.indexOf('ราคายืนยันแล้ว') >= 0)
              || (!i.tiers.length && PAGES[p].t.indexOf('ตามฤดูกาล') >= 0))) { target = p; break; }
        }
      }
      var li = el('li');
      var b = el('button');
      b.type = 'button';
      b.appendChild(el('span', 'hn', i.code + ' · หน้า ' + (target + 1) + ' '));
      b.appendChild(document.createTextNode(i.name));
      b.addEventListener('click', function () { if (target >= 0) go(target); });
      li.appendChild(b);
      hits.appendChild(li);
    });
  });
  qs('t-full').addEventListener('click', function () {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
  });
  qs('t-share').addEventListener('click', function () {
    var t = qs('t-share');
    if (navigator.share) {
      navigator.share({ title: document.title, url: location.href }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(location.href).then(function () {
        t.textContent = '✓ คัดลอกลิงก์แล้ว';
        setTimeout(function () { t.textContent = '↗ แชร์ไฟล์'; }, 2200);
      });
    } else {
      t.textContent = 'บันทึกหน้านี้เป็นไฟล์เพื่อส่งต่อ';
    }
  });
  var timer = null;
  qs('t-auto').addEventListener('click', function () {
    var b = qs('t-auto');
    var on = b.getAttribute('aria-pressed') !== 'true';
    b.setAttribute('aria-pressed', String(on));
    if (timer) { clearInterval(timer); timer = null; }
    if (on) timer = setInterval(function () { go(page + 1); }, 6000);
  });

  go(0);
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
