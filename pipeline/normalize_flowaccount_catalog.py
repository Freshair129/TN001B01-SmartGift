# -*- coding: utf-8 -*-
"""
SmartGift FlowAccount Catalog Normalization Engine (with Factory Cost Pairing)
Converts FlowAccount 1,319 raw products into clean, deduplicated ProductMaster models:
  * Collapses artificial 5x tier codes (-10, -20, -50, -100, -500) into native price_tiers
  * Extracts authoritative factory cost tiers from the 110-page factory PDF
  * Displays selling price (FlowAccount) alongside factory cost (PDF) and calculates margins
  * Segregates Services (printing/laser/freight) and Packaging (boxes/sleeves) from products
  * Generates zero-SKU-bloat normalized catalog JSON in data-pipeline/02_prepared/
"""

import openpyxl
import pypdf
import os
import sys
import re
import json
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r'C:\Users\pc\workspace\business-01-smart-gift'
# Primary canonical path with fallback to legacy junction
PDF_PATH = os.path.join(BASE_DIR, r'data-pipeline\01_raw\02_catalog_srp_pricelists_pdf\01-ใบเสนอราคา-update12กย68(แปลอังกฤษ to ไทยยังไม่เสร็จ).pdf')
if not os.path.exists(PDF_PATH):
    PDF_PATH = os.path.join(BASE_DIR, r'data-pipeline\01_raw\02_factory_pricelists_pdf\01-ใบเสนอราคา-update12กย68(แปลอังกฤษ to ไทยยังไม่เสร็จ).pdf')
XLSX_PATH = os.path.join(BASE_DIR, r'data-pipeline\01_raw\01_flowaccount_exports\บริษัท เทราบิส จำกัด_product.xlsx')
OUT_JSON = os.path.join(BASE_DIR, r'data-pipeline\02_prepared\flowaccount_catalog_normalized.json')
OUT_AUDIT = os.path.join(BASE_DIR, r'data-pipeline\04_review_reports\flowaccount_normalization_audit_2026-09-10.json')

EXCLUDE_WORDS = {'USB', 'TYPE', 'DC', 'UPF', 'SUS', 'LED', 'PP', 'TPE', 'ABS', 'VIP', 'ESG', 'MIN', 'MAX', 'SET', 'SETS', 'CTN', 'HTML'}

def extract_factory_catalog(pdf_path):
    print('Loading factory PDF pricelist from:', pdf_path)
    reader = pypdf.PdfReader(pdf_path)
    factory_catalog = {}

    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.split('\n')
        current_code = None

        for l in lines:
            # Check if line contains a model code
            code_match = re.search(r'\b([A-Z]{2,4}[0-9]{1,4}(?:-[0-9A-Za-z]+)?)\b', l)
            if code_match:
                c = code_match.group(1)
                if c not in EXCLUDE_WORDS:
                    current_code = c
                    if current_code not in factory_catalog:
                        factory_catalog[current_code] = {
                            'factory_code': current_code,
                            'pdf_page': page_idx + 1,
                            'available_colors': None,
                            'factory_price_tiers': {}
                        }

            # Check for color specification
            if current_code and 'สี' in l:
                color_m = re.search(r'สี\s+([^\n\r0-9]+)', l)
                if color_m and not factory_catalog[current_code]['available_colors']:
                    factory_catalog[current_code]['available_colors'] = color_m.group(1).strip()

            # Check for quantity tier & price in line e.g. '10 1,310' or '500 890'
            if current_code:
                tier_match = re.search(r'\b(10|20|50|100|300|500|1000)\s+([0-9]{1,3}(?:,[0-9]{3})*)\b', l)
                if tier_match:
                    qty = int(tier_match.group(1))
                    price = float(tier_match.group(2).replace(',', ''))
                    if 50 <= price <= 50000:
                        factory_catalog[current_code]['factory_price_tiers'][qty] = price

    print(f'-> Extracted {len(factory_catalog)} unique factory models from PDF')
    return factory_catalog

def run_normalization():
    factory_catalog = extract_factory_catalog(PDF_PATH)

    print('\nLoading FlowAccount products from:', XLSX_PATH)
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))

    header_idx = -1
    for i, r in enumerate(rows[:10]):
        if r and 'ProductCode' in r:
            header_idx = i
            break

    headers = rows[header_idx]
    code_idx = headers.index('ProductCode')
    name_idx = headers.index('Name')
    unit_idx = headers.index('Unit')
    cat_idx = headers.index('Category')
    desc_idx = headers.index('Description')
    price_idx = headers.index('UnitPrice')

    normalized_products = {}
    services = []
    packaging = []
    deprecated = []
    custom_lines = []

    for row_no, r in enumerate(rows[header_idx+1:], start=header_idx+2):
        if not r or not any(r):
            continue
        raw_code = str(r[code_idx] or '').strip()
        name = str(r[name_idx] or '').strip()
        desc = str(r[desc_idx] or '').strip()
        unit = str(r[unit_idx] or 'ชิ้น').strip()
        category = str(r[cat_idx] or '').strip()
        price = float(r[price_idx] or 0)

        if 'ไม่ใช้งานแล้ว' in name:
            deprecated.append({'row': row_no, 'name': name, 'raw_code': raw_code})
            continue

        # Case 1: Has tier suffix e.g. BE0011(P-09)-10 or THB03-2(P-20)-500
        tier_match = re.match(r'^([A-Za-z0-9_-]+(?:\([A-Za-z0-9_-]+\))?)-(\d+)$', raw_code)
        if tier_match:
            base_code = tier_match.group(1)
            min_qty = int(tier_match.group(2))
            
            pkg_match = re.match(r'^([A-Za-z0-9_-]+)\(([A-Za-z0-9_-]+)\)$', base_code)
            if pkg_match:
                model_code = pkg_match.group(1)
                package_code = pkg_match.group(2)
            else:
                model_code = base_code
                package_code = None

            if base_code not in normalized_products:
                fc_info = factory_catalog.get(model_code)
                normalized_products[base_code] = {
                    'code': base_code,
                    'model_code': model_code,
                    'package_code': package_code,
                    'name': name,
                    'unit': unit,
                    'category': category or 'Gift Set',
                    'stock_policy': 'UNTRACKED',
                    'description': desc,
                    'factory_info': fc_info,
                    'price_tiers': [],
                    'source_rows': []
                }
            normalized_products[base_code]['source_rows'].append(row_no)
            normalized_products[base_code]['price_tiers'].append({
                'min_qty': min_qty,
                'unit_price': price
            })
            continue

        # Case 2: Code present without tier suffix e.g. CK-003
        if raw_code:
            if raw_code not in normalized_products:
                fc_info = factory_catalog.get(raw_code)
                normalized_products[raw_code] = {
                    'code': raw_code,
                    'model_code': raw_code,
                    'package_code': None,
                    'name': name,
                    'unit': unit,
                    'category': category or 'General',
                    'stock_policy': 'UNTRACKED',
                    'description': desc,
                    'factory_info': fc_info,
                    'price_tiers': [{'min_qty': 1, 'unit_price': price}] if price > 0 else [],
                    'source_rows': [row_no]
                }
            continue

        # Case 3: Empty code - check services / packaging
        is_service = any(k in name for k in ['สกรีน', 'เลเซอร์', 'พิมพ์', 'บันทึกข้อมูล', 'ค่าจัดส่ง'])
        is_pkg = any(k in name for k in ['กล่อง', 'ปลอก', 'โบว์', 'ริบบิ้น', 'ถุง'])
        
        if is_service:
            services.append({'row': row_no, 'name': name, 'unit': unit, 'price': price, 'description': desc, 'category': 'SERVICE'})
            continue
        if is_pkg:
            packaging.append({'row': row_no, 'name': name, 'unit': unit, 'price': price, 'description': desc, 'category': 'PACKAGING'})
            continue

        # Match embedded model code in name
        model_found = None
        for fc in factory_catalog:
            if fc in name:
                model_found = fc
                break
        if not model_found:
            m_search = re.search(r'(?:Model\s*[:\.]?\s*|รหัส\s*[:\.]?\s*)([A-Za-z0-9_-]+)', name)
            if m_search:
                model_found = m_search.group(1).upper()

        if model_found:
            gen_code = model_found
            if gen_code not in normalized_products:
                fc_info = factory_catalog.get(model_found)
                normalized_products[gen_code] = {
                    'code': gen_code,
                    'model_code': model_found,
                    'package_code': None,
                    'name': name,
                    'unit': unit,
                    'category': category or 'Gift Set',
                    'stock_policy': 'UNTRACKED',
                    'description': desc,
                    'factory_info': fc_info,
                    'price_tiers': [{'min_qty': 1, 'unit_price': price}] if price > 0 else [],
                    'source_rows': [row_no]
                }
            else:
                normalized_products[gen_code]['source_rows'].append(row_no)
                if price > 0 and not any(t['unit_price'] == price for t in normalized_products[gen_code]['price_tiers']):
                    normalized_products[gen_code]['price_tiers'].append({'min_qty': 1, 'unit_price': price})
        else:
            custom_lines.append({'row': row_no, 'name': name, 'unit': unit, 'category': category or 'Custom', 'price': price, 'description': desc})

    # Pair price_tiers with factory costs and calculate margins
    for p in normalized_products.values():
        p['price_tiers'].sort(key=lambda x: x['min_qty'])
        fc_tiers = p.get('factory_info', {}).get('factory_price_tiers', {}) if p.get('factory_info') else {}

        for tier in p['price_tiers']:
            qty = tier['min_qty']
            unit_price = tier['unit_price']
            
            # Match exact tier or find closest matching tier from factory
            factory_cost = None
            if qty in fc_tiers:
                factory_cost = fc_tiers[qty]
            elif fc_tiers:
                # Find tier with closest min_qty <= qty, or lowest tier
                eligible_qtys = [q for q in fc_tiers.keys() if q <= qty]
                if eligible_qtys:
                    factory_cost = fc_tiers[max(eligible_qtys)]
                else:
                    factory_cost = fc_tiers[min(fc_tiers.keys())]

            tier['factory_cost'] = factory_cost
            if factory_cost is not None and unit_price > 0:
                tier['margin_thb'] = round(unit_price - factory_cost, 2)
                tier['margin_percent'] = round(((unit_price - factory_cost) / unit_price) * 100, 1)
            else:
                tier['margin_thb'] = None
                tier['margin_percent'] = None

    output_payload = {
        'metadata': {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'source_flowaccount_file': 'บริษัท เทราบิส จำกัด_product.xlsx',
            'source_factory_pdf': '01-ใบเสนอราคา-update12กย68(แปลอังกฤษ to ไทยยังไม่เสร็จ).pdf',
            'total_source_rows': len(rows) - header_idx - 1,
            'total_normalized_products': len(normalized_products),
            'total_services': len(services),
            'total_packaging': len(packaging),
            'total_custom_unclassified': len(custom_lines),
            'total_deprecated': len(deprecated)
        },
        'products': list(normalized_products.values()),
        'services': services,
        'packaging': packaging,
        'custom_lines': custom_lines,
        'deprecated': deprecated
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)
    print(f'-> Successfully wrote normalized catalog with factory cost pairing to: {OUT_JSON}')

    os.makedirs(os.path.dirname(OUT_AUDIT), exist_ok=True)
    with open(OUT_AUDIT, 'w', encoding='utf-8') as f:
        json.dump(output_payload['metadata'], f, ensure_ascii=False, indent=2)
    print(f'-> Successfully wrote audit summary to: {OUT_AUDIT}')

if __name__ == '__main__':
    run_normalization()
