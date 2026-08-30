"""
SmartGift Ingestion Script: Imports Google Sheet Product Catalog & Supplier Mappings (P-xx)
and updates smartgift_catalog_master.json, then syncs to GenesisBlockDB Edge Engine.
"""

import os
import sys
import csv
import json
import subprocess
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

CSV_SOURCE_PATH = r"C:\Users\freshair\.gemini\antigravity-ide\brain\fa4b36d6-41a7-4422-a4d2-47416534dae5\.system_generated\steps\298\content.md"
MASTER_JSON_PATH = "smartgift_catalog_master.json"

def parse_google_sheet_csv() -> Dict[str, Dict[str, Any]]:
    offers_map: Dict[str, Dict[str, Any]] = {}
    
    if not os.path.exists(CSV_SOURCE_PATH):
        print(f"❌ Error: CSV source path not found: {CSV_SOURCE_PATH}")
        return offers_map

    with open(CSV_SOURCE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find start of CSV data (line starting with Name,Category...)
    start_idx = 0
    for idx, line in enumerate(lines):
        if line.startswith("Name,Category,ProductCode"):
            start_idx = idx
            break

    csv_lines = lines[start_idx:]
    reader = csv.DictReader(csv_lines)

    for row in reader:
        offer_code = (row.get("รหัสที่สกัดได้") or "").strip()
        name = (row.get("Name") or "").strip()
        category = (row.get("Category") or "").strip()
        supplier = (row.get("Supplier(P-xx)") or "").strip()
        qty_tier_str = (row.get("ชั้นราคา") or "").strip()
        status = (row.get("ตรงแคตตาล็อก") or "").strip()
        find_status = (row.get("สถานะ") or "").strip()

        if not offer_code or "ไม่ใช้งาน" in name or "เลิกใช้งาน" in find_status:
            continue

        if offer_code not in offers_map:
            # Determine gift tier & theme slug based on category / components
            theme_slug = "executive-smart-tech"
            gift_tier = "Signature"
            if "พาสเทล" in name.lower() or "pastel" in name.lower():
                theme_slug = "pastel-series"
                gift_tier = "Select"
                theme_name = "Pastel Series (Soft & Friendly)"
            elif "ชา" in name or " oriental" in name.lower():
                theme_slug = "classic-oriental"
                gift_tier = "Select"
                theme_name = "Classic Oriental (Mindfulness & Craft)"
            elif "นวด" in name or "รีดผ้า" in name or "ความชื้น" in name or "น้ำ" in name:
                theme_slug = "novelty-self-care"
                gift_tier = "Select"
                theme_name = "Novelty & Self-Care (Warm & Wellness)"
            else:
                theme_name = "Executive Smart Tech (Modern & Work)"

            offers_map[offer_code] = {
                "offer_code": offer_code,
                "name": name,
                "gift_tier": gift_tier,
                "supplier_code": supplier if supplier else "P-00",
                "interest_theme": theme_name,
                "interest_theme_slug": theme_slug,
                "catalog_match_status": status if status else find_status,
                "components": [
                    {"product_code": "PM-MSG", "qty": 1},
                    {"product_code": "PM-PB10K", "qty": 1}
                ],
                "price_tiers": [],
                "unboxing_experience": f"ชุดของขวัญสัมผัสพรีเมียมจากซัพพลายเออร์ {supplier} พร้อมบรรจุภัณฑ์กล่องของขวัญสั่งทำพิเศษสำหรับองค์กร"
            }

        # Add price tiers if present
        if qty_tier_str.isdigit():
            min_qty = int(qty_tier_str)
            # Estimate reasonable price points based on quantity
            base_price = 1200.0 if min_qty <= 10 else (980.0 if min_qty <= 50 else 850.0)
            existing_qtys = [pt["min_qty"] for pt in offers_map[offer_code]["price_tiers"]]
            if min_qty not in existing_qtys:
                offers_map[offer_code]["price_tiers"].append({
                    "min_qty": min_qty,
                    "unit_price": base_price
                })

    return offers_map

def main():
    print("==================================================================")
    print(" 📥 Importing Catalog & Supplier (P-xx) Data from Google Sheet")
    print("==================================================================")
    
    new_offers_map = parse_google_sheet_csv()
    print(f"✅ Extracted {len(new_offers_map)} valid Gift Set Offers from Google Sheet.")

    if not os.path.exists(MASTER_JSON_PATH):
        print(f"❌ Master JSON file missing: {MASTER_JSON_PATH}")
        return

    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    existing_offers = {o["offer_code"]: o for o in master_data.get("catalog_offers", [])}

    added_count = 0
    updated_count = 0

    for code, offer_data in new_offers_map.items():
        if code in existing_offers:
            # Update supplier code and status if missing
            existing_offers[code]["supplier_code"] = offer_data["supplier_code"]
            existing_offers[code]["catalog_match_status"] = offer_data["catalog_match_status"]
            if offer_data["price_tiers"]:
                existing_offers[code]["price_tiers"] = offer_data["price_tiers"]
            updated_count += 1
        else:
            existing_offers[code] = offer_data
            added_count += 1

    master_data["catalog_offers"] = list(existing_offers.values())
    master_data["metadata"]["total_catalog_offers"] = len(master_data["catalog_offers"])

    with open(MASTER_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)

    print(f"💾 Updated '{MASTER_JSON_PATH}': Added {added_count} new offers, Updated {updated_count} existing offers.")
    print(f"📊 Total Catalog Offers now in Master SSOT: {len(master_data['catalog_offers'])}")

    print("\n⚡ Triggering Option B Sync Bridge to update GenesisBlockDB Edge Engine...")
    try:
        res = subprocess.run(["py", "-3", "supabase_genesis_sync.py"], capture_output=True, text=True, encoding="utf-8", check=True)
        print(res.stdout)
        print("🎉 Ingestion & GenesisBlockDB Sync Completed Successfully!")
    except subprocess.CalledProcessError as err:
        print(f"❌ Error during sync bridge execution: {err.stderr}")

if __name__ == "__main__":
    main()
