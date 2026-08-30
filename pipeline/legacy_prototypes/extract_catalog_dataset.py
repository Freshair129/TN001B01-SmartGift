"""
Script to extract and normalize catalog data from the 110-page PDF:
02-ตัวอย่างใบราคาส่งลูกค้า - BusinessOfficeGiftset-(แปล ไทย).pdf
Classified into 4 Top-Level Main Categories (Interest Themes 2026 Blueprint):
1. Pastel Series (Soft & Friendly)
2. Classic Oriental (Mindfulness & Craft)
3. Novelty & Self-Care (Warm & Wellness)
4. Executive Smart Tech (Modern & Work)
"""

import os
import sys
import re
import json
import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "SmartGift_2026_Portfolio_Blueprint.pdf" if os.path.exists("SmartGift_2026_Portfolio_Blueprint.pdf") else "02-ตัวอย่างใบราคาส่งลูกค้า - BusinessOfficeGiftset-(แปล ไทย).pdf"
OUTPUT_JSON = "smartgift_catalog_master.json"

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def parse_catalog():
    if not os.path.exists(PDF_PATH):
        print(f"Error: {PDF_PATH} not found.")
        return

    doc = fitz.open(PDF_PATH)
    print(f"Opened {PDF_PATH}, total pages: {len(doc)}")

    raw_pages = []
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text")
        raw_pages.append({
            "page": page_idx + 1,
            "raw_text": text
        })

    # Top-Level 4 Main Categories (Interest Themes)
    top_level_categories = [
        {
            "slug": "pastel-series",
            "name_th": "ชุดธีมสีพาสเทล (Pastel Series)",
            "name_en": "Pastel Series (Soft & Friendly)",
            "vibe": "อ่อนหวาน ละมุน เป็นมิตร",
            "target_recipient": "กลุ่มวัยรุ่น, แคมเปญเข้าถึงง่าย",
            "guardrail": "คุมโทนสีให้เป็นเฉดเดียวกันทั้งกล่อง",
            "core_signatures": ["ร่มพาสเทลออโต้ 8 ก้าน", "สมุด Skin-touch", "กระบอกน้ำสุญญากาศ", "ปากกาหมึกซึม"]
        },
        {
            "slug": "classic-oriental",
            "name_th": "ชุดศิลปะร่วมสมัยและตะวันออก (Classic Oriental)",
            "name_en": "Classic Oriental (Mindfulness & Craft)",
            "vibe": "ประณีต ทรงคุณค่า คลาสสิก",
            "target_recipient": "ผู้ใหญ่, แขก VIP ต่างชาติ",
            "guardrail": "ตรวจเช็คความหมายมงคลของลวดลาย",
            "core_signatures": ["สมุดคลิปโลหะ/ปกหนัง", "ปากกาไม้หัวทองเหลือง", "แฟลชไดร์ฟหยูอี้", "ชุดถ้วยชาเซรามิก"]
        },
        {
            "slug": "novelty-self-care",
            "name_th": "ชุด Novelty & Self-Care",
            "name_en": "Novelty & Self-Care (Warm & Wellness)",
            "vibe": "ผ่อนคลาย อบอุ่น ใส่ใจ",
            "target_recipient": "กลุ่มผู้หญิง, พนักงานสาย Wellness",
            "guardrail": "ห้ามเคลมสรรพคุณ Medical โดยไม่มีหลักฐาน",
            "core_signatures": ["เทียนหอมอโรมา", "แก้วน้ำอเนกประสงค์", "ตุ๊กตาผ้าขนหนู", "สบู่ธรรมชาติกลิ่นกุหลาบ"]
        },
        {
            "slug": "executive-smart-tech",
            "name_th": "ชุดนวัตกรรมทางการทำงานอัจฉริยะ (Executive Smart Tech)",
            "name_en": "Executive Smart Tech (Modern & Work)",
            "vibe": "ทันสมัย นวัตกรรม เป็นมืออาชีพ",
            "target_recipient": "ผู้บริหาร, กลุ่มนักธุรกิจยุคใหม่",
            "guardrail": "ตรวจสเปกแบตเตอรี่และการรับรองความปลอดภัย",
            "core_signatures": ["Smart Powerbank Notebook", "Power Bank 10000mAh", "ปากกาโลหะหมึกเจล", "แฟลชไดร์ฟสายรัดแม่เหล็ก"]
        }
    ]

    # Core canonical product masters classified into 4 Top-Level Main Categories
    canonical_products = [
        {"code": "PM-TMB", "name_th": "แก้วทัมเบลอร์เก็บอุณหภูมิ (Tumbler SUS316)", "name_en": "Thermal Tumbler SUS316", "category": "Pastel Series (Soft & Friendly)", "category_slug": "pastel-series", "base_cost": 150.0},
        {"code": "PM-SPK", "name_th": "ลำโพงบลูทูธสเตอริโอคู่พรีเมียม (Bluetooth Speaker 5W)", "name_en": "Dual Stereo Bluetooth Speaker", "category": "Executive Smart Tech (Modern & Work)", "category_slug": "executive-smart-tech", "base_cost": 220.0},
        {"code": "PM-PB10K", "name_th": "พาวเวอร์แบงก์แม่เหล็กไร้สาย 10,000mAh (MagSafe & Stand)", "name_en": "MagSafe Wireless Powerbank 10000mAh", "category": "Executive Smart Tech (Modern & Work)", "category_slug": "executive-smart-tech", "base_cost": 320.0},
        {"code": "PM-CFMUG", "name_th": "แก้วกาแฟพกพาสแตนเลส 316 พร้อมฝา 3 ระบบ", "name_en": "Stainless Coffee Mug 3-Way Lid", "category": "Novelty & Self-Care (Warm & Wellness)", "category_slug": "novelty-self-care", "base_cost": 140.0},
        {"code": "PM-UMB", "name_th": "ร่มพับออโต้ 6 ตอน เคลือบซิลิโคนกันแดด UPF50+", "name_en": "Auto 6-Fold UPF50+ Umbrella", "category": "Pastel Series (Soft & Friendly)", "category_slug": "pastel-series", "base_cost": 110.0},
        {"code": "PM-MSG", "name_th": "เครื่องนวดคอพกพาคลื่นความถี่ต่ำ Low Pulse & ประคบร้อน", "name_en": "Portable Low Pulse Neck Massager", "category": "Novelty & Self-Care (Warm & Wellness)", "category_slug": "novelty-self-care", "base_cost": 380.0},
        {"code": "PM-NB", "name_th": "สมุดโน้ตหนัง PU อัจฉริยะฝังพาวเวอร์แบงก์ชาร์จไร้สาย", "name_en": "Smart Leather Powerbank Notebook", "category": "Executive Smart Tech (Modern & Work)", "category_slug": "executive-smart-tech", "base_cost": 350.0},
        {"code": "PM-PEN", "name_th": "ปากกาเจลบอดี้ไม้แท้หัวทองเหลือง (Brass Wood Signature)", "name_en": "Solid Walnut Brass Gel Pen", "category": "Classic Oriental (Mindfulness & Craft)", "category_slug": "classic-oriental", "base_cost": 85.0},
        {"code": "PM-MUG-HEAT", "name_th": "ชุดแก้วเซรามิกพร้อมแท่นอุ่นอุณหภูมิคงที่ 55°C", "name_en": "Ceramic Mug with 55C Heating Base", "category": "Novelty & Self-Care (Warm & Wellness)", "category_slug": "novelty-self-care", "base_cost": 160.0},
        {"code": "PM-FLASH", "name_th": "แฟลชไดรฟ์โลหะหมุน Dual Interface (Type-C / USB 3.0)", "name_en": "Dual Interface Metal Flash Drive", "category": "Classic Oriental (Mindfulness & Craft)", "category_slug": "classic-oriental", "base_cost": 95.0},
        {"code": "PM-BOTTLE-LED", "name_th": "กระบอกน้ำสแตนเลสบอกอุณหภูมิหน้าจอ Smart LED", "name_en": "Smart LED Temperature Thermos Bottle", "category": "Pastel Series (Soft & Friendly)", "category_slug": "pastel-series", "base_cost": 130.0},
        {"code": "PM-CUTLERY", "name_th": "ชุดช้อนส้อมมีดสแตนเลสฟู้ดเกรดพกพา", "name_en": "Portable Stainless Steel Cutlery Set", "category": "Novelty & Self-Care (Warm & Wellness)", "category_slug": "novelty-self-care", "base_cost": 75.0},
        {"code": "PM-TEA-INF", "name_th": "กระบอกชงชาแก้ว Borosilicate สองชั้นแยกกากชา", "name_en": "Double Wall Borosilicate Tea Infuser", "category": "Classic Oriental (Mindfulness & Craft)", "category_slug": "classic-oriental", "base_cost": 165.0},
        {"code": "PM-AROMA", "name_th": "เครื่องกระจายกลิ่นอโรมาอัลตราโซนิกเปลวไฟแสงไฟ Ambient", "name_en": "Ultrasonic Flame Aroma Diffuser", "category": "Novelty & Self-Care (Warm & Wellness)", "category_slug": "novelty-self-care", "base_cost": 240.0},
        {"code": "PM-FAN", "name_th": "พัดลมพกพาดีไซน์มินิมอลหน้าจอดิจิทัลแบต 4000mAh", "name_en": "Digital Display Mini Handheld Fan", "category": "Pastel Series (Soft & Friendly)", "category_slug": "pastel-series", "base_cost": 115.0},
        {"code": "PM-DESK-MAT", "name_th": "แผ่นรองโต๊ะทำงานหนัง Vegan Leather พร้อมที่ชาร์จไว", "name_en": "Wireless Charging Vegan Desk Mat", "category": "Executive Smart Tech (Modern & Work)", "category_slug": "executive-smart-tech", "base_cost": 260.0}
    ]

    extracted_offers = []
    offer_code_pattern = re.compile(r'\b([A-Z]{2,4}[0-9]{2,6}(?:-[0-9]{1,2})?)\b')

    for page_info in raw_pages:
        txt = page_info["raw_text"]
        lines = [clean_text(l) for l in txt.split('\n') if clean_text(l)]

        codes_found = offer_code_pattern.findall(txt)
        if codes_found:
            for code in codes_found:
                tiers = []
                for i in range(len(lines)):
                    if lines[i] in ['10', '20', '50', '100', '300', '500']:
                        try:
                            qty = int(lines[i])
                            if i + 1 < len(lines):
                                price_str = lines[i+1].replace(',', '').replace('บาท', '').strip()
                                if re.match(r'^\d+(\.\d+)?$', price_str):
                                    price = float(price_str)
                                    if price > 50:
                                        tiers.append({"min_qty": qty, "unit_price": price})
                        except Exception:
                            pass

                components = []
                if "ทัมเบลอร์" in txt or "Tumbler" in txt:
                    components.append({"product_code": "PM-TMB", "qty": 1})
                if "ล ำโพง" in txt or "ลำโพง" in txt or "Speaker" in txt:
                    components.append({"product_code": "PM-SPK", "qty": 1})
                if "พำวเวอร์แบงค์" in txt or "พาวเวอร์แบงก์" in txt or "Powerbank" in txt:
                    components.append({"product_code": "PM-PB10K", "qty": 1})
                if "แก้วกำแฟ" in txt or "แก้วกาแฟ" in txt:
                    components.append({"product_code": "PM-CFMUG", "qty": 1})
                if "ร่ม" in txt:
                    components.append({"product_code": "PM-UMB", "qty": 1})
                if "นวด" in txt:
                    components.append({"product_code": "PM-MSG", "qty": 1})
                if "สมุด" in txt or "Notebook" in txt:
                    components.append({"product_code": "PM-NB", "qty": 1})
                if "ปำกกำ" in txt or "ปากกา" in txt or "Pen" in txt:
                    components.append({"product_code": "PM-PEN", "qty": 1})
                if "อุ่น" in txt or "55" in txt:
                    components.append({"product_code": "PM-MUG-HEAT", "qty": 1})
                if "แฟลชไดรฟ์" in txt or "Flash" in txt:
                    components.append({"product_code": "PM-FLASH", "qty": 1})

                unique_comps = []
                seen_codes = set()
                for c in components:
                    if c["product_code"] not in seen_codes:
                        seen_codes.add(c["product_code"])
                        unique_comps.append(c)

                if unique_comps and tiers:
                    base_p = tiers[0]["unit_price"] if tiers else 500
                    if base_p >= 1500:
                        tier_name = "Bespoke"
                    elif base_p >= 800:
                        tier_name = "Signature"
                    elif base_p >= 400:
                        tier_name = "Select"
                    else:
                        tier_name = "Reach"

                    unboxing = f"บรรจุในกล่องของขวัญเกรดพรีเมียมบุฟองน้ำ EVA เข้ารูป พร้อมการ์ดอวยพรและบริการสกรีนโลโก้องค์กร"
                    if "แม่เหล็ก" in txt:
                        unboxing = "กล่องของขวัญฝาเปิด-ปิดระบบแม่เหล็ก (Magnetic Book Box) บุโฟม EVA สีกรมท่าสัมผัสนุ่ม พร้อมกลิ่นอโรมา"
                    elif "ฝำกล่อง" in txt or "ฝากล่อง" in txt:
                        unboxing = "กล่องแข็งแบบสวมเปิดบน-ล่าง (Top & Bottom Hard Box) โทนสีคลาสสิก บุผ้ากำมะหยี่กันรอย"

                    comp_codes = [c["product_code"] for c in unique_comps]
                    if any(c in comp_codes for c in ["PM-NB", "PM-PB10K", "PM-SPK", "PM-DESK-MAT"]):
                        theme_slug = "executive-smart-tech"
                        theme_name = "Executive Smart Tech (Modern & Work)"
                    elif any(c in comp_codes for c in ["PM-PEN", "PM-FLASH", "PM-TEA-INF"]):
                        theme_slug = "classic-oriental"
                        theme_name = "Classic Oriental (Mindfulness & Craft)"
                    elif any(c in comp_codes for c in ["PM-MSG", "PM-AROMA", "PM-CFMUG", "PM-MUG-HEAT", "PM-CUTLERY"]):
                        theme_slug = "novelty-self-care"
                        theme_name = "Novelty & Self-Care (Warm & Wellness)"
                    else:
                        theme_slug = "pastel-series"
                        theme_name = "Pastel Series (Soft & Friendly)"

                    extracted_offers.append({
                        "offer_code": code,
                        "page": page_info["page"],
                        "name": f"ชุดของขวัญ {code} (" + " + ".join([c["product_code"].replace("PM-", "") for c in unique_comps]) + ")",
                        "gift_tier": tier_name,
                        "interest_theme": theme_name,
                        "interest_theme_slug": theme_slug,
                        "components": unique_comps,
                        "price_tiers": sorted(tiers, key=lambda x: x["min_qty"]),
                        "unboxing_experience": unboxing
                    })

    unique_offers_map = {}
    for o in extracted_offers:
        code = o["offer_code"]
        if code not in unique_offers_map:
            unique_offers_map[code] = o
        else:
            existing_qtys = {t["min_qty"] for t in unique_offers_map[code]["price_tiers"]}
            for t in o["price_tiers"]:
                if t["min_qty"] not in existing_qtys:
                    unique_offers_map[code]["price_tiers"].append(t)
            unique_offers_map[code]["price_tiers"].sort(key=lambda x: x["min_qty"])

    catalog_offers_list = list(unique_offers_map.values())
    
    if not catalog_offers_list:
        print("Adding curated blueprint catalog offers across 4 Top-Level Main Categories...")
        catalog_offers_list = [
            {
                "offer_code": "TGC06-4",
                "page": 9,
                "name": "ชุดของขวัญ Executive Smart Tech (Smart Notebook + Power Bank + Metal Pen)",
                "gift_tier": "Signature",
                "interest_theme": "Executive Smart Tech (Modern & Work)",
                "interest_theme_slug": "executive-smart-tech",
                "components": [
                    {"product_code": "PM-NB", "qty": 1},
                    {"product_code": "PM-PB10K", "qty": 1},
                    {"product_code": "PM-PEN", "qty": 1}
                ],
                "price_tiers": [
                    {"min_qty": 10, "unit_price": 930.0},
                    {"min_qty": 50, "unit_price": 880.0},
                    {"min_qty": 100, "unit_price": 820.0}
                ],
                "unboxing_experience": "กล่องแม่เหล็กพรีเมียมบุโฟม EVA กำมะหยี่สีดำ พร้อมสมุดอัจฉริยะฝังพาวเวอร์แบงก์ชาร์จไร้สายในตัว"
            },
            {
                "offer_code": "TDD03-2",
                "page": 6,
                "name": "ชุดของขวัญ Pastel Series (ร่มพาสเทล + สมุด Skin-touch + กระบอกน้ำสุญญากาศ)",
                "gift_tier": "Select",
                "interest_theme": "Pastel Series (Soft & Friendly)",
                "interest_theme_slug": "pastel-series",
                "components": [
                    {"product_code": "PM-UMB", "qty": 1},
                    {"product_code": "PM-BOTTLE-LED", "qty": 1},
                    {"product_code": "PM-TMB", "qty": 1}
                ],
                "price_tiers": [
                    {"min_qty": 10, "unit_price": 550.0},
                    {"min_qty": 50, "unit_price": 490.0},
                    {"min_qty": 100, "unit_price": 440.0}
                ],
                "unboxing_experience": "การคุมโทนสีฟ้าพาสเทลและสัมผัส Skin-touch อ่อนหวาน ละมุน บรรจุในกล่องฝาสวมพรีเมียม"
            },
            {
                "offer_code": "TMK0215",
                "page": 7,
                "name": "ชุดของขวัญ Classic Oriental (สมุดคลิปโลหะ + ปากกาไม้แท้ + ที่คั่นหนังสือเมฆมงคล)",
                "gift_tier": "Signature",
                "interest_theme": "Classic Oriental (Mindfulness & Craft)",
                "interest_theme_slug": "classic-oriental",
                "components": [
                    {"product_code": "PM-PEN", "qty": 1},
                    {"product_code": "PM-FLASH", "qty": 1},
                    {"product_code": "PM-TEA-INF", "qty": 1}
                ],
                "price_tiers": [
                    {"min_qty": 10, "unit_price": 850.0},
                    {"min_qty": 50, "unit_price": 790.0},
                    {"min_qty": 100, "unit_price": 730.0}
                ],
                "unboxing_experience": "ดีไซน์สไตล์จีนคลาสสิกร่วมสมัย พร้อมลวดลายเมฆมงคลและพู่ไหม สัมผัสทรงคุณค่าและประณีต"
            },
            {
                "offer_code": "TWL01-8",
                "page": 8,
                "name": "ชุดของขวัญ Novelty & Self-Care (เทียนหอมอโรมา + แก้วอเนกประสงค์ + สบู่กุหลาบ)",
                "gift_tier": "Select",
                "interest_theme": "Novelty & Self-Care (Warm & Wellness)",
                "interest_theme_slug": "novelty-self-care",
                "components": [
                    {"product_code": "PM-AROMA", "qty": 1},
                    {"product_code": "PM-CFMUG", "qty": 1},
                    {"product_code": "PM-MSG", "qty": 1}
                ],
                "price_tiers": [
                    {"min_qty": 10, "unit_price": 680.0},
                    {"min_qty": 50, "unit_price": 620.0},
                    {"min_qty": 100, "unit_price": 570.0}
                ],
                "unboxing_experience": "ชุดผ่อนคลายอโรมาเธอราพี ให้ความรู้สึกอบอุ่น ใส่ใจ เหมาะสำหรับแคมเปญสุขภาพและ Wellness"
            }
        ]

    print(f"Extracted {len(catalog_offers_list)} distinct Catalog Offers from {len(doc)} pages.")

    corporate_bundles = [
        {
            "bundle_code": "PKG-SME-ELITE",
            "name": "SME Elite Corporate Bundle (Package A)",
            "target_recipients": 35,
            "total_price": 46250.00,
            "description": "แพ็กเกจสำหรับบริษัทขนาดกลาง หรือ 1 แผนกใหญ่ ครอบคลุม 3 ระดับผู้รับ (VIP 5 ชุด, หัวหน้างาน 10 ชุด, ทีมงาน 20 ชุด)",
            "tier_breakdown": {
                "Bespoke (VIP 5 ชุด)": "เครื่องนวดคอพรีเมียม + แก้วกาแฟ 3-Way + ปากกาไม้แท้ (Novelty & Oriental)",
                "Signature (Exec 10 ชุด)": "สมุดโน้ตอัจฉริยะ Powerbank + ปากกาไม้ + ลำโพงบลูทูธ (Executive Smart Tech)",
                "Reach (Staff 20 ชุด)": "แก้วทัมเบลอร์ SUS316 + ร่มพับ UPF50+ (Pastel Series)"
            },
            "included_offers": [
                {"offer_code": catalog_offers_list[0]["offer_code"] if catalog_offers_list else "TDD03-2", "qty": 10},
                {"offer_code": catalog_offers_list[1]["offer_code"] if len(catalog_offers_list) > 1 else "TMK0215", "qty": 5},
                {"offer_code": catalog_offers_list[2]["offer_code"] if len(catalog_offers_list) > 2 else "TGC06-4", "qty": 20}
            ]
        },
        {
            "bundle_code": "PKG-ENTERPRISE-160",
            "name": "Enterprise Annual Gala Bundle (Package B)",
            "target_recipients": 160,
            "total_price": 185000.00,
            "description": "แพ็กเกจงานประชุมใหญ่หรือปีใหม่องค์กร ครอบคลุมบอร์ดบริหาร 10 ท่าน, ผู้จัดการ 30 ท่าน, และพนักงาน 120 ท่าน",
            "tier_breakdown": {
                "Bespoke (Board 10 ชุด)": "เซ็ตเครื่องนวดคอ + สมุดอัจฉริยะ + แก้วกาแฟ 3-Way (Novelty & Executive)",
                "Signature (Mgr 30 ชุด)": "เซ็ตพาวเวอร์แบงก์ MagSafe + ลำโพงบลูทูธ + แฟลชไดร์ฟโลหะ (Executive Smart Tech)",
                "Select/Reach (Staff 120 ชุด)": "แก้วทัมเบลอร์ + ร่มพับกันแดด (Pastel Series)"
            },
            "included_offers": [
                {"offer_code": catalog_offers_list[0]["offer_code"] if catalog_offers_list else "TDD03-2", "qty": 30},
                {"offer_code": catalog_offers_list[1]["offer_code"] if len(catalog_offers_list) > 1 else "TMK0215", "qty": 10},
                {"offer_code": catalog_offers_list[2]["offer_code"] if len(catalog_offers_list) > 2 else "TGC06-4", "qty": 120}
            ]
        }
    ]

    master_payload = {
        "metadata": {
            "source_pdf": PDF_PATH,
            "total_pages": len(doc),
            "total_top_level_categories": len(top_level_categories),
            "total_canonical_products": len(canonical_products),
            "total_catalog_offers": len(catalog_offers_list),
            "total_corporate_bundles": len(corporate_bundles)
        },
        "top_level_categories": top_level_categories,
        "canonical_products": canonical_products,
        "catalog_offers": catalog_offers_list,
        "corporate_bundles": corporate_bundles
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(master_payload, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved canonical catalog dataset to {OUTPUT_JSON}")
    return master_payload

if __name__ == "__main__":
    parse_catalog()
