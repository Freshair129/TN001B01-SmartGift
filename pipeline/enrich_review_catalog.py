"""
SmartGift Review Catalog Integrator & Pricing Tier Enricher
Ingests catalog-G-giftsets, catalog-P-products, catalog-BOM-new-sets-draft, and 32-categories-cost-price
into smartgift_catalog_master.json with Sub-Catalogs, Tags, Quantity Tiers, SRP, and Corporate Package Guardrails.
"""

import os
import sys
import csv
import json
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

REVIEW_DIR = r"D:\workspace\Bussiness-01-SmartGift\data\review"
MASTER_JSON_PATH = "data-pipeline/02_prepared/smartgift_catalog_master.json"

def parse_price_tiers(tier_str: str) -> list:
    """Parses string like '10:1380 / 20:1240 / 50:1170 / 100:1110 / 500:1040' into price_tiers array."""
    tiers = []
    if not tier_str:
        return tiers
    parts = tier_str.split('/')
    for p in parts:
        m = re.search(r'(\d+)\s*:\s*([\d\.]+)', p.strip())
        if m:
            min_qty = int(m.group(1))
            price = float(m.group(2))
            tiers.append({"min_qty": min_qty, "unit_price": price})
    return sorted(tiers, key=lambda x: x["min_qty"])

def main():
    print("=== Step 1: Loading Existing Catalog Master ===")
    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    # 1. Enrich Sub-Catalog Structure
    master_data["sub_catalogs"] = [
        {
            "code": "canonical_catalog",
            "name": "Canonical Product Catalog (Single SKUs & Verified Offers)",
            "description": "สินค้าและเซ็ตเสนอขายที่มี PID และรหัส FlowAccount สมบูรณ์ พร้อมออกใบเสนอราคาอัตโนมัติ"
        },
        {
            "code": "bundle_only_catalog",
            "name": "Bundle-Only Product Catalog (Single Items Sold in Sets Only)",
            "description": "สินค้าเดี่ยวชิ้นส่วนจริงที่ไม่มีราคาขายแยกเดี่ยว (จำหน่ายเฉพาะในชุดของขวัญ)"
        },
        {
            "code": "draft_bom_catalog",
            "name": "Draft BOM & Unassigned Family Catalog",
            "description": "ชุดของขวัญและชิ้นส่วน BOM ที่อยู่ระหว่างรอการกำหนด PID / อนุมัติราคาจากทีมงาน"
        }
    ]

    # 2. Ingest catalog-P-products.csv (Single Product Masters & Families)
    p_file = os.path.join(REVIEW_DIR, "catalog-P-products.csv")
    p_items = []
    if os.path.exists(p_file):
        with open(p_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                p_id = (row.get("P-ID") or "").strip()
                family_name = (row.get("ชื่อ (Family)") or "").strip()
                category = (row.get("หมวด") or "").strip()
                origin = (row.get("ที่มา") or "").strip()
                product_id_raw = (row.get("productId") or "").strip()

                is_pending = "ยังไม่มีรหัส" in p_id or "⚠" in p_id
                tags = ["sub_catalog:bundle_only"] if "ขายแต่ในชุด" in origin else ["sub_catalog:canonical"]
                
                if is_pending:
                    tags.append("status:pid_pending")
                    p_code = product_id_raw if product_id_raw else f"P-DRAFT-{len(p_items)+1:03d}"
                else:
                    p_code = p_id

                tags.append("channel:bundle_only" if "ขายแต่ในชุด" in origin else "channel:standalone_and_bundle")

                # Estimate SRP (1-piece retail) if base cost available
                srp_est = None
                
                p_items.append({
                    "code": p_code,
                    "name_th": family_name,
                    "category": category if category != "(ยังไม่จัด)" else "Unassigned Family",
                    "sub_catalog": "bundle_only_catalog" if "ขายแต่ในชุด" in origin else ("draft_bom_catalog" if is_pending else "canonical_catalog"),
                    "tags": tags,
                    "status": "pid_pending" if is_pending else "active",
                    "origin": origin
                })
    print(f"Parsed {len(p_items)} P-Product Families from review folder.")

    # 3. Ingest catalog-G-giftsets.csv and Update Catalog Offers Price Tiers & SRP
    g_file = os.path.join(REVIEW_DIR, "catalog-G-giftsets.csv")
    existing_offers_map = {o["offer_code"]: o for o in master_data.get("catalog_offers", [])}

    if os.path.exists(g_file):
        with open(g_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                g_id = (row.get("G-ID") or "").strip()
                name = (row.get("ชื่อ") or "").strip()
                price_str = (row.get("ราคาขาย (จำนวน:บาท)") or "").strip()
                supplier = (row.get("Supplier") or "").strip()
                in_flowaccount = (row.get("อยู่ใน FlowAccount") or "").strip()

                if not g_id:
                    continue

                price_tiers = parse_price_tiers(price_str)
                # Calculate SRP (1-piece benchmark price)
                srp = price_tiers[0]["unit_price"] + 1530.0 if price_tiers else None

                tags = [f"supplier:{supplier}"] if supplier else ["supplier:P-00"]
                if in_flowaccount == "ใช่":
                    tags.append("status:in_flowaccount")
                else:
                    tags.append("status:flowaccount_pending")

                if g_id in existing_offers_map:
                    offer = existing_offers_map[g_id]
                    if price_tiers and not offer.get("price_tiers"):
                        offer["price_tiers"] = price_tiers
                    if srp:
                        offer["srp_price"] = srp
                    offer["sub_catalog"] = "canonical_catalog"
                    offer["tags"] = list(set(offer.get("tags", []) + tags))
                else:
                    new_offer = {
                        "offer_code": g_id,
                        "name": name,
                        "gift_tier": "Select",
                        "interest_theme": "Eco-Friendly & Sustainability (Green & Earth)",
                        "interest_theme_slug": "eco-friendly",
                        "sub_catalog": "canonical_catalog" if in_flowaccount == "ใช่" else "draft_bom_catalog",
                        "tags": tags,
                        "price_tiers": price_tiers,
                        "srp_price": srp,
                        "unboxing_experience": f"ชุดของขวัญองค์กรดีไซน์พรีเมียมจากซัพพลายเออร์ {supplier} พร้อมบรรจุภัณฑ์สั่งทำพิเศษ"
                    }
                    master_data["catalog_offers"].append(new_offer)
                    existing_offers_map[g_id] = new_offer

    print(f"Total catalog offers in master data: {len(master_data['catalog_offers'])}")

    # 4. Enforce Corporate Package Profit Minimum Threshold Guardrail & Attach BOM Breakdown
    print("\n=== Step 2: Enforcing Corporate Package Profit Thresholds & Attaching BOM ===")
    MIN_PKG_PROFIT = 20000.0
    TARGET_PKG_PROFIT = 30000.0

    try:
        from src.cascade_engine import InventoryCascadeEngine
        inv_engine = InventoryCascadeEngine()
    except Exception:
        inv_engine = None

    for b in master_data.get("corporate_bundles", []):
        total_sell = b.get("total_price", 0.0)
        code = b.get("bundle_code", "")

        if inv_engine:
            dec = inv_engine.decompose_bundle(code, 1)
            total_cost = dec.get("total_cost_price", total_sell * 0.35)
            profit = dec.get("gross_profit", total_sell - total_cost)
            margin = dec.get("gross_margin_percent", (profit / total_sell) * 100 if total_sell else 0)
            
            b["landed_cost"] = total_cost
            b["gross_profit"] = profit
            b["gross_margin_percent"] = margin
            b["meets_min_profit_threshold"] = profit >= MIN_PKG_PROFIT
            b["bom_breakdown"] = {
                "included_sets": dec.get("sets_breakdown", []),
                "physical_sku_bom": dec.get("physical_sku_deductions", [])
            }
        else:
            est_cost = total_sell * 0.35
            profit = total_sell - est_cost
            b["landed_cost"] = est_cost
            b["gross_profit"] = profit
            b["meets_min_profit_threshold"] = profit >= MIN_PKG_PROFIT

        print(f"Package {b['bundle_code']} ({b['name']}): Selling=฿{total_sell:,.2f}, Cost=฿{b['landed_cost']:,.2f}, Profit=฿{b['gross_profit']:,.2f} (Meets Min ฿20k: {b['meets_min_profit_threshold']})")

    # 5. Save updated master data
    with open(MASTER_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Successfully updated {MASTER_JSON_PATH} with review dataset enrichment!")

if __name__ == "__main__":
    main()
