"""
Boundary regression test for the deployed customer-safe web surface.

ADR-004 Decision #3 and SPEC-WEB-OFFLINE-CATALOG-INTERACTION §4 forbid factory
cost, CBM/freight, supplier identity, internal source paths, and profit-gate
internals on the public surface. The internal dashboard lives in
public/internal.html, which .vercelignore keeps out of the deployment — every
other deployed HTML/JS file must stay free of those markers.
"""

import os
import unittest

DEPLOYED_FILES = [
    "public/index.html",
    "public/customer-catalog.js",
    "public/gift-anatomy-25d.js",
    "public/gift-anatomy-3d.js",
]

FORBIDDEN_MARKERS = [
    "data-pipeline",
    "factory",
    "freight",
    "cbm",
    "landed",
    "supplier_code",
    "profit_evaluation",
    "audit-logs",
]


class TestPublicSurfaceBoundary(unittest.TestCase):
    def test_deployed_files_have_no_internal_markers(self):
        violations = []
        for path in DEPLOYED_FILES:
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            for marker in FORBIDDEN_MARKERS:
                if marker in content:
                    violations.append(f"{path}: contains '{marker}'")
        self.assertFalse(violations, "\n".join(violations))

    def test_internal_dashboard_is_vercelignored(self):
        with open(".vercelignore", "r", encoding="utf-8") as f:
            rules = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        self.assertIn("public/internal.html", rules)
        self.assertTrue(os.path.exists("public/internal.html"))


if __name__ == "__main__":
    unittest.main()
