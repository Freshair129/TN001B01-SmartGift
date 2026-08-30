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
        
        # Check Integrity Hashes
        hashes = manifest.get("data_integrity_hashes", {})
        self.assertIn("smartgift_catalog_master", hashes)
        self.assertTrue(len(hashes["smartgift_catalog_master"]["sha256"]) > 0)

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

if __name__ == "__main__":
    unittest.main()
