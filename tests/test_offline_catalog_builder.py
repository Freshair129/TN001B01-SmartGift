"""
Tests for pipeline/build_offline_catalog.py — the offline customer catalog
must stay customer-safe (SPEC-WEB-OFFLINE-CATALOG §4/§6) and self-contained.
Builds the flipbook HTML in-memory (no PDF/ZIP) and checks the boundary.
"""

import json
import unittest

from pipeline.build_offline_catalog import (
    FONT_CSS_PLACEHOLDER,
    SIZE_BUDGET_BYTES,
    build_dataset,
    build_font_css,
    ladder_from_prices,
    render_flipbook,
    render_pages,
    scan_offline_html,
)


class TestOfflineCatalogBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_dataset()
        cls.pages = render_pages(cls.data)
        cls.html = render_flipbook(cls.data, cls.pages)

    def test_boundary_scan_passes(self):
        self.assertEqual(scan_offline_html(self.html), [])

    def test_scan_catches_injected_marker(self):
        self.assertTrue(scan_offline_html(self.html + "<!-- factory -->"))
        self.assertTrue(scan_offline_html(self.html + '<a href="https://x.example">x</a>'))

    def test_size_budget(self):
        self.assertLessEqual(len(self.html.encode("utf-8")), SIZE_BUDGET_BYTES)

    def test_dataset_is_customer_safe(self):
        blob = json.dumps(
            {k: v for k, v in self.data.items() if k != "images"},
            ensure_ascii=False,
        ).lower()
        for marker in ("factory", "cbm", "freight", "data-pipeline", "supplier",
                       "profit", "margin", "flowaccount"):
            self.assertNotIn(marker, blob, f"dataset leaks '{marker}'")

    def test_version_and_disclaimer_present(self):
        self.assertIn(self.data["catalog_version"], self.html)
        self.assertIn(self.data["snapshot_sha256"][:12], self.html)
        self.assertIn("snapshot", self.html)

    def test_pages_have_cover_toc_and_back(self):
        titles = [t for t, _ in self.pages]
        self.assertEqual(titles[0], "ปก")
        self.assertEqual(titles[1], "สารบัญ")
        self.assertEqual(titles[-1], "ติดต่อ")
        self.assertGreater(len(titles), 10)

    def test_ladder_excludes_missing_and_non_standard_tiers(self):
        rows = [
            {"offer_code": "X", "qty_tier": 10, "unit_price": 100, "price_missing": False,
             "data_quality_issues": []},
            {"offer_code": "X", "qty_tier": 20, "unit_price": 90, "price_missing": False,
             "data_quality_issues": []},
            {"offer_code": "X", "qty_tier": None, "unit_price": 0, "price_missing": True,
             "data_quality_issues": ["missing_or_nonpositive_price", "missing_or_nonpositive_qty_tier"]},
            {"offer_code": "X", "qty_tier": 5012, "unit_price": 85, "price_missing": False,
             "data_quality_issues": ["non_standard_qty_tier"]},
        ]
        ladder = ladder_from_prices(rows, "X")
        self.assertEqual(ladder, [{"qty": 10, "unit_price": 100}, {"qty": 20, "unit_price": 90}])

    def test_offline_dataset_sets_have_no_non_standard_tiers(self):
        # Regression guard for the live bug found 2026-08-30: TDS07-2 and
        # TYD0262 are customer-facing media sets whose ladder used to include
        # a raw, unfiltered 5012/11-14 quantity tier.
        for s in self.data["sets"]:
            qtys = {t["qty"] for t in s["ladder"]}
            self.assertTrue(qtys.issubset({1, 10, 20, 50, 100, 300, 500, 1000}),
                            f"{s['code']} ladder has a non-standard qty: {qtys}")

    def test_sarabun_subset_embeds_and_scans_clean(self):
        font_css = build_font_css("ทดสอบภาษาไทย SmartGift 123")
        self.assertIn("font-weight:400", font_css)
        self.assertIn("font-weight:700", font_css)
        self.assertIn("data:font/woff;base64,", font_css)
        final = self.html.replace(FONT_CSS_PLACEHOLDER, font_css, 1)
        self.assertEqual(scan_offline_html(final), [])

    def test_no_fetch_or_external_links(self):
        low = self.html.lower()
        self.assertNotIn("fetch(", low)
        self.assertNotIn("<link", low)
        self.assertNotIn("@import", low)


if __name__ == "__main__":
    unittest.main()
