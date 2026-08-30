"""
Unit tests for pipeline/generate_product_manifest.py
Verifies catalog integrity hashing, multi-file category slicing, and image asset mapping.
"""

import os
import json
import unittest
from pipeline.generate_product_manifest import ProductManifestGenerator, PUBLIC_MANIFEST_PATH, CATEGORIES_DIR

class TestProductManifestGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ProductManifestGenerator()

    def test_generate_manifest_output(self):
        manifest = self.generator.generate_manifest()
        
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.get("schema_version"), "1.3.0")
        self.assertEqual(manifest.get("tenant_id"), "Org-EtohGroup")
        self.assertEqual(manifest.get("business_id"), "SmartGift")
        self.assertIn("catalog_version", manifest)
        
        # Public manifest carries only customer-safe artifact hashes with
        # endpoint-style paths (ADR-004: no internal source path/hash on the
        # public surface)
        hashes = manifest.get("data_integrity_hashes", {})
        self.assertEqual(set(hashes.keys()), {"pricelist_public", "catalog_media"})
        for entry in hashes.values():
            self.assertTrue(entry["path"].startswith("/data/"))
            self.assertNotIn("data-pipeline", entry["path"])
            self.assertTrue(len(entry["sha256"]) > 0)

        # Full source lineage lives only in the internal audit hashes
        internal = self.generator.compute_internal_integrity_hashes()
        self.assertIn("smartgift_catalog_master", internal)
        self.assertIn("factory_costs", internal)
        self.assertTrue(len(internal["smartgift_catalog_master"]["sha256"]) > 0)

        # Check Multi-file index
        slices = manifest.get("multi_file_index", [])
        self.assertGreater(len(slices), 0)
        for s in slices:
            self.assertTrue(os.path.exists(f"public{s['endpoint_url']}"))

        # Check Image Index
        img_index = manifest.get("product_image_index", {})
        self.assertGreater(len(img_index), 0)
        for code, info in img_index.items():
            self.assertIn("image_url", info)
            self.assertIn("visual_status", info)

        # Verify output file exists
        self.assertTrue(os.path.exists(PUBLIC_MANIFEST_PATH))

    def test_category_slices_exclude_forbidden_fields(self):
        self.generator.generate_manifest()
        forbidden_keys = {"logistics_freight_est", "packaging_carton", "product_master"}
        for fname in os.listdir(CATEGORIES_DIR):
            if not fname.endswith(".json"):
                continue
            with open(os.path.join(CATEGORIES_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            for product in data.get("products", []):
                leaked = forbidden_keys & set(product.keys())
                self.assertFalse(leaked, f"{fname}: forbidden fields {leaked} in {product.get('code')}")

    def test_public_boundary_scan_passes(self):
        self.generator.generate_manifest()
        # generate_manifest raises SystemExit(1) on violation; reaching here means pass.
        self.generator.verify_public_boundary()

if __name__ == "__main__":
    unittest.main()
