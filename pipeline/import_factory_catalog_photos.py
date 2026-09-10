#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""นำภาพสินค้าจากไฟล์ต้นทุนโรงงาน (lane 08) เข้าคลังภาพแคตตาล็อก

    python pipeline/import_factory_catalog_photos.py --dry-run
    python pipeline/import_factory_catalog_photos.py --apply

ต่างจาก scripts/extract_customer_catalog_photos.py ตรงที่ต้นทางคนละ lane:
lane 02 = ใบราคาที่ส่งลูกค้า · lane 08 = ไฟล์ต้นทุนโรงงาน (เอกสารภายใน)
ภาพที่ฝังอยู่เป็นภาพสินค้า ไม่ใช่ตัวเลขต้นทุน แต่เพราะต้นทางเป็นเอกสารภายใน
จึงต้องผ่านการอนุมัติจากเจ้าของก่อน และบันทึกที่มาแยกไว้ใน manifest

ไม่เขียนทับไฟล์ที่มีอยู่ — ภาพจาก lane 02 มีสิทธิ์เหนือกว่าเสมอ
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data-pipeline/01_raw/08_factory_costs/extracted_images"
DEST = ROOT / "public/assets/catalog-media"
MANIFEST = ROOT / "data-pipeline/02_prepared/catalog_media_lane08.json"
PRICELIST = ROOT / "data-pipeline/02_prepared/pricelist_master.json"

MAX_EDGE = 1200          # พอสำหรับการ์ดและ modal ไม่ต้องใหญ่กว่านี้
WEBP_QUALITY = 82


def candidates():
    """รหัส -> ไฟล์ภาพ (ตัด _2 _3 ที่เป็นมุมมองเพิ่มออก เอาใบแรก)"""
    by_code = defaultdict(list)
    for sub in sorted(SOURCE.iterdir()):
        if not sub.is_dir():
            continue
        for f in sorted(sub.iterdir()):
            stem = re.sub(r"_\d+$", "", f.stem)
            by_code[stem].append(f)
    return by_code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="เขียนไฟล์จริง (ค่าเริ่มต้นคือ dry-run)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply:
        print("dry-run — ยังไม่เขียนไฟล์ ใส่ --apply เพื่อเขียนจริง\n")

    offers = {o["code"] for o in json.loads(PRICELIST.read_text(encoding="utf-8"))["catalog_offers"]}
    by_code = candidates()
    existing = {re.sub(r"^source-offer-", "", f.stem) for f in DEST.glob("source-offer-*")}

    written, skipped_existing, skipped_unknown, failed = [], 0, 0, []
    saved_bytes = 0
    for code in sorted(by_code):
        if code not in offers:
            skipped_unknown += 1
            continue
        if code in existing:            # lane 02 มาก่อนเสมอ
            skipped_existing += 1
            continue
        src = by_code[code][0]
        target = DEST / f"source-offer-{code}.webp"
        try:
            with Image.open(src) as im:
                im = im.convert("RGB")
                before = src.stat().st_size
                im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
                if args.apply:
                    im.save(target, "WEBP", quality=WEBP_QUALITY, method=6)
                    saved_bytes += before - target.stat().st_size
                written.append({"code": code, "source": str(src.relative_to(ROOT)).replace("\\", "/"),
                                "file": target.name, "size": im.size})
        except Exception as exc:                      # noqa: BLE001
            failed.append((code, str(exc)[:60]))

    print(f"นำเข้า        {len(written)}")
    print(f"มีอยู่แล้ว     {skipped_existing}  (ภาพจาก lane 02 ไม่ถูกทับ)")
    print(f"ไม่ใช่ offer   {skipped_unknown}")
    print(f"ล้มเหลว        {len(failed)}")
    for code, err in failed[:10]:
        print(f"   {code}: {err}")
    if args.apply:
        print(f"ประหยัดพื้นที่  {saved_bytes / 1048576:.0f} MB")
        MANIFEST.write_text(json.dumps({
            "lane": "08_factory_costs",
            "note": "ภาพสินค้าจากไฟล์ต้นทุนโรงงาน อนุมัติโดยเจ้าของ 2026-09-11 · "
                    "ที่มาต่างจากภาพ lane 02 ที่มาจากใบราคาลูกค้า",
            "max_edge": MAX_EDGE, "webp_quality": WEBP_QUALITY,
            "count": len(written), "items": written,
        }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"เขียน {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
