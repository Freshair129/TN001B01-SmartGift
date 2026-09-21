"""Export ProductMaster records in the shape GenesisRAG17's SmartGift adapter accepts.

The adapter (zuri-ai `apps/server/src/modules/knowledge/smartgift-catalog-adapter.js`)
parses an upload with `z.array(zSmartGiftCatalogRecord).min(1)` and every member schema
is `.strict()`, so an unknown key fails the whole file. This script is the missing
translation layer between the two systems:

    data-pipeline/02_prepared/ProductMaster.json   ->   adapter upload payload
      dict wrapper, snake_case                          bare array, camelCase
      base_cost / source_price_tiers                    srpPriceThbQty1 / priceTiersThb

Only `records[]` is exported. `source_projection[]` holds raw supplier rows that carry
`contract_validation.status == "incomplete"`, no `PM-` code and no `name_th`; the
adapter requires `nameTh`, so those rows cannot be admitted until the catalog owner
promotes them. Run with --audit-raw to see exactly which field each raw row is missing.

Usage
    python pipeline/export_genesisrag17_productmaster.py
    python pipeline/export_genesisrag17_productmaster.py --audit-raw
    python pipeline/export_genesisrag17_productmaster.py --out some/where.json
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SOURCE = REPO / "data-pipeline" / "02_prepared" / "ProductMaster.json"
# ProductMaster.records carries identity and names; the selling prices live in
# pricelist_master.srp_reference_products, keyed by the same PM- code. base_cost in
# ProductMaster is a factory COST and must never be mapped onto srpPriceThbQty1.
PRICES = REPO / "data-pipeline" / "02_prepared" / "pricelist_master.json"
DEFAULT_OUT = REPO / "data-pipeline" / "05_genesisrag17" / "ProductMaster.genesisrag17.json"

ENTITY_TYPE = "ProductMaster"
UPSTREAM_FILE = "data-pipeline/02_prepared/ProductMaster.json"
PRICES_FILE = "data-pipeline/02_prepared/pricelist_master.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# zText: trimmed, 1..500 chars. Anything outside that is dropped rather than sent,
# because .strict() rejects the whole file on one bad member.
TEXT_MAX = 500


def text(value):
    """zText or None. Empty, blank and over-long values become None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s or len(s) > TEXT_MAX:
        return None
    return s


def money(value):
    """zMoney: finite, non-negative number, or None."""
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    if n != n or n in (float("inf"), float("-inf")) or n < 0:
        return None
    return n


def qty(value):
    """zQty: positive integer, or None."""
    if value is None or isinstance(value, bool):
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def price_tiers(raw):
    """price_tiers -> [{minQty, unitPriceThb}] sorted, deduped by minQty.

    Accepts the two shapes seen in the prepared files: a list of dicts with
    qty/price-ish keys, and a mapping of quantity -> price.
    """
    out = {}
    if isinstance(raw, dict):
        items = raw.items()
    elif isinstance(raw, list):
        items = []
        for row in raw:
            if not isinstance(row, dict):
                continue
            q = next((row[k] for k in ("min_qty", "minQty", "qty", "quantity") if k in row), None)
            p = next(
                (row[k] for k in ("unit_price_thb", "unitPriceThb", "price_thb", "unit_price", "price")
                 if k in row),
                None,
            )
            items.append((q, p))
    else:
        return []

    for q, p in items:
        mq, up = qty(q), money(p)
        if mq is not None and up is not None:
            out[mq] = up
    return [{"minQty": q, "unitPriceThb": out[q]} for q in sorted(out)]


def dimensions(record):
    """dimensionsCm is all-or-nothing: the adapter's object is .strict() with three
    required numbers, so a partial measurement is dropped instead of half-sent."""
    src = record.get("dimensions_cm") or record.get("dimensionsCm")
    if not isinstance(src, dict):
        return None
    got = {}
    for out_key, keys in (
        ("height", ("height", "h")),
        ("length", ("length", "l", "depth")),
        ("width", ("width", "w")),
    ):
        val = next((src[k] for k in keys if k in src), None)
        m = money(val)
        if m is None:
            return None
        got[out_key] = m
    return got


def catalog_version_date(metadata):
    for key in ("catalog_version_date", "version_date", "generated_at", "exported_at"):
        raw = metadata.get(key)
        if not raw:
            continue
        s = str(raw)[:10]
        if DATE_RE.match(s):
            return s
    return None


def to_adapter_record(record, srp, version_date):
    """Map one canonical record joined to its SRP row.

    Returns (payload, reason_it_cannot_be_sent).
    """
    code = text(record.get("code"))
    name_th = text(record.get("name_th")) or text(srp.get("name_th"))
    if not code:
        return None, "code missing"
    if not name_th:
        return None, "name_th missing (adapter requires nameTh)"

    provenance = record.get("provenance") or {}
    upstream_record_id = text(provenance.get("source_key")) or code

    tiers = price_tiers(srp.get("price_tiers"))
    # srpPriceThbQty1 is the qty-1 selling price: the explicit srp_price, else the
    # qty-1 tier. base_cost is deliberately not consulted - it is a factory cost.
    srp_qty1 = money(srp.get("srp_price"))
    if srp_qty1 is None:
        srp_qty1 = next((t["unitPriceThb"] for t in tiers if t["minQty"] == 1), None)

    payload = {
        "entityType": ENTITY_TYPE,
        "externalId": code,          # ADR-075 D4: identity is externalId, not the FlowAccount code
        "code": code,
        "nameTh": name_th,
        "nameEn": text(record.get("name_en")) or text(srp.get("name_en")),
        "category": text(srp.get("category_slug")) or text(record.get("category")),
        "productFamily": text(srp.get("product_family")) or text(record.get("product_family_id")),
        "flowaccountModelCode": text(record.get("flowaccount_model_code")) or text(srp.get("factory_product_code")),
        "dimensionsCm": dimensions(record),
        "unitWeightKg": money(record.get("unit_weight_kg")),
        "srpPriceThbQty1": srp_qty1,
        "priceTiersThb": tiers,
        "catalogVersionDate": version_date,
        "provenance": {
            "upstreamFile": UPSTREAM_FILE,
            "upstreamRecordId": upstream_record_id,
            "supplementUpstreamFile": PRICES_FILE if srp else None,
        },
    }
    payload["provenance"] = {k: v for k, v in payload["provenance"].items() if v is not None}
    # The adapter is .strict(): send a key or omit it, never send an explicit null
    # for an optional field.
    return {k: v for k, v in payload.items() if v is not None}, None


def audit_raw(rows):
    """Why each source_projection row cannot be admitted, counted by cause."""
    causes = collections.Counter()
    for row in rows:
        if not text(row.get("code")):
            causes["code missing"] += 1
        elif not str(row.get("code")).startswith("PM-"):
            causes["code is not a canonical PM- identity"] += 1
        if not text(row.get("name_th")):
            causes["name_th missing (adapter requires nameTh)"] += 1
        status = (row.get("contract_validation") or {}).get("status")
        if status and status != "required_fields_present":
            causes["contract_validation.status=%s" % status] += 1
    return causes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="output path for the adapter payload")
    ap.add_argument("--audit-raw", action="store_true", help="also report why source_projection rows are held back")
    args = ap.parse_args()

    if not SOURCE.exists():
        print("source not found: %s" % SOURCE, file=sys.stderr)
        return 2

    doc = json.loads(SOURCE.read_text(encoding="utf-8"))
    metadata = doc.get("metadata") or {}
    canonical = doc.get("records") or []
    raw = doc.get("source_projection") or []
    version_date = catalog_version_date(metadata)

    srp_by_code = {}
    if PRICES.exists():
        prices_doc = json.loads(PRICES.read_text(encoding="utf-8"))
        for row in prices_doc.get("srp_reference_products") or []:
            key = text(row.get("product_code"))
            if key:
                srp_by_code[key] = row

    payload, skipped, unpriced = [], [], []
    for record in canonical:
        code = text(record.get("code"))
        srp = srp_by_code.get(code, {})
        if not srp:
            unpriced.append(code)
        mapped, reason = to_adapter_record(record, srp, version_date)
        if mapped is None:
            skipped.append((record.get("code"), reason))
        else:
            payload.append(mapped)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("source            : %s" % SOURCE.relative_to(REPO))
    print("prices            : %s (%d srp rows)" % (PRICES.relative_to(REPO), len(srp_by_code)))
    print("metadata.status   : %s | canonical_promotion=%s" % (metadata.get("status"), metadata.get("canonical_promotion")))
    print("catalogVersionDate: %s" % (version_date or "(none - export is undated)"))
    print("canonical records : %d" % len(canonical))
    print("exported          : %d" % len(payload))
    if skipped:
        print("held back         : %d" % len(skipped))
        for code, reason in skipped:
            print("   - %-16s %s" % (code, reason))
    with_tiers = sum(1 for r in payload if r.get("priceTiersThb"))
    with_srp = sum(1 for r in payload if "srpPriceThbQty1" in r)
    print("with price tiers  : %d/%d" % (with_tiers, len(payload)))
    print("with srp qty1     : %d/%d" % (with_srp, len(payload)))
    if unpriced:
        print("no srp row        : %s" % ", ".join(c for c in unpriced if c))
    print("written           : %s" % out_path.relative_to(REPO))

    if args.audit_raw:
        print()
        print("source_projection : %d raw supplier rows, none exported" % len(raw))
        for cause, n in audit_raw(raw).most_common():
            print("   %5d  %s" % (n, cause))
        print("   promoting these is a catalog-owner decision, not a transform: the adapter")
        print("   requires nameTh, and metadata.canonical_promotion is false.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
