"""
Tests for pipeline/build_offline_catalog.py — the offline customer catalog
must stay customer-safe (SPEC-WEB-OFFLINE-CATALOG §4/§6) and self-contained.
Builds the flipbook HTML in-memory (no PDF/ZIP) and checks the boundary.
"""

import json
import unittest

from pipeline.build_offline_catalog import (
    SIZE_BUDGET_BYTES,
    build_dataset,
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

    def test_no_fetch_or_external_links(self):
        low = self.html.lower()
        self.assertNotIn("fetch(", low)
        self.assertNotIn("<link", low)
        self.assertNotIn("@import", low)


if __name__ == "__main__":
    unittest.main()
