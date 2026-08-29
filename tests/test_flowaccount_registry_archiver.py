"""
Unit tests for FlowAccount Registry & Archiver Engine
"""

import unittest
import os
import tempfile
from pipeline.flowaccount_registry_archiver import FlowAccountRegistryArchiver, compute_file_sha256

class TestFlowAccountRegistryArchiver(unittest.TestCase):
    def setUp(self):
        self.archiver = FlowAccountRegistryArchiver()

    def test_sha256_computation(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("test_content_123")
            temp_path = f.name
        
        try:
            h1 = compute_file_sha256(temp_path)
            self.assertEqual(len(h1), 64)
        finally:
            os.remove(temp_path)

    def test_registry_loaded(self):
        self.assertIn("tenant_id", self.archiver.registry)
        self.assertEqual(self.archiver.registry["tenant_id"], "Org-EtohGroup")
        self.assertIn("files", self.archiver.registry)

    def test_duplicate_file_detection(self):
        # Processing an existing file should return UNCHANGED_DUPLICATE_SKIPPED
        res = self.archiver.process_export_file("บริษัท เทราบิส จำกัด_product.xlsx")
        self.assertEqual(res["status"], "UNCHANGED_DUPLICATE_SKIPPED")

if __name__ == "__main__":
    unittest.main()
