"""
Export config/pricing_rules_formula.yaml to the JSON shape the browser pricing
engine (price-boss/pricing.html) can fetch.

The browser cannot read YAML, so before 2026-09-10 every constant in pricing.html
was a second hand-maintained copy of the same numbers. This script makes the YAML
the single source and the JSON a generated artifact: run it whenever the formula
config changes. pricing.html still ships the built-in defaults so that opening it
from file:// (where fetch is blocked) keeps working.

    python -m pipeline.export_pricing_config [--check]

--check exits non-zero when the committed JSON no longer matches the YAML, which
is what a pre-commit hook or CI step should call.
"""

import argparse
import hashlib
import io
import json
import math
import os
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - dependency is declared in requirements.txt
    yaml = None

SOURCE_PATH = "config/pricing_rules_formula.yaml"
OUTPUT_PATHS = ("price-boss/pricing-config.json",)
GENERATOR = "pipeline/export_pricing_config.py"

# JSON has no infinity, so open-ended tiers are written as null and the browser
# treats null as "no upper bound".
INF = float("inf")


def _bound(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isinf(value):
        return None
    return value


def _tiers(rows, bound_key, *value_keys):
    out = []
    for row in rows or []:
        tier = {"max": _bound(row.get(bound_key))}
        for key in value_keys:
            tier[key] = row.get(key)
        out.append(tier)
    return out


def _rate_matrix(matrix):
    """Lowercase the tier keys so the browser can index them by its own tier ids."""
    out = {}
    for warehouse, modes in (matrix or {}).items():
        out[warehouse] = {}
        for mode, goods in modes.items():
            out[warehouse][mode] = {}
            for goods_type, tiers in goods.items():
                out[warehouse][mode][goods_type] = {
                    str(tier).lower(): {"cbm": cell.get("cbm"), "kg": cell.get("kg")}
                    for tier, cell in tiers.items()
                }
    return out


def _profile(block, fallback_markup_bands=None):
    if not isinstance(block, dict):
        return None
    profile = {
        "label": block.get("name", ""),
        "breaks": block.get("breaks"),
        "factors": block.get("factors"),
        "anchor": block.get("anchor_qty", block.get("anchor")),
        "basis": block.get("basis"),
        "note": block.get("note", ""),
    }
    if block.get("flat_markup") is not None:
        profile["flatMarkup"] = block["flat_markup"]
    if block.get("reference_goods_type"):
        profile["refGoods"] = block["reference_goods_type"]
    if block.get("markup_source") == "markup_bands_standard":
        profile["markupBands"] = fallback_markup_bands
    return profile


def build(rules, source_sha256):
    fx = rules.get("currency_exchange_rates") or {}
    log = rules.get("logistics_density_and_freight") or {}
    inland = log.get("inland_china_freight") or {}
    lead = rules.get("lead_time_working_days") or {}
    bands = _tiers(rules.get("markup_bands_standard"), "max_cost_thb", "markup_multiplier")
    bands = [{"max": b["max"], "f": b["markup_multiplier"]} for b in bands]

    return {
        "generated_by": GENERATOR,
        "source_file": SOURCE_PATH,
        "source_sha256": source_sha256,
        "formula_version": rules.get("version"),
        "contract_reference": rules.get("contract_reference"),
        "fx": {"cnyToThb": fx.get("cny_to_thb"), "usdToThb": fx.get("usd_to_thb")},
        "logistics": {
            "densitySwitch": log.get("density_threshold_kg_per_cbm"),
            "minCbm": log.get("min_chargeable_cbm"),
            "seaThreshold": log.get("sea_threshold_cbm"),
            "seasonMonths": log.get("seasonality_peak_months"),
            "inlandRmbPerSet": inland.get("default_rate_cny_per_set"),
        },
        "priceStepThb": (rules.get("price_rounding") or {}).get("ladder_price_step_thb"),
        "floors": [{"max": t["max"], "thb": t["thb"]} for t in _tiers(rules.get("profit_floors"), "max_qty", "thb")],
        "smallOrder": [{"max": t["max"], "f": t["sof"]} for t in _tiers(rules.get("small_order_factors"), "max_qty", "sof")],
        "markupBands": bands,
        "rates": _rate_matrix(rules.get("shipping_rate_matrix")),
        "profiles": {
            "standard": _profile(rules.get("standard_quote_profile"), bands),
            "corporate": _profile(rules.get("corporate_quote_profile"), bands),
        },
        "logoMethods": _serialize_logo(rules.get("logo_methods") or {}),
        "logoPositions": rules.get("logo_positions_rule") or {},
        "leadTime": {
            "artwork": lead.get("artwork_confirm"),
            "sample": lead.get("sample"),
            "production": [{"max": t["max"], "min": t["min"], "max_days": t["max_days"]}
                           for t in _production(lead.get("production"))],
            "freight": lead.get("freight"),
        },
        "sources": rules.get("sources") or {},
    }


def _production(rows):
    out = []
    for row in rows or []:
        out.append({"max": _bound(row.get("max_qty")), "min": row.get("min"), "max_days": row.get("max")})
    return out


def _serialize_logo(methods):
    out = {}
    for name, spec in methods.items():
        clean = {}
        for key, value in (spec or {}).items():
            if isinstance(value, list):
                clean[key] = [{"max": _bound(row.get("max_qty")), "usd": row.get("usd")} for row in value]
            else:
                clean[key] = value
        out[name] = clean
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the generated JSON differs from what is on disk")
    args = parser.parse_args(argv)

    if yaml is None:
        print("PyYAML is required: pip install pyyaml", file=sys.stderr)
        return 2
    if not os.path.exists(SOURCE_PATH):
        print(f"missing {SOURCE_PATH}", file=sys.stderr)
        return 2

    with open(SOURCE_PATH, "rb") as handle:
        raw = handle.read()
    rules = yaml.safe_load(raw.decode("utf-8-sig"))
    payload = build(rules, hashlib.sha256(raw).hexdigest())
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    status = 0
    for path in OUTPUT_PATHS:
        # Compared newline-insensitively: a Windows checkout with core.autocrlf=true
        # rewrites the committed LF file to CRLF, which is not a stale config.
        current = None
        if os.path.exists(path):
            with io.open(path, "rb") as handle:
                current = handle.read().decode("utf-8-sig").replace("\r\n", "\n")
        if args.check:
            if current != text:
                print(f"STALE  {path} — run: python -m pipeline.export_pricing_config", file=sys.stderr)
                status = 1
            else:
                print(f"ok     {path}")
            continue
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print(f"wrote  {path}  ({len(text):,} bytes)")

    if not args.check:
        print(f"source {SOURCE_PATH}  sha256 {payload['source_sha256']}")
        print(f"formula version {payload['formula_version']}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
