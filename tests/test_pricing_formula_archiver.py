"""
Unit tests for Pricing Rules Formula Archiver Engine
"""

import unittest
import os
import tempfile
from pipeline.pricing_formula_archiver import PricingFormulaArchiver, compute_file_sha256

class TestPricingFormulaArchiver(unittest.TestCase):
    def setUp(self):
        self.archiver = PricingFormulaArchiver()

    def test_sha256_computation(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("currency_fx:\n  cny_to_thb: 5.0\n")
            temp_path = f.name
        try:
            h1 = compute_file_sha256(temp_path)
            self.assertEqual(len(h1), 64)
        finally:
            os.remove(temp_path)

    def test_registry_loaded(self):
        self.assertIn("tenant_id", self.archiver.registry)
        self.assertEqual(self.archiver.registry["tenant_id"], "Org-EtohGroup")
        self.assertIn("formulas", self.archiver.registry)

    def test_formula_archiving(self):
        res = self.archiver.process_all_formulas()
        self.assertTrue(len(res) > 0)
        self.assertIn("status", res[0])

if __name__ == "__main__":
    unittest.main()
