---
version: "1.1.1b"
created_at: "2026-08-30T10:33:17+07:00,ATHER"
last_update: "2026-08-30T11:08:07+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-data"
  doc_type: "architecture-decision"
  scope: "local pricelist projection and occasion packages mapped to portfolio catalogs and customer tiers"
  language: "th"
---

# ADR-002 — สัญญา pricelist_master.json จาก SQL snapshot

**Status:** Beta — ทำ local artifact ตามคำขอเดิมและ taxonomy/schema ที่ผู้ใช้ยืนยัน; ไม่อนุมัติราคา/BOM หรือ runtime promotion
**Date:** 2026-08-30  
**Decided by:** Boss ยืนยันใช้ `config/schema_genesisblock.yaml` และ Reach / Select / Signature / Bespoke (2026-08-30)
**Complexity / Risk:** C-2 / MEDIUM — เปลี่ยน mapping หลาย entity แต่ไม่เปลี่ยนฐานข้อมูลหรือ runtime  
**Relates to:** [สถาปัตยกรรมหลัก](../SMARTGIFT_SYSTEM_ARCHITECTURE.md), [Data Pipeline](../DATA_PIPELINE_AND_VAULT_STRUCTURE.md), [ADR-001](ADR-001-ECO-FRIENDLY-CATEGORY-REFACTOR.md), [ontology v1.3.0](../../config/schema_genesisblock.yaml), [Price Boss migration](../../price-boss/sql/migrate_to_smartgift_db.sql), [Price Boss schema](../../price-boss/sql/schema.sql)

## Context

ผู้ใช้ขอ `pricelist_master.json` ซึ่งครอบคลุม ProductMaster, product family, pkg และ BOM โดยใช้ข้อมูลจาก `price-boss/sql` ได้

**คำชี้แจงจากผู้ใช้ 2026-08-30:** pkg หมายถึงแพ็กเกจที่ mapping กับ **4 catalog + customer 4 tier** เช่น **ชุดต้อนรับพนักงานใหม่** จึงยกเลิกข้อเสนอเดิมที่ใช้ pkg เป็น index ของ 1,080 SQL sets ความหมายของ pkg ได้รับการชี้แจงแล้ว แต่รายละเอียด schema และชื่อ customer tiers ยังรอยืนยัน ไม่ถือว่าคำชี้แจงนี้เป็นการอนุมัติ implementation ทั้งฉบับ

**ข้อกำหนดเพิ่มเติมจากผู้ใช้:** ทุก pkg ต้องมีกำไร **ไม่ต่ำกว่า 25,000 บาทต่อ pkg** เป็นข้อบังคับ ไม่ใช่เป้าหมายเฉลี่ยหรือคำแนะนำ หลักเกณฑ์การคำนวณที่เสนออยู่ใน D5

ตรวจ SQL ด้วย SQLite ในหน่วยความจำเท่านั้น ไม่รันกับฐานข้อมูลจริง ไม่แก้ SQL/Excel และไม่เรียก pipeline ที่มีผลข้างเคียง ผลตรวจ ณ วันที่เอกสาร:

| หลักฐานใน snapshot | จำนวน / ความหมาย |
|---|---|
| `smartgift_model` | 427 แถว; `source_ref.rowKey` ไม่ซ้ำ 427 ค่า |
| สถานะ model | `review_required` 336, `unclassified` 49, `auto` 42; ไม่มีความหมายว่าเจ้าของอนุมัติแล้ว |
| `smartgift_type` | 32 types ภายใต้ 4 source groups |
| `smartgift_offer` | 1,110 offers: `set` 1,080, `single` 30 |
| `smartgift_price` | 669 แถวราคา ครอบคลุม 221 offer codes; ไม่มี price→offer orphan |
| `price_missing=true` | 102 แถว; ทั้งหมดเก็บ `unit_price=0` ในต้นทาง ห้ามตีความเป็นแจกฟรี |
| qty tier ที่ไม่เป็นจำนวนบวก | 118 แถว (`NULL` หรือ ≤ 0); ห้ามแทนด้วย MOQ ที่เดาเอง |
| `smartgift_model.offer_codes` | 3,200 คู่ model–offer ไม่ซ้ำ ครอบคลุม 1,016 offers; ไม่มี orphan แต่ไม่มี component quantity |
| model ที่ไม่มี type | 50 แถว ต้องรักษา null ไม่จัดหมวดเอง |
| BOM / corporate bundle export | ไม่พบตารางพร้อมข้อมูลใน SQL folder นี้ |
| `catalogs` | schema เรียกเป็น product family บนเว็บ แต่ไม่มี INSERT ของ catalogs ใน SQL folder นี้ |
| `pkg_*` | ฟิลด์ packaging ใน `china_sourcing`; ไม่ใช่ master ของชุดขาย และไม่ใช่ BOM |

ไฟล์เดิม `data-pipeline/02_prepared/smartgift_catalog_master.json` มี 16 canonical products, 357 catalog offers และ 2 corporate bundles ซึ่งเป็นอีกชุดข้อมูลหนึ่ง จึงไม่สามารถรวม identity/ราคา/BOM โดยอาศัยชื่อเหมือนกันอย่างเดียว

## Decision

ดำเนินการเฉพาะ local JSON/exporter ตามคำขอสร้างไฟล์เดิมและคำยืนยัน schema รอบล่าสุด ส่วนข้อมูล package options/BOM/จำนวน/ต้นทุนที่ยังไม่มีหลักฐานคงสถานะ missing ไม่ใช่การอนุมัติ implementation ในระบบอื่น

### D1 — สร้าง local projection แยกจาก master เดิม

เสนอไฟล์เป้าหมาย `data-pipeline/02_prepared/pricelist_master.json` ใช้ UTF-8 ไม่มี BOM และตั้ง `schema_version="1.1.0b"`, `status="review_required"` ใน metadata

ใช้ `price-boss/sql/smartgiftpricelist.postgres.sql` เป็น input เดียวสำหรับแถวสินค้า/ราคาในรอบนี้ MySQL copy ใช้ประกอบการตรวจเท่านั้น ไม่โหลดทั้งสองไฟล์รวมกัน และไม่เปิด connection ไปยังฐานข้อมูลหรือ upstream store

ใช้ Category/GiftTier จาก YAML เป็น authority และอ่าน `top_level_categories` จาก master เดิมเฉพาะชื่อสี่ catalog โดยตรวจ slug ให้ตรงกัน ไม่อ่านราคา/BOM ของ master เดิมมาผสม SQL อัตโนมัติ ส่วน pkg ตามโอกาสใช้งานและ tier mapping มาจากนิยามธุรกิจที่ผู้ใช้ยืนยัน ไม่อ้างว่า SQL export มีข้อมูลนี้แล้ว

บันทึก provenance ต่อไปนี้:

- SQL relative path, SHA-256, ขนาดไฟล์, เวลา export และ store run ID
- snapshot SHA-256: `263556642064f6398e4cd00a7a4897ca7ba841b7c3bae5b8d2165b3186b2fdd4`
- store run ID: `2026-08-24T08-46-40-226Z`; exported at `2026-08-29T15:13:46.720Z`
- source table, source key, SQL statement line และ `source_ref` เดิม (`file`, `rowKey`, `sha256`) ของแต่ละ record
- scope: tenant `Org-EtohGroup`, business `SmartGift`; ไม่ assign vault identity หรือ `gks:` reference

### D2 — แยก entity ตามหลักฐาน ไม่เพิ่มความหมายให้ source โดยอัตโนมัติ

| JSON key | Mapping ที่เสนอ | จำนวนคาดหวังกับ hash นี้ |
|---|---|---:|
| `product_masters` | 1 ต่อ `smartgift_model`; ใช้ `source_ref.rowKey` เป็น source product ID; เก็บ base signature, names, type/group, status, colors และ price_source เดิม | 427 |
| `product_families` | เก็บ 1 ต่อ `smartgift_type` โดยระบุ `source_semantics="product_type"`; เป็น source taxonomy เท่านั้น ไม่สร้าง ProductFamily node ใหม่ใน YAML และไม่อ้างว่าเป็น `catalogs` family ของเว็บ | 32 |
| `portfolio_catalogs` | นิยามสี่ catalog ตาม ADR-001 และ master เดิม แยกจาก 32 types และสี่ source groups ใน SQL | 4 จากแหล่ง portfolio |
| `customer_tiers` | ชื่อ key สำหรับผู้ใช้ แต่ `entity_type="GiftTier"` และค่า Reach / Select / Signature / Bespoke อ่านจาก YAML ตามที่ผู้ใช้ยืนยัน; ไม่ใช่ CRM tier | 4 |
| `catalog_offers` | ทุก `smartgift_offer`; ใช้ code เดิม เก็บชนิด/ชื่อ/รายละเอียด/ราคาอ้างอิง/สถานะ ไม่เปลี่ยน set เป็น single จากการอ่านข้อความ | 1,110 |
| `pkg` | แพ็กเกจตามโอกาสใช้งาน เช่น ชุดต้อนรับพนักงานใหม่ มีตัวเลือก mapping ไป portfolio catalog + customer tier และอ้าง BOM ของตัวเลือกนั้น | ยังไม่กำหนดจำนวน; ไม่ใช่จำนวน SQL sets |
| `offer_product_links` | คลี่ `smartgift_model.offer_codes` เป็นคู่ source product ID–offer code; relation เป็น `source_association` ไม่ใช่ BOM | 3,200 |
| `bom` | array ของ BOM ที่มีหลักฐานและจำนวนจริงเท่านั้น; snapshot นี้ส่งออกเป็น `[]` พร้อม coverage=`not_exported` | 0 |
| `prices` | ทุก `smartgift_price` พร้อม source ID, offer_code, qty_tier, ราคา/VAT, missing flag, supplier group, FlowAccount code และวัน export | 669 |
| `metadata` | source/run/hash/scope/counts/coverage, profit_policy ตาม D5 และข้อจำกัดการใช้งาน | 1 object |

ProductMaster ในไฟล์ใหม่นี้เป็น **source model projection** ไม่ใช่การ promote ให้เป็น canonical ProductMaster ที่อนุมัติแล้ว และไม่ใช่ replacement ของ ontology/vault contract เดิมที่ต้องมี base_cost ไม่สร้าง SKU หรือ stock value จากข้อมูลที่ไม่มี

รักษา `group_id` ตาม source (`home_travel`, `office`, `smart_tech`, `care_wellness`) โดยไม่แทนที่สี่หมวด portfolio ตาม ADR-001 ไม่ใช้ theme, gift tier, product family และ supplier group แทนกัน

ถ้าผู้ใช้หมายถึง **product family ของเว็บ (`catalogs`)** ให้เก็บช่อง family ว่างพร้อม `not_exported` จนมี export; ห้ามนำ 32 types มาอ้างว่าเป็นข้อมูล catalogs การชี้แจง pkg รอบนี้ไม่ได้อนุมัติ product-family mapping เดิมโดยปริยาย

### D2.1 — pkg เป็นแพ็กเกจตามโอกาสใช้งาน พร้อม catalog–tier mapping

สี่ catalog ที่ตรวจพบใน master ปัจจุบันตรงกับ ADR-001:

| Catalog slug | ชื่อ |
|---|---|
| `eco-friendly` | Eco-Friendly & Sustainability |
| `classic-oriental` | Classic Oriental |
| `novelty-self-care` | Novelty & Self-Care |
| `executive-smart-tech` | Executive Smart Tech |

เสนอแต่ละ pkg มี `pkg_code`, `name_th`, `occasion`, `status` และ `options` แต่ละ option มี `option_id`, `catalog_slug`, `customer_tier_code`, `bom_id`, `bom_status` โดย `bom_id` เป็น null ได้เมื่อยังไม่ได้ออกแบบหรือยืนยันส่วนประกอบ ไม่ใส่ product quantity หรือราคาเป็น placeholder ที่ดูเหมือนข้อมูลจริง

ตัวอย่างเชิงโครงสร้าง: **ชุดต้อนรับพนักงานใหม่ → option ตาม catalog และ customer tier → BOM ที่ระบุสินค้า/จำนวน → ราคาอ้างอิงเมื่อข้อมูลครบ** ชื่อพนักงานใหม่เป็นกลุ่มผู้รับตามโอกาส ไม่บังคับให้เท่ากับ tier ใด tier หนึ่ง

สี่ catalog × สี่ tier เป็นพื้นที่ mapping ที่เป็นไปได้ 16 คู่ ไม่ใช่คำสั่งสร้าง 16 ชุดให้ทุก pkg โดยอัตโนมัติ กรอกเฉพาะตัวเลือกที่ออกแบบและยืนยันแล้ว; คู่ที่ยังไม่มีต้องแสดงว่าไม่ถูกกำหนด แพ็กเกจหนึ่งจึงมีหลายตัวเลือกได้โดยไม่ทำสำเนา ProductMaster

1,080 `offer_kind=set` ยังคงเป็น catalog_offers จาก SQL ใช้เป็นรายการให้พิจารณาจัดแพ็กเกจได้ แต่ไม่กลายเป็น pkg ตามโอกาสใช้งานโดยตรง และ model–offer associations ไม่กลายเป็น BOM ของ option โดยอัตโนมัติ

**ผู้ใช้ยืนยันแล้ว:** ใช้ `Reach`, `Select`, `Signature`, `Bespoke` จาก GiftTier ใน `config/schema_genesisblock.yaml` เป็น authority พร้อม Category slugs และ edge contracts ในไฟล์เดียวกัน ไม่ใช้ CRM tiers (`P1`, `A`, `B`, `C`, `WINBACK`) บันทึก hash ของ YAML และ master ที่อ่านเฉพาะชื่อ catalog ด้วย; ห้ามแก้ source ที่มีงานค้าง

pkg ตัวอย่าง `PKG-NEW-EMPLOYEE-WELCOME` เป็น draft ของ BundleOffer มีขอบเขตการออกแบบอ้างสี่ Category และสี่ GiftTier แต่ `options=[]`, `target_recipients=null`, `total_price=null` และยังไม่ผ่าน contract required fields จนกว่าจะมีข้อมูลจริง ProductMaster/CatalogOffer จาก SQL ก็ต้องรายงาน required fields ที่ขาดตาม YAML โดยไม่สร้างค่า default เพื่อให้ผ่าน schema

### D3 — ราคาเป็น snapshot และ BOM ที่ขาดต้องเห็นได้ชัด

- เก็บราคาต้นทางและ `price_missing` ตามจริง ไม่เติมราคาที่หาย ไม่เปลี่ยน 0 ให้เป็นราคาขายที่ใช้ได้
- `price_tiers` เดิมของ models/offers เก็บใน `source_price_tiers` เพื่อรักษาหลักฐาน แต่ไม่รวมซ้ำกับตาราง prices และไม่ถือเป็นราคาชิ้นส่วน standalone เมื่อ source ระบุ `via_offer`
- `unit_price_with_vat` เป็น field จากต้นทาง ไม่คำนวณ VAT ใหม่; `rmb` เป็นค่าอ้างอิงจาก source ไม่ใช่ landed/base cost
- metadata ต้องบอก `quote_ready=false`, `inventory_ready=false`, `bom_coverage="not_exported"` จนผ่าน gate ที่เกี่ยวข้อง ไม่ยกระดับ price-boss snapshot ให้แทน price authority ตาม AGENTS.md
- ความสัมพันธ์ model–offer ไม่มี quantity: ห้ามใส่ `qty=1` หรือใช้การเดาจากชื่อเป็น BOM
- ห้ามผสม BOM/ต้นทุน 16 product masters และ 2 corporate bundles จากไฟล์เดิมโดยไม่มี identity reconciliation และการอนุมัติแยก

### D4 — ขอบเขตข้อมูลและไฟล์ที่อนุญาตหลังอนุมัติ

ขอบเขต implementation ที่เสนอมีเพียง exporter หนึ่งไฟล์, JSON เป้าหมายที่รวม package definitions/mappings ตามอนุมัติ, การตรวจ parser/reconciliation ที่จำเป็น และผลตรวจใน ADR นี้ ไม่เปลี่ยน application, price formula, inventory logic, database schema, seed, UI หรือ vault state

อ่านเฉพาะตาราง export_run/type/model/offer/price และ field allowlist ร่วมกับนิยาม portfolio catalogs และ package/customer-tier definitions ที่อนุมัติ ไม่ดึง CRM customer records, contact, employee, quotation, supplier contact หรือ free-form sourcing notes นิยาม tier และแพ็กเกจเก็บเฉพาะข้อมูลระดับกลุ่ม ไม่มีตัวบุคคล ตรวจข้อความสินค้าที่ส่งออกด้วย หากพบข้อมูลส่วนบุคคลที่น่าสงสัยให้หยุดส่งออกเพื่อ review ไม่อ้างว่า allowlist เพียงอย่างเดียวพิสูจน์ Zero-PII ได้

ไม่รัน `run_pipeline.py`, sync, import SQL, embedding, migration หรือ write ไป repo อื่น การอนุมัติเอกสารนี้ไม่ใช่การอนุมัติ quote, publish, deploy หรือ upstream/vault promotion

### D5 — กำไรขั้นต่ำ 25,000 บาทต่อ pkg

`profit_policy` กำหนด `minimum_profit=25000`, `currency="THB"`, `scope="per_configured_pkg"` และใช้กับทุก catalog/customer tier เท่ากัน ไม่เฉลี่ยหรือชดเชยกำไรระหว่างคนละ pkg และไม่ใช้ target เดิม 30,000 บาทมาแทนข้อบังคับใหม่นี้

[ASSUMPTIONS]

1. หน่วย pkg ที่ใช้ตรวจคือแพ็กเกจที่กำหนดตัวเลือกและจำนวนส่งมอบครบแล้วสำหรับการขายหนึ่งแพ็กเกจ ไม่ใช่สินค้าต่อชิ้นหรือชื่อ template ที่ยังไม่มีจำนวน
2. กำไรหมายถึงยอดขายสุทธิของแพ็กเกจหลังส่วนลด หักต้นทุนตรงทั้งหมดที่จำเป็นต่อการส่งมอบแพ็กเกจ ไม่ใช่กำไรสุทธิทางบัญชีหลังค่าใช้จ่ายบริษัทและภาษีเงินได้
3. ยอดขายและต้นทุนใช้ฐาน VAT ที่เปรียบเทียบกันได้ ไม่หักต้นทุนรวม VAT จากรายได้ไม่รวม VAT โดยไม่มีการปรับฐาน

สูตรตรวจรับ: **package_profit = package_net_revenue − package_total_cost ≥ 25,000 บาท**

ต้นทุนต้องครอบคลุม BOM สินค้า, landed cost, บรรจุภัณฑ์, งานแบรนด์/พิมพ์, ประกอบ/แพ็ก, ขนส่งส่งมอบ และค่าใช้จ่ายตรงอื่นที่เกี่ยวข้อง โดยแยกว่าอะไรอยู่ใน landed cost แล้วเพื่อไม่คิดซ้ำ ทุกหมวดต้องมีหลักฐานหรือระบุว่าไม่เกี่ยวข้องพร้อมเหตุผล ไม่เติมต้นทุนที่หายเป็นศูนย์หรือใช้สัดส่วนยอดขายโดยอัตโนมัติ

เสนอ `profit_evaluation` สำหรับ pkg ที่ตั้งค่าการขายแล้ว มี `net_revenue`, `total_cost`, `profit`, `status` และ `missing_inputs`:

- `pass`: BOM/จำนวน/ราคา/ต้นทุนครบและเปรียบเทียบฐานเดียวกัน; กำไร ≥ 25,000
- `below_minimum`: ข้อมูลครบแต่กำไร < 25,000; ห้ามประกาศ pkg ผ่านเกณฑ์
- `missing_inputs`: ขาด BOM, จำนวน, ราคา, ต้นทุน หรือฐาน VAT ไม่ชัด; `profit=null` และห้ามถือว่าผ่าน

หาก pkg เดียวส่งมอบหลายตัวเลือก ให้รวมเฉพาะตัวเลือกและจำนวนที่ขายจริงภายใน pkg นั้นเพื่อตรวจขั้นต่ำ ตัวเลือกทางเลือกที่ลูกค้ายังไม่ได้เลือกไม่นับเป็นรายได้ และการผ่าน profit gate ไม่ได้แปลว่าผ่าน price authority หรือพร้อม quote

**Peer implementation ปัจจุบันยังไม่ตรงกับข้อกำหนดใหม่:** `pipeline/enrich_review_catalog.py:150` ใช้ `MIN_PKG_PROFIT=20000.0` และมีทางเลือกประมาณต้นทุนเป็น 35% ของยอดขาย จึงห้ามคัดลอก `meets_min_profit_threshold` เดิมมาเป็นหลักฐานผ่านเกณฑ์ 25,000 ของ artifact ใหม่ รอบนี้บันทึกข้อกำหนดและข้อจำกัดเท่านั้น ไม่แก้ engine หรือสูตรเดิม

## Consequences

- ได้ artifact แยก **SQL snapshot** ออกจาก **portfolio/package definitions** แต่ยังไม่ใช่ BOM หรือ price list พร้อมขาย
- แยกข้อมูลที่มีจริงออกจากช่องว่าง โดยไม่ทำให้ consumer เก่าของ `smartgift_catalog_master.json` เปลี่ยนพฤติกรรม
- pkg และสี่ tier ยึดตามคำยืนยันผู้ใช้แล้ว; product family คงเป็น source taxonomy ไม่สร้าง ontology node ใหม่
- ProductMaster ชื่อเดียวกับ ontology ไม่ได้ทำให้ source IDs กลายเป็น UUIDv7 หรือ identity ใน GKS
- ทุก pkg ต้องผ่านเกณฑ์กำไร 25,000 บาทจากข้อมูลครบก่อนแสดงว่าผ่าน; template ที่ยังไม่มีราคา/ต้นทุนยังคงอยู่ในสถานะรอข้อมูล

## Verification and exit criteria

1. Source SHA-256 และ store run ID ตรงกับรอบที่อนุมัติ; ถ้าเปลี่ยนต้องตรวจ diff/count ใหม่
2. JSON parse ผ่าน; IDs ไม่ซ้ำ; model/type/offer/price references ไม่มี orphan; null type ทั้ง 50 ไม่ถูกแปลงเป็นหมวดที่เดาเอง
3. Counts ตรงตาราง D2; ทุก source row ถูกเก็บครบครั้งเดียว; decimal, NULL, boolean, Thai, apostrophe และ nested JSON ไม่สูญหายระหว่าง parse
4. Missing price ทั้ง 102 และ invalid/absent tier ทั้ง 118 ยังตรวจพบได้; ไม่มีการประกาศราคาใช้งานได้จากค่าที่ขาด
5. BOM เป็น empty พร้อม not_exported ไม่ใช่ verified-empty; ไม่มีการแปลง associations เป็น quantity-bearing edges
6. Provenance ครบ; ตรวจ field allowlist และข้อความเสี่ยง PII; metadata ไม่อ้าง quote/inventory readiness
7. เขียน output หลัง validation ผ่านเท่านั้น; regeneration ให้ข้อมูลเรียงลำดับคงที่และ counts/content เดิมสำหรับ source bytes เดิม
8. Relevant parser/export checks และ `py -3 -m unittest discover tests` ผ่านหลัง implementation; ไม่เรียก master pipeline ที่อาจ sync ข้อมูล
9. ตรวจ version diff และ working-tree scope; source files, master เดิม, vaults และงานค้างของ session อื่นไม่เปลี่ยน
10. pkg แต่ละ option อ้าง catalog และ customer tier ที่อนุมัติและมีอยู่จริง; ไม่สร้าง 16 คู่โดยอัตโนมัติ และไม่ถือว่า pkg count เท่ากับ SQL set count; BOM ที่ยังไม่กำหนดต้องมี null reference และสถานะ missing ชัดเจน
11. Profit gate ตรวจขอบเขต 24,999.99 = below_minimum, 25,000.00 = pass เมื่อข้อมูลครบ; missing cost/quantity/BOM/VAT basis = missing_inputs; ไม่รวมทางเลือกที่ไม่ได้ขาย ไม่ใช้กำไร pkg อื่นชดเชย และไม่คัดลอกผลผ่านจาก threshold เดิม 20,000

**ผลตรวจ implementation 2026-08-30:**

- สร้าง [exporter](../../pipeline/export_pricelist_master.py), [JSON master](../../data-pipeline/02_prepared/pricelist_master.json) และ [tests](../../tests/test_pricelist_master_export.py) แล้ว
- Count: ProductMaster projections 427, source product families/types 32, Category 4, GiftTier 4, offers 1,110, draft pkg 1, model–offer associations 3,200, verified BOM 0, prices 669
- YAML contract v1.3.0 SHA-256 ณ export: `bcd507d791e406e8114ab636f3905518a58c569791e6d1f87c7b1ef302c00419`; source hashes ทั้งหมดอยู่ใน metadata ของ artifact รวม master ที่อ่านเฉพาะ labels
- Tests ใหม่ 15/15 ผ่าน: SQL Thai/quotes/NULL/JSON/ON CONFLICT, reject expressions, orphan/duplicate checks, missing price/BOM, contact-pattern quarantine, deterministic export, no overwrite on validation failure และ profit floor 24,999.99 / 25,000
- เปรียบเทียบ price cells ทั้ง 669 แถวกับ SQLite ใน memory เป็น independent parser check; exporter เองไม่ execute SQL
- Baseline เดิม 42 tests และหลังเพิ่มงานใหม่รวม 57 tests ผ่านในสำเนาทดสอบชั่วคราว เพื่อกัน archiver tests เขียน source registry/audit log ใน shared checkout
- `py -3 pipeline/export_pricelist_master.py --check` ผ่าน โดยเทียบ output bytes กับการสร้างใหม่จาก sources ปัจจุบัน
- ยังไม่ยืนยัน BOM, package quantities, cost coverage, ราคาอนุมัติ หรือ Zero-PII แบบ human-reviewed; ไม่รัน sync/vault/quote/publish

สร้างใหม่: `py -3 pipeline/export_pricelist_master.py` โดย exporter จำกัด input hash ของ SQL, allowlist tables/fields, ตรวจ input ไม่เปลี่ยนระหว่างรัน และเขียน output แบบ atomic หลังตรวจผ่านเท่านั้น JSON ใช้ UTF-8 ไม่มี BOM; ไม่ overwrite artifact ที่ระบุ generator อื่น

## Open questions / approval

ความหมาย pkg ยึดตามผู้ใช้: **แพ็กเกจตามโอกาสใช้งาน mapping กับ 4 catalog + customer 4 tier** ตัวอย่างแรกคือ **ชุดต้อนรับพนักงานใหม่**

กำไรขั้นต่ำยึดตามผู้ใช้ที่ **25,000 บาทต่อ pkg** โดยมีสมมติฐานฐานคำนวณใน D5 เพื่อทบทวนพร้อม schema ไม่ถือเป็นการอนุมัติค่า BOM/ราคา/ต้นทุนที่ยังไม่มีหลักฐาน

ปิดคำถามเรื่องชื่อ tier แล้วด้วยคำยืนยันผู้ใช้ให้ยึด YAML ดำเนินการ local source projection ได้ตามคำขอเดิม ส่วนประกอบ จำนวน ราคา ต้นทุน และ option mappings ที่ไม่มีหลักฐานยังรอข้อมูลจริง ไม่รวมถึงการแก้ engine/vault หรือ publication

## Version diff

- `0.1.0b → 1.0.0b`: ยกเลิก pkg=SQL sets เปลี่ยนเป็นแพ็กเกจตามโอกาสใช้งาน เพิ่ม portfolio catalogs, customer tiers และ option mappings; major bump เพราะเปลี่ยนโครงสร้างและความหมาย pkg
- `1.0.0b → 1.1.0b candidate`: เพิ่มข้อบังคับกำไรขั้นต่ำ 25,000 บาทต่อ pkg, ฐานต้นทุนและกฎเมื่อข้อมูลขาด พร้อมเกณฑ์ตรวจขอบเขต
- `1.1.0b → 1.1.1b beta`: ยืนยัน GiftTier/Category authority จาก YAML ตามผู้ใช้; local export เท่านั้นและแสดง contract gaps โดยไม่เดาข้อมูล
- รอบ implementation เพิ่ม exporter/test/JSON เป้าหมายเท่านั้นและอัปเดต ADR นี้; ไม่แก้ schema, master เดิม, engine, vaults หรือ UI ที่มีงานจาก session อื่น

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---------|------|--------|---------|-------------|-------|
| 1.1.1b | 2026-08-30 | beta | ยืนยัน schema/tier ตามผู้ใช้; สร้าง local artifact และตรวจ 15 targeted / 57 regression tests โดยไม่ promote BOM/ราคา | uncommitted | ATHER |
| 1.1.0b | 2026-08-30 | candidate | เพิ่มกำไรขั้นต่ำ 25,000 บาทต่อ pkg ตามผู้ใช้ พร้อม profit gate ที่ไม่ผ่านเมื่อข้อมูลขาด | uncommitted | ATHER |
| 1.0.0b | 2026-08-30 | candidate | แก้ pkg ตามคำชี้แจงผู้ใช้เป็น occasion package + catalog/customer-tier mapping; ยังรอยืนยัน tier master | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | เสนอ local SQL snapshot projection และกำหนดคำถาม family/pkg ก่อน implementation | uncommitted | ATHER |
