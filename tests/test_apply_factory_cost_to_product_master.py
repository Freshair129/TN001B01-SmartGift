"""
Tests for pipeline/apply_factory_cost_to_product_master.py.

Covers: refuses to apply an unconfirmed mapping, applies confirmed pairs
with correct provenance and contract_validation, leaves unmatched records
untouched, and is idempotent on a second run.
"""

import copy
import json
import unittest

from pipeline.apply_factory_cost_to_product_master import (
    REQUIRED_FIELDS,
    apply_cost_mapping,
)

CONFIRMED_MAPPING = {
    "metadata": {
        "status": "confirmed",
        "confirmed_by": "Boss",
        "confirmed_at": "2026-08-30",
        "cost_basis_note": "EXW ต่อหน่วย ยังไม่รวม freight/duty",
        "unmatched_pm": ["PM-NOCOST"],
        "unmatched_reason": "no single-item quote on file",
    },
    "mapping": [
        {
            "pm_code": "PM-MSG", "factory_item_code": "TBY17-1",
            "factory_item_name": "Neck massager", "source_file": "x.xlsx",
            "source_sha256": "deadbeef", "exw_price": 3.6, "currency": "USD",
            "fx_rate_to_thb": 32.5, "exw_cost_thb": 117.0, "price_basis": "EXW",
            "confidence": "high", "note": "matches spec",
        },
        {
            "pm_code": "PM-FLASH", "factory_item_code": None,
            "factory_item_name": "USB flash", "source_file": "y.xlsx",
            "source_sha256": "cafef00d", "exw_price": 16.8, "currency": "RMB",
            "fx_rate_to_thb": 5.0, "exw_cost_thb": 84.0, "price_basis": "EXW",
            "confidence": "medium", "note": None,
        },
    ],
}

UNCONFIRMED_MAPPING = {**CONFIRMED_MAPPING, "metadata": {**CONFIRMED_MAPPING["metadata"], "status": "proposed"}}


def make_product_master():
    return {
        "records": [
            {"code": "PM-MSG", "name_th": "a", "name_en": "b", "category": "cat",
             "base_cost": None, "factory_match_status": "missing_factory_match",
             "factory_product_code": None, "factory_unit_cny": None, "factory_provenance": None,
             "contract_validation": {"status": "incomplete", "missing_fields": ["base_cost"], "promoted": False}},
            {"code": "PM-FLASH", "name_th": "c", "name_en": "d", "category": "cat",
             "base_cost": None, "factory_match_status": "missing_factory_match",
             "factory_product_code": None, "factory_unit_cny": None, "factory_provenance": None,
             "contract_validation": {"status": "incomplete", "missing_fields": ["base_cost"], "promoted": False}},
            {"code": "PM-NOCOST", "name_th": "e", "name_en": "f", "category": "cat",
             "base_cost": None, "factory_match_status": "missing_factory_match",
             "factory_product_code": None, "factory_unit_cny": None, "factory_provenance": None,
             "contract_validation": {"status": "incomplete", "missing_fields": ["base_cost"], "promoted": False}},
        ]
    }


class TestApplyFactoryCostToProductMaster(unittest.TestCase):
    def test_refuses_unconfirmed_mapping(self):
        pm = make_product_master()
        with self.assertRaises(SystemExit):
            apply_cost_mapping(pm, UNCONFIRMED_MAPPING, "somesha")
        # Nothing touched.
        self.assertIsNone(pm["records"][0]["base_cost"])

    def test_applies_confirmed_pairs_with_provenance(self):
        pm = make_product_master()
        applied, already, unmatched = apply_cost_mapping(pm, CONFIRMED_MAPPING, "mapshasum")
        self.assertEqual(set(applied), {"PM-MSG", "PM-FLASH"})
        self.assertEqual(unmatched, ["PM-NOCOST"])

        msg = next(r for r in pm["records"] if r["code"] == "PM-MSG")
        self.assertEqual(msg["base_cost"], 117.0)
        self.assertEqual(msg["factory_match_status"], "confirmed_supplier_mapping")
        self.assertEqual(msg["factory_product_code"], "TBY17-1")
        self.assertIsNone(msg["factory_unit_cny"])  # USD row -> no _cny value
        self.assertEqual(msg["factory_provenance"]["mapping_source_sha256"], "mapshasum")
        self.assertIn("EXW", msg["factory_provenance"]["cost_basis_note"])
        self.assertEqual(msg["contract_validation"],
                          {"status": "required_fields_present", "missing_fields": [], "promoted": False})

    def test_rmb_row_sets_factory_unit_cny(self):
        pm = make_product_master()
        apply_cost_mapping(pm, CONFIRMED_MAPPING, "mapshasum")
        flash = next(r for r in pm["records"] if r["code"] == "PM-FLASH")
        self.assertEqual(flash["factory_unit_cny"], 16.8)

    def test_unmatched_record_untouched(self):
        pm = make_product_master()
        apply_cost_mapping(pm, CONFIRMED_MAPPING, "mapshasum")
        nocost = next(r for r in pm["records"] if r["code"] == "PM-NOCOST")
        self.assertIsNone(nocost["base_cost"])
        self.assertEqual(nocost["factory_match_status"], "missing_factory_match")
        self.assertEqual(nocost["contract_validation"]["status"], "incomplete")

    def test_promoted_never_flips_true(self):
        pm = make_product_master()
        pm["records"][0]["contract_validation"]["promoted"] = False
        apply_cost_mapping(pm, CONFIRMED_MAPPING, "mapshasum")
        self.assertFalse(pm["records"][0]["contract_validation"]["promoted"])

    def test_idempotent_second_run_reapplies_nothing(self):
        pm = make_product_master()
        apply_cost_mapping(pm, CONFIRMED_MAPPING, "mapshasum")
        before = copy.deepcopy(pm)
        applied2, already2, unmatched2 = apply_cost_mapping(pm, CONFIRMED_MAPPING, "mapshasum")
        self.assertEqual(applied2, [])
        self.assertEqual(set(already2), {"PM-MSG", "PM-FLASH"})
        self.assertEqual(pm, before)

    def test_required_fields_constant_matches_schema_expectation(self):
        self.assertEqual(set(REQUIRED_FIELDS), {"code", "name_th", "name_en", "category", "base_cost"})


if __name__ == "__main__":
    unittest.main()
