#!/usr/bin/env python3
"""สร้างรายการ catalog (listing) จาก PM — แยก "สินค้าเดี่ยว" กับ "ชุดของขวัญ"

แหล่งข้อมูล (อ่านอย่างเดียว ไม่แก้ raw):
  - public/data/product_manifest.json      : PM / index หมวด + image index
  - public/data/categories/<slug>.json     : สินค้าเดี่ยว canonical 16 รายการ
  - public/data/pricelist_public.json      : catalog_offers, seasonal_offers, bom, prices
  - public/data/catalog_media.json         : ภาพที่ตรวจรหัสแล้ว

ผลลัพธ์:
  - public/data/catalog_listing.json

กติกาการแยก (deterministic):
  เดี่ยว = PM canonical (ยืนยันราคา 8 ขั้น) + catalog offer ที่ offer_kind == "single"
  ชุด    = seasonal offer ที่มีส่วนประกอบยืนยัน (BOM) + catalog offer ที่ offer_kind == "set"
ไม่เดา ไม่เติมราคา/ภาพ — รายการที่ไม่มีหลักฐานถูกทำเครื่องหมายสถานะตามจริง
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
ASSETS = ROOT / "public" / "assets"

CAT_ORDER = ["eco-friendly", "executive-smart-tech", "classic-oriental", "novelty-self-care"]


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# visual_status จากต้นทาง → ระดับหลักฐานภาพ
# ตาม SPEC-CUSTOMER-CATALOG-IMAGE-FIRST: ภาพ fallback/ภาพสร้างขึ้น ห้ามนับเป็นภาพสินค้าจริง
EVIDENCE_BY_VISUAL = {
    "source-photo": "source_photo",
    "source_matched_creative_proof": "creative_proof",
    "generated_from_source_reference": "creative_proof",
    "fallback-placeholder": "placeholder",
}


def image_state(url, visual_status=None):
    """คืน (สถานะไฟล์, url, ระดับหลักฐานภาพ)

    ตรวจว่าไฟล์มีจริงบนดิสก์ (ไม่เชื่อ path ใน JSON เพียงอย่างเดียว) แล้วจัดระดับหลักฐาน:
      source_photo   = ภาพต้นฉบับที่ตรวจรหัสแล้ว ใช้เป็นภาพสินค้าได้
      creative_proof = ภาพสร้างจากต้นฉบับ ใช้ดูรูปทรง ไม่ใช่ภาพสินค้าจริง
      placeholder    = ภาพแทนที่ ต้องแสดง "ยังไม่มีภาพสินค้า"
      none           = ไม่มีภาพ
    """
    evidence = EVIDENCE_BY_VISUAL.get(visual_status, "none" if not visual_status else "unverified")
    if not url:
        return "no_image", None, "none"
    rel = url.lstrip("/")
    if not rel.startswith("assets/"):
        return "no_image", None, "none"
    if not (ASSETS / rel[len("assets/"):]).is_file():
        return "missing_file", url, "none"
    if evidence == "placeholder":
        return "placeholder_only", url, "placeholder"
    return "verified_file", url, evidence


def main() -> int:
    manifest = load(DATA / "product_manifest.json")
    pricelist = load(DATA / "pricelist_public.json")
    media = load(DATA / "catalog_media.json")

    img_index = manifest["product_image_index"]
    media_by_code = {m["code"]: m for m in media.get("sets", []) + media.get("products", [])}

    prices_by_offer = defaultdict(list)
    for p in pricelist["prices"]:
        if not p.get("price_missing"):
            prices_by_offer[p["offer_code"]].append(p)

    bom_by_offer = defaultdict(list)
    for b in pricelist["bom"]:
        bom_by_offer[b["offer_id"]].append(b)

    # ---------- เดี่ยว: PM canonical ----------
    singles_core = []
    for slug in CAT_ORDER:
        cat = load(DATA / "categories" / f"{slug}.json")
        for p in cat["products"]:
            info = p.get("image_info") or {}
            state, url, evidence = image_state(info.get("image_url"), info.get("visual_status"))
            singles_core.append({
                "code": p["code"],
                "kind": "single",
                "tier": "core",
                "name_th": p["name_th"],
                "name_en": p.get("name_en"),
                "category_slug": slug,
                "product_family": p.get("product_family"),
                "dimensions_cm": p.get("dimensions_cm"),
                "unit_weight_kg": p.get("unit_weight_kg"),
                "srp_price": p.get("srp_price"),
                "price_status": "confirmed_tiers" if p.get("price_tiers") else "ask_for_quote",
                "price_tiers": p.get("price_tiers") or [],
                "image_url": url,
                "image_status": state,
                "image_evidence": evidence,
                "visual_status": info.get("visual_status"),
            })

    # ---------- ชุด: seasonal offers ที่มีส่วนประกอบยืนยัน ----------
    sets_core = []
    core_set_codes = set()
    for s in pricelist["seasonal_offers"]:
        comps = s.get("contains") or []
        bom = bom_by_offer.get(s["id"], [])
        by_code = {b["product_code"]: b for b in bom}
        components = [{
            "product_code": c["product_code"],
            "qty": c.get("qty"),
            "name_th": (by_code.get(c["product_code"]) or {}).get("name_th"),
            "unit_srp_qty1": (by_code.get(c["product_code"]) or {}).get("unit_srp_qty1"),
        } for c in comps]
        tiers = s.get("price_tiers") or []
        s_img = img_index.get(s["code"]) or {}
        state, url, evidence = image_state(s_img.get("image_url"), s_img.get("visual_status"))
        core_set_codes.add(s["code"])
        sets_core.append({
            "code": s["code"],
            "kind": "set",
            "tier": "core",
            "name_th": s.get("name"),
            "gift_tier": s.get("gift_tier"),
            "category_slug": s.get("catalog_slug"),
            "unboxing_experience": s.get("unboxing_experience"),
            "component_count": len(components),
            "components": components,
            "components_status": "confirmed_bom" if bom else "pending_confirmation",
            "price_status": "confirmed_tiers" if tiers else "ask_for_quote",
            "price_tiers": tiers,
            "image_url": url,
            "image_status": state,
            "image_evidence": evidence,
            "visual_status": s_img.get("visual_status"),
        })

    # ---------- catalog offers (supplier layer) ----------
    singles_supplier, sets_supplier = [], []
    for o in pricelist["catalog_offers"]:
        if o["code"] in core_set_codes:
            continue  # ถูกยกระดับเป็น core set แล้ว ไม่นับซ้ำ
        rows = prices_by_offer.get(o["code"], [])
        tiers = sorted(
            ({"min_qty": r["qty_tier"], "unit_price": r["unit_price"]} for r in rows if r.get("qty_tier")),
            key=lambda t: t["min_qty"],
        )
        # ภาพ: ใช้ media ที่ตรวจรหัสแล้วก่อน แล้วค่อย fallback ไป path ใน offer
        o_media = media_by_code.get(o["code"]) or {}
        o_img = img_index.get(o["code"]) or {}
        cand = o_media.get("image") or o_img.get("image_url") or o.get("image")
        vis = o_media.get("visual_status") or o_img.get("visual_status")
        state, url, evidence = image_state(cand, vis)
        rec = {
            "code": o["code"],
            "kind": o["offer_kind"],
            "tier": "supplier",
            "name_th": o.get("name_th") or o.get("name"),
            "name_en": o.get("name_en"),
            "description": o.get("description"),
            "branding": o.get("branding"),
            "classification_status": o.get("status"),
            "price_status": "confirmed_tiers" if tiers else "ask_for_quote",
            "price_tiers": tiers,
            "image_url": url,
            "image_status": state,
            "image_evidence": evidence,
            "visual_status": vis,
        }
        (singles_supplier if o["offer_kind"] == "single" else sets_supplier).append(rec)

    singles = singles_core + singles_supplier
    sets_ = sets_core + sets_supplier

    def stat(rows):
        return {
            "total": len(rows),
            "core": sum(r["tier"] == "core" for r in rows),
            "supplier": sum(r["tier"] == "supplier" for r in rows),
            "priced": sum(r["price_status"] == "confirmed_tiers" for r in rows),
            "ask_for_quote": sum(r["price_status"] == "ask_for_quote" for r in rows),
            "source_photo": sum(r["image_evidence"] == "source_photo" for r in rows),
            "creative_proof": sum(r["image_evidence"] == "creative_proof" for r in rows),
            "no_usable_image": sum(r["image_evidence"] in ("placeholder", "none", "unverified") for r in rows),
        }

    out = {
        "schema_version": "0.1.0b",
        "status": "listing_draft",
        "generated_at": date.today().isoformat(),
        "source": {
            "product_manifest_version": manifest["catalog_version"],
            "pricelist_schema": pricelist["metadata"]["schema_version"],
            "files": [
                "public/data/product_manifest.json",
                "public/data/categories/*.json",
                "public/data/pricelist_public.json",
                "public/data/catalog_media.json",
            ],
        },
        "disclaimer_th": (
            "รายการนี้สร้างจากข้อมูลที่มีอยู่เท่านั้น ไม่เติมราคา ส่วนประกอบ หรือภาพที่ยังไม่ยืนยัน "
            "รายการที่ price_status = ask_for_quote ให้ใช้ข้อความ 'สอบถามราคา' และห้ามแสดง 0 บาท"
        ),
        "categories": pricelist["portfolio_catalogs"],
        "summary": {"singles": stat(singles), "sets": stat(sets_)},
        "singles": singles,
        "sets": sets_,
    }

    out_path = DATA / "catalog_listing.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote " + str(out_path.relative_to(ROOT)))
    print(json.dumps(out["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
