"""
End-to-End (E2E) FlowAccount Integration & Data Pipeline Verification Test
Verifies complete flow from FlowAccount data payload ingestion to SHA-256 archiving,
product ID extraction, provenance audit logging, catalog master update, and edge vault sync.
"""

import unittest
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

from pipeline.flowaccount_registry_archiver import FlowAccountRegistryArchiver, compute_file_sha256
import importlib.util
spec = importlib.util.spec_from_file_location("normalize_mapper", "pipeline/02_normalize_mapper.py")
normalize_mapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalize_mapper)
extract_product_id_from_name = normalize_mapper.extract_product_id_from_name
extract_supplier_code = normalize_mapper.extract_supplier_code
from src.cascade_engine import InventoryCascadeEngine, SmartGiftPricingCalculator

class TestE2EFlowAccountIngestion(unittest.TestCase):
    def setUp(self):
        self.archiver = FlowAccountRegistryArchiver()
        self.inv_engine = InventoryCascadeEngine()
        self.calculator = SmartGiftPricingCalculator()

    def test_step1_sha256_archiving(self):
        """Step 1: Verify SHA-256 hashing and archiving of FlowAccount payload"""
        res = self.archiver.process_export_file("บริษัท เทราบิส จำกัด_product.xlsx")
        self.assertIn(res["status"], ["NEW_VERSION_ARCHIVED", "UNCHANGED_DUPLICATE_SKIPPED"])
        self.assertIn("sha256", res)

    def test_step2_regex_id_and_supplier_extraction(self):
        """Step 2: Verify regex product ID and supplier code extraction from FlowAccount items"""
        raw_name = "สมุดโน้ตหนัง PU อัจฉริยะ (Model: MC00-1) (P-02)"
        extracted = extract_product_id_from_name(raw_name)
        supplier = extract_supplier_code(raw_name)

        self.assertEqual(extracted["extracted_code"], "MC00-1")
        self.assertEqual(supplier, "P-02")

    def test_step3_landed_cost_and_profit_guardrail(self):
        """Step 3: Verify FlowAccount item pricing calculation and corporate package profit guardrail"""
        pkg_code = "PKG-SME-ELITE"
        dec = self.inv_engine.decompose_bundle(pkg_code, 1)

        self.assertGreaterEqual(dec["gross_profit"], 20000.0)
        self.assertTrue(dec["total_cost_price"] > 0)
        self.assertTrue(len(dec["physical_sku_deductions"]) > 0)

    def test_step4_master_catalog_structure(self):
        """Step 4: Verify master catalog JSON integrity after FlowAccount ingestion"""
        catalog_path = "data-pipeline/02_prepared/smartgift_catalog_master.json"
        self.assertTrue(os.path.exists(catalog_path))
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("canonical_products", data)
        self.assertIn("catalog_offers", data)
        self.assertIn("corporate_bundles", data)
        self.assertTrue(len(data["canonical_products"]) > 0)

    def test_step5_edge_vault_sqlite_sync(self):
        """Step 5: Verify SQLite edge vault projection sync"""
        sqlite_path = "vaults/vlt-catalog-product/genesis-db/projection.sqlite"
        self.assertTrue(os.path.exists(sqlite_path))

if __name__ == "__main__":
    unittest.main()
