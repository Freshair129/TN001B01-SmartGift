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
    CATALOG_PATH, GENERATOR, OUTPUT_PATH, ROOT, SCHEMA_PATH, SQL_PATH,
    build_master, evaluate_profit, export_master, parse_snapshot, parse_values,
    validate_master,
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


class TestPricelistMasterExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_master()

    def test_snapshot_counts_and_independent_sql_price_reconciliation(self):
        self.assertEqual(self.data["metadata"]["counts"], {
            "product_masters": 427, "product_families": 32, "portfolio_catalogs": 4,
            "customer_tiers": 4, "catalog_offers": 1110, "pkg": 1,
            "offer_product_links": 3200, "bom": 0, "prices": 669,
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

    def test_missing_prices_and_contract_gaps_remain_visible(self):
        prices = self.data["prices"]
        self.assertEqual(sum(row["price_missing"] for row in prices), 102)
        self.assertTrue(all(row["data_quality_issues"] for row in prices if row["price_missing"]))
        self.assertEqual(sum(row["qty_tier"] is None or row["qty_tier"] <= 0 for row in prices), 118)
        self.assertTrue(all(row["base_cost"] is None and row["category"] is None
                            and row["contract_validation"]["status"] == "incomplete"
                            for row in self.data["product_masters"]))
        self.assertEqual(self.data["bom"], [])
        self.assertFalse(any("qty" in link for link in self.data["offer_product_links"]))

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
            for relative in (SQL_PATH, SCHEMA_PATH, CATALOG_PATH):
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
