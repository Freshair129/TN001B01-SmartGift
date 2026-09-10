"""Extract original embedded photos from reviewed Business Gift PDF table rows.

This is a presentation-asset helper, not a canonical entity/price/BOM importer.
It never writes source documents, master data, or the media manifest.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CODE = re.compile(r"[A-Z]{1,8}[0-9][A-Z0-9]*(?:-[A-Z0-9]+)*\Z")

# Verified column geometries for the A4 portrait price tables. Each entry describes ONE printed
# layout, measured from its pages; they are tried in order and the first that yields rows wins for
# that page. Do not merge them into a single loose band — a wider band can pair a code with the
# photo from a neighbouring column, which puts the wrong product picture on the catalogue.
#   narrow  the original verified layout (code x1<=50, photo 45..155)
#   wide    the 110-page ใบเสนอราคา / ใบราคาส่งลูกค้า tables: code x1 measured 67-73,
#           photo x0 measured 74-77 and x1 164-169
LAYOUTS = (
    {"name": "narrow", "code_x1": 50, "image_x0": 45, "image_x1": 155, "crop_x1": 306},
    {"name": "wide", "code_x1": 80, "image_x0": 45, "image_x1": 180, "crop_x1": 380},
)


def match_rows(words, images, target_codes, page_height, layout):
    codes = sorted((w for w in words if w["x0"] < 45 and w["x1"] <= layout["code_x1"]
                    and CODE.fullmatch(w["text"])), key=lambda w: w["top"])
    result = []
    for index, word in enumerate(codes):
        # Text hidden under the repeated page header is not visible identity evidence.
        if word["text"] not in target_codes or word["top"] < 40:
            continue
        end = codes[index + 1]["top"] if index + 1 < len(codes) else page_height - 15
        pictures = [im for im in images
                    if layout["image_x0"] <= im["x0"] and im["x1"] <= layout["image_x1"]
                    and im["top"] >= word["top"] - 2 and im["bottom"] <= end + 2
                    and im["bottom"] <= page_height - 15
                    and im["x1"] - im["x0"] >= 40 and im["bottom"] - im["top"] >= 35]
        # More than one candidate photo in the row band is not evidence of identity — skip it.
        if len(pictures) == 1:
            result.append({"code": word["text"], "image_name": pictures[0]["name"],
                           "row_top": word["top"], "row_bottom": end, "layout": layout["name"],
                           "crop_x1": layout["crop_x1"]})
    return result


def collect(source):
    import pdfplumber
    from pypdf import PdfReader

    # Every offer code the business knows about. smartgift_catalog_master carries the 357 canonical
    # ones; pricelist_master carries all 1,110, and the price tables print codes from both.
    master = json.loads((ROOT / "data-pipeline/02_prepared/smartgift_catalog_master.json").read_text(encoding="utf-8"))
    pricelist = json.loads((ROOT / "data-pipeline/02_prepared/pricelist_master.json").read_text(encoding="utf-8"))
    targets = {row["offer_code"] for row in master["catalog_offers"]}
    targets |= {row["code"] for row in pricelist["catalog_offers"]}
    reader = PdfReader(source)
    found = {}
    with pdfplumber.open(source) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            # These coordinates describe the verified A4 portrait price-table layout only.
            if abs(page.width - 595.2) > 1 or abs(page.height - 841.8) > 1:
                continue
            words = page.extract_words()
            for layout in LAYOUTS:
                rows = match_rows(words, page.images, targets, page.height, layout)
                if rows:
                    break
            if not rows:
                continue
            embedded = {Path(im.name).stem: im for im in reader.pages[page_number - 1].images}
            for row in rows:
                im = embedded.get(row["image_name"])
                if im is None or min(im.image.size) < 100 or Path(im.name).suffix.lower() not in (".jpg", ".png"):
                    continue
                row.update(page=page_number, width=im.image.width, height=im.image.height,
                           sha256=hashlib.sha256(im.data).hexdigest(),
                           filename=f"source-offer-{row['code']}{Path(im.name).suffix.lower()}", data=im.data)
                found.setdefault(row["code"], []).append(row)
    # Duplicate codes with different photos require a human choice; do not choose a page silently.
    accepted = [rows[0] for rows in found.values() if len({r["sha256"] for r in rows}) == 1]
    ambiguous = sorted(code for code, rows in found.items() if len({r["sha256"] for r in rows}) > 1)
    return sorted(accepted, key=lambda row: (row["page"], row["row_top"])), ambiguous


def review_sheets(source, rows, directory):
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw

    directory.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(source))
    page_cache = {}
    for offset in range(0, len(rows), 16):
        sheet = Image.new("RGB", (1200, 1120), "white")
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(rows[offset:offset + 16]):
            x, y = (index % 4) * 300, (index // 4) * 280
            draw.text((x + 8, y + 8), f"{row['code']} | PDF p.{row['page']}", fill="black")
            if row["page"] not in page_cache:
                page_cache[row["page"]] = document[row["page"] - 1].render(scale=2).to_pil().convert("RGB")
            page_image = page_cache[row["page"]]
            crop = page_image.crop((15, max(0, int((row["row_top"] - 2) * 2)), row.get("crop_x1", 306),
                                    min(page_image.height, int(row["row_bottom"] * 2))))
            crop.thumbnail((280, 245))
            sheet.paste(crop, (x + 8, y + 28))
        sheet.save(directory / f"source-rows-{offset // 16 + 1:02}.png")
    document.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--review-dir", type=Path)
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--codes", nargs="+", help="Only human-reviewed exact codes may be extracted")
    args = parser.parse_args()
    if args.extract and not args.codes:
        parser.error("--extract requires an explicit --codes review allowlist")
    rows, ambiguous = collect(args.source)
    if args.codes:
        selected = set(args.codes)
        if selected - {row["code"] for row in rows}:
            parser.error("Requested code absent or ambiguous; no assets written")
        rows = [row for row in rows if row["code"] in selected]
    if args.review_dir:
        review_sheets(args.source, rows, args.review_dir)
    if args.extract:
        destination = ROOT / "public/assets/catalog-media"
        for row in rows:
            target = destination / row["filename"]
            if target.exists() and target.read_bytes() != row["data"]:
                raise ValueError(f"Refusing to overwrite different asset: {target.name}")
        for row in rows:
            target = destination / row["filename"]
            if not target.exists():
                target.write_bytes(row["data"])
    report = {"source": str(args.source), "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
              "count": len(rows), "ambiguous_codes": ambiguous,
              "rows": [{key: value for key, value in row.items() if key != "data"} for row in rows]}
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
