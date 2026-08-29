"""
SmartGift Catalog Versioning & Diff Tracking Engine
Compares current catalog snapshot with incoming/previous versions,
identifies ADDED, REMOVED, PRICE_MODIFIED, and BOM_DRIFT items,
and records immutable catalog_version manifests with SHA-256 snapshots.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

sys.stdout.reconfigure(encoding='utf-8')

MASTER_CATALOG_PATH = "data-pipeline/02_prepared/smartgift_catalog_master.json"
DIFF_REPORT_PATH = "data-pipeline/04_review_reports/catalog_version_diff_report.json"
VERSION_HISTORY_DIR = "data-pipeline/04_review_reports/version_snapshots"

def compute_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def compute_content_sha256(data: Any) -> str:
    canonical_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

class CatalogVersioningEngine:
    def __init__(self, master_path: str = MASTER_CATALOG_PATH):
        self.master_path = master_path
        os.makedirs(VERSION_HISTORY_DIR, exist_ok=True)
        self.load_current_catalog()

    def load_current_catalog(self):
        if not os.path.exists(self.master_path):
            raise FileNotFoundError(f"Master catalog missing: {self.master_path}")
        with open(self.master_path, "r", encoding="utf-8") as f:
            self.current_data = json.load(f)

    def generate_version_snapshot(self, version_label: str = None) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        snapshot_hash = compute_content_sha256(self.current_data)
        
        if not version_label:
            # Auto-generate semantic version based on date
            date_tag = datetime.now(timezone.utc).strftime("%Y.%m.%d")
            version_label = f"catalog-v{date_tag}-{snapshot_hash[:8]}"

        snapshot_manifest = {
            "catalog_version": version_label,
            "tenant_id": "Org-EtohGroup",
            "business_id": "SmartGift",
            "vault_id": "vlt-catalog-product",
            "snapshot_sha256": snapshot_hash,
            "created_at": timestamp,
            "summary": {
                "total_categories": len(self.current_data.get("top_level_categories", [])),
                "total_canonical_products": len(self.current_data.get("canonical_products", [])),
                "total_catalog_offers": len(self.current_data.get("catalog_offers", [])),
                "total_corporate_bundles": len(self.current_data.get("corporate_bundles", []))
            },
            "offers_index": {
                o["offer_code"]: {
                    "name": o["name"],
                    "gift_tier": o.get("gift_tier", ""),
                    "price_tiers": o.get("price_tiers", []),
                    "components": o.get("components", []),
                    "supplier_code": o.get("supplier_code", "P-00")
                }
                for o in self.current_data.get("catalog_offers", [])
            }
        }

        # Save snapshot
        snapshot_filename = f"{version_label}.json"
        snapshot_filepath = os.path.join(VERSION_HISTORY_DIR, snapshot_filename)
        with open(snapshot_filepath, "w", encoding="utf-8") as f:
            json.dump(snapshot_manifest, f, ensure_ascii=False, indent=2)

        return snapshot_manifest

    def compare_with_previous_snapshot(self, previous_snapshot_path: str = None) -> Dict[str, Any]:
        """Compares current catalog against the latest historical snapshot to compute diffs"""
        snapshots = sorted([
            os.path.join(VERSION_HISTORY_DIR, f)
            for f in os.listdir(VERSION_HISTORY_DIR)
            if f.endswith(".json")
        ])

        if not snapshots and not previous_snapshot_path:
            # First run, generate initial snapshot
            current_snap = self.generate_version_snapshot()
            diff_report = {
                "status": "INITIAL_VERSION_ESTABLISHED",
                "current_version": current_snap["catalog_version"],
                "previous_version": None,
                "diff_summary": {
                    "total_offers": current_snap["summary"]["total_catalog_offers"],
                    "added_offers_count": current_snap["summary"]["total_catalog_offers"],
                    "removed_offers_count": 0,
                    "price_changed_count": 0,
                    "bom_drift_count": 0
                },
                "details": {
                    "added": list(current_snap["offers_index"].keys())[:20],
                    "removed": [],
                    "price_changes": [],
                    "bom_changes": []
                }
            }
            with open(DIFF_REPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(diff_report, f, ensure_ascii=False, indent=2)
            return diff_report

        prev_path = previous_snapshot_path if previous_snapshot_path else snapshots[-1]
        with open(prev_path, "r", encoding="utf-8") as f:
            prev_snap = json.load(f)

        current_snap = self.generate_version_snapshot()

        prev_offers = prev_snap.get("offers_index", {})
        curr_offers = current_snap.get("offers_index", {})

        added = []
        removed = []
        price_changes = []
        bom_changes = []

        for code, offer in curr_offers.items():
            if code not in prev_offers:
                added.append({"offer_code": code, "name": offer["name"]})
            else:
                prev_off = prev_offers[code]
                # Check price diff
                if offer["price_tiers"] != prev_off["price_tiers"]:
                    price_changes.append({
                        "offer_code": code,
                        "old_price_tiers": prev_off["price_tiers"],
                        "new_price_tiers": offer["price_tiers"]
                    })
                # Check BOM diff
                if offer["components"] != prev_off["components"]:
                    bom_changes.append({
                        "offer_code": code,
                        "old_components": prev_off["components"],
                        "new_components": offer["components"]
                    })

        for code in prev_offers:
            if code not in curr_offers:
                removed.append({"offer_code": code, "name": prev_offers[code]["name"]})

        diff_report = {
            "current_version": current_snap["catalog_version"],
            "previous_version": prev_snap["catalog_version"],
            "has_changes": bool(added or removed or price_changes or bom_changes),
            "diff_summary": {
                "added_offers_count": len(added),
                "removed_offers_count": len(removed),
                "price_changed_count": len(price_changes),
                "bom_drift_count": len(bom_changes)
            },
            "details": {
                "added": added,
                "removed": removed,
                "price_changes": price_changes,
                "bom_changes": bom_changes
            }
        }

        with open(DIFF_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(diff_report, f, ensure_ascii=False, indent=2)

        return diff_report


def main():
    print("==================================================================")
    print(" 🏷️ SmartGift Catalog Versioning & Diff Tracking Engine")
    print("==================================================================")

    engine = CatalogVersioningEngine()
    diff_report = engine.compare_with_previous_snapshot()

    print(f"✅ Current Catalog Version : {diff_report.get('current_version')}")
    print(f"📊 Previous Catalog Version: {diff_report.get('previous_version') or 'None (Baseline Initialized)'}")
    print(f"🔍 Added Offers            : {diff_report['diff_summary']['added_offers_count']}")
    print(f"🔍 Price Changes Detected  : {diff_report['diff_summary']['price_changed_count']}")
    print(f"🔍 BOM Drifts Detected     : {diff_report['diff_summary']['bom_drift_count']}")
    print(f"💾 Diff Report saved to    : '{DIFF_REPORT_PATH}'")

if __name__ == "__main__":
    main()
