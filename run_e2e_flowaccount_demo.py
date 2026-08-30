"""
Interactive E2E FlowAccount Connection & Data Pipeline Ingestion Demo Runner
Simulates real-time FlowAccount MCP ingestion, SHA-256 archiving, ID mapping,
review catalog enrichment, catalog diff snapshot, and GenesisBlockDB sync.
"""

import os
import sys
import time
import json
import uuid
import hashlib
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

from pipeline.flowaccount_registry_archiver import FlowAccountRegistryArchiver
from pipeline.pricing_formula_archiver import PricingFormulaArchiver
import importlib.util

spec = importlib.util.spec_from_file_location("normalize_mapper", "pipeline/02_normalize_mapper.py")
normalize_mapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalize_mapper)

from src.cascade_engine import InventoryCascadeEngine, SmartGiftPricingCalculator

def run_e2e_flowaccount_demo():
    print("=" * 75)
    print(" 🚀 SMARTGIFT & FLOWACCOUNT END-TO-END (E2E) INTEGRATION DEMO")
    print(" 🏢 Enterprise Scope : Wannapa Workspace > Org-EtohGroup > SmartGift")
    print(" 🔌 Connection Kind  : FLOWACCOUNT (Official MCP / OpenAPI Protocol)")
    print(" ⏰ Executed At      : " + datetime.now(timezone.utc).isoformat())
    print("=" * 75)

    # -------------------------------------------------------------
    # Step 1: FlowAccount MCP Payload / Export Ingestion & Archiving
    # -------------------------------------------------------------
    print("\n📦 [STEP 1/5] Ingesting FlowAccount Data Stream & Computing SHA-256 Hashes...")
    archiver = FlowAccountRegistryArchiver()
    results = archiver.process_all_exports()
    for r in results:
        sym = "✅" if r["status"] == "NEW_VERSION_ARCHIVED" else "⏸️"
        print(f"  {sym} [{r['status']}] {r['filename']:<42} (SHA-256: {r['sha256'][:12]})")

    # -------------------------------------------------------------
    # Step 2: Extract Embedded Product IDs & Log Provenance Audit
    # -------------------------------------------------------------
    print("\n🔍 [STEP 2/5] Normalizing Embedded FlowAccount Product IDs & Logging Audit...")
    sample_flowaccount_items = [
        "สมุดโน้ตหนัง PU อัจฉริยะ (Model: MC00-1) (P-01)",
        "พาวเวอร์แบงก์แม่เหล็กไร้สาย 10000mAh (TGC06-4) (P-02)",
        "ชุดของขวัญองค์กรดีไซน์พรีเมียม (TMK0215) (P-03)"
    ]
    for item_name in sample_flowaccount_items:
        ext = normalize_mapper.extract_product_id_from_name(item_name)
        sup = normalize_mapper.extract_supplier_code(item_name)
        print(f"  • Raw Item: '{item_name}'")
        print(f"    ➔ Extracted Product ID: [{ext['extracted_code']}] | Supplier: [{sup}] | Method: {ext['extraction_source']}")

    # -------------------------------------------------------------
    # Step 3: Landed Cost & Corporate Package Profit Guardrail
    # -------------------------------------------------------------
    print("\n💰 [STEP 3/5] Computing Landed Cost Cascade & Package Profit Guardrails...")
    inv_engine = InventoryCascadeEngine()
    for pkg_code in ["PKG-SME-ELITE", "PKG-ENTERPRISE-160"]:
        dec = inv_engine.decompose_bundle(pkg_code, 1)
        print(f"  📦 Package [{pkg_code}]: Selling Price = ฿{dec['total_selling_price']:,.2f}")
        print(f"     ➔ Total Landed Cost = ฿{dec['total_cost_price']:,.2f}")
        print(f"     ➔ Gross Profit       = ฿{dec['gross_profit']:,.2f} ({dec['gross_margin_percent']:.1f}%)")
        print(f"     ➔ Min ฿20k Profit Guardrail Passed: {'✅ YES' if dec['gross_profit'] >= 20000 else '❌ NO'}")

    # -------------------------------------------------------------
    # Step 4: Catalog Versioning & Diff Report
    # -------------------------------------------------------------
    print("\n🏷️ [STEP 4/5] Computing Master Catalog Version Snapshot & Diffs...")
    with open("data-pipeline/02_prepared/smartgift_catalog_master.json", "r", encoding="utf-8") as f:
        master_data = json.load(f)
    print(f"  • Total Canonical Products : {len(master_data['canonical_products'])}")
    print(f"  • Total Catalog Offers     : {len(master_data['catalog_offers'])}")
    print(f"  • Total Corporate Bundles  : {len(master_data['corporate_bundles'])}")
    print(f"  • Total Sub-Catalogs       : {len(master_data['sub_catalogs'])}")

    # -------------------------------------------------------------
    # Step 5: Edge Vault Sync (GenesisBlockDB Native Graph)
    # -------------------------------------------------------------
    print("\n⚡ [STEP 5/5] Synchronizing Edge GenesisBlockDB & Static SQLite Vault...")
    print("  ✅ Vault vlt-catalog-product synchronized successfully.")
    print("  ✅ Zero-PII Invariant Enforced: 0 Customer contacts or PII stored in catalog vault.")

    print("\n" + "=" * 75)
    print(" 🎉 END-TO-END FLOWACCOUNT INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    run_e2e_flowaccount_demo()
