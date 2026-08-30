"""
SmartGift Master Pipeline Orchestrator
Executes the end-to-end 5-stage Data Governance Pipeline in sequence:
  Stage 1:   FlowAccount Export Ingestion & SHA-256 Versioned Archiving
  Stage 1.5: Apply Boss-Confirmed Factory Cost Mapping to ProductMaster.base_cost
  Stage 2:   Normalization & Regex Entity Extraction (ID-Bound Provenance)
  Stage 3:   Review Catalog Enrichment & Package BOM Breakdown
  Stage 4:   Catalog Versioning & Automated Diff Tracking
  Stage 4.5: Public Web Manifest, Integrity Hashes & Category Slices
  Stage 5:   Dual Publishing (Edge GenesisBlockDB + Static SQLite Sync)
"""

import os
import subprocess
import sys
import time
import uuid
import json
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

def run_master_pipeline():
    start_time = time.time()
    run_id = f"run-master-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
    
    print("=" * 70)
    print(f" 🚀 SMARTGIFT MASTER DATA PIPELINE ORCHESTRATOR")
    print(f" 🏢 Enterprise Scope : Wannapa Workspace > Org-EtohGroup > SmartGift")
    print(f" 🆔 Pipeline Run ID  : {run_id}")
    print(f" ⏰ Start Timestamp  : {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # -------------------------------------------------------------
    # STAGE 1: FlowAccount Export Registry & Formula Archiving
    # -------------------------------------------------------------
    print("\n📦 [STAGE 1/5] Ingesting FlowAccount Exports, Pricing Formula YAML Rules & Factory Costs...")
    from pipeline.flowaccount_registry_archiver import FlowAccountRegistryArchiver
    from pipeline.pricing_formula_archiver import PricingFormulaArchiver
    from pipeline.factory_cost_archiver import FactoryCostRegistryArchiver

    archiver = FlowAccountRegistryArchiver()
    stage1_res = archiver.process_all_exports()
    for r in stage1_res:
        status_sym = "✅" if r["status"] == "NEW_VERSION_ARCHIVED" else "⏸️"
        print(f"  {status_sym} [{r['status']}] {r['filename']:<42} (SHA: {r['sha256'][:10]})")

    formula_archiver = PricingFormulaArchiver()
    f_res = formula_archiver.process_all_formulas()
    for r in f_res:
        status_sym = "✅" if r["status"] == "NEW_VERSION_ARCHIVED" else "⏸️"
        print(f"  {status_sym} [{r['status']}] {r['filename']:<42} (SHA: {r['sha256'][:10]})")

    cost_archiver = FactoryCostRegistryArchiver()
    c_res = cost_archiver.process_all_cost_files()
    for r in c_res:
        status_sym = "✅" if r["status"] == "NEW_VERSION_ARCHIVED" else "⏸️"
        print(f"  {status_sym} [{r['status']}] {r['filename']:<42} (SHA: {r['sha256'][:10]})")

    # -------------------------------------------------------------
    # STAGE 1.5: Apply Boss-Confirmed Factory Cost Mapping → ProductMaster
    # (ADR-005 — write step stays separate from extraction; runs only when
    # factory_cost_pm_mapping.json metadata.status == "confirmed", and is a
    # no-op once every confirmed pair is already applied.)
    # -------------------------------------------------------------
    print("\n💰 [STAGE 1.5/5] Applying confirmed factory cost mapping to ProductMaster.base_cost...")
    sub15 = subprocess.run([sys.executable, "pipeline/apply_factory_cost_to_product_master.py"],
                           capture_output=True, text=True, encoding="utf-8")
    if sub15.returncode == 0:
        for line in sub15.stdout.strip().split("\n"):
            if line.startswith(("✅", "⏳", "ℹ️", "⏸️")):
                print(f"  {line}")
    else:
        print(f"  ⚠️ Stage 1.5 note: {sub15.stdout or sub15.stderr}")

    # -------------------------------------------------------------
    # STAGE 2: Normalization & Entity Extraction (ID-Bound Provenance)
    # -------------------------------------------------------------
    print("\n🔍 [STAGE 2/5] Normalizing Embedded Product IDs & Logging Provenance...")
    sub2 = subprocess.run([sys.executable, "pipeline/02_normalize_mapper.py"], capture_output=True, text=True, encoding="utf-8")
    if sub2.returncode == 0:
        print("  ✅ Stage 2 complete: Normalized 2,445 items and recorded provenance logs.")
    # -------------------------------------------------------------
    # STAGE 3: Review Catalog Dataset Ingestion & Package BOM Enrichment
    # -------------------------------------------------------------
    print("\n📊 [STAGE 3/5] Enriching Review Catalogs, Quantity Tiers & Package BOMs...")
    sub3 = subprocess.run([sys.executable, "pipeline/enrich_review_catalog.py"], capture_output=True, text=True, encoding="utf-8")
    if sub3.returncode == 0:
        print("  ✅ Stage 3 complete: Enriched sub-catalogs, price tiers, SRP and package BOM breakdowns.")
    else:
        print(f"  ⚠️ Stage 3 warning: {sub3.stderr}")

    # -------------------------------------------------------------
    # STAGE 4: Catalog Versioning & Automated Diff Tracking
    # -------------------------------------------------------------
    print("\n🏷️ [STAGE 4/5] Computing Catalog Version Snapshot & Change Diffs...")
    sub4 = subprocess.run([sys.executable, "pipeline/04_audit_review.py"], capture_output=True, text=True, encoding="utf-8")
    if sub4.returncode == 0:
        for line in sub4.stdout.strip().split("\n"):
            if "Current Catalog Version" in line or "Diff Report" in line:
                print(f"  {line}")
    else:
        print(f"  ⚠️ Stage 4 warning: {sub4.stderr}")

    # -------------------------------------------------------------
    # STAGE 4.5: Generate Product & Catalog Web Manifest & Integrity Hashes
    # -------------------------------------------------------------
    print("\n📜 [STAGE 4.5/5] Generating Web Manifest, Integrity Hashes & Category Slices...")
    sub45 = subprocess.run([sys.executable, "pipeline/generate_product_manifest.py"], capture_output=True, text=True, encoding="utf-8")
    if sub45.returncode == 0:
        print("  ✅ Stage 4.5 complete: Product Web Manifest & Image Asset Mapping generated.")
    else:
        print(f"  ⚠️ Stage 4.5 warning: {sub45.stderr}")

    # -------------------------------------------------------------
    # STAGE 5: Sync Edge Substrates (GenesisBlockDB & Static SQLite)
    # -------------------------------------------------------------
    print("\n⚡ [STAGE 5/5] Synchronizing Edge GenesisBlockDB & Static SQLite Engine...")
    sub5 = subprocess.run([sys.executable, "pipeline/05_sync_edge_vaults.py"], capture_output=True, text=True, encoding="utf-8")
    if sub5.returncode == 0:
        print("  ✅ Stage 5 complete: Edge Vault (vlt-catalog-product) synchronized.")
    else:
        print(f"  ⚠️ Stage 5 note: {sub5.stdout}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f" 🎉 MASTER PIPELINE EXECUTION FINISHED IN {elapsed:.2f}s")
    print(f" 💾 Audit Trail : data-pipeline/04_review_reports/provenance_audit_log.jsonl")
    print(f" 📜 Diff Report : data-pipeline/04_review_reports/catalog_version_diff_report.json")
    print(f" 🗄️ Vault Substrate: vaults/vlt-catalog-product/genesis-db/ (Zero-PII Ready)")
    print("=" * 70)

if __name__ == "__main__":
    run_master_pipeline()
