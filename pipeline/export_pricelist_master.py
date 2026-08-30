"""Export a review-only pricelist snapshot. Never execute SQL or sync a vault."""

import argparse
import hashlib
import json
import math
import os
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
SCHEMA_PATH = "config/schema_genesisblock.yaml"
CATALOG_PATH = "data-pipeline/02_prepared/smartgift_catalog_master.json"
OUTPUT_PATH = "data-pipeline/02_prepared/pricelist_master.json"
SQL_SHA256 = "263556642064f6398e4cd00a7a4897ca7ba841b7c3bae5b8d2165b3186b2fdd4"
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
JSON_FIELDS = {"aliases_th", "aliases_en", "offer_codes", "colors", "price_tiers", "source_ref"}
INSERT = re.compile(r"INSERT INTO (\w+)\s*\(([^)]+)\)\s*VALUES\s*\((.*?)\)\s*(?:ON CONFLICT \(\w+\) DO NOTHING\s*)?;", re.S)
LITERAL = re.compile(r"\s*('(?:[^']|'')*'|NULL|TRUE|FALSE|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(,|$)", re.S)
PII_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"
    r"|(?<![\w])(?:\+66|0)[ -]?[689](?:[ -]?\d){8}(?![\w])"
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


def evaluate_profit(net_revenue=None, total_cost=None, *, bom_complete=False,
                    quantity_complete=False, costs_complete=False, vat_basis_aligned=False):
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


def _scan_privacy(value, path="root"):
    if isinstance(value, dict):
        for key, child in value.items():
            _scan_privacy(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_privacy(child, f"{path}[{index}]")
    elif isinstance(value, str) and PII_PATTERN.search(value):
        raise ValueError(f"Potential contact data requires review at {path}")


def validate_master(data):
    def ids(key, field):
        values = [row[field] for row in data[key]]
        if len(values) != len(set(values)) or any(value is None for value in values):
            raise ValueError(f"Duplicate or missing ID in {key}")
        return set(values)

    products = ids("product_masters", "code")
    families = ids("product_families", "code")
    offers = ids("catalog_offers", "code")
    categories = ids("portfolio_catalogs", "slug")
    tiers = ids("customer_tiers", "name")
    ids("prices", "id")
    ids("pkg", "code")
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
    for pkg in data["pkg"]:
        if set(pkg["design_scope"]["catalog_slugs"]) != categories:
            raise ValueError("Package catalog scope mismatch")
        if set(pkg["design_scope"]["gift_tiers"]) != tiers:
            raise ValueError("Package GiftTier scope mismatch")
        if pkg["options"] or pkg["profit_evaluation"] != evaluate_profit():
            raise ValueError("Snapshot has no evidence for configured package options or profit")
    if data["bom"]:
        raise ValueError("Snapshot has no quantity-bearing BOM")
    _scan_privacy(data)


def build_master(root=ROOT):
    root = Path(root)
    inputs = {path: (root / path).read_bytes() for path in (SQL_PATH, SCHEMA_PATH, CATALOG_PATH)}
    hashes = {path: hashlib.sha256(content).hexdigest() for path, content in inputs.items()}
    if hashes[SQL_PATH] != SQL_SHA256:
        raise ValueError("SQL snapshot hash changed; review source diff before exporting")
    tables = parse_snapshot(inputs[SQL_PATH].decode("utf-8-sig"))
    if {table: len(rows) for table, rows in tables.items()} != EXPECTED_COUNTS:
        raise ValueError("SQL snapshot counts do not reconcile")
    schema = yaml.safe_load(inputs[SCHEMA_PATH].decode("utf-8-sig"))
    catalog = json.loads(inputs[CATALOG_PATH].decode("utf-8-sig"))
    nodes = schema["node_ontology"]
    category_slugs = nodes["Category"]["properties"]["slug"]["values"]
    tiers = nodes["GiftTier"]["properties"]["name"]["values"]
    if tiers != ["Reach", "Select", "Signature", "Bespoke"] or len(set(category_slugs)) != 4:
        raise ValueError("Confirmed Category/GiftTier contract changed")
    categories_by_slug = {row["slug"]: row for row in catalog["top_level_categories"]}
    if set(categories_by_slug) != set(category_slugs):
        raise ValueError("Catalog labels disagree with YAML Category enum")
    run = {key: value for key, value in tables["smartgift_export_run"][0].items() if key != "_line"}
    data = {
        "metadata": {
            "schema_version": "1.1.0b", "generator": GENERATOR,
            "status": "review_required", "tenant_id": "Org-EtohGroup", "business_id": "SmartGift",
            "contract_ref": schema["client_contract"]["schema_ref"],
            "contract_version": schema["client_contract"]["schema_version"],
            "source_run": run,
            "sources": [{"path": path, "sha256": hashes[path], "size_bytes": len(content),
                         "scope": "catalog_labels_only" if path == CATALOG_PATH else "snapshot_or_contract"}
                        for path, content in inputs.items()],
            "quote_ready": False, "inventory_ready": False, "bom_coverage": "not_exported",
            "profit_policy": {"minimum_profit": 25000, "currency": "THB", "scope": "per_configured_pkg",
                              "basis": "net_revenue_minus_complete_direct_delivery_costs_same_vat_basis",
                              "missing_inputs_pass": False},
            "privacy_review": {"table_field_allowlist": True, "contact_pattern_scan": "passed",
                               "human_review": "pending", "zero_pii_certified": False},
        },
        "product_masters": [], "product_families": [], "portfolio_catalogs": [],
        "customer_tiers": [{"entity_type": "GiftTier", "name": name,
                            "source_ref": {"file": SCHEMA_PATH, "path": "node_ontology.GiftTier.properties.name.values"}}
                           for name in tiers],
        "catalog_offers": [], "pkg": [], "offer_product_links": [], "bom": [], "prices": [],
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
    for row in sorted(tables["smartgift_price"], key=lambda row: row["id"]):
        record = {key: row[key] for key in TABLE_COLUMNS["smartgift_price"].split() if key != "source_ref"}
        reasons = []
        if row["price_missing"] or row["unit_price"] is None or row["unit_price"] <= 0:
            reasons.append("missing_or_nonpositive_price")
        if row["qty_tier"] is None or row["qty_tier"] <= 0:
            reasons.append("missing_or_nonpositive_qty_tier")
        record.update(data_quality_issues=reasons, quote_ready=False,
                      provenance=_provenance("smartgift_price", row, row["id"]))
        data["prices"].append(record)
    pkg = {"code": "PKG-NEW-EMPLOYEE-WELCOME", "name": "ชุดต้อนรับพนักงานใหม่",
           "occasion": "new_employee_welcome", "status": "draft",
           "target_recipients": None, "total_price": None, "tier_breakdown": {},
           "design_scope": {"catalog_slugs": category_slugs, "gift_tiers": tiers,
                            "status": "configuration_space_only"},
           "options": [], "bom_status": "not_designed", "quote_ready": False,
           "profit_evaluation": evaluate_profit(),
           "source_ref": {"kind": "user_requirement", "date": "2026-08-30"}}
    data["pkg"].append(_contract_check(pkg, "BundleOffer", schema))
    data["metadata"]["edge_contracts"] = {key: schema["edge_ontology"][key] for key in (
        "IN_CATEGORY", "VARIANT_OF", "CONTAINS", "BELONGS_TO_TIER", "INCLUDES_OFFER")}
    data["metadata"]["counts"] = {key: len(value) for key, value in data.items() if isinstance(value, list)}
    data["metadata"]["quality_summary"] = {
        "models_without_type": sum(row["product_family_id"] is None for row in data["product_masters"]),
        "missing_prices": sum(row["price_missing"] for row in data["prices"]),
        "missing_or_nonpositive_qty_tiers": sum(row["qty_tier"] is None or row["qty_tier"] <= 0 for row in data["prices"]),
        "priced_offer_count": len({row["offer_code"] for row in data["prices"]}),
        "verified_bom_edges": 0,
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
    if check:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Export differs from current sources; regenerate and review")
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
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate determinism without writing")
    args = parser.parse_args()
    result = export_master(check=args.check)
    print(json.dumps({"output": OUTPUT_PATH, "checked_only": args.check,
                      "counts": result["metadata"]["counts"],
                      "quality": result["metadata"]["quality_summary"]}, ensure_ascii=False, indent=2))
