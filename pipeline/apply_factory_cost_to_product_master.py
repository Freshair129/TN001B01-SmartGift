"""
Apply Confirmed Factory Cost Mapping → ProductMaster.base_cost
(ADR-005 §Decision 4 — extraction stays separate from writing cost; this is
that write step, gated on human confirmation.)

Reads data-pipeline/02_prepared/factory_cost_pm_mapping.json and, ONLY if its
metadata.status == "confirmed" (Boss-approved), writes each confirmed pair's
EXW cost (THB) into the matching record's base_cost in
data-pipeline/02_prepared/ProductMaster.json — in place, idempotent, with
full provenance kept per record.

Invariants respected:
  - base_cost carries EXW-only cost (see mapping metadata.cost_basis_note);
    it is NOT landed cost — freight/duty/logo still apply via
    pricing_rules_formula.yaml at quote time. Every touched record's
    factory_provenance repeats this note so no downstream reader mistakes
    base_cost for a finished landed cost.
  - Records with no confirmed pair are left untouched (base_cost stays null,
    factory_match_status stays "missing_factory_match") — this script never
    guesses a cost.
  - contract_validation is recomputed against the schema's required-field
    list, but "promoted" always stays False: cost being present is not a
    canonical-promotion decision, which remains a separate governance step.
  - Fails closed (raises, writes nothing) if the mapping file is missing,
    unparseable, or not status=="confirmed".

Usage: python pipeline/apply_factory_cost_to_product_master.py
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

PRODUCT_MASTER_PATH = "data-pipeline/02_prepared/ProductMaster.json"
COST_MAPPING_PATH = "data-pipeline/02_prepared/factory_cost_pm_mapping.json"
REPORT_PATH = "data-pipeline/04_review_reports/product_master_cost_apply_report.json"

# ProductMaster required properties per config/schema_genesisblock.yaml —
# kept as a literal list here (not re-parsed from YAML) so this script has
# no dependency beyond the two JSON files it is documented to touch.
REQUIRED_FIELDS = ("code", "name_th", "name_en", "category", "base_cost")


def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def recompute_contract_validation(record):
    missing = [f for f in REQUIRED_FIELDS if record.get(f) is None or record.get(f) == ""]
    record["contract_validation"] = {
        "status": "incomplete" if missing else "required_fields_present",
        "missing_fields": missing,
        # Promotion is a separate, human-reviewed governance gate — filling
        # base_cost here must never flip it.
        "promoted": record.get("contract_validation", {}).get("promoted", False),
    }
    return record


def apply_cost_mapping(product_master, mapping_doc, mapping_sha256):
    meta = mapping_doc.get("metadata", {})
    if meta.get("status") != "confirmed":
        raise SystemExit(
            f"⛔ REFUSING TO APPLY: {COST_MAPPING_PATH} metadata.status is "
            f"'{meta.get('status')}', not 'confirmed'. Cost stays out of "
            f"ProductMaster until a human confirms the mapping (ADR-005)."
        )

    mapping_by_code = {row["pm_code"]: row for row in mapping_doc.get("mapping", [])}
    applied, already_applied, unmatched = [], [], []
    now = datetime.now(timezone.utc).isoformat()

    for record in product_master.get("records", []):
        code = record.get("code")
        row = mapping_by_code.get(code)
        if row is None:
            if record.get("base_cost") is None:
                unmatched.append(code)
            continue

        exw_cost_thb = round(row["exw_cost_thb"], 2)
        if record.get("base_cost") == exw_cost_thb and (record.get("factory_provenance") or {}).get(
            "mapping_source_sha256"
        ) == mapping_sha256:
            already_applied.append(code)
            continue

        record["base_cost"] = exw_cost_thb
        record["factory_match_status"] = "confirmed_supplier_mapping"
        record["factory_product_code"] = row.get("factory_item_code")
        # Established convention (pipeline/export_pricelist_master.py): this
        # field only carries a value when the source quote was itself in RMB.
        record["factory_unit_cny"] = row["exw_price"] if row.get("currency") == "RMB" else None
        record["factory_provenance"] = {
            "kind": "confirmed_factory_cost_pm_mapping",
            "factory_item_code": row.get("factory_item_code"),
            "factory_item_name": row.get("factory_item_name"),
            "price_basis": row.get("price_basis"),
            "cost_basis_note": meta.get("cost_basis_note"),
            "exw_price": row.get("exw_price"),
            "currency": row.get("currency"),
            "fx_rate_to_thb": row.get("fx_rate_to_thb"),
            "exw_cost_thb": exw_cost_thb,
            "confidence": row.get("confidence"),
            "note": row.get("note"),
            "source_file": row.get("source_file"),
            "source_sha256": row.get("source_sha256"),
            "mapping_confirmed_by": meta.get("confirmed_by"),
            "mapping_confirmed_at": meta.get("confirmed_at"),
            "mapping_source_file": COST_MAPPING_PATH,
            "mapping_source_sha256": mapping_sha256,
            "applied_at": now,
        }
        recompute_contract_validation(record)
        applied.append(code)

    return applied, already_applied, unmatched


def main():
    print("🔨 Applying confirmed factory cost mapping to ProductMaster.base_cost…")
    if not os.path.exists(COST_MAPPING_PATH):
        raise SystemExit(f"⛔ {COST_MAPPING_PATH} not found — nothing to apply.")
    if not os.path.exists(PRODUCT_MASTER_PATH):
        raise SystemExit(f"⛔ {PRODUCT_MASTER_PATH} not found.")

    mapping_sha256 = sha256_of(COST_MAPPING_PATH)
    mapping_doc = load_json(COST_MAPPING_PATH)
    product_master = load_json(PRODUCT_MASTER_PATH)

    applied, already_applied, unmatched = apply_cost_mapping(product_master, mapping_doc, mapping_sha256)

    if applied:
        with open(PRODUCT_MASTER_PATH, "w", encoding="utf-8") as f:
            json.dump(product_master, f, ensure_ascii=False, indent=2)
        print(f"✅ base_cost applied to {len(applied)} record(s): {', '.join(sorted(applied))}")
    else:
        print("ℹ️ No records needed updating (already applied or nothing new confirmed).")

    if already_applied:
        print(f"⏸️ Already up to date: {', '.join(sorted(already_applied))}")
    if unmatched:
        reason = mapping_doc.get("metadata", {}).get("unmatched_reason", "")
        print(f"⏳ Still missing_factory_match ({len(unmatched)}): {', '.join(sorted(unmatched))}")
        if reason:
            print(f"   reason on file: {reason}")

    report = {
        "artifact": "product_master_cost_apply_report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product_master_path": PRODUCT_MASTER_PATH,
        "mapping_source": {"path": COST_MAPPING_PATH, "sha256": mapping_sha256,
                            "status": mapping_doc.get("metadata", {}).get("status"),
                            "confirmed_by": mapping_doc.get("metadata", {}).get("confirmed_by"),
                            "confirmed_at": mapping_doc.get("metadata", {}).get("confirmed_at")},
        "applied_this_run": sorted(applied),
        "already_applied": sorted(already_applied),
        "still_missing_factory_match": sorted(unmatched),
        "unmatched_reason": mapping_doc.get("metadata", {}).get("unmatched_reason"),
        "cost_basis_note": mapping_doc.get("metadata", {}).get("cost_basis_note"),
    }
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
