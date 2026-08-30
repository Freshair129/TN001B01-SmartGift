"""Export a review-only pricelist snapshot. Never execute SQL or sync a vault."""

import argparse
import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
from decimal import Decimal

import yaml

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = "price-boss/sql/smartgiftpricelist.postgres.sql"
FACTORY_PATH = "price-boss/ราคา.sql"
SCHEMA_PATH = "config/schema_genesisblock.yaml"
CATALOG_PATH = "data-pipeline/02_prepared/smartgift_catalog_master.json"
PRICING_RULES_PATH = "config/pricing_rules_formula.yaml"
OUTPUT_PATH = "data-pipeline/02_prepared/pricelist_master.json"
PUBLIC_OUTPUT_PATH = "public/data/pricelist_public.json"
PUBLIC_GENERATOR = "pipeline/export_pricelist_master.py#build_public_projection"
PUBLIC_FORBIDDEN_FIELDS = frozenset({
    "base_cost", "rmb", "factory_cost_thb", "factory_unit_cny", "factory_product_code",
    "factory_reference_thb", "factory_adjusted_estimate_thb", "factory_match_status",
    "unit_profit", "margin_percent", "profit_evaluation", "cbm_per_unit", "carton_cbm",
    "freight_total_thb", "freight_per_unit_thb", "delivered_unit_cost", "supplier",
    "flow_account_code", "flow_account_name", "provenance", "source_ref", "source_file",
    "source_sha256", "customer_contacts", "contact", "email", "phone",
    "cost_reference", "exw_cost_thb", "exw_cost_per_set_thb", "factory_unit_price",
    "factory_currency", "factory_cost_basis", "fx_rate_to_thb", "indicative_set_profit_thb",
})
SQL_SHA256 = "263556642064f6398e4cd00a7a4897ca7ba841b7c3bae5b8d2165b3186b2fdd4"
FACTORY_SHA256 = "d85e114018a4792d7a3aa8fc9b4f35475f40e9948bffd5aa04cf0171b5c9cb24"
PRICING_RULES_SHA256 = "f4473230f10b59133936974a0cacf84bbe84865d61db76553d8cc2a58ba635fc"
COST_MAPPING_PATH = "data-pipeline/02_prepared/factory_cost_pm_mapping.json"
COST_MAPPING_SHA256 = "e2dd1f99fca79f184c0b76fc405ea29c99388018f2c23aa7eb4d961037f86503"
MIN_PROFIT = Decimal("25000.00")
GENERATOR = "pipeline/export_pricelist_master.py"
TABLE_COLUMNS = {
    "smartgift_export_run": "run_id exported_at source_path commercial_skus offers models",
    "smartgift_type": "type_id group_id name_th name_en aliases_th aliases_en",
    "smartgift_model": "base_signature display_name english_name type_id group_id status price_source offer_codes colors price_tiers source_ref",
    "smartgift_offer": "code name_th name_en description offer_kind status branding origin rmb image price_tiers source_ref",
    "smartgift_price": "id offer_code qty_tier unit_price unit_price_with_vat price_missing price_list_group flow_account_code flow_account_name export_date source_ref",
}
EXPECTED_COUNTS = {
    "smartgift_export_run": 1, "smartgift_type": 32, "smartgift_model": 427,
    "smartgift_offer": 1110, "smartgift_price": 669,
}
FACTORY_TABLE_COLUMNS = {
    "catalogs": "catalog_key label product_count source_url synced_at",
    "products": "catalog_key code name rmb upc dim_l dim_w dim_h kg exclusive_flag img synced_at",
}
EXPECTED_FACTORY_COUNTS = {"catalogs": 2, "products": 1087}
SRP_QTY_TIERS = (1, 10, 20, 50, 100, 300, 500, 1000)
# A smartgift_price.qty_tier value counts as part of FlowAccount's normal
# group-pricing ladder if it is one of the codebase's own declared
# meaningful quantities (SRP_QTY_TIERS) or if it recurs at least this many
# times across the raw table — computed from this run's own rows, not a
# hardcoded snapshot, so a genuinely new ladder point is recognized rather
# than perpetually flagged. A one-off value (e.g. a single row with an
# unrepeated, non-canonical qty_tier) reads as a probable FlowAccount
# data-entry artifact — flagged for human review, never altered or dropped.
MIN_STANDARD_TIER_OCCURRENCES = 5
JSON_FIELDS = {"aliases_th", "aliases_en", "offer_codes", "colors", "price_tiers", "source_ref"}
PACKAGE_STATUSES = {"draft", "mapping_pending", "cost_pending", "missing_inputs", "below_minimum", "pass", "approved", "rejected"}
INSERT = re.compile(r"INSERT INTO (\w+)\s*\(([^)]+)\)\s*VALUES\s*\((.*?)\)\s*(?:ON CONFLICT \(\w+\) DO NOTHING\s*)?;", re.S)
FACTORY_INSERT = re.compile(r"INSERT INTO (\w+)\s*\(([^)]+)\)\s*VALUES\s*\((.*)\);", re.S)
LITERAL = re.compile(r"\s*('(?:[^']|'')*'|NULL|TRUE|FALSE|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(,|$)", re.S)
PII_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"
    r"|(?<![\w])(?:\+66|0)[ -]?[689](?:[ -]?\d){8}(?![\w])"
)

SEASONAL_PACKAGE_DEFINITIONS = (
    {
        "event_key": "christmas_2026",
        "event_id": "campaign:smartgift-2026-christmas",
        "event_name_th": "Christmas 2026",
        "event_name_en": "Christmas 2026",
        "headline_th": "ของขวัญปลายปีที่ทีมอยากหยิบใช้จริง",
        "supporting_copy_th": "เลือกชุดตามบทบาท ตั้งแต่ทีมปฏิบัติการถึงผู้บริหาร",
        "visual_direction": "warm red/green accent, product-first unboxing",
        "packages": (
            {
                "slug": "reach-operations",
                "pkg_code": "PKG-XMAS-2026-REACH-OPS",
                "name": "ชุดส่งต่อความอบอุ่นสำหรับทีมปฏิบัติการ",
                "tier": "Reach",
                "segment": "Operations",
                "offer_id": "offer:smartgift-2026-christmas-reach-operations",
                "offer_code": "SG-OFFER-XMAS-2026-REACH-OPS",
                "source_offer_code": None,
                "product_codes": ("PM-UMB", "PM-BOTTLE-LED", "PM-TMB"),
                "derived": True,
                "unboxing_experience": "โทนอบอุ่น ใช้จริงในชีวิตประจำวัน พร้อมข้อความขอบคุณทีมงาน",
            },
            {
                "slug": "select-mid-management",
                "pkg_code": "PKG-XMAS-2026-SELECT-MID",
                "name": "ชุดดูแลใจและโต๊ะทำงานสำหรับหัวหน้าทีม",
                "tier": "Select",
                "segment": "Mid-Management",
                "offer_id": "offer:TDD03-2",
                "offer_code": "TDD03-2",
                "source_offer_code": "TDD03-2",
                "product_codes": ("PM-UMB", "PM-BOTTLE-LED", "PM-TMB"),
                "derived": False,
                "unboxing_experience": None,
            },
            {
                "slug": "signature-c-level",
                "pkg_code": "PKG-XMAS-2026-SIGNATURE-CLEVEL",
                "name": "ชุด Smart Executive สำหรับผู้บริหาร",
                "tier": "Signature",
                "segment": "C-Level",
                "offer_id": "offer:TGC06-4",
                "offer_code": "TGC06-4",
                "source_offer_code": "TGC06-4",
                "product_codes": ("PM-NB", "PM-PB10K", "PM-PEN"),
                "derived": False,
                "unboxing_experience": None,
            },
            {
                "slug": "bespoke",
                "pkg_code": "PKG-XMAS-2026-BESPOKE",
                "name": "ชุด Bespoke สำหรับผู้บริหารตาม brief",
                "tier": "Bespoke",
                "segment": "C-Level",
                "offer_id": None,
                "offer_code": None,
                "source_offer_code": None,
                "product_codes": (),
                "derived": False,
                "unboxing_experience": None,
            },
        ),
    },
    {
        "event_key": "new_year_2027",
        "event_id": "campaign:smartgift-2027-new-year",
        "event_name_th": "New Year 2027",
        "event_name_en": "New Year 2027",
        "headline_th": "เริ่มปีใหม่ด้วยของขวัญที่บอกว่าองค์กรใส่ใจ",
        "supporting_copy_th": "จัดชุดให้เหมาะกับทุกระดับ พร้อมดูรายละเอียดในชุดได้",
        "visual_direction": "clean gold/blue accent, fresh-start utility",
        "packages": (
            {
                "slug": "reach-operations",
                "pkg_code": "PKG-NY-2027-REACH-OPS",
                "name": "ชุด Fresh Start Essentials สำหรับทีมปฏิบัติการ",
                "tier": "Reach",
                "segment": "Operations",
                "offer_id": "offer:smartgift-2027-new-year-reach-operations",
                "offer_code": "SG-OFFER-NY-2027-REACH-OPS",
                "source_offer_code": None,
                "product_codes": ("PM-TMB", "PM-BOTTLE-LED"),
                "derived": True,
                "unboxing_experience": "โทนสะอาดและสดใหม่ อุปกรณ์ที่หยิบใช้ได้ตั้งแต่วันแรกของปี",
            },
            {
                "slug": "select-mid-management",
                "pkg_code": "PKG-NY-2027-SELECT-MID",
                "name": "ชุด Reset & Recharge สำหรับหัวหน้าทีม",
                "tier": "Select",
                "segment": "Mid-Management",
                "offer_id": "offer:TWL01-8",
                "offer_code": "TWL01-8",
                "source_offer_code": "TWL01-8",
                "product_codes": ("PM-AROMA", "PM-CFMUG", "PM-MSG"),
                "derived": False,
                "unboxing_experience": None,
            },
            {
                "slug": "signature-c-level",
                "pkg_code": "PKG-NY-2027-SIGNATURE-CLEVEL",
                "name": "ชุด Plan & Power สำหรับผู้บริหาร",
                "tier": "Signature",
                "segment": "C-Level",
                "offer_id": "offer:TMK0215",
                "offer_code": "TMK0215",
                "source_offer_code": "TMK0215",
                "product_codes": ("PM-PEN", "PM-FLASH", "PM-TEA-INF"),
                "derived": False,
                "unboxing_experience": None,
            },
            {
                "slug": "bespoke",
                "pkg_code": "PKG-NY-2027-BESPOKE",
                "name": "ชุด Bespoke สำหรับผู้บริหารตาม brief",
                "tier": "Bespoke",
                "segment": "C-Level",
                "offer_id": None,
                "offer_code": None,
                "source_offer_code": None,
                "product_codes": (),
                "derived": False,
                "unboxing_experience": None,
            },
        ),
    },
)


def parse_values(text):
    """Accept SQL literals only; expressions, functions and trailing data fail closed."""
    result, pos = [], 0
    while pos < len(text):
        match = LITERAL.match(text, pos)
        if not match:
            raise ValueError("Unsupported SQL literal")
        token, separator = match.groups()
        if token.startswith("'"):
            value = token[1:-1].replace("''", "'")
        elif token in ("NULL", "TRUE", "FALSE"):
            value = {"NULL": None, "TRUE": True, "FALSE": False}[token]
        else:
            decimal = Decimal(token)
            value = int(decimal) if decimal == decimal.to_integral_value() else float(decimal)
            if not math.isfinite(value) or Decimal(str(value)) != decimal:
                raise ValueError("SQL number cannot be exported losslessly")
        result.append(value)
        pos = match.end()
        if separator and not text[pos:].strip():
            raise ValueError("Trailing SQL value separator")
    return result


def parse_snapshot(text):
    """Use SQLite only to recognize statement boundaries, never to execute input."""
    tables = {name: [] for name in TABLE_COLUMNS}
    buffer, start_line = "", 1
    for line_no, line in enumerate(text.splitlines(keepends=True), 1):
        buffer += line
        if not sqlite3.complete_statement(buffer):
            continue
        statement = buffer.strip()
        if statement.startswith("INSERT"):
            match = INSERT.fullmatch(statement)
            if not match or match[1] not in TABLE_COLUMNS:
                raise ValueError(f"Unsupported INSERT at line {start_line}")
            table, columns, values = match.groups()
            columns = [column.strip() for column in columns.split(",")]
            if columns != TABLE_COLUMNS[table].split():
                raise ValueError(f"Unexpected columns in {table}")
            values = parse_values(values)
            if len(columns) != len(values):
                raise ValueError(f"Column/value mismatch in {table}")
            row = dict(zip(columns, values))
            for field in JSON_FIELDS.intersection(row):
                row[field] = json.loads(row[field]) if row[field] is not None else None
            if "source_ref" in row:
                ref = row["source_ref"]
                if not isinstance(ref, dict) or set(ref) != {"file", "rowKey", "sha256"}:
                    raise ValueError(f"Unexpected source_ref in {table}")
                if not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]):
                    raise ValueError(f"Invalid source hash in {table}")
            offset = buffer.index("INSERT")
            row["_line"] = start_line + buffer[:offset].count("\n")
            tables[table].append(row)
        buffer, start_line = "", line_no + 1
    if buffer.strip():
        raise ValueError("Incomplete SQL statement")
    return tables


def parse_factory_catalog(text):
    """Parse the factory catalog dump without executing its DDL or SQL."""
    tables = {name: [] for name in FACTORY_TABLE_COLUMNS}
    buffer, start_line = "", 1
    for line_no, line in enumerate(text.splitlines(keepends=True), 1):
        buffer += line
        if not sqlite3.complete_statement(buffer):
            continue
        statement = re.sub(r"(?m)^\s*--[^\n]*(?:\n|$)", "", buffer.strip()).strip()
        if statement.startswith("INSERT"):
            match = FACTORY_INSERT.fullmatch(statement)
            if not match or match[1] not in FACTORY_TABLE_COLUMNS:
                raise ValueError(f"Unsupported factory INSERT at line {start_line}")
            table, columns, values = match.groups()
            columns = [column.strip() for column in columns.split(",")]
            if columns != FACTORY_TABLE_COLUMNS[table].split():
                raise ValueError(f"Unexpected factory columns in {table}")
            # PostgreSQL dump uses a cast only on the final timestamp literal.
            values = re.sub(r"('(?:[^']|'')*')::timestamptz\s*$", r"\1", values)
            parsed = parse_values(values)
            if len(columns) != len(parsed):
                raise ValueError(f"Factory column/value mismatch in {table}")
            row = dict(zip(columns, parsed))
            row["_line"] = start_line + buffer[:buffer.index("INSERT")].count("\n")
            tables[table].append(row)
        buffer, start_line = "", line_no + 1
    if buffer.strip():
        raise ValueError("Incomplete factory SQL statement")
    return tables


def evaluate_profit(net_revenue=None, total_cost=None, *, bom_complete=False,
                    quantity_complete=False, costs_complete=False, vat_basis_aligned=False,
                    extra_missing=()):
    """A configured pkg passes only with complete inputs and >= THB 25,000 profit."""
    missing = [name for name, complete in (
        ("bom", bom_complete), ("quantity", quantity_complete),
        ("cost_breakdown", costs_complete), ("vat_basis", vat_basis_aligned),
    ) if complete is not True]
    amounts = {}
    for key, value in (("net_revenue", net_revenue), ("total_cost", total_cost)):
        try:
            number = Decimal(str(value))
            if isinstance(value, bool) or not number.is_finite() or number < 0:
                raise ValueError("Invalid amount")
            amounts[key] = number
        except (ValueError, ArithmeticError):
            missing.append(key)
    for name in extra_missing:
        if name not in missing:
            missing.append(name)
    profit = amounts["net_revenue"] - amounts["total_cost"] if not missing else None
    return {
        "net_revenue": float(amounts["net_revenue"]) if "net_revenue" in amounts else None,
        "total_cost": float(amounts["total_cost"]) if "total_cost" in amounts else None,
        "profit": float(profit) if profit is not None else None,
        "minimum_profit": 25000, "currency": "THB",
        "status": "missing_inputs" if missing else ("pass" if profit >= MIN_PROFIT else "below_minimum"),
        "missing_inputs": missing,
    }


def _provenance(table, row, key):
    return {"source_file": SQL_PATH, "source_sha256": SQL_SHA256,
            "source_table": table, "source_key": key, "statement_line": row["_line"],
            "source_ref": row.get("source_ref")}


def _contract_check(record, node, schema):
    required = [key for key, spec in schema["node_ontology"][node]["properties"].items()
                if spec.get("required")]
    missing = [key for key in required if record.get(key) is None or record.get(key) == ""]
    record["entity_type"] = node
    record["contract_validation"] = {"status": "incomplete" if missing else "required_fields_present",
                                     "missing_fields": missing, "promoted": False}
    return record


def _extension_contract_check(record, required):
    missing = [key for key in required if record.get(key) is None or record.get(key) == ""]
    record["contract_validation"] = {
        "status": "incomplete" if missing else "required_fields_present",
        "missing_fields": missing,
        "promoted": False,
    }
    return record


def _canonical_provenance(catalog_hash, source_key, *, kind="canonical_portfolio"):
    return {
        "source_file": CATALOG_PATH,
        "source_sha256": catalog_hash,
        "source_key": source_key,
        "kind": kind,
    }


def _price_at_qty(price_tiers, qty):
    for tier in price_tiers or []:
        if int(tier["min_qty"]) == qty:
            return tier["unit_price"]
    return None


def _offer_price_reference(offer, canonical_products):
    components = offer.get("contains", []) if offer else []
    component_srp_qty1 = Decimal("0")
    component_rows = []
    for component in components:
        product = canonical_products[component["product_code"]]
        unit_price = _price_at_qty(product.get("price_tiers"), 1)
        if unit_price is not None:
            component_srp_qty1 += Decimal(str(unit_price)) * Decimal(str(component["qty"]))
        component_rows.append({
            "product_master_id": component["product_master_id"],
            "product_code": component["product_code"],
            "qty": component["qty"],
            "srp_qty1": unit_price,
        })
    return {
        "offer_price_qty1": _price_at_qty(offer.get("price_tiers"), 1) if offer else None,
        "offer_price_tiers": offer.get("price_tiers", []) if offer else [],
        "component_srp_qty1_reference_total": float(component_srp_qty1) if components else None,
        "component_srp_qty1_reference": component_rows,
        "price_basis": "canonical_master_declared_reference",
        "quote_ready": False,
    }


def _build_seasonal_offers(catalog, catalog_hash):
    canonical_products = {row["code"]: row for row in catalog["canonical_products"]}
    canonical_offers = {row["offer_code"]: row for row in catalog["catalog_offers"]}
    offers = {}
    for event in SEASONAL_PACKAGE_DEFINITIONS:
        for definition in event["packages"]:
            if not definition["offer_id"]:
                continue
            for product_code in definition["product_codes"]:
                if product_code not in canonical_products:
                    raise ValueError(f"Seasonal package references unknown canonical product: {product_code}")
            source = canonical_offers.get(definition["source_offer_code"]) if definition["source_offer_code"] else None
            if definition["source_offer_code"] and source is None:
                raise ValueError(f"Seasonal package references unknown source offer: {definition['source_offer_code']}")
            if source is not None and source["gift_tier"] != definition["tier"]:
                raise ValueError(
                    f"Seasonal offer tier mismatch for {definition['source_offer_code']}: "
                    f"expected {definition['tier']}, got {source['gift_tier']}"
                )
            source_components = source.get("components", []) if source is not None else []
            if source is not None:
                source_product_codes = tuple(component.get("product_code") for component in source_components)
                if source_product_codes != definition["product_codes"]:
                    raise ValueError(
                        f"Seasonal offer component mismatch for {definition['source_offer_code']}: "
                        f"expected {definition['product_codes']}, got {source_product_codes}"
                    )
                component_defs = source_components
            else:
                component_defs = [{"product_code": code, "qty": 1} for code in definition["product_codes"]]
            contains = [
                {
                    "edge_type": "CONTAINS",
                    "product_master_id": f"pm:{component['product_code']}",
                    "product_code": component["product_code"],
                    "qty": component["qty"],
                }
                for component in component_defs
            ]
            if source is not None:
                name = source["name"]
                name_en = source.get("interest_theme") or source["name"]
                unboxing = source["unboxing_experience"]
                price_tiers = source["price_tiers"]
                category_slug = source["interest_theme_slug"]
                source_ref = _canonical_provenance(catalog_hash, source["offer_code"])
                source_kind = "canonical_portfolio_offer"
                offer_status = "candidate"
            else:
                name = definition["name"]
                name_en = definition["name"]
                unboxing = definition["unboxing_experience"]
                price_tiers = []
                category_slug = canonical_products[definition["product_codes"][0]]["category_slug"]
                source_ref = _canonical_provenance(
                    catalog_hash,
                    ",".join(definition["product_codes"]),
                    kind="derived_from_canonical_products",
                )
                source_kind = "derived_recipe_pending_approval"
                offer_status = "candidate"
            record = {
                "id": definition["offer_id"],
                "entity_type": "CatalogOffer",
                "code": definition["offer_code"],
                "source_offer_code": definition["source_offer_code"],
                "name": name,
                "name_en": name_en,
                "gift_tier": definition["tier"],
                "unboxing_experience": unboxing,
                "base_price": _price_at_qty(price_tiers, 1),
                "price_tiers": price_tiers,
                "catalog_slug": category_slug,
                "contains": contains,
                "source_kind": source_kind,
                "status": offer_status,
                "quote_ready": False,
                "provenance": source_ref,
            }
            _extension_contract_check(record, ("id", "code", "name", "gift_tier", "unboxing_experience"))
            existing = offers.get(record["id"])
            if existing is not None and existing != record:
                raise ValueError(f"Conflicting seasonal offer identity: {record['id']}")
            offers[record["id"]] = record
    return [offers[key] for key in sorted(offers)]


def _package_missing_inputs(*, offer, target_recipients=None,
                            factory_identity_complete=False, factory_cost_complete=False):
    missing = []
    if not factory_identity_complete:
        missing.append("factory_identity")
    if not factory_cost_complete:
        missing.append("factory_cost")
    missing.extend((
        "freight_or_cbm_evidence",
        "direct_cost_breakdown",
        "vat_basis",
        "package_price",
        "quote_quantity",
    ))
    if offer is None:
        missing.extend(("catalog_offer", "bom"))
    if target_recipients is None:
        missing.append("target_recipients")
    return tuple(missing)


def _standard_qty_tiers(price_rows):
    """Quantity tiers that are commercially plausible for smartgift_price:
    the codebase's own declared meaningful quantities (SRP_QTY_TIERS) plus
    whatever else recurs often enough in this run's raw rows to be a real
    FlowAccount group-ladder point rather than a one-off data-entry slip."""
    counts = Counter(row["qty_tier"] for row in price_rows
                     if row["qty_tier"] is not None and row["qty_tier"] > 0)
    frequent = {tier for tier, count in counts.items() if count >= MIN_STANDARD_TIER_OCCURRENCES}
    return frozenset(SRP_QTY_TIERS) | frequent


def _cost_mapping_entry(cost_mapping, product_code):
    entry = cost_mapping.get(product_code)
    if entry is None:
        return None
    # A composite entry (e.g. USB shell + chip) carries no single supplier code.
    factory_code = entry.get("factory_item_code") or f"COMPOSITE:{entry.get('factory_item_name')}"
    return {
        "factory_product_code": factory_code,
        "factory_unit_price": entry["exw_price"],
        "factory_currency": entry["currency"],
        "factory_unit_cny": entry["exw_price"] if entry["currency"] == "RMB" else None,
        "fx_rate_to_thb": entry["fx_rate_to_thb"],
        "factory_cost_thb": entry["exw_cost_thb"],
        "factory_cost_basis": "EXW_confirmed_mapping",
        "confidence": entry.get("confidence"),
    }


def _build_package_bom(bundle_id, offer, canonical_products, catalog_hash, cost_mapping):
    rows = []
    if offer is None:
        return rows
    for component in offer["contains"]:
        product = canonical_products[component["product_code"]]
        packaging = product.get("packaging_carton") or {}
        logistics = product.get("logistics_freight_est") or {}
        cost = _cost_mapping_entry(cost_mapping, component["product_code"])
        rows.append({
            "bundle_id": bundle_id,
            "offer_id": offer["id"],
            "product_master_id": component["product_master_id"],
            "product_code": component["product_code"],
            "qty": component["qty"],
            "name_th": product["name_th"],
            "name_en": product["name_en"],
            "product_family": product["product_family"],
            "category_slug": product["category_slug"],
            "unit_srp_qty1": _price_at_qty(product.get("price_tiers"), 1),
            "factory_product_code": cost["factory_product_code"] if cost else None,
            "factory_unit_price": cost["factory_unit_price"] if cost else None,
            "factory_currency": cost["factory_currency"] if cost else None,
            "factory_unit_cny": cost["factory_unit_cny"] if cost else None,
            "fx_rate_to_thb": cost["fx_rate_to_thb"] if cost else None,
            "factory_cost_thb": cost["factory_cost_thb"] if cost else None,
            "factory_cost_basis": cost["factory_cost_basis"] if cost else None,
            "factory_match_status": ("confirmed_supplier_mapping" if cost else "missing_factory_match"),
            "cbm_per_unit": packaging.get("cbm_per_unit"),
            "cbm_source": "master_packaging_estimate",
            "declared_freight_reference_per_unit_thb": logistics.get("freight_thb_per_unit"),
            "freight_basis": "declared_scenario" if logistics.get("freight_thb_per_unit") is not None else None,
            "cost_status": "exw_cost_confirmed" if cost else "missing_factory_identity",
            "verified": False,
            "provenance": _canonical_provenance(
                catalog_hash,
                f"{offer['code']}:{component['product_code']}",
                kind="canonical_offer_component",
            ),
            "cost_provenance": ({
                "source_file": COST_MAPPING_PATH,
                "source_sha256": COST_MAPPING_SHA256,
                "source_key": component["product_code"],
                "kind": "confirmed_factory_cost_mapping",
            } if cost else None),
        })
    return rows


def _package_cost_reference(offer, bom_rows, canonical_products):
    """Internal-only EXW cost roll-up per set. Never enters the public projection."""
    if offer is None:
        return None
    components = offer.get("contains", [])
    costed = [row for row in bom_rows if row["factory_cost_thb"] is not None]
    fully_costed = len(costed) == len(components) and components
    exw_total = round(sum(row["factory_cost_thb"] * row["qty"] for row in costed), 2) if fully_costed else None
    lowest_tier = min(offer.get("price_tiers") or [], key=lambda tier: tier["min_qty"], default=None)
    indicative = None
    if fully_costed and lowest_tier is not None:
        indicative = {
            "basis": f"offer_price_at_min_qty_{int(lowest_tier['min_qty'])}_minus_exw_component_cost",
            "offer_unit_price": lowest_tier["unit_price"],
            "at_qty": int(lowest_tier["min_qty"]),
            "indicative_set_profit_thb": round(lowest_tier["unit_price"] - exw_total, 2),
            "excludes": ["freight", "duty", "packaging", "branding", "vat_alignment"],
        }
    srp_total = sum(
        (_price_at_qty(canonical_products[component["product_code"]].get("price_tiers"), 1) or 0)
        * component["qty"] for component in components
    ) if components else None
    return {
        "costed_components": len(costed),
        "total_components": len(components),
        "coverage": "full" if fully_costed else ("partial" if costed else "none"),
        "exw_cost_per_set_thb": exw_total,
        "component_srp_qty1_total": srp_total if components else None,
        "cost_basis": "EXW_confirmed_mapping_no_freight_no_duty",
        "indicative_profit": indicative,
        "quote_ready": False,
    }


def _build_seasonal_packages(catalog, schema, catalog_hash, category_slugs, cost_mapping):
    canonical_products = {row["code"]: row for row in catalog["canonical_products"]}
    seasonal_offers = _build_seasonal_offers(catalog, catalog_hash)
    offer_by_id = {row["id"]: row for row in seasonal_offers}
    packages, bom = [], []
    for event in SEASONAL_PACKAGE_DEFINITIONS:
        fixed = []
        for definition in event["packages"]:
            bundle_id = f"bundle:smartgift-{event['event_key']}-{definition['slug']}"
            offer = offer_by_id.get(definition["offer_id"]) if definition["offer_id"] else None
            options = []
            package_bom = []
            if offer is not None:
                options.append({
                    "option_id": f"option:{bundle_id.removeprefix('bundle:')}:{offer['code']}",
                    "bundle_id": bundle_id,
                    "catalog_slug": offer["catalog_slug"],
                    "gift_tier_id": f"tier:{definition['tier']}",
                    "recipient_segment_id": f"seg:{definition['segment']}",
                    "offer_id": offer["id"],
                    "offer_code": offer["code"],
                    "qty": 1,
                    "bom_ref": {"bundle_id": bundle_id, "offer_id": offer["id"]},
                    "bom_status": "proposed_recipe",
                })
                fixed.append((definition, offer))
                package_bom = _build_package_bom(bundle_id, offer, canonical_products, catalog_hash, cost_mapping)
                bom.extend(package_bom)
            cost_reference = _package_cost_reference(offer, package_bom, canonical_products)
            fully_costed = cost_reference is not None and cost_reference["coverage"] == "full"
            if offer is None:
                status = "draft"
            elif definition["derived"]:
                status = "mapping_pending"
            elif fully_costed:
                status = "missing_inputs"  # factory cost landed; commercial inputs still open
            else:
                status = "cost_pending"
            package = {
                "id": bundle_id,
                "code": definition["pkg_code"],
                "name": definition["name"],
                "occasion": event["event_key"],
                "event": {
                    "id": event["event_id"],
                    "name_th": event["event_name_th"],
                    "name_en": event["event_name_en"],
                    "date_status": "year_assumption_pending_confirmation",
                },
                "status": status,
                "target_recipients": None,
                "total_price": None,
                "gift_tier": definition["tier"],
                "gift_tier_id": f"tier:{definition['tier']}",
                "recipient_segment": definition["segment"],
                "recipient_segment_id": f"seg:{definition['segment']}",
                "tier_breakdown": {
                    definition["segment"]: {
                        "segment_id": f"seg:{definition['segment']}",
                        "tier_id": f"tier:{definition['tier']}",
                        "count": None,
                    }
                },
                "design_scope": {
                    "catalog_slugs": sorted({canonical_products[code]["category_slug"] for code in definition["product_codes"]})
                    if definition["product_codes"] else [],
                    "gift_tiers": [definition["tier"]],
                    "status": "seasonal_candidate",
                },
                "options": options,
                "bom_status": "proposed_recipe" if offer is not None else "not_designed",
                "quote_ready": False,
                "price_reference": _offer_price_reference(offer, canonical_products),
                "cost_reference": cost_reference,
                "profit_evaluation": evaluate_profit(
                    bom_complete=offer is not None,
                    quantity_complete=False,
                    extra_missing=_package_missing_inputs(
                        offer=offer, target_recipients=None,
                        factory_identity_complete=fully_costed,
                        factory_cost_complete=fully_costed,
                    ),
                ),
                "ad_creative": {
                    "customer_safe": True,
                    "headline_th": event["headline_th"],
                    "supporting_copy_th": event["supporting_copy_th"],
                    "visual_direction": event["visual_direction"],
                    "cta_th": "ดูของในชุด",
                    "claim_status": "draft_copy",
                },
                "source_ref": {
                    "kind": "approved_seasonal_design",
                    "definition_key": f"{event['event_key']}:{definition['slug']}",
                    "catalog_source_file": CATALOG_PATH,
                    "catalog_source_sha256": catalog_hash,
                },
            }
            _contract_check(package, "BundleOffer", schema)
            packages.append(package)
        # A mixed parent is only a template until the company order brief supplies counts.
        mixed_slug = f"{event['event_key']}-corporate-mix"
        mixed_id = f"bundle:smartgift-{mixed_slug}"
        mixed_offers = []
        tier_breakdown = {}
        for definition in fixed:
            package_definition, offer = definition
            segment = package_definition["segment"]
            mixed_offers.append({
                "option_id": f"option:{mixed_id.removeprefix('bundle:')}:{offer['code']}",
                "bundle_id": mixed_id,
                "catalog_slug": offer["catalog_slug"],
                "gift_tier_id": f"tier:{package_definition['tier']}",
                "recipient_segment_id": f"seg:{segment}",
                "offer_id": offer["id"],
                "offer_code": offer["code"],
                "qty": None,
                "qty_source": "company_order_brief",
                "bom_ref": None,
                "bom_status": "pending_segment_counts",
            })
            tier_breakdown[segment] = {
                "segment_id": f"seg:{segment}",
                "tier_id": f"tier:{package_definition['tier']}",
                "offer_id": offer["id"],
                "count": None,
            }
        mixed = {
            "id": mixed_id,
            "code": f"PKG-{('XMAS-2026' if event['event_key'] == 'christmas_2026' else 'NY-2027')}-CORP-MIX",
            "name": f"แพ็กเกจองค์กร {event['event_name_th']} (Corporate Mix)",
            "occasion": event["event_key"],
            "event": {
                "id": event["event_id"],
                "name_th": event["event_name_th"],
                "name_en": event["event_name_en"],
                "date_status": "year_assumption_pending_confirmation",
            },
            "status": "draft",
            "target_recipients": None,
            "total_price": None,
            "gift_tier": None,
            "gift_tier_id": None,
            "recipient_segment": "mixed",
            "recipient_segment_id": None,
            "tier_breakdown": tier_breakdown,
            "design_scope": {"catalog_slugs": sorted({offer["catalog_slug"] for _, offer in fixed}),
                             "gift_tiers": sorted({definition["tier"] for definition, _ in fixed}),
                             "status": "company_order_brief_required"},
            "options": mixed_offers,
            "bom_status": "pending_segment_counts",
            "quote_ready": False,
            "price_reference": {offer["id"]: _offer_price_reference(offer, canonical_products)
                                 for _, offer in fixed},
            "profit_evaluation": evaluate_profit(extra_missing=(
                "segment_counts", "package_price", "quote_quantity", "factory_identity",
                "factory_cost", "freight_or_cbm_evidence", "direct_cost_breakdown", "vat_basis",
            )),
            "ad_creative": {
                "customer_safe": True,
                "headline_th": event["headline_th"],
                "supporting_copy_th": "จัดชุดตามโครงสร้าง C-Level, Mid-Management และ Operations",
                "visual_direction": event["visual_direction"],
                "cta_th": "ดูของในชุด",
                "claim_status": "draft_copy",
            },
            "source_ref": {
                "kind": "approved_seasonal_design",
                "definition_key": mixed_slug,
                "catalog_source_file": CATALOG_PATH,
                "catalog_source_sha256": catalog_hash,
            },
        }
        _contract_check(mixed, "BundleOffer", schema)
        packages.append(mixed)
    return seasonal_offers, packages, bom


def _scan_privacy(value, path="root"):
    if isinstance(value, dict):
        for key, child in value.items():
            _scan_privacy(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_privacy(child, f"{path}[{index}]")
    elif isinstance(value, str) and PII_PATTERN.search(value):
        raise ValueError(f"Potential contact data requires review at {path}")


def _positive_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def _valid_qty(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == int(value) and value > 0


def _factory_provenance(row):
    return {
        "source_file": FACTORY_PATH,
        "source_sha256": FACTORY_SHA256,
        "source_table": "products",
        "source_key": f"{row['catalog_key']}:{row['code']}",
        "statement_line": row["_line"],
    }


def _small_order_factor(qty, rules):
    if not _valid_qty(qty):
        return None
    for tier in rules["small_order_factors"]:
        max_qty = tier["max_qty"]
        if isinstance(max_qty, str) and max_qty == ".inf":
            return float(tier["sof"])
        if qty <= max_qty:
            return float(tier["sof"])
    return None


def _goods_type(catalog_key):
    return "electronic_tisi" if catalog_key == "powerbank" else "general"


def _freight_estimate(row, qty, rules, *, catalog_key=None):
    """Calculate a declared shipping scenario only when carton data is complete."""
    empty = {
        "units_per_carton": row.get("upc") if row else None,
        "carton_dimensions_cm": ({key: row.get(key) for key in ("length", "width", "height")}
                                  if row and "length" in row else None),
        "carton_cbm": None, "carton_gross_kg": row.get("kg") if row else None,
        "shipping_context": None, "rate_thb_per_cbm": None, "rate_thb_per_kg": None,
        "cartons": None, "chargeable_basis": None, "charged_volume_cbm": None,
        "freight_total_thb": None, "freight_per_unit_thb": None,
    }
    if not row or not _valid_qty(qty):
        return empty
    upc = row.get("upc")
    dimensions = [row.get(key) for key in ("length", "width", "height")]
    kg = row.get("kg")
    if not _positive_number(upc) or not all(_positive_number(value) for value in dimensions):
        return empty
    carton_cbm = round(dimensions[0] * dimensions[1] * dimensions[2] / 1_000_000, 6)
    if not _positive_number(carton_cbm):
        return empty
    route, mode, tier = "guangzhou_shenzhen", "truck", "GOLD"
    goods = _goods_type(catalog_key or row.get("catalog_key"))
    rate = rules["shipping_rate_matrix"][route][mode][goods][tier]
    cartons = math.ceil(qty / int(upc))
    charged_volume = round(cartons * max(carton_cbm, float(rules["logistics_density_and_freight"]["min_chargeable_cbm"])), 2)
    density = (kg / carton_cbm) if _positive_number(kg) else None
    chargeable_basis = "weight" if density is not None and density >= float(rules["logistics_density_and_freight"]["density_threshold_kg_per_cbm"]) else "volume"
    weight = round(cartons * kg, 2) if _positive_number(kg) else None
    if chargeable_basis == "weight" and weight is not None:
        freight_total = round(weight * rate["kg"], 2)
    else:
        freight_total = round(charged_volume * rate["cbm"], 2)
    return {
        "units_per_carton": int(upc),
        "carton_dimensions_cm": {"length": dimensions[0], "width": dimensions[1], "height": dimensions[2]},
        "carton_cbm": carton_cbm,
        "carton_gross_kg": kg,
        "shipping_context": {"warehouse": route, "mode": mode, "goods_type": goods,
                              "member_tier": tier, "basis": "declared_scenario"},
        "rate_thb_per_cbm": rate["cbm"], "rate_thb_per_kg": rate["kg"],
        "cartons": cartons, "chargeable_basis": chargeable_basis,
        "charged_volume_cbm": charged_volume, "freight_total_thb": freight_total,
        "freight_per_unit_thb": round(freight_total / qty, 4),
    }


def _factory_reference(row, qty, rules):
    factory_cny = row.get("rmb") if row and _positive_number(row.get("rmb")) else None
    fx = float(rules["currency_exchange_rates"]["cny_to_thb"])
    reference = round(factory_cny * fx, 4) if factory_cny is not None else None
    sof = _small_order_factor(qty, rules)
    adjusted = round(reference * sof, 4) if reference is not None and sof is not None else None
    return factory_cny, fx, reference, sof, adjusted


def _comparison_status(*, sale_valid, qty_valid, factory_row, factory_cny, freight):
    if not sale_valid or not qty_valid:
        return "invalid_sale_or_qty"
    if factory_row is None or factory_cny is None:
        return "missing_factory_match"
    if freight["freight_per_unit_thb"] is None:
        return "factory_reference_only"
    return "freight_estimate_only"


def _build_price_comparison(price_row, factory_row, rules, source_run_id):
    sale_valid = (not price_row["price_missing"] and _positive_number(price_row.get("unit_price")))
    qty_valid = _valid_qty(price_row.get("qty_tier"))
    qty = int(price_row["qty_tier"]) if qty_valid else None
    factory_cny, fx, factory_reference, sof, factory_adjusted = _factory_reference(factory_row, qty, rules)
    freight_row = None
    if factory_row is not None:
        freight_row = {"catalog_key": factory_row["catalog_key"], "upc": factory_row["upc"],
                       "length": factory_row["dim_l"], "width": factory_row["dim_w"],
                       "height": factory_row["dim_h"], "kg": factory_row["kg"]}
    freight = _freight_estimate(freight_row, qty, rules,
                                catalog_key=factory_row["catalog_key"] if factory_row else None)
    missing = []
    if not sale_valid:
        missing.append("sale_price")
    if not qty_valid:
        missing.append("qty_tier")
    if factory_row is None:
        missing.extend(["factory_identity", "factory_cost"])
    elif factory_cny is None:
        missing.append("factory_cost")
    if factory_row is not None and freight["freight_per_unit_thb"] is None:
        for field in ("units_per_carton", "carton_dimensions_cm", "carton_gross_kg"):
            if freight[field] is None or (isinstance(freight[field], dict) and any(value is None for value in freight[field].values())):
                missing.append(f"logistics_{field}")
    missing.append("direct_cost_breakdown")
    status = _comparison_status(sale_valid=sale_valid, qty_valid=qty_valid,
                                factory_row=factory_row, factory_cny=factory_cny, freight=freight)
    sale_price = price_row["unit_price"] if sale_valid else None
    delivered = None
    profit = None
    margin = None
    return {
        "comparison_id": f"PRICE-{price_row['id']}",
        "price_id": price_row["id"], "offer_code": price_row["offer_code"],
        "qty_tier": qty, "price_list_group": price_row["price_list_group"],
        "source_run_id": source_run_id,
        "sale_unit_price": sale_price,
        "sale_unit_price_with_vat": price_row.get("unit_price_with_vat") if sale_valid else None,
        "sale_vat_basis": "source_unit_price_pair_unverified",
        "sale_export_date": price_row["export_date"],
        "factory_catalog_key": factory_row["catalog_key"] if factory_row else None,
        "factory_product_code": factory_row["code"] if factory_row else None,
        "factory_unit_cny": factory_cny, "fx_thb_per_cny": fx,
        "factory_reference_thb": factory_reference,
        "factory_cost_thb": factory_reference,
        "small_order_factor": sof, "factory_adjusted_estimate_thb": factory_adjusted,
        "factory_export_date": factory_row["synced_at"][:10] if factory_row else None,
        **freight,
        "delivered_unit_cost": delivered, "unit_profit": profit, "margin_percent": margin,
        "comparison_status": status, "missing_inputs": sorted(set(missing)),
        "identity_review_required": True, "quote_ready": False,
        "provenance": {"sale": _provenance("smartgift_price", price_row, price_row["id"]),
                       "factory": _factory_provenance(factory_row) if factory_row else None,
                       "pricing_rules": {"source_file": PRICING_RULES_PATH,
                                         "source_sha256": PRICING_RULES_SHA256}},
    }


def _build_srp_comparisons(catalog, factory_by_code, rules, catalog_hash):
    references, comparisons = [], []
    for product in sorted(catalog["canonical_products"], key=lambda row: row["code"]):
        tiers = {int(tier["min_qty"]): tier["unit_price"] for tier in product["price_tiers"]}
        if tuple(sorted(tiers)) != SRP_QTY_TIERS:
            raise ValueError(f"SRP quantity tiers must be {list(SRP_QTY_TIERS)} for {product['code']}")
        factory = factory_by_code.get(product["code"])
        factory_cny = factory["rmb"] if factory and _positive_number(factory.get("rmb")) else None
        references.append({
            "product_code": product["code"], "product_master_id": product["product_master"],
            "product_family": product["product_family"], "category_slug": product["category_slug"],
            "name_th": product["name_th"], "name_en": product["name_en"],
            "srp_price": product["srp_price"], "price_tiers": product["price_tiers"],
            "factory_match_status": "exact_code_match" if factory else "missing_factory_match",
            "factory_product_code": factory["code"] if factory else None,
            "factory_catalog_key": factory["catalog_key"] if factory else None,
            "factory_unit_cny": factory_cny,
            "factory_provenance": _factory_provenance(factory) if factory else None,
            "srp_provenance": {"source_file": CATALOG_PATH, "source_sha256": catalog_hash,
                               "source_key": product["code"]},
        })
        packaging = product.get("packaging_carton") or {}
        logistics = product.get("logistics_freight_est") or {}
        dims = {"length": packaging.get("carton_length_cm"), "width": packaging.get("carton_width_cm"),
                "height": packaging.get("carton_height_cm"), "upc": packaging.get("upc"),
                "kg": packaging.get("carton_weight_kg"),
                "catalog_key": "powerbank" if product["category_slug"] == "executive-smart-tech" else "giftset"}
        for qty in SRP_QTY_TIERS:
            freight = _freight_estimate(dims, qty, rules, catalog_key=dims["catalog_key"])
            factory_ref = round(factory_cny * float(rules["currency_exchange_rates"]["cny_to_thb"]), 4) if factory_cny is not None else None
            sof = _small_order_factor(qty, rules) if factory_cny is not None else None
            adjusted = round(factory_ref * sof, 4) if factory_ref is not None and sof is not None else None
            missing = ["direct_cost_breakdown"]
            if factory is None:
                missing.extend(["factory_identity", "factory_cost"])
            if freight["freight_per_unit_thb"] is None:
                missing.append("cbm_logistics")
            comparisons.append({
                "comparison_id": f"SRP-{product['code']}-{qty}",
                "product_code": product["code"], "product_master_id": product["product_master"],
                "product_family": product["product_family"], "category_slug": product["category_slug"],
                "qty": qty, "srp_unit_price": tiers[qty], "srp_source": "master_declared",
                "factory_catalog_key": factory["catalog_key"] if factory else None,
                "factory_product_code": factory["code"] if factory else None,
                "factory_unit_cny": factory_cny,
                "fx_thb_per_cny": float(rules["currency_exchange_rates"]["cny_to_thb"]),
                "factory_reference_thb": factory_ref, "small_order_factor": sof,
                "factory_adjusted_estimate_thb": adjusted,
                "factory_cost_thb": factory_ref,
                "cbm_source": "master_packaging_estimate",
                **freight,
                "cbm_per_unit": packaging.get("cbm_per_unit"),
                "master_freight_estimate_per_unit_thb": logistics.get("freight_thb_per_unit"),
                "delivered_unit_cost": None, "unit_profit": None, "margin_percent": None,
                "comparison_status": "missing_factory_match" if factory is None else "factory_reference_only",
                "missing_inputs": sorted(set(missing)), "identity_review_required": True,
                "quote_ready": False,
                "provenance": {"srp": {"source_file": CATALOG_PATH, "source_sha256": catalog_hash,
                                         "source_key": product["code"], "qty": qty},
                               "factory": _factory_provenance(factory) if factory else None,
                               "pricing_rules": {"source_file": PRICING_RULES_PATH,
                                                 "source_sha256": PRICING_RULES_SHA256}},
            })
    return references, comparisons


def validate_master(data):
    def ids(key, field):
        values = [row[field] for row in data[key]]
        if len(values) != len(set(values)) or any(value is None for value in values):
            raise ValueError(f"Duplicate or missing ID in {key}")
        return set(values)

    products = ids("product_masters", "code")
    families = ids("product_families", "code")
    offers = ids("catalog_offers", "code")
    seasonal_offers = data.get("seasonal_offers", [])
    seasonal_offer_ids = {row.get("id") for row in seasonal_offers}
    seasonal_offer_codes = {row.get("code") for row in seasonal_offers}
    if None in seasonal_offer_ids or None in seasonal_offer_codes:
        raise ValueError("Missing seasonal CatalogOffer identity")
    if len(seasonal_offer_ids) != len(seasonal_offers) or len(seasonal_offer_codes) != len(seasonal_offers):
        raise ValueError("Duplicate seasonal CatalogOffer identity")
    categories = ids("portfolio_catalogs", "slug")
    tiers = ids("customer_tiers", "name")
    ids("prices", "id")
    package_codes = ids("pkg", "code")
    package_ids = {row.get("id") for row in data["pkg"]}
    if None in package_ids or len(package_ids) != len(data["pkg"]):
        raise ValueError("Missing or duplicate BundleOffer identity")
    if any(not value.startswith("bundle:") for value in package_ids):
        raise ValueError("BundleOffer identity must use bundle: prefix")
    if any(not value.startswith("offer:") for value in seasonal_offer_ids):
        raise ValueError("Seasonal CatalogOffer identity must use offer: prefix")
    srp_products = ids("srp_reference_products", "product_code")
    ids("price_comparisons", "comparison_id")
    ids("srp_qty_comparisons", "comparison_id")
    for product in data["product_masters"]:
        if product["product_family_id"] is not None and product["product_family_id"] not in families:
            raise ValueError("Orphan product family")
    pairs = set()
    for link in data["offer_product_links"]:
        pair = (link["product_code"], link["offer_code"])
        if pair in pairs or pair[0] not in products or pair[1] not in offers or "qty" in link:
            raise ValueError("Invalid model-offer association")
        pairs.add(pair)
    if any(row["offer_code"] not in offers for row in data["prices"]):
        raise ValueError("Orphan price offer")
    for offer in seasonal_offers:
        if offer["gift_tier"] not in tiers:
            raise ValueError("Unknown seasonal GiftTier")
        if not offer["contract_validation"]["status"] in ("required_fields_present", "incomplete"):
            raise ValueError("Invalid seasonal CatalogOffer contract status")
        contains_keys = set()
        for component in offer.get("contains", []):
            key = (component.get("product_master_id"), component.get("product_code"))
            if key in contains_keys or component.get("product_code") not in srp_products:
                raise ValueError("Invalid seasonal CONTAINS reference")
            if component.get("product_master_id") != f"pm:{component.get('product_code')}":
                raise ValueError("Seasonal ProductMaster identity mismatch")
            if not _valid_qty(component.get("qty")):
                raise ValueError("Seasonal CONTAINS quantity must be positive integer")
            contains_keys.add(key)
    for pkg in data["pkg"]:
        if pkg.get("status") not in PACKAGE_STATUSES:
            raise ValueError("Unknown package status")
        if not set(pkg["design_scope"]["catalog_slugs"]).issubset(categories):
            raise ValueError("Package catalog scope mismatch")
        if not set(pkg["design_scope"]["gift_tiers"]).issubset(tiers):
            raise ValueError("Package GiftTier scope mismatch")
        if pkg["profit_evaluation"]["minimum_profit"] != int(MIN_PROFIT):
            raise ValueError("Package profit floor mismatch")
        if pkg["profit_evaluation"]["status"] not in PACKAGE_STATUSES:
            raise ValueError("Unknown package profit status")
        for option in pkg.get("options", []):
            if option.get("bundle_id") != pkg["id"]:
                raise ValueError("Package option FK mismatch")
            offer_id = option.get("offer_id")
            if offer_id not in seasonal_offer_ids:
                raise ValueError("Orphan seasonal package offer")
            qty = option.get("qty")
            if qty is None:
                if pkg["status"] != "draft":
                    raise ValueError("Configured package option cannot have null qty")
            elif not _valid_qty(qty):
                raise ValueError("Package option quantity must be positive integer")
    bom_keys = set()
    for row in data.get("bom", []):
        key = (row.get("bundle_id"), row.get("offer_id"), row.get("product_code"))
        if key in bom_keys or row.get("bundle_id") not in package_ids:
            raise ValueError("Invalid seasonal BOM package reference")
        if row.get("offer_id") not in seasonal_offer_ids or row.get("product_code") not in srp_products:
            raise ValueError("Invalid seasonal BOM identity reference")
        if row.get("product_master_id") != f"pm:{row.get('product_code')}":
            raise ValueError("Seasonal BOM ProductMaster identity mismatch")
        if not _valid_qty(row.get("qty")):
            raise ValueError("Seasonal BOM quantity must be positive integer")
        if row.get("verified") is not False:
            raise ValueError("Seasonal BOM must remain unverified until cost evidence is approved")
        if row.get("factory_product_code") is None and any(row.get(field) is not None for field in (
                "factory_unit_cny", "factory_cost_thb")):
            raise ValueError("Factory cost fabricated without seasonal identity")
        product_ref = next((item for item in data["srp_reference_products"]
                            if item["product_code"] == row["product_code"]), None)
        tier_prices = {tier["min_qty"]: tier["unit_price"] for tier in product_ref["price_tiers"]} if product_ref else {}
        if row.get("unit_srp_qty1") != tier_prices.get(1):
            raise ValueError("Seasonal BOM SRP reference mismatch")
        bom_keys.add(key)
    expected_bom_keys = set()
    for pkg in data["pkg"]:
        for option in pkg.get("options", []):
            if option.get("qty") is None or option.get("bom_status") != "proposed_recipe":
                continue
            offer = next(row for row in seasonal_offers if row["id"] == option["offer_id"])
            for component in offer.get("contains", []):
                expected_bom_keys.add((pkg["id"], offer["id"], component["product_code"]))
    if expected_bom_keys != bom_keys:
        raise ValueError("Seasonal BOM coverage mismatch")
    if {row["price_id"] for row in data["price_comparisons"]} != {row["id"] for row in data["prices"]}:
        raise ValueError("Price comparison coverage mismatch")
    if len(data["price_comparisons"]) != len(data["prices"]):
        raise ValueError("Duplicate or missing price comparison")
    for row in data["price_comparisons"]:
        if row["factory_product_code"] is None and any(row[field] is not None for field in (
                "factory_unit_cny", "factory_reference_thb", "factory_cost_thb",
                "factory_adjusted_estimate_thb")):
            raise ValueError("Factory cost fabricated without price identity")
    srp_pairs = set()
    srp_by_product = {row["product_code"]: row for row in data["srp_reference_products"]}
    for row in data["srp_qty_comparisons"]:
        pair = (row["product_code"], row["qty"])
        if pair in srp_pairs or row["product_code"] not in srp_products or row["qty"] not in SRP_QTY_TIERS:
            raise ValueError("Invalid SRP quantity comparison")
        srp_pairs.add(pair)
        tier_prices = {tier["min_qty"]: tier["unit_price"]
                       for tier in srp_by_product[row["product_code"]]["price_tiers"]}
        if row["qty"] not in tier_prices or row["srp_unit_price"] != tier_prices[row["qty"]]:
            raise ValueError("SRP quantity price mismatch")
        if row["factory_product_code"] is None and any(row[field] is not None for field in (
                "factory_unit_cny", "factory_reference_thb", "factory_adjusted_estimate_thb", "factory_cost_thb")):
            raise ValueError("Factory cost fabricated without identity")
    if len(srp_pairs) != len(data["srp_reference_products"]) * len(SRP_QTY_TIERS):
        raise ValueError("SRP quantity tier coverage mismatch")
    _scan_privacy(data)


def build_public_projection(data):
    """Return the customer-safe allowlist used by the deployed Expo endpoint."""

    def pick(row, fields):
        return {field: row.get(field) for field in fields if field in row}

    public = {
        "metadata": {
            "schema_version": data["metadata"]["schema_version"],
            "contract_ref": data["metadata"]["contract_ref"],
            "contract_version": data["metadata"]["contract_version"],
            "status": "customer_safe",
            "public_allowlist_version": "1.0.0",
            "quantity_tiers": list(SRP_QTY_TIERS),
        },
        "product_masters": [pick(row, (
            "code", "name_th", "name_en", "category", "product_family_id",
            "display_name", "colors", "entity_type")) for row in data["product_masters"]],
        "product_families": [pick(row, (
            "code", "name_th", "name_en", "aliases_th", "aliases_en"))
            for row in data["product_families"]],
        "portfolio_catalogs": [pick(row, ("entity_type", "slug", "name_th", "name_en"))
                               for row in data["portfolio_catalogs"]],
        "customer_tiers": [pick(row, ("entity_type", "name")) for row in data["customer_tiers"]],
        "catalog_offers": [pick(row, (
            "code", "name_th", "name_en", "description", "offer_kind", "status",
            "branding", "image", "name", "gift_tier", "unboxing_experience",
            "entity_type")) for row in data["catalog_offers"]],
        "seasonal_offers": [pick(row, (
            "id", "entity_type", "code", "source_offer_code", "name", "name_en",
            "gift_tier", "unboxing_experience", "base_price", "price_tiers", "catalog_slug",
            "contains", "source_kind", "status"))
            for row in data["seasonal_offers"]],
        "pkg": [pick(row, (
            "id", "code", "name", "occasion", "event", "status", "target_recipients",
            "total_price", "gift_tier", "gift_tier_id", "recipient_segment",
            "recipient_segment_id", "tier_breakdown", "design_scope", "options", "bom_status",
            "price_reference", "ad_creative", "entity_type"))
            for row in data["pkg"]],
        "bom": [pick(row, (
            "bundle_id", "offer_id", "product_master_id", "product_code", "qty", "name_th",
            "name_en", "product_family", "category_slug", "unit_srp_qty1"))
            for row in data["bom"]],
        "prices": [pick(row, (
            "id", "offer_code", "qty_tier", "unit_price", "unit_price_with_vat",
            "price_missing", "data_quality_issues"))
            for row in data["prices"]],
        "srp_reference_products": [pick(row, (
            "product_code", "product_master_id", "product_family", "category_slug", "name_th",
            "name_en", "srp_price", "price_tiers")) for row in data["srp_reference_products"]],
        "srp_qty_comparisons": [pick(row, (
            "comparison_id", "product_code", "product_master_id", "product_family",
            "category_slug", "qty", "srp_unit_price", "srp_source"))
            for row in data["srp_qty_comparisons"]],
    }
    public["metadata"]["counts"] = {
        key: len(value) for key, value in public.items() if isinstance(value, list)
    }
    validate_public_projection(public)
    return public


def validate_public_projection(data):
    """Fail closed if an internal or personal field enters the public allowlist."""
    found = []

    def walk(value, path=""):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in PUBLIC_FORBIDDEN_FIELDS:
                    found.append(f"{path}/{key}")
                walk(child, f"{path}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}/{index}")

    walk(data)
    if found:
        raise ValueError(f"Forbidden field in public projection: {found[0]}")


def build_master(root=ROOT):
    root = Path(root)
    inputs = {path: (root / path).read_bytes() for path in (
        SQL_PATH, FACTORY_PATH, SCHEMA_PATH, CATALOG_PATH, PRICING_RULES_PATH, COST_MAPPING_PATH)}
    hashes = {path: hashlib.sha256(content).hexdigest() for path, content in inputs.items()}
    if hashes[SQL_PATH] != SQL_SHA256:
        raise ValueError("SQL snapshot hash changed; review source diff before exporting")
    if hashes[FACTORY_PATH] != FACTORY_SHA256:
        raise ValueError("Factory catalog hash changed; review source diff before exporting")
    if hashes[PRICING_RULES_PATH] != PRICING_RULES_SHA256:
        raise ValueError("Pricing rules hash changed; review source diff before exporting")
    if hashes[COST_MAPPING_PATH] != COST_MAPPING_SHA256:
        raise ValueError("Confirmed cost mapping hash changed; review mapping diff before exporting")
    tables = parse_snapshot(inputs[SQL_PATH].decode("utf-8-sig"))
    if {table: len(rows) for table, rows in tables.items()} != EXPECTED_COUNTS:
        raise ValueError("SQL snapshot counts do not reconcile")
    factory_tables = parse_factory_catalog(inputs[FACTORY_PATH].decode("utf-8-sig"))
    if {table: len(rows) for table, rows in factory_tables.items()} != EXPECTED_FACTORY_COUNTS:
        raise ValueError("Factory catalog counts do not reconcile")
    schema = yaml.safe_load(inputs[SCHEMA_PATH].decode("utf-8-sig"))
    catalog = json.loads(inputs[CATALOG_PATH].decode("utf-8-sig"))
    pricing_rules = yaml.safe_load(inputs[PRICING_RULES_PATH].decode("utf-8-sig"))
    nodes = schema["node_ontology"]
    category_slugs = nodes["Category"]["properties"]["slug"]["values"]
    tiers = nodes["GiftTier"]["properties"]["name"]["values"]
    if tiers != ["Reach", "Select", "Signature", "Bespoke"] or len(set(category_slugs)) != 4:
        raise ValueError("Confirmed Category/GiftTier contract changed")
    categories_by_slug = {row["slug"]: row for row in catalog["top_level_categories"]}
    if set(categories_by_slug) != set(category_slugs):
        raise ValueError("Catalog labels disagree with YAML Category enum")
    factory_by_code = {}
    for row in factory_tables["products"]:
        if row["code"] in factory_by_code:
            raise ValueError(f"Duplicate factory product code: {row['code']}")
        factory_by_code[row["code"]] = row
    run = {key: value for key, value in tables["smartgift_export_run"][0].items() if key != "_line"}
    srp_reference_products, srp_qty_comparisons = _build_srp_comparisons(
        catalog, factory_by_code, pricing_rules, hashes[CATALOG_PATH])
    price_comparisons = [
        _build_price_comparison(row, factory_by_code.get(row["offer_code"]), pricing_rules, run["run_id"])
        for row in sorted(tables["smartgift_price"], key=lambda row: row["id"])
    ]
    cost_mapping_doc = json.loads(inputs[COST_MAPPING_PATH].decode("utf-8-sig"))
    if cost_mapping_doc.get("metadata", {}).get("status") != "confirmed":
        raise ValueError("Cost mapping artifact is not confirmed; refusing to apply costs")
    cost_mapping = {row["pm_code"]: row for row in cost_mapping_doc["mapping"]}
    seasonal_offers, seasonal_packages, seasonal_bom = _build_seasonal_packages(
        catalog, schema, hashes[CATALOG_PATH], category_slugs, cost_mapping)
    data = {
        "metadata": {
            "schema_version": "1.3.0b", "generator": GENERATOR,
            "status": "review_required", "tenant_id": "Org-EtohGroup", "business_id": "SmartGift",
            "contract_ref": schema["client_contract"]["schema_ref"],
            "contract_version": schema["client_contract"]["schema_version"],
            "source_run": run,
            "sources": [{"path": path, "sha256": hashes[path], "size_bytes": len(content),
                         "scope": ("catalog_srp_and_labels" if path == CATALOG_PATH else
                                   "factory_catalog_reference" if path == FACTORY_PATH else
                                   "pricing_formula_and_shipping_scenario" if path == PRICING_RULES_PATH else
                                   "confirmed_factory_cost_mapping" if path == COST_MAPPING_PATH else
                                   "snapshot_or_contract")}
                        for path, content in inputs.items()],
            "quote_ready": False, "inventory_ready": False, "bom_coverage": "proposed_recipe",
            "profit_policy": {"minimum_profit": 25000, "currency": "THB", "scope": "per_configured_pkg",
                              "basis": "net_revenue_minus_complete_direct_delivery_costs_same_vat_basis",
                              "missing_inputs_pass": False},
            "privacy_review": {"table_field_allowlist": True, "contact_pattern_scan": "passed",
                               "human_review": "pending", "zero_pii_certified": False},
            "comparison_policy": {
                "srp_source": "smartgift_catalog_master.json canonical_products.price_tiers",
                "quantity_tiers": list(SRP_QTY_TIERS), "factory_identity": "exact_code_only",
                "fx_thb_per_cny": float(pricing_rules["currency_exchange_rates"]["cny_to_thb"]),
                "shipping_scenario": {"warehouse": "guangzhou_shenzhen", "mode": "truck",
                                       "member_tier": "GOLD", "basis": "declared_scenario"},
                "delivered_cost_requires": ["factory_cost", "carton_logistics", "direct_cost_breakdown",
                                             "vat_basis_alignment"],
            },
        },
        "product_masters": [], "product_families": [], "portfolio_catalogs": [],
        "customer_tiers": [{"entity_type": "GiftTier", "name": name,
                            "source_ref": {"file": SCHEMA_PATH, "path": "node_ontology.GiftTier.properties.name.values"}}
                           for name in tiers],
        "catalog_offers": [], "seasonal_offers": seasonal_offers, "pkg": [],
        "offer_product_links": [], "bom": seasonal_bom, "prices": [],
        "price_comparisons": price_comparisons,
        "srp_reference_products": srp_reference_products,
        "srp_qty_comparisons": srp_qty_comparisons,
    }
    for slug in category_slugs:
        source = categories_by_slug[slug]
        data["portfolio_catalogs"].append({"entity_type": "Category", "slug": slug,
            "name_th": source["name_th"], "name_en": source["name_en"],
            "source_ref": {"enum_file": SCHEMA_PATH, "labels_file": CATALOG_PATH}})
    for row in sorted(tables["smartgift_type"], key=lambda row: row["type_id"]):
        data["product_families"].append({
            "code": row["type_id"], "source_semantics": "product_type", "source_group_id": row["group_id"],
            **{key: row[key] for key in ("name_th", "name_en", "aliases_th", "aliases_en")},
            "provenance": _provenance("smartgift_type", row, row["type_id"]),
        })
    for row in sorted(tables["smartgift_model"], key=lambda row: row["source_ref"]["rowKey"]):
        code = row["source_ref"]["rowKey"]
        record = {"code": code, "name_th": None, "name_en": row["english_name"],
                  "category": None, "base_cost": None, "product_family_id": row["type_id"],
                  "source_group_id": row["group_id"], "source_status": row["status"],
                  "display_name": row["display_name"], "base_signature": row["base_signature"],
                  "colors": row["colors"], "price_source": row["price_source"],
                  "source_price_tiers": row["price_tiers"],
                  "provenance": _provenance("smartgift_model", row, row["base_signature"])}
        data["product_masters"].append(_contract_check(record, "ProductMaster", schema))
        for offer in sorted(row["offer_codes"]):
            data["offer_product_links"].append({"product_code": code, "offer_code": offer,
                "relation": "source_association", "source_field": "smartgift_model.offer_codes"})
    for row in sorted(tables["smartgift_offer"], key=lambda row: row["code"]):
        record = {key: row[key] for key in ("code", "name_th", "name_en", "description", "offer_kind",
                                           "status", "branding", "origin", "rmb", "image")}
        record.update(name=row["name_th"] or row["name_en"], gift_tier=None, unboxing_experience=None,
                      source_price_tiers=row["price_tiers"],
                      provenance=_provenance("smartgift_offer", row, row["code"]))
        data["catalog_offers"].append(_contract_check(record, "CatalogOffer", schema))
    standard_qty_tiers = _standard_qty_tiers(tables["smartgift_price"])
    for row in sorted(tables["smartgift_price"], key=lambda row: row["id"]):
        record = {key: row[key] for key in TABLE_COLUMNS["smartgift_price"].split() if key != "source_ref"}
        price_present = not row["price_missing"] and row["unit_price"] is not None and row["unit_price"] > 0
        tier_present = row["qty_tier"] is not None and row["qty_tier"] > 0
        reasons = []
        if not price_present:
            reasons.append("missing_or_nonpositive_price")
        if not tier_present:
            reasons.append("missing_or_nonpositive_qty_tier")
        if price_present and not tier_present:
            # A real price with no ladder position — most likely a
            # price_list_group flat rate (see flow_account_code/name), not a
            # missing quantity tier. Distinct from a genuinely blank row so
            # nothing filtering on "missing qty_tier" silently drops a real
            # price along with it (never happens automatically: this value
            # only ever informs review, it does not change qty_tier itself).
            reasons.append("priced_without_qty_tier")
        if tier_present and row["qty_tier"] not in standard_qty_tiers:
            # A positive qty_tier outside both SRP_QTY_TIERS and this run's
            # observed FlowAccount ladder — flagged for a human to confirm
            # with FlowAccount, never treated as invalid or corrected here.
            reasons.append("non_standard_qty_tier")
        record.update(data_quality_issues=reasons, quote_ready=False,
                      provenance=_provenance("smartgift_price", row, row["id"]))
        data["prices"].append(record)
    legacy_pkg = {"id": "bundle:smartgift-new-employee-welcome", "code": "PKG-NEW-EMPLOYEE-WELCOME", "name": "ชุดต้อนรับพนักงานใหม่",
           "occasion": "new_employee_welcome", "status": "draft",
           "target_recipients": None, "total_price": None, "tier_breakdown": {},
           "design_scope": {"catalog_slugs": category_slugs, "gift_tiers": tiers,
                            "status": "configuration_space_only"},
           "options": [], "bom_status": "not_designed", "quote_ready": False,
           "profit_evaluation": evaluate_profit(),
           "source_ref": {"kind": "user_requirement", "date": "2026-08-30"}}
    data["pkg"].append(_contract_check(legacy_pkg, "BundleOffer", schema))
    data["pkg"].extend(seasonal_packages)
    data["metadata"]["edge_contracts"] = {key: schema["edge_ontology"][key] for key in (
        "IN_CATEGORY", "VARIANT_OF", "CONTAINS", "BELONGS_TO_TIER", "INCLUDES_OFFER")}
    data["metadata"]["counts"] = {key: len(value) for key, value in data.items() if isinstance(value, list)}
    data["metadata"]["quality_summary"] = {
        "models_without_type": sum(row["product_family_id"] is None for row in data["product_masters"]),
        "missing_prices": sum(row["price_missing"] for row in data["prices"]),
        "missing_or_nonpositive_qty_tiers": sum(row["qty_tier"] is None or row["qty_tier"] <= 0 for row in data["prices"]),
        "priced_without_qty_tier_count": sum(
            "priced_without_qty_tier" in row["data_quality_issues"] for row in data["prices"]),
        "non_standard_qty_tier_count": sum(
            "non_standard_qty_tier" in row["data_quality_issues"] for row in data["prices"]),
        "standard_qty_tiers": sorted(standard_qty_tiers),
        # Distinct offer_code with >=1 row where a real price is actually
        # present — NOT "has a prices-table row" (a row can exist and still
        # carry price_missing=true). Presence-of-row overstated this by 99
        # offer_codes in an earlier read of this exact table (2026-08-30
        # cross-session review) — this field is defined to not repeat that.
        "offers_with_confirmed_price_count": len({
            row["offer_code"] for row in data["prices"]
            if not row["price_missing"] and row["unit_price"] is not None and row["unit_price"] > 0}),
        "priced_offer_count": len({row["offer_code"] for row in data["prices"]}),
        "verified_bom_edges": sum(row.get("verified") is True for row in data["bom"]),
        "proposed_bom_edges": len(data["bom"]),
        "seasonal_offer_count": len(data["seasonal_offers"]),
        "seasonal_package_count": len(seasonal_packages),
        "bom_edges_with_confirmed_cost": sum(row.get("factory_cost_thb") is not None for row in data["bom"]),
        "confirmed_cost_mapping_pairs": len(cost_mapping),
        "packages_fully_costed": sum(
            1 for row in data["pkg"]
            if (row.get("cost_reference") or {}).get("coverage") == "full"),
        "packages_partially_costed": sum(
            1 for row in data["pkg"]
            if (row.get("cost_reference") or {}).get("coverage") == "partial"),
        "package_gate_status_counts": {status: sum(row["profit_evaluation"]["status"] == status for row in data["pkg"])
                                        for status in sorted({row["profit_evaluation"]["status"] for row in data["pkg"]})},
        "factory_catalog_product_count": len(factory_tables["products"]),
        "factory_exact_matches_for_price_rows": len({row["offer_code"] for row in tables["smartgift_price"] if row["offer_code"] in factory_by_code}),
        "factory_exact_match_price_rows": sum(row["offer_code"] in factory_by_code for row in tables["smartgift_price"]),
        "srp_reference_product_count": len(srp_reference_products),
        "srp_comparison_count": len(srp_qty_comparisons),
        "srp_quantity_tiers": list(SRP_QTY_TIERS),
        "comparison_status_counts": {status: sum(row["comparison_status"] == status for row in price_comparisons)
                                     for status in sorted({row["comparison_status"] for row in price_comparisons})},
    }
    validate_master(data)
    for path, content in inputs.items():
        if (root / path).read_bytes() != content:
            raise ValueError(f"Input changed during export: {path}; retry after edits finish")
    return data


def export_master(root=ROOT, check=False):
    root = Path(root)
    data = build_master(root)
    content = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    output = root / OUTPUT_PATH
    public_content = (json.dumps(build_public_projection(data), ensure_ascii=False, indent=2,
                                  allow_nan=False) + "\n").encode("utf-8")
    public_output = root / PUBLIC_OUTPUT_PATH
    if check:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Export differs from current sources; regenerate and review")
        if not public_output.exists() or public_output.read_bytes() != public_content:
            raise ValueError("Public export differs from current sources; regenerate and review")
        return data
    if output.exists() and json.loads(output.read_bytes()).get("metadata", {}).get("generator") != GENERATOR:
        raise ValueError("Refusing to overwrite an artifact owned by another generator")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".pricelist-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    public_output.parent.mkdir(parents=True, exist_ok=True)
    public_temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=public_output.parent, prefix=".pricelist-public-",
                                         suffix=".tmp", delete=False) as handle:
            public_temporary = Path(handle.name)
            handle.write(public_content)
        os.replace(public_temporary, public_output)
    finally:
        if public_temporary is not None and public_temporary.exists():
            public_temporary.unlink()
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate determinism without writing")
    args = parser.parse_args()
    result = export_master(check=args.check)
    print(json.dumps({"output": OUTPUT_PATH, "public_output": PUBLIC_OUTPUT_PATH,
                      "checked_only": args.check,
                      "counts": result["metadata"]["counts"],
                      "quality": result["metadata"]["quality_summary"]}, ensure_ascii=False, indent=2))
