"""
FlowAccount Export Ingestion Registry & Versioned Archiver Engine
Solves identical filename overwrites by computing SHA-256 content hashes,
archiving immutable historical snapshots, tracking row-level diffs,
and recording an append-only JSON registry.
"""

import os
import sys
import shutil
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

EXPORTS_DIR = "data-pipeline/01_raw/01_flowaccount_exports"
ARCHIVE_DIR = "data-pipeline/01_raw/archive"
REGISTRY_PATH = "data-pipeline/01_raw/exports_registry.json"
AUDIT_LOG_PATH = "data-pipeline/04_review_reports/provenance_audit_log.jsonl"

TENANT_ID = "Org-EtohGroup"
BUSINESS_ID = "SmartGift"
VAULT_ID = "vlt-catalog-product"

def file_key(filename: str) -> str:
    """Stable, non-identifying registry key for a source file.

    FlowAccount export filenames carry the customer's registered company name,
    so keying the registry on the filename put a named legal entity — and the
    documents exchanged with it — into a tracked JSON file (CR-006, CR-007).

    This hashes the NAME, not the content: it stays the same across every
    version of the same export, which is what a registry key has to do, while
    revealing nothing. Do not switch it to a content hash — `sha256` of the file
    already lives in each history entry and changes on every ingest; a key that
    moves is not a key, and the version history would fragment into one entry
    per version.
    """
    return hashlib.sha256(filename.encode("utf-8")).hexdigest()[:16]


def compute_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def extract_excel_summary(filepath: str) -> Dict[str, Any]:
    """Reads Excel file and returns row count, headers, and primary keys"""
    try:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return {"total_rows": 0, "headers": [], "sample_keys": []}
        
        headers = [str(c) if c is not None else f"col_{idx}" for idx, c in enumerate(rows[0])]
        data_rows = rows[1:]
        sample_keys = [str(r[0]) for r in data_rows[:10] if r and r[0] is not None]

        return {
            "total_rows": len(data_rows),
            "headers": headers,
            "sample_keys": sample_keys
        }
    except Exception as e:
        return {"total_rows": 0, "headers": [], "error": str(e)}

class FlowAccountRegistryArchiver:
    def __init__(self):
        os.makedirs(EXPORTS_DIR, exist_ok=True)
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
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_ingested_versions": 0,
                "files": {}
            }

    def save_registry(self):
        self.registry["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)

    def process_export_file(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(EXPORTS_DIR, filename)
        if not os.path.isfile(filepath):
            return {"status": "FILE_NOT_FOUND", "filename": filename}

        sha256 = compute_file_sha256(filepath)
        size_bytes = os.path.getsize(filepath)
        now_utc = datetime.now(timezone.utc)
        timestamp_iso = now_utc.isoformat()
        date_prefix = now_utc.strftime("%Y%m%dT%H%M%SZ")

        # Keyed on a hash of the filename, never the filename itself — the
        # export names carry a customer's company name (CR-006/CR-007).
        key = file_key(filename)
        if key not in self.registry["files"]:
            self.registry["files"][key] = {
                "current_sha256": None,
                "versions_count": 0,
                "history": []
            }

        file_record = self.registry["files"][key]

        # Check if identical hash already exists
        for hist in file_record["history"]:
            if hist["sha256"] == sha256:
                return {
                    "status": "UNCHANGED_DUPLICATE_SKIPPED",
                    "filename": filename,
                    "sha256": sha256,
                    "existing_version_id": hist["version_id"],
                    "first_ingested_at": hist["ingested_at"]
                }

        # New version detected!
        version_num = file_record["versions_count"] + 1
        # Both of these previously embedded `filename`, so the customer's name
        # travelled into the registry, the audit log, and every archived file's
        # name on disk. The key identifies the source; the extension is kept so
        # the archive stays openable.
        version_id = f"ver-{key}-v{version_num}-{sha256[:8]}"
        archive_filename = f"{date_prefix}_{sha256[:12]}_{key}{os.path.splitext(filename)[1]}"
        archive_filepath = os.path.join(ARCHIVE_DIR, archive_filename)

        # Copy to immutable archive
        shutil.copy2(filepath, archive_filepath)

        # Extract summary & diff
        excel_meta = extract_excel_summary(filepath)
        prev_rows = file_record["history"][-1]["total_rows"] if file_record["history"] else 0
        diff_rows = excel_meta["total_rows"] - prev_rows

        version_entry = {
            "version_id": version_id,
            "version_number": version_num,
            "sha256": sha256,
            "size_bytes": size_bytes,
            "archive_path": archive_filepath,
            "ingested_at": timestamp_iso,
            "total_rows": excel_meta["total_rows"],
            "row_diff_from_previous": diff_rows,
            "headers": excel_meta.get("headers", [])
        }

        file_record["current_sha256"] = sha256
        file_record["versions_count"] = version_num
        file_record["history"].append(version_entry)
        self.registry["total_ingested_versions"] += 1

        # Append to audit log
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "pipeline_run_id": f"run-archiver-{date_prefix}",
            "tenant_id": TENANT_ID,
            "business_id": BUSINESS_ID,
            "vault_id": VAULT_ID,
            "entity_type": "FlowAccountExportSnapshot",
            "entity_id": version_id,
            "source_ref": {
                "file_key": key,
                "archive_path": archive_filepath,
                "sha256": sha256,
                "size_bytes": size_bytes
            },
            "action": "EXPORT_SNAPSHOT_ARCHIVED",
            "total_rows": excel_meta["total_rows"],
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
            "total_rows": excel_meta["total_rows"],
            "row_diff": diff_rows
        }

    def process_all_exports(self) -> List[Dict[str, Any]]:
        results = []
        for filename in sorted(os.listdir(EXPORTS_DIR)):
            if filename.endswith(".xlsx") or filename.endswith(".csv"):
                res = self.process_export_file(filename)
                results.append(res)
        return results


def main():
    print("==================================================================")
    print(" 📦 FlowAccount Export Ingestion Registry & Archiver Engine")
    print("==================================================================")

    archiver = FlowAccountRegistryArchiver()
    results = archiver.process_all_exports()

    for r in results:
        status = r["status"]
        fn = r["filename"]
        if status == "NEW_VERSION_ARCHIVED":
            print(f"✅ [NEW VERSION]  {fn:<40} ➔ Ver: {r['version_number']} (Rows: {r['total_rows']}, Diff: {r['row_diff']:+d}) | SHA: {r['sha256'][:12]}")
        elif status == "UNCHANGED_DUPLICATE_SKIPPED":
            print(f"⏸️ [DUPLICATE]    {fn:<40} ➔ Unchanged (Existing: {r['existing_version_id']})")

    print("------------------------------------------------------------------")
    print(f"💾 Registry updated at '{REGISTRY_PATH}'.")
    print(f"🗄️ Immutable archives saved in '{ARCHIVE_DIR}/'.")

if __name__ == "__main__":
    main()
