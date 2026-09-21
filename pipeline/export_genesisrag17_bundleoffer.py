"""Export canonical CatalogOffer records as GenesisRAG17 BundleOffer records.

A SmartGift portfolio offer (a gift set with components, a gift tier, a category and
tiered prices) is what the zuri-ai adapter models as `BundleOffer`, so offers are mapped
onto that existing entity type rather than a new one. The adapter conventions this
follows, taken from its own fixture `tests/fixtures/genesisrag17/smartgift-catalog/bundles.json`:

  * `code` and `externalId` live in the package namespace `PKG-...`. The structured
    renderer refuses a BundleOffer whose code is outside it
    (genesisrag17-structured-record.js, "record code does not match its type namespace").
  * the upstream offer code is carried as `flowaccountOfferCode`, never as the key.
  * every component carries its qty-1 selling price; `srpQty1Thb` is required, so an
    offer with an unpriced component is held back rather than sent.

Only `records[]` is exported; `source_projection[]` rows are unpromoted supplier rows.

Usage
    python pipeline/export_genesisrag17_bundleoffer.py
    python pipeline/export_genesisrag17_bundleoffer.py --out some/where.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from export_genesisrag17_productmaster import (  # noqa: E402  (shared zText/zMoney rules)
    PRICES,
    PRICES_FILE,
    REPO,
    catalog_version_date,
    money,
    price_tiers,
    qty,
    text,
)

SOURCE = REPO / "data-pipeline" / "02_prepared" / "CatalogOffer.json"
DEFAULT_OUT = REPO / "data-pipeline" / "05_genesisrag17" / "BundleOffer.genesisrag17.json"
UPSTREAM_FILE = "data-pipeline/02_prepared/CatalogOffer.json"
PACKAGE_PREFIX = "PKG-"
# The renderer rejects any descriptive section that contains an ISO date.
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def package_code(source_code):
    code = text(source_code)
    if not code:
        return None
    return code if code.startswith(PACKAGE_PREFIX) else PACKAGE_PREFIX + code


def components(contains, srp_by_code):
    """contains[] -> [{productExternalId, qty, srpQty1Thb}], or (None, reason)."""
    out = []
    for item in contains or []:
        code = text(item.get("product_code"))
        n = qty(item.get("qty"))
        if not code or n is None:
            return None, "component without a product code or a positive qty"
        srp = srp_by_code.get(code) or {}
        price = money(srp.get("srp_price"))
        if price is None:
            tiers = price_tiers(srp.get("price_tiers"))
            price = next((t["unitPriceThb"] for t in tiers if t["minQty"] == 1), None)
        if price is None:
            return None, "component %s has no qty-1 selling price" % code
        out.append({"productExternalId": code, "qty": n, "srpQty1Thb": price})
    return out, None


def to_adapter_record(offer, srp_by_code, version_date):
    source_code = text(offer.get("code")) or text(offer.get("source_offer_code"))
    code = package_code(source_code)
    name_th = text(offer.get("name"))
    if not code:
        return None, "code missing"
    if not name_th:
        return None, "name missing (adapter requires nameTh)"

    comps, reason = components(offer.get("contains"), srp_by_code)
    if comps is None:
        return None, reason

    unboxing = text(offer.get("unboxing_experience"))
    if unboxing and ISO_DATE.search(unboxing):
        return None, "unboxing_experience contains an ISO date (renderer refuses dated descriptive text)"

    total = sum(c["srpQty1Thb"] * c["qty"] for c in comps) if comps else None

    payload = {
        "entityType": "BundleOffer",
        "externalId": code,
        "code": code,
        "nameTh": name_th,
        "nameEn": text(offer.get("name_en")),
        "category": text(offer.get("catalog_slug")),
        "occasion": text(offer.get("occasion")),
        "giftTier": text(offer.get("gift_tier")),
        "recipientSegment": text(offer.get("recipient_segment")),
        "unboxingExperience": unboxing,
        "flowaccountOfferCode": source_code if source_code != code else None,
        "componentSrpQty1TotalThb": round(total, 2) if total is not None else None,
        "components": comps,
        "offerPriceTiersThb": price_tiers(offer.get("price_tiers")),
        "catalogVersionDate": version_date,
        "provenance": {
            "upstreamFile": UPSTREAM_FILE,
            "upstreamRecordId": text(offer.get("id")) or source_code,
            "supplementUpstreamFile": PRICES_FILE,
        },
    }
    return {k: v for k, v in payload.items() if v is not None}, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    doc = json.loads(SOURCE.read_text(encoding="utf-8"))
    metadata = doc.get("metadata") or {}
    offers = doc.get("records") or []
    version_date = catalog_version_date(metadata)

    srp_by_code = {}
    for row in json.loads(PRICES.read_text(encoding="utf-8")).get("srp_reference_products") or []:
        key = text(row.get("product_code"))
        if key:
            srp_by_code[key] = row

    payload, held = [], []
    for offer in offers:
        mapped, reason = to_adapter_record(offer, srp_by_code, version_date)
        if mapped is None:
            held.append((offer.get("code"), reason))
        else:
            payload.append(mapped)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("source            : %s" % SOURCE.relative_to(REPO))
    print("metadata.status   : %s | canonical_promotion=%s" % (metadata.get("status"), metadata.get("canonical_promotion")))
    print("canonical offers  : %d" % len(offers))
    print("exported          : %d  (as BundleOffer)" % len(payload))
    for code, reason in held:
        print("   held %-12s %s" % (code, reason))
    print("with unboxing text: %d/%d" % (sum(1 for r in payload if "unboxingExperience" in r), len(payload)))
    print("with price tiers  : %d/%d" % (sum(1 for r in payload if r.get("offerPriceTiersThb")), len(payload)))
    print("components total  : %d" % sum(len(r["components"]) for r in payload))
    print("written           : %s" % out_path.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
