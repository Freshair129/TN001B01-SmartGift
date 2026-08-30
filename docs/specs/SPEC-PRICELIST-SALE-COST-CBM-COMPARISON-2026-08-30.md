---
version: "0.3.0b"
created_at: "2026-08-30T13:14:02+07:00,ATHER"
last_update: "2026-08-30T15:25:41+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-pricing"
  doc_type: "comparison-report-and-specification"
  scope: "read-only sale versus factory-reference cost and CBM comparison; JSON extension implemented"
  language: "th"
---

# เปรียบเทียบราคาขาย ราคาทุนอ้างอิง และค่าขนส่ง CBM

**Complexity / Risk:** C-2 / MEDIUM

ผลเปรียบเทียบในเอกสารนี้คำนวณจากไฟล์ที่ตรวจจริง และ export ลง JSON แบบ local review-only; ไม่แก้ Excel, schema, engine หรือ vault

อ้างอิง parent/peer: [ADR-002](../decisions/ADR-002-PRICELIST-MASTER-SQL-SNAPSHOT.md), [ontology](../../config/schema_genesisblock.yaml), [สูตรราคา](../../config/pricing_rules_formula.yaml), [pricing calculator](../../src/cascade_engine/pricing_calculator.py), [Price Boss schema](../../price-boss/sql/schema.sql)

## 1. ความหมายของราคาและขอบเขต

- **ราคาขาย:** `smartgift_price.unit_price` ของ FlowAccount snapshot แสดงพร้อม quantity tier, price ID, supplier group และวัน export ไม่ใช่ราคาปัจจุบันที่ยืนยันพร้อมเสนอขาย
- **ต้นทุนโรงงานอ้างอิง:** `products.rmb` จาก `price-boss/ราคา.sql` × FX ที่ระบุ ยังไม่ใช่ราคาซื้อที่ยืนยันด้วย PO/invoice หรือ landed cost
- **ต้นทุนตามสูตรก่อนขนส่ง:** ต้นทุนโรงงานอ้างอิง × small-order factor (SOF) ของ calculator เป็น model estimate ไม่ใช่การแก้ราคาต้นทาง
- **ราคา CBM:** แสดงทั้งอัตรา THB/CBM, ปริมาตรกล่อง, ปริมาตรคิดเงิน, ค่าขนส่งรวม และค่าขนส่งต่อหน่วย หากคิดตามน้ำหนักต้องแสดง THB/kg และฐานคิดเงินจริงด้วย
- **ต้นทุนรวมส่งมอบ:** สินค้า + ขนส่งจีน–ไทย + ค่าใช้จ่ายตรงที่เกี่ยวข้องทั้งหมด โดยไม่บวกค่าใช้จ่ายเดียวกันซ้ำ หากต้นทุนไม่ครบ ให้เป็น null แทนศูนย์
- **กำไร pkg:** ยอดขายสุทธิหลังส่วนลด − ต้นทุนรวมส่งมอบ ต้อง ≥ **25,000 บาทต่อ pkg** ตามข้อกำหนดผู้ใช้ ไม่ใช้ floor 3,000/5,000 ของ quote engine หรือค่าเดิม 20,000 มาแทน

[ASSUMPTIONS]

1. ตัวอย่างเปรียบเทียบราคาขายใช้ quantity tier **100 หน่วย** จาก SQL จริง ไม่เปลี่ยน tier ที่หายเป็น 100
2. FX **5 THB/CNY** เป็นค่าที่ประกาศใน config สำหรับสถานการณ์อ้างอิง ไม่ใช่อัตราตลาดที่ตรวจสด
3. สมมติว่า RMB และราคาขายอ้างหน่วยขายเดียวกันเพื่อเปรียบเทียบเบื้องต้น ต้องตรวจ variant/ชุดสินค้า/ผู้ขายและฐาน VAT ก่อนใช้เสนอราคาหรือคำนวณกำไรจริง
4. ตัวอย่าง CBM แยกต่างหากใช้ **กวางโจว/เซินเจิ้น → รถ → สินค้าทั่วไป → สมาชิกขนส่ง GOLD → 100 หน่วย** เป็น scenario ไม่ใช่คำสั่งเลือกขนส่งให้ทุกสินค้า

GiftTier `Reach / Select / Signature / Bespoke` เป็นระดับแพ็กเกจ ส่วน `ELITE / GOLD / SILVER / MEMBER` เป็นสมาชิกขนส่ง ห้าม mapping สองแกนนี้เข้าหากันอัตโนมัติ

## 2. ข้อมูลที่ตรวจพบ

| แหล่งข้อมูล | ผลตรวจ |
|---|---|
| `pricelist_master.json` / SQL snapshot | 669 แถวราคา; 551 แถวมีราคาบวกที่ไม่ missing และ qty tier บวก |
| `price-boss/ราคา.sql` | 1,087 product rows / 1,087 codes ไม่ซ้ำ: giftset 1,016, powerbank 71; RMB บวก 1,086 |
| ข้อมูล logistics ใน `ราคา.sql` | UPC และขนาดกล่องครบ 316 รายการ; มีน้ำหนักบวกเพียง 1 รายการ |
| จับคู่ราคา → catalog ด้วย code ตรง | 404 แถวราคา / 131 offer codes; ไม่พบคู่ 265 แถวราคา |
| มีราคาขาย + qty tier บวก + RMB อ้างอิง | **333 แถวราคา** เปรียบเทียบราคาขายกับต้นทุนโรงงานอ้างอิงได้ |
| มีราคาขาย + qty tier + RMB + logistics ครบ | **0 แถว** ยังไม่มีแถวที่พิสูจน์ราคาทั้งสามส่วนครบ |
| แถวที่จับคู่แล้วมีขนาดกล่อง | FXD8816 / price ID 526 และ FXD37-3 / price ID 742 แต่ทั้งสองมีราคา 0, `price_missing=true`, qty tier null |
| Excel ที่ hash ตรง lineage SQL | `01_raw/01_flowaccount_exports/บริษัท เทราบิส จำกัด_product.xlsx`, sheet products, headers row 3, data rows 4–1322; BuyPrice บวกเพียง 1 แถว (I23 = 390, B23 code ว่าง) จึงไม่สามารถจับคู่ต้นทุนให้ price rows ได้ |
| Excel อีกสำเนาที่ `01_raw/` | data rows 4–1338; BuyPrice บวกเพียงแถว I40 = 390 และ B40 code ว่าง เช่นเดียวกัน แต่ hash ต่างกัน จึงไม่ปน snapshot |
| master เดิม | canonical_products ทั้ง 16 มี `base_cost == srp_price`; ยังไม่มีหลักฐานราคาโรงงาน/ใบซื้อผูกกับค่าเหล่านี้ จึงไม่ใช้เป็นต้นทุนจริง |

การ match code เป็น **candidate match** สำหรับเปรียบเทียบ ไม่ใช่การยืนยัน BOM/variant หรือ price authority และไม่รวมทุกราคา tier เป็นสินค้าใหม่

ราคาขายอ้าง FlowAccount export **2026-06-21** ส่วน catalog factory-reference dump สร้าง **2026-08-29** เป็นคนละ snapshot ต้องแสดงทั้งสองวัน ไม่อ้างว่าส่วนต่างเป็นกำไรของช่วงเวลาเดียวกัน

## 3. ตัวอย่างราคาขายเทียบต้นทุนโรงงานอ้างอิง

หน่วยเงินบาทต่อหน่วยขายที่ qty tier 100; SOF ที่ qty 100 ใน calculator = **1.2** ทุกช่องทุนเป็น **reference/estimate** ส่วนค่าขนส่งและต้นทุนรวมยังไม่พร้อม คอลัมน์ CBM ไม่ใช่ศูนย์

| รหัส | ราคาขาย snapshot | โรงงาน RMB | โรงงาน × FX 5 | หลัง SOF 1.2 ก่อนขนส่ง | ค่าขนส่ง CBM/หน่วย | Price ID | บรรทัด `ราคา.sql` |
|---|---:|---:|---:|---:|---|---:|---:|
| TBS01-2 | 620.00 | 36.00 | 180.00 | 216.00 | ขาดขนาดกล่อง/UPC | 210 | 824 |
| TSP06-2 | 1,680.00 | 158.00 | 790.00 | 948.00 | ขาดขนาดกล่อง/UPC | 222 | 727 |
| TSQ06-4 | 1,300.00 | 91.00 | 455.00 | 546.00 | ขาดขนาดกล่อง/UPC | 254 | 746 |
| TBH04-2 | 570.00 | 105.00 | 525.00 | 630.00 | ขาดขนาดกล่อง/UPC | 265 | 706 |
| TSPB2-2 | 1,660.00 | 155.00 | 775.00 | 930.00 | ขาดขนาดกล่อง/UPC | 279 | 733 |
| TBS02-4 | 820.00 | 52.00 | 260.00 | 312.00 | ขาดขนาดกล่อง/UPC | 286 | 827 |
| TBH06-2 | 570.00 | 95.00 | 475.00 | 570.00 | ขาดขนาดกล่อง/UPC | 307 | 704 |
| TBJ03-3 | 1,090.00 | 62.00 | 310.00 | 372.00 | ขาดขนาดกล่อง/UPC | 320 | 846 |

ข้อสังเกตสำหรับทบทวนราคา: TBH04-2 มีราคาขาย snapshot ต่ำกว่าต้นทุนตามสูตรก่อนขนส่ง **60 บาท/หน่วย** และ TBH06-2 เท่ากันพอดี ภายใต้สมมติฐาน FX/SOF/หน่วยขายข้างต้น ยังไม่ใช่ข้อสรุปว่าธุรกรรมจริงขาดทุน เพราะ snapshot และต้นทุนซื้อยังไม่ได้ยืนยัน

## 4. ตารางอัตรา CBM ที่มีในระบบ

หน่วย **บาท/CBM** อ่านเทียบกับ runtime rate table ของ calculator ปัจจุบัน ไม่ใช่ใบเสนอราคาจากผู้ขนส่งที่ตรวจสด

| ต้นทาง / วิธี / ประเภท | ELITE | GOLD | SILVER | MEMBER |
|---|---:|---:|---:|---:|
| กวางโจว–เซินเจิ้น / รถ / ทั่วไป | 5,900 | 6,400 | 6,900 | 7,400 |
| กวางโจว–เซินเจิ้น / รถ / electronic_tisi | 6,400 | 6,900 | 7,400 | 7,900 |
| กวางโจว–เซินเจิ้น / เรือ / ทั่วไป | 3,900 | 4,400 | 4,900 | 5,400 |
| กวางโจว–เซินเจิ้น / เรือ / electronic_tisi | 4,400 | 4,900 | 5,400 | 5,900 |
| อี้อู / รถ / ทั่วไป | 6,400 | 6,900 | 7,400 | 7,900 |
| อี้อู / รถ / electronic_tisi | 6,900 | 7,400 | 7,900 | 8,400 |
| อี้อู / เรือ / ทั่วไป | 3,900 | 4,400 | 4,900 | 5,400 |
| อี้อู / เรือ / electronic_tisi | 4,400 | 4,900 | 5,400 | 5,900 |

สำหรับสินค้าทั่วไป กวางโจว–เซินเจิ้น/รถ/GOLD มี rate **6,400 บาท/CBM หรือ 16 บาท/kg** และ engine เลือกน้ำหนักเมื่อ density ≥ 400 kg/CBM ถ้าน้ำหนักหาย การคำนวณเฉพาะปริมาตรเป็น scenario เท่านั้น ห้ามบอกว่าเป็นราคาขนส่งสุดท้าย

### ตัวอย่างคำนวณ CBM จากแถวที่มี logistics ครบ

`BW16-2`, `ราคา.sql:577`: RMB 23.5, 40 หน่วย/กล่อง, กล่อง 80.5 × 51 × 24 cm, น้ำหนัก 17 kg/กล่อง ขนาดใช้ตาม semantics ของ `seed_china_sourcing.sql` ที่ map dim_l/w/h ไป carton_*_cm ยังต้องยืนยัน packing specification จากโรงงานก่อนใช้จริง

| รายการ | ค่า |
|---|---:|
| จำนวนใน scenario | 100 หน่วย |
| CBM จริงต่อกล่อง = L×W×H / 1,000,000 | 0.098532 |
| กล่องที่ต้องใช้ = ceil(100/40) | 3 |
| ปริมาตรรวมก่อนปัดเศษ | 0.295596 CBM |
| ปริมาตรคิดเงินตาม rounding ใน engine ปัจจุบัน | 0.30 CBM |
| น้ำหนักรวม / ความหนาแน่น | 51 kg / 172.53 kg/CBM |
| ฐานคิดเงิน | volume |
| ค่าขนส่งรวม = 0.30×6,400 | 1,920 บาท |
| ค่าขนส่งต่อหน่วย = 1,920/100 | **19.20 บาท** |
| ทุนโรงงานอ้างอิง = 23.5×5 | 117.50 บาท/หน่วย |
| ทุนหลัง SOF 1.2 | 141.00 บาท/หน่วย |
| รวมสองส่วนที่คำนวณได้ = 141+19.20 | **160.20 บาท/หน่วย ก่อนค่าใช้จ่ายอื่น** |
| ราคาขายที่จับคู่ได้จาก price snapshot | ไม่พบแถวราคา |

160.20 ไม่ใช่ landed cost ที่ครบ ไม่รวม inland จีน, branding, packaging เพิ่มเติม, ประกอบ, ส่งมอบปลายทาง และต้นทุนตรงอื่นที่ยังไม่ยืนยัน จึงไม่คำนวณกำไรหรือสถานะผ่าน 25,000 บาทจากตัวอย่างนี้

## 5. ข้อจำกัดและข้อมูลที่ต้องขอเพิ่ม

1. ราคาโรงงาน/ใบซื้อที่ยืนยัน พร้อม supplier, currency, MOQ, หน่วยขาย, validity และฐาน VAT
2. carton UPC, L/W/H (cm), gross kg และ source document ต่อ SKU/variant ที่จับคู่ราคาขาย โดยไม่ยืมขนาดจากคนละรหัส
3. shipping warehouse/mode/goods classification/member tier และอัตราที่ใช้งานจริง ไม่ใช้ GiftTier แทนสมาชิกขนส่ง
4. package BOM, จำนวนสั่งและต้นทุนตรงทั้งหมด เพื่อประเมินกำไร 25,000 บาทต่อ pkg

ไม่ใช้ `logistics_freight_est` ของ master เดิมเป็น measured evidence: `pipeline/enrich_review_catalog.py:254–282` ใส่ dimensions/specs แบบตารางค่าคงที่ และมี fallback; `pipeline/add_dimensions_weight.py` ใส่ขนาด/น้ำหนักเริ่มต้นเมื่อข้อมูลหาย ไม่พบเอกสารวัดหรือโรงงานกำกับค่าเหล่านั้นจากการตรวจรอบนี้

ค่า `base_cost == srp_price` เป็นข้อสังเกตที่พิสูจน์จากข้อมูลได้ แต่ยังไม่ยืนยันว่า process ใดเขียนค่า จึงไม่กล่าวอ้าง RCA ของการเขียนทับและไม่แก้ค่าเหล่านั้นในงานนี้

## 6. ตารางเปรียบเทียบใน JSON — implementation local

เพิ่ม `price_comparisons` ใน `pricelist_master.json` โดยคง prices ต้นฉบับครบ **669 แถว** มี 1 comparison ต่อ price ID และไม่ drop แถวที่จับคู่ไม่ได้ ไม่ปรับ sale price หรือ cost เดิม

เพิ่ม `srp_reference_products` 16 แถว และ `srp_qty_comparisons` **128 แถว** (16 สินค้า × qty `1, 10, 20, 50, 100, 300, 500, 1000`) เพื่อให้มีราคาชิ้นเดียวตามคำยืนยันล่าสุดของผู้ใช้ แหล่ง SRP คือ `canonical_products.price_tiers` ใน `smartgift_catalog_master.json`; ไม่ใช้ `base_cost` ที่เท่ากับ SRP เป็นทุนโรงงาน

ฟิลด์ที่เสนอ:

- Identity: `price_id`, `offer_code`, `qty_tier`, `price_list_group`, `source_run_id`
- ขาย: `sale_unit_price`, `sale_vat_basis`, `sale_export_date`
- โรงงาน: `factory_catalog_key`, `factory_unit_cny`, `fx_thb_per_cny`, `factory_reference_thb`, `small_order_factor`, `factory_adjusted_estimate_thb`, `factory_export_date`
- Logistics: `units_per_carton`, `carton_dimensions_cm`, `carton_cbm`, `carton_gross_kg`, `shipping_context`, `rate_thb_per_cbm`, `rate_thb_per_kg`, `cartons`, `chargeable_basis`, `charged_volume_cbm`, `freight_total_thb`, `freight_per_unit_thb`
- ผลเทียบ: `delivered_unit_cost`, `unit_profit`, `margin_percent`, `comparison_status`, `missing_inputs`, `identity_review_required`, `quote_ready=false`
- Provenance: source path/hash/row key หรือ statement line ของทั้งฝั่งขาย, factory catalog และ rate/config

`factory_reference_thb` และ `factory_adjusted_estimate_thb` ต้องบอกชัดว่าเป็นราคาอ้างอิง/model estimate และไม่เขียนลง `ProductMaster.base_cost` อัตโนมัติ

สถานะ: `missing_factory_match`, `invalid_sale_or_qty`, `factory_reference_only`, `freight_estimate_only`, `complete_reference_comparison` แยกจาก quote approval และ pkg profit approval โดยชัดเจน ข้อมูล/ฐานภาษีไม่ครบให้ `delivered_unit_cost`, `unit_profit`, `margin_percent` เป็น null

ผล local snapshot นี้มี exact factory match สำหรับ price rows 404/669 (131 offer codes) แต่ไม่มี exact code match ระหว่าง `PM-*` ทั้ง 16 รายการกับ `price-boss/ราคา.sql`; ดังนั้นแถว SRP ทั้ง 128 แถวมี `factory_cost_thb=null` และสถานะ `missing_factory_match` โดยไม่เดาชื่อหรือ variant

ใช้ [pricing_calculator.py](../../src/cascade_engine/pricing_calculator.py) เดิมสำหรับสูตร แต่ตรวจ input/context ก่อนเรียก ไม่ใช้ fallback warehouse/rate, upc=1, kg หาย หรือค่าทุนที่เดาเองเป็นหลักฐานว่าราคาพร้อมใช้ ไม่ขยายงานไปแก้ engine/config หากจำเป็นต้องแก้ให้แยก RCA และขออนุมัติ scope

## 7. เกณฑ์ตรวจรับหลังอนุมัติ implementation

1. แถวราคา 669 คงเดิม; 404 matched, 265 unmatched, 333 มี sale/qty/factory reference ที่ใช้เทียบได้สำหรับ source hashes นี้
2. Source identity ใช้ `(catalog_key, code)`; duplicate/ambiguous matches ต้องหยุดไม่เลือกอัตโนมัติ; supplier/variant/unit review แยกจาก code match
3. ต้นทุน missing ไม่เป็น 0, SRP ไม่กลายเป็นทุน, sale price ไม่ถูกเขียนทับ และคนละ snapshot ไม่ถูกอ้างว่าเป็นต้นทุน/ราคาวันเดียวกัน
4. CBM หน่วย cm→m³ ถูกต้อง; จำนวนกล่องใช้ ceil; ตรวจ rounding, minimum CBM และ boundary density 400 ตาม engine พร้อมแสดง basis
5. Weight/route/goods/tier หายหรือไม่รู้จักไม่ผ่าน final freight gate; GiftTier ไม่ผูกเป็น shipping-member tier
6. ประเมิน pkg profit ≥ 25,000 เฉพาะข้อมูลส่งมอบครบ โดยไม่ใช้กำไร SKU ตัวเดียวแทนทั้ง pkg
7. Regeneration reproducible; source hashes ตรง; tests ของ mapping/units/missing-data/VAT-context/rounding ผ่าน และไม่แก้ source/shared dirty files

## 8. Source fingerprint และผลตรวจรอบนี้

| Source | SHA-256 |
|---|---|
| `price-boss/ราคา.sql` | `d85e114018a4792d7a3aa8fc9b4f35475f40e9948bffd5aa04cf0171b5c9cb24` |
| `price-boss/sql/smartgiftpricelist.postgres.sql` | `263556642064f6398e4cd00a7a4897ca7ba841b7c3bae5b8d2165b3186b2fdd4` |
| `pricelist_master.json` หลังเพิ่ม seasonal projection | `d0cde107f8351bf3e59487204987cfde5584817ccbc2f1bc31a100691fbe447a` |
| `smartgift_catalog_master.json` ณ ตรวจ | `63f3e5668de6818cc3517543bdf0d1331bf7926d1769815290dbcd5f740c0ac7` |
| `config/pricing_rules_formula.yaml` | `f4473230f10b59133936974a0cacf84bbe84865d61db76553d8cc2a58ba635fc` |
| `src/cascade_engine/pricing_calculator.py` | `c09de992ca1001fbc6abc4ee39e68a1eb6b326a33054bb8cc0c0c2cee8a811d1` |
| FlowAccount product export ที่ตรง lineage SQL | `da7452ffd91baca7c5e24198e0418585f8da17265bd190447f7c83b755fca318` |
| Product Excel อีกสำเนาที่ `01_raw/` | `38be21ae9ba0748e4249d99097b7923a87c1dee3b7ac0510d40774f6f87c4032` |

ตรวจ parse/match/count, คอลัมน์ BuyPrice ของ Excel ทั้งสองสำเนาแบบ read-only และผล `calculate_freight` สำหรับ BW16-2 แล้ว; implementation เพิ่ม parser/export comparison และ seasonal package/BOM projection ใน [exporter](../../pipeline/export_pricelist_master.py) และตรวจด้วย targeted tests 18/18 ผ่าน พร้อม `py -3 pipeline/export_pricelist_master.py --check` ผ่าน

## Version diff

ไม่มีเอกสาร → `0.1.0b candidate`: เพิ่มผลเปรียบเทียบตัวอย่าง อัตรา/ตัวอย่าง CBM, source coverage, ข้อจำกัด และข้อเสนอ JSON extension ไม่เปลี่ยนราคา master หรือสูตร
`0.1.0b → 0.2.0b beta`: implement `price_comparisons` 669 แถว, SRP quantity matrix 128 แถวรวม qty 1, exact-code factory reference และ CBM declared scenario โดยคง null เมื่อข้อมูลไม่ครบ
`0.2.0b → 0.3.0b beta`: อัปเดต artifact hash หลังเพิ่ม seasonal offers 6, packages 11 และ proposed BOM 17; cost identity ของ PM canonical ยังเป็น missing

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---------|------|--------|---------|-------------|-------|
| 0.3.0b | 2026-08-30 | beta | อัปเดต comparison artifact หลังเพิ่ม seasonal package/BOM projection; exact factory match ของ PM 0/16 จึงไม่เติมต้นทุน | uncommitted | ATHER |
| 0.2.0b | 2026-08-30 | beta | Implement comparison JSON 669 + SRP/qty 128 รวม qty 1; exact factory match และ CBM scenario แบบไม่เดาต้นทุน | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | ตรวจเทียบ sale/factory-reference/CBM และเสนอ extension โดยไม่เดาต้นทุนที่ขาด | uncommitted | ATHER |
