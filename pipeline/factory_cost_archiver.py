"""
Factory Cost Intake Registry & Versioned Archiver Engine (lane 08_factory_costs)
Ingests supplier cost catalogs (.xlsx via openpyxl, legacy .xls via xlrd),
computes SHA-256 content hashes, archives immutable historical snapshots,
tracks row-level diffs, and records an append-only JSON registry.
See docs/decisions/ADR-005-FACTORY-COST-INTAKE-LANE.md
"""

import os
import sys
import shutil
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

COSTS_DIR = "data-pipeline/01_raw/08_factory_costs"
ARCHIVE_DIR = "data-pipeline/01_raw/archive/factory_costs"
REGISTRY_PATH = "data-pipeline/01_raw/factory_cost_registry.json"
AUDIT_LOG_PATH = "data-pipeline/04_review_reports/provenance_audit_log.jsonl"

TENANT_ID = "Org-EtohGroup"
BUSINESS_ID = "SmartGift"
VAULT_ID = "vlt-catalog-product"

SUPPORTED_EXTENSIONS = (".xlsx", ".xls", ".csv")


def compute_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_workbook_summary(filepath: str) -> Dict[str, Any]:
    """Reads .xlsx (openpyxl) or legacy .xls (xlrd) and returns per-sheet row counts."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            sheets = [{"name": ws.title, "rows": ws.max_row or 0} for ws in wb.worksheets]
            wb.close()
        elif ext == ".xls":
            import xlrd
            wb = xlrd.open_workbook(filepath)
            sheets = [{"name": ws.name, "rows": ws.nrows} for ws in wb.sheets()]
        else:  # .csv
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                count = sum(1 for _ in f)
            sheets = [{"name": "csv", "rows": count}]
        return {"total_rows": sum(s["rows"] for s in sheets), "sheets": sheets}
    except Exception as e:
        return {"total_rows": 0, "sheets": [], "error": str(e)}


class FactoryCostRegistryArchiver:
    def __init__(self):
        os.makedirs(COSTS_DIR, exist_ok=True)
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        self.load_registry()

    def load_registry(self):
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "tenant_id": TENANT_ID,
                "business_id": BUSINESS_ID,
                "lane": "08_factory_costs",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_ingested_versions": 0,
                "files": {}
            }

    def save_registry(self):
        self.registry["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)

    def process_cost_file(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(COSTS_DIR, filename)
        if not os.path.isfile(filepath):
            return {"status": "FILE_NOT_FOUND", "filename": filename}

        sha256 = compute_file_sha256(filepath)
        size_bytes = os.path.getsize(filepath)
        now_utc = datetime.now(timezone.utc)
        timestamp_iso = now_utc.isoformat()
        date_prefix = now_utc.strftime("%Y%m%dT%H%M%SZ")

        if filename not in self.registry["files"]:
            self.registry["files"][filename] = {
                "original_filename": filename,
                "current_sha256": None,
                "versions_count": 0,
                "history": []
            }

        file_record = self.registry["files"][filename]

        for hist in file_record["history"]:
            if hist["sha256"] == sha256:
                return {
                    "status": "UNCHANGED_DUPLICATE_SKIPPED",
                    "filename": filename,
                    "sha256": sha256,
                    "existing_version_id": hist["version_id"],
                    "first_ingested_at": hist["ingested_at"]
                }

        version_num = file_record["versions_count"] + 1
        version_id = f"ver-{os.path.splitext(filename)[0]}-v{version_num}-{sha256[:8]}"
        archive_filename = f"{date_prefix}_{sha256[:12]}_{filename}"
        archive_filepath = os.path.join(ARCHIVE_DIR, archive_filename)

        shutil.copy2(filepath, archive_filepath)

        wb_meta = extract_workbook_summary(filepath)
        prev_rows = file_record["history"][-1]["total_rows"] if file_record["history"] else 0
        diff_rows = wb_meta["total_rows"] - prev_rows

        version_entry = {
            "version_id": version_id,
            "version_number": version_num,
            "sha256": sha256,
            "size_bytes": size_bytes,
            "archive_path": archive_filepath.replace("\\", "/"),
            "ingested_at": timestamp_iso,
            "total_rows": wb_meta["total_rows"],
            "row_diff_from_previous": diff_rows,
            "sheets": wb_meta.get("sheets", [])
        }
        if "error" in wb_meta:
            version_entry["read_error"] = wb_meta["error"]

        file_record["current_sha256"] = sha256
        file_record["versions_count"] = version_num
        file_record["history"].append(version_entry)
        self.registry["total_ingested_versions"] += 1

        audit_event = {
            "event_id": str(uuid.uuid4()),
            "pipeline_run_id": f"run-cost-archiver-{date_prefix}",
            "tenant_id": TENANT_ID,
            "business_id": BUSINESS_ID,
            "vault_id": VAULT_ID,
            "entity_type": "FactoryCostSnapshot",
            "entity_id": version_id,
            "source_ref": {
                "original_filename": filename,
                "archive_path": archive_filepath.replace("\\", "/"),
                "sha256": sha256,
                "size_bytes": size_bytes
            },
            "action": "FACTORY_COST_SNAPSHOT_ARCHIVED",
            "total_rows": wb_meta["total_rows"],
            "row_diff": diff_rows,
            "timestamp": timestamp_iso
        }

        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_event, ensure_ascii=False) + "\n")

        self.save_registry()

        return {
            "status": "NEW_VERSION_ARCHIVED",
            "filename": filename,
            "version_id": version_id,
            "version_number": version_num,
            "sha256": sha256,
            "archive_filename": archive_filename,
            "total_rows": wb_meta["total_rows"],
            "row_diff": diff_rows
        }

    def process_all_cost_files(self) -> List[Dict[str, Any]]:
        results = []
        for filename in sorted(os.listdir(COSTS_DIR)):
            if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                results.append(self.process_cost_file(filename))
        return results


def main():
    print("==================================================================")
    print(" 🏭 Factory Cost Intake Registry & Archiver Engine (lane 08)")
    print("==================================================================")

    archiver = FactoryCostRegistryArchiver()
    results = archiver.process_all_cost_files()

    for r in results:
        status = r["status"]
        fn = r["filename"]
        if status == "NEW_VERSION_ARCHIVED":
            print(f"✅ [NEW VERSION]  {fn:<55} ➔ Ver: {r['version_number']} (Rows: {r['total_rows']}, Diff: {r['row_diff']:+d}) | SHA: {r['sha256'][:12]}")
        elif status == "UNCHANGED_DUPLICATE_SKIPPED":
            print(f"⏸️ [DUPLICATE]    {fn:<55} ➔ Unchanged (Existing: {r['existing_version_id']})")

    print("------------------------------------------------------------------")
    print(f"💾 Registry updated at '{REGISTRY_PATH}'.")
    print(f"🗄️ Immutable archives saved in '{ARCHIVE_DIR}/'.")


if __name__ == "__main__":
    main()
