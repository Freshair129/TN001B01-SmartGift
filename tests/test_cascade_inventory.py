"""
Unit tests for SmartGift Cascade Waterfall Inventory Engine
"""

import unittest
import os
import sys

# Ensure parent directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from inventory_cascade_engine import InventoryCascadeEngine

class TestInventoryCascade(unittest.TestCase):
    def setUp(self):
        self.engine = InventoryCascadeEngine()

    def test_catalog_loaded(self):
        self.assertGreater(len(self.engine.products), 0)
        self.assertGreater(len(self.engine.offers), 0)
        self.assertGreater(len(self.engine.bundles), 0)

    def test_decompose_set(self):
        # TDD03-2 should decompose into components
        comps = self.engine.decompose_set("TDD03-2", set_quantity=5)
        self.assertGreater(len(comps), 0)
        for c in comps:
            self.assertEqual(c["total_qty_needed"], c["unit_qty_per_set"] * 5)
            self.assertGreater(c["total_cost"], 0)

    def test_decompose_bundle(self):
        bundle_res = self.engine.decompose_bundle("PKG-SME-ELITE", bundle_quantity=1)
        self.assertEqual(bundle_res["bundle_code"], "PKG-SME-ELITE")
        self.assertEqual(bundle_res["total_selling_price"], 46250.00)
        self.assertGreater(bundle_res["total_cost_price"], 0)
        self.assertGreater(bundle_res["gross_profit"], 0)
        self.assertGreater(bundle_res["gross_margin_percent"], 0)
        self.assertTrue(bundle_res["is_fulfillable"])
        self.assertGreater(len(bundle_res["physical_sku_deductions"]), 0)

    def test_order_deduction_execution(self):
        initial_stock = dict(self.engine.inventory)
        result = self.engine.execute_order_deduction("PKG-SME-ELITE", 1)
        self.assertEqual(result["order_status"], "CONFIRMED_AND_DEDUCTED")

        # Verify inventory has decreased by exact required units
        for sku_data in result["physical_sku_deductions"]:
            pcode = sku_data["product_code"]
            required = sku_data["total_units_required"]
            self.assertEqual(self.engine.inventory[pcode], initial_stock[pcode] - required)

if __name__ == "__main__":
    unittest.main()
