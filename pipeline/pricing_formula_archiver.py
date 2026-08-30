"""
Pricing Rules Formula Ingestion Registry & Versioned Archiver Engine
Computes SHA-256 content hashes for pricing formula YAML files,
archives immutable historical snapshots in data-pipeline/01_raw/archive/pricing_formulas,
maintains an append-only JSON registry at data-pipeline/01_raw/pricing_formula_registry.json,
and logs audit records into provenance_audit_log.jsonl.
"""

import os
import sys
import shutil
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
try:
    import yaml
except ImportError:
    yaml = None

sys.stdout.reconfigure(encoding='utf-8')

FORMULA_CONFIG_PATH = "config/pricing_rules_formula.yaml"
RAW_FORMULAS_DIR = "data-pipeline/01_raw/07_pricing_formulas"
ARCHIVE_DIR = "data-pipeline/01_raw/archive/pricing_formulas"
REGISTRY_PATH = "data-pipeline/01_raw/pricing_formula_registry.json"
AUDIT_LOG_PATH = "data-pipeline/04_review_reports/provenance_audit_log.jsonl"

TENANT_ID = "Org-EtohGroup"
BUSINESS_ID = "SmartGift"
VAULT_ID = "vlt-catalog-product"

def compute_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class PricingFormulaArchiver:
    def __init__(self):
        os.makedirs(RAW_FORMULAS_DIR, exist_ok=True)
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        self.load_registry()

    def load_registry(self):
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "tenant_id": TENANT_ID,
                "business_id": BUSINESS_ID,
                "vault_id": VAULT_ID,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "active_formula_sha256": None,
                "total_ingested_versions": 0,
                "formulas": {}
            }

    def save_registry(self):
        self.registry["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)

    def log_provenance_event(self, event_type: str, details: Dict[str, Any]):
        audit_entry = {
            "event_id": f"evt-{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": TENANT_ID,
            "business_id": BUSINESS_ID,
            "vault_id": VAULT_ID,
            "event_type": event_type,
            "provenance": details
        }
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")

    def archive_formula_file(self, filepath: str) -> Dict[str, Any]:
        if not os.path.isfile(filepath):
            return {"status": "FILE_NOT_FOUND", "filepath": filepath}

        filename = os.path.basename(filepath)
        sha256 = compute_file_sha256(filepath)
        size_bytes = os.path.getsize(filepath)
        now_utc = datetime.now(timezone.utc)
        timestamp_iso = now_utc.isoformat()
        date_prefix = now_utc.strftime("%Y%m%dT%H%M%SZ")

        if filename not in self.registry["formulas"]:
            self.registry["formulas"][filename] = {
                "filename": filename,
                "current_sha256": None,
                "versions_count": 0,
                "history": []
            }

        file_reg = self.registry["formulas"][filename]

        if file_reg["current_sha256"] == sha256:
            return {
                "status": "UNCHANGED_SKIPPED",
                "filename": filename,
                "sha256": sha256
            }

        archive_filename = f"{date_prefix}_{sha256[:10]}_{filename}"
        archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
        shutil.copy2(filepath, archive_path)

        version_entry = {
            "version_id": f"v-{date_prefix}-{sha256[:6]}",
            "sha256": sha256,
            "archived_at": timestamp_iso,
            "archive_path": archive_path,
            "size_bytes": size_bytes
        }

        file_reg["current_sha256"] = sha256
        file_reg["versions_count"] += 1
        file_reg["history"].append(version_entry)
        self.registry["active_formula_sha256"] = sha256
        self.registry["total_ingested_versions"] += 1
        self.save_registry()

        self.log_provenance_event("PRICING_FORMULA_INGESTED", {
            "action": "ARCHIVE_PRICING_FORMULA",
            "filename": filename,
            "sha256": sha256,
            "archive_path": archive_path,
            "version_id": version_entry["version_id"]
        })

        return {
            "status": "NEW_VERSION_ARCHIVED",
            "filename": filename,
            "sha256": sha256,
            "archive_path": archive_path,
            "version_id": version_entry["version_id"]
        }

    def process_all_formulas(self) -> List[Dict[str, Any]]:
        results = []
        if os.path.isfile(FORMULA_CONFIG_PATH):
            res = self.archive_formula_file(FORMULA_CONFIG_PATH)
            results.append(res)

        if os.path.isdir(RAW_FORMULAS_DIR):
            for fname in os.listdir(RAW_FORMULAS_DIR):
                if fname.endswith(('.yaml', '.yml', '.json')):
                    fpath = os.path.join(RAW_FORMULAS_DIR, fname)
                    res = self.archive_formula_file(fpath)
                    results.append(res)
        return results

if __name__ == "__main__":
    archiver = PricingFormulaArchiver()
    res = archiver.process_all_formulas()
    print(json.dumps(res, ensure_ascii=False, indent=2))
