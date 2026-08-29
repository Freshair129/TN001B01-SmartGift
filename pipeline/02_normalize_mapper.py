"""
SmartGift Product ID Mapper & Normalizer Engine (v3 - Enterprise Provenance Edition)
Extracts embedded Product IDs, Model Codes, and Supplier P-xx tags
from both FlowAccount SQL exports and the Google Sheet catalog dataset,
and generates structured Audit & Provenance Logs with full ID bindings.
"""

import os
import sys
import re
import json
import csv
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

SQL_PATH = r"D:\workspace\zuri-rag-service\exports\smartgift-pricelist.postgres.sql"
CSV_PATH = r"C:\Users\freshair\.gemini\antigravity-ide\brain\fa4b36d6-41a7-4422-a4d2-47416534dae5\.system_generated\steps\298\content.md"
MASTER_JSON_PATH = "data-pipeline/02_prepared/smartgift_catalog_master.json"
OUTPUT_REPORT_PATH = "data-pipeline/04_review_reports/product_id_mapping_report.json"
OUTPUT_AUDIT_LOG_PATH = "data-pipeline/04_review_reports/provenance_audit_log.jsonl"

TENANT_ID = "Org-EtohGroup"
BUSINESS_ID = "SmartGift"
VAULT_ID = "vlt-catalog-product"

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

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
        for line_num, line in enumerate(f, 1):
            if "INSERT INTO smartgift_offer" in line:
                m = re.search(r"VALUES\s*\(\s*'([^']+)'\s*,\s*('[^']*'|NULL)", line)
                if m:
                    code = m.group(1)
                    raw_name = m.group(2)
                    name_th = raw_name.strip("'") if (raw_name and raw_name != "NULL") else ""
                    offers.append({
                        "flowaccount_code": code,
                        "raw_name_th": name_th,
                        "source": "smartgift-portfolio.postgres.sql",
                        "line_number": line_num,
                        "raw_sha256": compute_sha256(line)
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

    for row_num, row in enumerate(reader, 1):
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
                "source": "google_sheet_catalog",
                "row_number": row_num,
                "raw_sha256": compute_sha256(str(row))
            })
    return items

def main():
    print("==================================================================")
    print(" 🔍 SmartGift ID-Bound Provenance Logger & Product Mapper (v3)")
    print("==================================================================")

    pipeline_run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
    timestamp_iso = datetime.now(timezone.utc).isoformat()

    sql_offers = parse_sql_file()
    gs_items = parse_csv_file()
    print(f"📦 Parsed {len(sql_offers)} offers from FlowAccount SQL export.")
    print(f"📊 Parsed {len(gs_items)} items from Google Sheet Catalog.")

    mapping_results = []
    audit_log_entries = []
    mapped_count = 0
    unassigned_count = 0

    # 1. Process FlowAccount SQL
    for item in sql_offers:
        name = item["raw_name_th"]
        code = item["flowaccount_code"]
        extracted_info = extract_product_id_from_name(name, code)
        event_id = str(uuid.uuid4())
        
        if extracted_info["extracted_code"] != "UNASSIGNED":
            mapped_count += 1
        else:
            unassigned_count += 1

        record = {
            "source": item["source"],
            "flowaccount_code": code,
            "raw_name_th": name,
            "mapped_product_id": extracted_info["extracted_code"],
            "supplier_code": extracted_info["supplier_code"],
            "extraction_source": extracted_info["extraction_source"]
        }
        mapping_results.append(record)

        audit_log_entries.append({
            "event_id": event_id,
            "pipeline_run_id": pipeline_run_id,
            "tenant_id": TENANT_ID,
            "business_id": BUSINESS_ID,
            "vault_id": VAULT_ID,
            "entity_type": "ProductMaster",
            "entity_id": f"pm:{extracted_info['extracted_code']}",
            "source_ref": {
                "file": item["source"],
                "row_key": f"OFFER_{code}",
                "line_number": item["line_number"],
                "sha256": item["raw_sha256"]
            },
            "action": "ENTITY_NORMALIZED",
            "extraction_method": extracted_info["extraction_source"],
            "supplier_code": extracted_info["supplier_code"],
            "timestamp": timestamp_iso
        })

    # 2. Process Google Sheet items
    for item in gs_items:
        name = item["raw_name_th"]
        gs_code = item["extracted_code_gs"]
        extracted_info = extract_product_id_from_name(name, gs_code)
        event_id = str(uuid.uuid4())
        
        final_code = gs_code if gs_code else extracted_info["extracted_code"]
        supplier = item["supplier_code_gs"] if item["supplier_code_gs"] else extracted_info["supplier_code"]

        record = {
            "source": item["source"],
            "flowaccount_code": item["product_code_orig"],
            "raw_name_th": name,
            "mapped_product_id": final_code,
            "supplier_code": supplier,
            "extraction_source": "google_sheet_annotated" if gs_code else extracted_info["extraction_source"],
            "catalog_status": item["status_gs"]
        }
        mapping_results.append(record)

        audit_log_entries.append({
            "event_id": event_id,
            "pipeline_run_id": pipeline_run_id,
            "tenant_id": TENANT_ID,
            "business_id": BUSINESS_ID,
            "vault_id": VAULT_ID,
            "entity_type": "CatalogOffer",
            "entity_id": f"offer:{final_code}",
            "source_ref": {
                "file": item["source"],
                "row_number": item["row_number"],
                "sha256": item["raw_sha256"]
            },
            "action": "CATALOG_OFFER_EXTRACTED",
            "extraction_method": record["extraction_source"],
            "supplier_code": supplier,
            "timestamp": timestamp_iso
        })

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_REPORT_PATH), exist_ok=True)

    # Save mapping report
    report = {
        "pipeline_run_id": pipeline_run_id,
        "tenant_id": TENANT_ID,
        "business_id": BUSINESS_ID,
        "vault_id": VAULT_ID,
        "timestamp": timestamp_iso,
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

    # Save JSONL provenance audit log
    with open(OUTPUT_AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        for log in audit_log_entries:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    # Also keep root copy for backward compatibility
    with open("product_id_mapping_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ Product ID Mapping Complete with Full ID Bindings!")
    print(f"📊 Summary: Run ID '{pipeline_run_id}' | Analyzed {len(mapping_results)} items.")
    print(f"💾 Saved Audit Report to '{OUTPUT_REPORT_PATH}'.")
    print(f"📜 Saved Provenance Audit Log (JSONL) with {len(audit_log_entries)} events to '{OUTPUT_AUDIT_LOG_PATH}'.")

if __name__ == "__main__":
    main()
