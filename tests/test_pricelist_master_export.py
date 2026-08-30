"""SQL preservation, reference integrity and package profit safety checks."""

import copy
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

from pipeline.export_pricelist_master import (
    CATALOG_PATH, FACTORY_PATH, GENERATOR, OUTPUT_PATH, PRICING_RULES_PATH, PUBLIC_OUTPUT_PATH, ROOT,
    SCHEMA_PATH, SQL_PATH, SRP_QTY_TIERS, build_master, evaluate_profit, export_master,
    build_public_projection, parse_factory_catalog, parse_snapshot, parse_values,
    validate_master, validate_public_projection,
)

sys.stdout.reconfigure(encoding="utf-8")


class TestSQLLiteralParsing(unittest.TestCase):
    def test_thai_quotes_newlines_json_and_null(self):
        values = parse_values("'ชุด O''Brien, (welcome);\nสีเขียว', NULL, TRUE, FALSE, 577.80, '[\"กล่อง\",\"ปากกา\"]'")
        self.assertEqual(values, ["ชุด O'Brien, (welcome);\nสีเขียว", None, True, False, 577.8,
                                  '["กล่อง","ปากกา"]'])

    def test_expressions_and_trailing_values_are_rejected(self):
        for text in ("load_extension('anything')", "1,", "1); DROP TABLE x;", "'unterminated",
                     "0.1234567890123456789"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_values(text)

    def test_on_conflict_and_statement_line_are_preserved(self):
        sql = "\nINSERT INTO smartgift_type (type_id, group_id, name_th, name_en, aliases_th, aliases_en) VALUES ('pen', 'office', 'ปากกา', 'Pen', '[]', '[]') ON CONFLICT (type_id) DO NOTHING;\n"
        row = parse_snapshot(sql)["smartgift_type"][0]
        self.assertEqual(row["name_th"], "ปากกา")
        self.assertEqual(row["_line"], 2)

    def test_customer_table_and_unterminated_statement_are_rejected(self):
        for sql in ("INSERT INTO customers (name) VALUES ('synthetic');\n",
                    "INSERT INTO smartgift_type (type_id) VALUES ('pen')"):
            with self.assertRaises(ValueError):
                parse_snapshot(sql)


class TestPackageProfitGate(unittest.TestCase):
    def setUp(self):
        self.complete = dict(bom_complete=True, quantity_complete=True,
                             costs_complete=True, vat_basis_aligned=True)

    def test_exact_profit_floor(self):
        below = evaluate_profit("74999.99", "50000", **self.complete)
        at = evaluate_profit("75000", "50000", **self.complete)
        self.assertEqual(below["status"], "below_minimum")
        self.assertEqual(at["status"], "pass")
        self.assertEqual(at["profit"], 25000)

    def test_missing_cost_or_negative_nonfinite_amount_never_passes(self):
        for cost in (None, -1, "NaN", "Infinity", True):
            with self.subTest(cost=cost):
                result = evaluate_profit(100000, cost, **self.complete)
                self.assertEqual(result["status"], "missing_inputs")
                self.assertIsNone(result["profit"])

    def test_each_completeness_gate_is_required(self):
        for field in self.complete:
            flags = {**self.complete, field: False}
            with self.subTest(field=field):
                self.assertEqual(evaluate_profit(100000, 1000, **flags)["status"], "missing_inputs")

    def test_unconfigured_template_cannot_pass(self):
        result = evaluate_profit()
        self.assertEqual(result["status"], "missing_inputs")
        self.assertIsNone(result["profit"])
        self.assertIn("bom", result["missing_inputs"])
        self.assertIn("quantity", result["missing_inputs"])

    def test_extra_cost_evidence_gate_cannot_be_bypassed(self):
        result = evaluate_profit(100000, 50000, **self.complete, extra_missing=("factory_identity",))
        self.assertEqual(result["status"], "missing_inputs")
        self.assertIsNone(result["profit"])
        self.assertIn("factory_identity", result["missing_inputs"])


class TestPricelistMasterExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_master()

    def test_snapshot_counts_and_independent_sql_price_reconciliation(self):
        self.assertEqual(self.data["metadata"]["counts"], {
            "product_masters": 427, "product_families": 32, "portfolio_catalogs": 4,
            "customer_tiers": 4, "catalog_offers": 1110, "seasonal_offers": 6, "pkg": 11,
            "offer_product_links": 3200, "bom": 17, "prices": 669,
            "price_comparisons": 669, "srp_reference_products": 16,
            "srp_qty_comparisons": 128,
        })
        # Independent SQL engine checks every price cell against the dump.
        with sqlite3.connect(":memory:") as db:
            db.row_factory = sqlite3.Row
            db.executescript((ROOT / SQL_PATH).read_text(encoding="utf-8-sig"))
            expected = [dict(row) for row in db.execute("SELECT * FROM smartgift_price ORDER BY id")]
        for source, exported in zip(expected, self.data["prices"]):
            for key, value in source.items():
                actual = exported["provenance"]["source_ref"] if key == "source_ref" else exported[key]
                self.assertEqual(actual, json.loads(value) if key == "source_ref" else value)

    def test_yaml_tiers_and_package_are_not_sql_sets(self):
        self.assertEqual([tier["name"] for tier in self.data["customer_tiers"]],
                         ["Reach", "Select", "Signature", "Bespoke"])
        self.assertTrue(all(tier["entity_type"] == "GiftTier" for tier in self.data["customer_tiers"]))
        pkg = self.data["pkg"][0]
        self.assertEqual(pkg["entity_type"], "BundleOffer")
        self.assertEqual(pkg["name"], "ชุดต้อนรับพนักงานใหม่")
        self.assertEqual(len(pkg["design_scope"]["catalog_slugs"]), 4)
        self.assertEqual(pkg["options"], [])
        self.assertEqual(pkg["profit_evaluation"]["status"], "missing_inputs")
        self.assertFalse(pkg["quote_ready"])

    def test_seasonal_packages_use_schema_ids_and_explicit_bom(self):
        seasonal = [pkg for pkg in self.data["pkg"] if pkg["occasion"] in ("christmas_2026", "new_year_2027")]
        self.assertEqual(len(seasonal), 10)
        self.assertTrue(all(pkg["id"].startswith("bundle:") for pkg in seasonal))
        self.assertTrue(all(pkg["code"].startswith("PKG-") for pkg in seasonal))
        self.assertTrue(all(pkg["profit_evaluation"]["minimum_profit"] == 25000 for pkg in seasonal))
        self.assertTrue(all(pkg["profit_evaluation"]["status"] == "missing_inputs" for pkg in seasonal))
        self.assertEqual(self.data["metadata"]["bom_coverage"], "proposed_recipe")
        self.assertEqual(self.data["metadata"]["quality_summary"]["verified_bom_edges"], 0)
        self.assertEqual(self.data["metadata"]["quality_summary"]["proposed_bom_edges"], 17)

        offers = {offer["id"]: offer for offer in self.data["seasonal_offers"]}
        self.assertEqual(offers["offer:TDD03-2"]["gift_tier"], "Select")
        self.assertEqual(offers["offer:TWL01-8"]["gift_tier"], "Select")
        self.assertEqual(offers["offer:TGC06-4"]["gift_tier"], "Signature")
        self.assertEqual(offers["offer:TMK0215"]["gift_tier"], "Signature")
        self.assertEqual(offers["offer:smartgift-2026-christmas-reach-operations"]["gift_tier"], "Reach")
        self.assertEqual(offers["offer:smartgift-2027-new-year-reach-operations"]["gift_tier"], "Reach")
        self.assertTrue(all(offer["id"].startswith("offer:") for offer in offers.values()))
        self.assertTrue(all(component["product_master_id"] == f"pm:{component['product_code']}"
                            for offer in offers.values() for component in offer["contains"]))

        package_ids = {pkg["id"] for pkg in self.data["pkg"]}
        self.assertTrue(all(row["bundle_id"] in package_ids for row in self.data["bom"]))
        self.assertTrue(all(row["verified"] is False and row["factory_cost_thb"] is None
                            for row in self.data["bom"]))
        fixed_options = [option for pkg in seasonal for option in pkg["options"] if option["qty"] is not None]
        self.assertEqual(len(fixed_options), 6)
        self.assertTrue(all(option["bundle_id"] in package_ids for option in fixed_options))
        self.assertTrue(all(option["offer_id"] in offers for option in fixed_options))

    def test_missing_prices_and_contract_gaps_remain_visible(self):
        prices = self.data["prices"]
        self.assertEqual(sum(row["price_missing"] for row in prices), 102)
        self.assertTrue(all(row["data_quality_issues"] for row in prices if row["price_missing"]))
        self.assertEqual(sum(row["qty_tier"] is None or row["qty_tier"] <= 0 for row in prices), 118)
        self.assertTrue(all(row["base_cost"] is None and row["category"] is None
                            and row["contract_validation"]["status"] == "incomplete"
                            for row in self.data["product_masters"]))
        self.assertEqual(len(self.data["bom"]), 17)
        self.assertTrue(all(row["cost_status"] == "missing_factory_identity" for row in self.data["bom"]))
        self.assertFalse(any("qty" in link for link in self.data["offer_product_links"]))

    def test_factory_catalog_and_srp_quantity_matrix_are_explicit(self):
        factory = parse_factory_catalog((ROOT / FACTORY_PATH).read_text(encoding="utf-8-sig"))
        self.assertEqual({key: len(rows) for key, rows in factory.items()}, {"catalogs": 2, "products": 1087})
        self.assertEqual(self.data["metadata"]["quality_summary"]["factory_exact_match_price_rows"], 404)
        self.assertEqual(self.data["metadata"]["quality_summary"]["factory_exact_matches_for_price_rows"], 131)
        self.assertEqual({row["qty"] for row in self.data["srp_qty_comparisons"]}, set(SRP_QTY_TIERS))
        self.assertEqual(sum(row["qty"] == 1 for row in self.data["srp_qty_comparisons"]), 16)
        self.assertTrue(all(row["srp_source"] == "master_declared" for row in self.data["srp_qty_comparisons"]))
        self.assertTrue(all(row["factory_product_code"] is None and row["factory_cost_thb"] is None
                            for row in self.data["srp_qty_comparisons"]))
        matched = next(row for row in self.data["price_comparisons"]
                       if row["factory_product_code"] is not None and row["factory_cost_thb"] is not None)
        self.assertEqual(matched["factory_cost_thb"], matched["factory_reference_thb"])
        self.assertTrue(all(row["cbm_per_unit"] is not None and row["freight_per_unit_thb"] is not None
                            for row in self.data["srp_qty_comparisons"]))
        self.assertEqual(sum(row["comparison_status"] == "factory_reference_only"
                             for row in self.data["price_comparisons"]), 333)

    def test_public_projection_is_allowlisted_and_cost_safe(self):
        public = build_public_projection(self.data)
        validate_public_projection(public)
        self.assertEqual(public["metadata"]["status"], "customer_safe")
        self.assertEqual(public["metadata"]["counts"]["product_masters"], 427)
        self.assertEqual(len(public["pkg"]), 11)
        self.assertNotIn("factory_cost_thb", public["bom"][0])
        self.assertNotIn("cbm_per_unit", public["bom"][0])
        self.assertNotIn("profit_evaluation", public["pkg"][1])
        self.assertNotIn("provenance", public["catalog_offers"][0])
        artifact = json.loads((ROOT / PUBLIC_OUTPUT_PATH).read_text(encoding="utf-8"))
        self.assertEqual(artifact, public)

    def test_orphan_duplicate_and_fabricated_bom_are_rejected(self):
        mutations = (
            lambda data: data["prices"][0].update(offer_code="UNKNOWN"),
            lambda data: data["product_masters"][0].update(product_family_id="UNKNOWN"),
            lambda data: data["product_masters"].append(data["product_masters"][0]),
            lambda data: data["offer_product_links"][0].update(qty=1),
            lambda data: data["bom"].append({"qty": 1}),
        )
        for mutate in mutations:
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.assertRaises(ValueError):
                validate_master(data)

    def test_contact_text_is_quarantined_without_echoing_value(self):
        data = copy.deepcopy(self.data)
        data["catalog_offers"][0]["description"] = "Contact synthetic@example.com"
        with self.assertRaisesRegex(ValueError, "Potential contact data") as caught:
            validate_master(data)
        self.assertNotIn("synthetic@example.com", str(caught.exception))

    def test_repeat_export_is_deterministic_and_source_change_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="pricelist-export-test-") as folder:
            root = Path(folder)
            for relative in (SQL_PATH, FACTORY_PATH, SCHEMA_PATH, CATALOG_PATH, PRICING_RULES_PATH):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            export_master(root)
            before = (root / OUTPUT_PATH).read_bytes()
            self.assertFalse(before.startswith(b"\xef\xbb\xbf"))
            export_master(root)
            self.assertEqual(before, (root / OUTPUT_PATH).read_bytes())
            export_master(root, check=True)
            with (root / SQL_PATH).open("ab") as handle:
                handle.write(b"\n-- changed\n")
            with self.assertRaisesRegex(ValueError, "hash changed"):
                export_master(root)
            self.assertEqual(before, (root / OUTPUT_PATH).read_bytes())

    def test_validation_failure_does_not_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory(prefix="pricelist-atomic-test-") as folder:
            root = Path(folder)
            output = root / OUTPUT_PATH
            output.parent.mkdir(parents=True)
            original = json.dumps({"metadata": {"generator": GENERATOR}, "marker": "keep"}).encode()
            output.write_bytes(original)
            with patch("pipeline.export_pricelist_master.build_master", side_effect=ValueError("invalid input")):
                with self.assertRaises(ValueError):
                    export_master(root)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
