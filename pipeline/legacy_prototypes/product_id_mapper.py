"""
SmartGift Product ID Mapper & Normalizer Engine (v2)
Extracts embedded Product IDs, Model Codes, and Supplier P-xx tags
from both FlowAccount SQL exports and the Google Sheet catalog dataset.
"""

import os
import sys
import re
import json
import csv
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

SQL_PATH = r"D:\workspace\zuri-rag-service\exports\smartgift-pricelist.postgres.sql"
CSV_PATH = r"C:\Users\freshair\.gemini\antigravity-ide\brain\fa4b36d6-41a7-4422-a4d2-47416534dae5\.system_generated\steps\298\content.md"
MASTER_JSON_PATH = "smartgift_catalog_master.json"
OUTPUT_REPORT_PATH = "product_id_mapping_report.json"

def extract_product_id_from_name(name_th: str, default_code: str = "") -> Dict[str, str]:
    if not name_th:
        return {"extracted_code": default_code, "extraction_source": "default_code", "supplier_code": "P-00"}

    # Pattern A: Model : MC00-1 or Model: VC-002
    model_match = re.search(r'Model\s*:\s*([\w-]+)', name_th, re.IGNORECASE)
    if model_match:
        return {
            "extracted_code": model_match.group(1).upper(),
            "extraction_source": "model_keyword_regex",
            "supplier_code": extract_supplier_code(name_th)
        }

    # Pattern B: Standard Code Pattern like THB03-2, TSPS2-2, TYD0762, BE0011, TSQ06-4
    code_match = re.search(r'\b([A-Z]{2,4}\d{1,4}(?:-\d+)?)\b', name_th)
    if code_match:
        return {
            "extracted_code": code_match.group(1).upper(),
            "extraction_source": "name_pattern_regex",
            "supplier_code": extract_supplier_code(name_th)
        }

    # Pattern C: Numeric Model like 444, 445 embedded in name
    num_match = re.search(r'\b(\d{3,4})\b', name_th)
    if num_match:
        return {
            "extracted_code": num_match.group(1),
            "extraction_source": "numeric_embedded_regex",
            "supplier_code": extract_supplier_code(name_th)
        }

    return {
        "extracted_code": default_code if default_code else "UNASSIGNED",
        "extraction_source": "fallback_or_unassigned",
        "supplier_code": extract_supplier_code(name_th)
    }

def extract_supplier_code(text: str) -> str:
    m = re.search(r'\((P-[\w-]+)\)', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m2 = re.search(r'\b(P-\d{1,2}[A-Z]?)\b', text, re.IGNORECASE)
    if m2:
        return m2.group(1).upper()
    return "P-00"

def parse_sql_file() -> List[Dict[str, Any]]:
    offers = []
    if not os.path.exists(SQL_PATH):
        print(f"⚠️ Warning: SQL file not found at {SQL_PATH}")
        return offers

    with open(SQL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if "INSERT INTO smartgift_offer" in line:
                # Extract code and name_th from SQL line
                # FORMAT: VALUES ('AS00-2', 'แก้วมัค...', ...)
                m = re.search(r"VALUES\s*\(\s*'([^']+)'\s*,\s*('[^']*'|NULL)", line)
                if m:
                    code = m.group(1)
                    raw_name = m.group(2)
                    name_th = raw_name.strip("'") if (raw_name and raw_name != "NULL") else ""
                    offers.append({
                        "flowaccount_code": code,
                        "raw_name_th": name_th,
                        "source": "flowaccount_sql"
                    })
    return offers

def parse_csv_file() -> List[Dict[str, Any]]:
    items = []
    if not os.path.exists(CSV_PATH):
        return items

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = 0
    for idx, line in enumerate(lines):
        if line.startswith("Name,Category,ProductCode"):
            start_idx = idx
            break

    csv_lines = lines[start_idx:]
    reader = csv.DictReader(csv_lines)

    for row in reader:
        name = (row.get("Name") or "").strip()
        code_orig = (row.get("ProductCode_เดิม") or "").strip()
        code_extracted = (row.get("รหัสที่สกัดได้") or "").strip()
        supplier = (row.get("Supplier(P-xx)") or "").strip()
        status = (row.get("สถานะ") or "").strip()

        if name:
            items.append({
                "raw_name_th": name,
                "product_code_orig": code_orig,
                "extracted_code_gs": code_extracted,
                "supplier_code_gs": supplier,
                "status_gs": status,
                "source": "google_sheet"
            })
    return items

def main():
    print("==================================================================")
    print(" 🔍 SmartGift Product ID Mapping & Extraction Engine (v2)")
    print("==================================================================")

    sql_offers = parse_sql_file()
    gs_items = parse_csv_file()
    print(f"📦 Parsed {len(sql_offers)} offers from FlowAccount SQL export.")
    print(f"📊 Parsed {len(gs_items)} items from Google Sheet Catalog.")

    mapping_results = []
    mapped_count = 0
    unassigned_count = 0

    # 1. Process FlowAccount SQL
    for item in sql_offers:
        name = item["raw_name_th"]
        code = item["flowaccount_code"]
        extracted_info = extract_product_id_from_name(name, code)
        
        if extracted_info["extracted_code"] != "UNASSIGNED":
            mapped_count += 1
        else:
            unassigned_count += 1

        mapping_results.append({
            "source": "flowaccount_sql",
            "flowaccount_code": code,
            "raw_name_th": name,
            "mapped_product_id": extracted_info["extracted_code"],
            "supplier_code": extracted_info["supplier_code"],
            "extraction_source": extracted_info["extraction_source"]
        })

    # 2. Process Google Sheet items
    for item in gs_items:
        name = item["raw_name_th"]
        gs_code = item["extracted_code_gs"]
        extracted_info = extract_product_id_from_name(name, gs_code)
        
        final_code = gs_code if gs_code else extracted_info["extracted_code"]
        supplier = item["supplier_code_gs"] if item["supplier_code_gs"] else extracted_info["supplier_code"]

        mapping_results.append({
            "source": "google_sheet",
            "flowaccount_code": item["product_code_orig"],
            "raw_name_th": name,
            "mapped_product_id": final_code,
            "supplier_code": supplier,
            "extraction_source": "google_sheet_annotated" if gs_code else extracted_info["extraction_source"],
            "catalog_status": item["status_gs"]
        })

    # Save mapping report
    report = {
        "summary": {
            "total_items_analyzed": len(mapping_results),
            "flowaccount_sql_items": len(sql_offers),
            "google_sheet_items": len(gs_items),
            "successfully_mapped_product_ids": mapped_count + len(gs_items)
        },
        "sample_mappings": mapping_results[:50]
    }

    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ Product ID Mapping Complete!")
    print(f"📊 Summary: Analyzed {len(mapping_results)} total items | Successfully mapped product codes!")
    print(f"💾 Saved mapping report to '{OUTPUT_REPORT_PATH}'.")

if __name__ == "__main__":
    main()
