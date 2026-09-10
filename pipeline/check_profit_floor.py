#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ตรวจราคาขายองค์กรกับพื้นกำไรใน config/pricing_rules_formula.yaml

    python pipeline/check_profit_floor.py            # ตรวจทุกชุดข้อมูลใน docs/specs
    python pipeline/check_profit_floor.py --fix-hint # แสดงราคาที่ต้องเป็นเพื่อผ่านพื้น

พื้นกำไรมีสองชั้นและใช้ค่าที่สูงกว่า:
    effective_floor = max(profit_floors ตามช่วงจำนวน, profit_floors_by_kind ที่เข้าเงื่อนไข)
หน่วยเป็นกำไรขั้นต้นรวมทั้งออเดอร์ = (ราคาขาย - total_landed_cost_thb) x จำนวน

สคริปต์นี้อยู่ใน repo นี้เพราะต้องใช้ total_landed_cost_thb ซึ่งเป็นข้อมูลต้นทุน
ที่ห้ามออกไปยัง front-end — อย่าย้ายไป web-ui-smg
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "config" / "pricing_rules_formula.yaml"
SPECS = ROOT / "docs" / "specs"


def _num(text):
    return math.inf if text.strip() == ".inf" else float(text)


def load_floors(path=RULES):
    """อ่านพื้นกำไรจาก YAML ด้วย regex — เลี่ยงการเพิ่ม dependency ให้ pipeline"""
    src = path.read_text(encoding="utf-8")

    bands = []
    block = re.search(r"^profit_floors:\n((?:  [-\s].*\n)+)", src, re.M)
    if block:
        for qty, thb in re.findall(r"-\s*max_qty:\s*(\S+)\s*\n\s*thb:\s*([\d.]+)", block.group(1)):
            bands.append((_num(qty), float(thb)))

    by_kind = {}
    block = re.search(r"^profit_floors_by_kind:\n((?:  \S.*\n|    .*\n)+)", src, re.M)
    if block:
        for kind, body in re.findall(r"^  (\w+):\n((?:    .*\n)+)", block.group(1), re.M):
            by_kind[kind] = [
                (_num(q), float(t))
                for q, t in re.findall(r"-\s*min_qty:\s*(\S+)\s*\n\s*thb:\s*([\d.]+)", body)
            ]
    if not bands and not by_kind:
        sys.exit(f"ไม่พบ profit_floors ใน {path}")
    return bands, by_kind


def effective_floor(qty, kind, bands, by_kind):
    """พื้นที่ใช้จริง = ค่าที่สูงกว่าระหว่างพื้นตามช่วงจำนวน กับพื้นเฉพาะชนิดสินค้า"""
    floor = 0.0
    for max_qty, thb in sorted(bands, key=lambda b: b[0]):
        if qty <= max_qty:
            floor = max(floor, thb)
            break
    for min_qty, thb in by_kind.get(kind, []):
        if qty >= min_qty:
            floor = max(floor, thb)
    return floor


def rows_from(payload):
    ident = payload.get("codes_and_identification", {})
    suffix = str(ident.get("product_items_suffix", ""))
    kind = "single" if suffix in ("-0", "0") else "set"
    code = ident.get("flowaccount_product_code") or ident.get("factory_item_code") or "?"
    return code, kind, payload.get("pricing_comparison_table", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-hint", action="store_true", help="แสดงราคาที่ต้องเป็นเพื่อผ่านพื้น")
    ap.add_argument("paths", nargs="*", type=Path, help="ไฟล์ payload (ค่าเริ่มต้น: docs/specs/*_pricing_and_catalog*.json)")
    args = ap.parse_args()

    bands, by_kind = load_floors()
    print(f"พื้นตามช่วงจำนวน : {[(q, t) for q, t in bands]}")
    print(f"พื้นตามชนิดสินค้า : {by_kind}")
    print()

    files = args.paths or sorted(SPECS.glob("*_pricing_and_catalog*.json"))
    failures = 0
    checked = 0
    for f in files:
        code, kind, table = rows_from(json.loads(f.read_text(encoding="utf-8")))
        if not table:
            continue
        print(f"{code}  [{kind}]")
        for r in table:
            qty = r["quantity"]
            price = r.get("corporate_selling_price_thb")
            landed = r.get("total_landed_cost_thb")
            if price is None or landed is None:
                print(f"   @{qty:<5} ข้ามไป — ไม่มีราคาขายองค์กรหรือ landed cost")
                continue
            checked += 1
            profit = (price - landed) * qty
            floor = effective_floor(qty, kind, bands, by_kind)
            ok = profit >= floor
            failures += not ok
            line = (f"   @{qty:<5} corp {price:>7,.2f}  กำไรรวม {profit:>12,.0f}"
                    f"  พื้น {floor:>10,.0f}  {'ผ่าน' if ok else 'ไม่ผ่าน'}")
            if not ok and args.fix_hint:
                need = landed + floor / qty
                line += f"  -> ต้อง >= {need:,.2f} (+{need - price:,.2f})"
            print(line)
        print()

    print(f"ตรวจ {checked} แถว · ไม่ผ่าน {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
