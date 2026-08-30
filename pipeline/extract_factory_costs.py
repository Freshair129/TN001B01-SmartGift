"""
Factory Cost Extractor (Stage 2, lane 08_factory_costs)
Parses supplier cost catalogs into normalized cost records at
data-pipeline/02_prepared/factory_costs.json and writes a review report with
PROPOSED (unconfirmed) canonical PM mapping candidates. Deliberately does NOT
write any cost into pricelist_master.json — mapping requires human approval
(ADR-005; same principle as the 2026-08-30 source audit that declined to fill
costs without an exact factory match).

Supplier header/contact lines (rows above the item table) are excluded so no
personal names, emails or handles reach prepared artifacts.
"""

import os
import re
import sys
import json
import hashlib
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

COSTS_DIR = "data-pipeline/01_raw/08_factory_costs"
REGISTRY_PATH = "data-pipeline/01_raw/factory_cost_registry.json"
OUTPUT_JSON = "data-pipeline/02_prepared/factory_costs.json"
REPORT_DIR = "data-pipeline/04_review_reports"

GIFTSET_FILE = "01-ต้นทุน-20260612 Business Office Gift set catalog.xlsx"
POWERBANK_FILE = "02-ต้นทุน-20260417 Power bank notebook catalog.xlsx"
USB_FILE = "ต้นทุน USB Flashdrive.xls"

# Keyword → canonical PM candidates. Proposals only; a human confirms each pair
# before any cost is allowed near pricelist_master.
PM_KEYWORD_RULES = [
    (r"\bfan\b",                 "PM-FAN"),
    (r"umbrella",                "PM-UMB"),
    (r"notebook|note book",      "PM-NB"),
    (r"power ?bank",             "PM-PB10K"),
    (r"usb|flash ?drive",        "PM-FLASH"),
    (r"tumbler|thermos|bottle",  "PM-BOTTLE-LED"),
    (r"mug|cup",                 "PM-CFMUG"),
    (r"speaker",                 "PM-SPK"),
    (r"massag",                  "PM-MSG"),
    (r"pen\b",                   "PM-PEN"),
    (r"aroma|diffuser|humidifier", "PM-AROMA"),
    (r"tea infus",               "PM-TEA-INF"),
    (r"cutlery|spoon|fork",      "PM-CUTLERY"),
    (r"desk mat|mouse pad",      "PM-DESK-MAT"),
]


def propose_pm_codes(text: str) -> list:
    t = (text or "").lower()
    return sorted({pm for pat, pm in PM_KEYWORD_RULES if re.search(pat, t)})


def norm(v):
    if v is None:
        return ""
    return str(v).replace("\n", " ").strip()


def parse_giftset(path: str) -> list:
    """Item row: col A = item code, col C = set description, col E = EXW USD/set.
    Attribute rows follow with key in col C, value in col D."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Business Office Gift set"]
    records, current = [], None
    for row in ws.iter_rows(values_only=True):
        a, c, d, e = norm(row[0]), norm(row[2]), norm(row[3]), row[4]
        if a and a not in ("Item No.",) and not a.startswith("*"):
            if current:
                records.append(current)
            current = {
                "item_code": a,
                "item_name": c,
                "unit": "set",
                "currency": "USD",
                "price_basis": "EXW",
                "exw_price": float(e) if isinstance(e, (int, float)) else None,
                "attributes": {},
            }
        elif current and c and d:
            current["attributes"][c] = d
    if current:
        records.append(current)
    wb.close()
    return records


def parse_powerbank_notebook(path: str) -> list:
    """Item row: col A = item code, col B = first attribute key, col C = value,
    col E = EXW USD/set. Section headers sit alone in col A."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    records, current, section = [], None, None
    for row in ws.iter_rows(values_only=True):
        a, b, c, e = norm(row[0]), norm(row[1]), norm(row[2]), row[4]
        if a in ("Item No.",) or (a and "Zhimei" in a) or (a and "|" in a and not b):
            continue
        if a and not b and not isinstance(e, (int, float)):
            section = a.strip("✭ ")
            continue
        if a:
            if current:
                records.append(current)
            current = {
                "item_code": a,
                "item_name": None,
                "section": section,
                "unit": "set",
                "currency": "USD",
                "price_basis": "EXW",
                "exw_price": float(e) if isinstance(e, (int, float)) else None,
                "attributes": ({b: c} if b and c else {}),
            }
        elif current and b and c:
            current["attributes"][b] = c
    if current:
        records.append(current)
    wb.close()
    for r in records:
        r["item_name"] = r["attributes"].get("Function") or next(iter(r["attributes"].values()), "")
    return records


def parse_usb_flashdrive(path: str) -> list:
    """Legacy .xls, two side-by-side (NO, Item, Picture, Price) tables per sheet,
    plus a 'Chip price' capacity matrix. Prices are RMB. Items carry no codes."""
    import xlrd
    wb = xlrd.open_workbook(path)
    records = []
    for ws in wb.sheets():
        header = [norm(ws.cell_value(0, j)) for j in range(ws.ncols)]
        if ws.name.strip().lower().startswith("chip"):
            current_item, current_spec = None, None
            for i in range(1, ws.nrows):
                item = norm(ws.cell_value(i, 0))
                spec = norm(ws.cell_value(i, 2))
                cap = norm(ws.cell_value(i, 3))
                p2, p3 = ws.cell_value(i, 4), ws.cell_value(i, 5)
                if item:
                    current_item, current_spec = item, spec
                if not cap:
                    continue
                for label, price in (("USB 2.0", p2), ("USB 3.0", p3)):
                    if isinstance(price, (int, float)) and price:
                        records.append({
                            "item_code": None,
                            "item_name": f"{current_item} chip {cap} {label}",
                            "sheet": ws.name,
                            "unit": "pc",
                            "currency": "RMB",
                            "price_basis": "EXW",
                            "exw_price": float(price),
                            "attributes": {"shell_type": current_item, "capacity": cap,
                                           "interface": label, "spec": current_spec},
                        })
            continue
        moq_match = re.search(r"MOQ\s*(\d+)", " ".join(header))
        moq = int(moq_match.group(1)) if moq_match else None
        for i in range(1, ws.nrows):
            for no_col, item_col, price_col in ((0, 1, 3), (5, 6, 8)):
                if price_col >= ws.ncols:
                    continue
                item = norm(ws.cell_value(i, item_col))
                price = ws.cell_value(i, price_col)
                if item and isinstance(price, (int, float)) and price:
                    records.append({
                        "item_code": None,
                        "item_name": item,
                        "sheet": ws.name,
                        "unit": "pc",
                        "currency": "RMB",
                        "price_basis": "EXW",
                        "exw_price": float(price),
                        "moq": moq,
                        "attributes": {"shell_type": ws.name.strip()},
                    })
    return records


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    now = datetime.now(timezone.utc)
    sources = {}
    all_records = []

    for filename, parser in (
        (GIFTSET_FILE, parse_giftset),
        (POWERBANK_FILE, parse_powerbank_notebook),
        (USB_FILE, parse_usb_flashdrive),
    ):
        path = os.path.join(COSTS_DIR, filename)
        recs = parser(path)
        for r in recs:
            r["source_file"] = filename
            searchable = " ".join([r.get("item_name") or "", " ".join(f"{k} {v}" for k, v in r.get("attributes", {}).items())])
            r["proposed_pm_codes"] = propose_pm_codes(searchable)
            r["mapping_status"] = "proposed" if r["proposed_pm_codes"] else "unmapped"
        all_records.extend(recs)
        sources[filename] = {"sha256": sha256_of(path), "records_extracted": len(recs)}

    priced = [r for r in all_records if r.get("exw_price")]
    output = {
        "metadata": {
            "artifact": "factory_costs",
            "lane": "08_factory_costs",
            "extracted_at": now.isoformat(),
            "registry": REGISTRY_PATH,
            "sources": sources,
            "total_records": len(all_records),
            "records_with_price": len(priced),
            "currency_note": "EXW prices as quoted by supplier (USD for gift set / powerbank-notebook catalogs, RMB for USB flashdrive). No FX conversion applied; landed cost requires freight + duty + FX per pricing_rules_formula.yaml.",
            "mapping_note": "proposed_pm_codes are keyword-based CANDIDATES only (ADR-005). No cost enters pricelist_master.json until a human confirms each mapping.",
        },
        "records": all_records,
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # ---- Review report -------------------------------------------------
    date_tag = now.strftime("%Y-%m-%d")
    report_path = os.path.join(REPORT_DIR, f"factory-cost-intake-{date_tag}.md")
    pm_counts = {}
    for r in all_records:
        for pm in r["proposed_pm_codes"]:
            pm_counts[pm] = pm_counts.get(pm, 0) + 1
    unmapped = sum(1 for r in all_records if r["mapping_status"] == "unmapped")

    lines = [
        "---",
        'version: "0.1.0b"',
        f'created_at: "{now.astimezone().isoformat(timespec="seconds")},CLAUDE"',
        f'last_update: "{now.astimezone().isoformat(timespec="seconds")},CLAUDE"',
        'status: "beta"',
        "superseded_by: null",
        "attributes:",
        '  domain: "catalog-pricing"',
        '  doc_type: "intake-review"',
        '  scope: "factory cost lane 08 first ingest; proposed PM mapping awaiting human confirmation"',
        "---",
        "",
        "# Factory Cost Intake Review — lane 08_factory_costs",
        "",
        "ไฟล์ต้นทุนโรงงาน 3 ไฟล์ (ชุดข้อมูล drive 2026-08-12) ถูก ingest พร้อม SHA-256 provenance",
        "และ extract เป็น `02_prepared/factory_costs.json` — **ยังไม่มีการเขียนต้นทุนเข้า",
        "`pricelist_master.json`** เพราะ PM mapping เป็นเพียง keyword candidates (ADR-005)",
        "",
        "## Sources",
        "",
        "| File | SHA-256 (12) | Records extracted |",
        "|---|---|---:|",
    ]
    for fn, meta in sources.items():
        lines.append(f"| {fn} | `{meta['sha256'][:12]}` | {meta['records_extracted']} |")
    lines += [
        "",
        f"รวม {len(all_records)} records (มีราคา {len(priced)}); unmapped {unmapped} records",
        "",
        "## Proposed PM mapping candidates (ยังไม่ยืนยัน)",
        "",
        "| PM code | จำนวน records ที่เข้าเกณฑ์ keyword |",
        "|---|---:|",
    ]
    for pm, cnt in sorted(pm_counts.items()):
        lines.append(f"| {pm} | {cnt} |")
    lines += [
        "",
        "## เงื่อนไขก่อนใช้ราคา",
        "",
        "- ราคาเป็น EXW (USD / RMB ตาม source) ยังไม่รวม freight, duty, FX — ต้องผ่าน",
        "  `pricing_rules_formula.yaml` ก่อนเป็น landed cost",
        "- สินค้าใน gift set catalog เป็นราคาต่อ **ชุด** ไม่ใช่ต่อชิ้นส่วน; การ map เข้า BOM",
        "  ต้องตัดสินใจว่าจับที่ระดับ set หรือ component",
        "- ไฟล์ USB flashdrive ไม่มี item code — จับคู่ได้เฉพาะระดับหมวด (PM-FLASH) + capacity",
        "- ผู้อนุมัติต้องยืนยันคู่ mapping ทีละรายการก่อน จึงจะเติม `factory_cost_thb` ใน",
        "  pricelist master ได้ (คงหลักการ audit 2026-08-30 ที่ไม่เติมต้นทุนเมื่อไม่มี exact match)",
        "",
        "## CHANGELOG",
        "",
        "| Version | Date | Status | Summary | Commit Hash | Agent |",
        "|---|---|---|---|---|---|",
        f"| 0.1.0b | {date_tag} | beta | first ingest of 3 factory cost files; extraction + proposed mapping only | uncommitted | CLAUDE |",
        "",
    ]
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Extracted {len(all_records)} records ({len(priced)} priced) → {OUTPUT_JSON}")
    print(f"📋 Review report → {report_path}")
    print(f"🔎 PM candidates: {json.dumps(pm_counts, ensure_ascii=False)} | unmapped: {unmapped}")


if __name__ == "__main__":
    main()
