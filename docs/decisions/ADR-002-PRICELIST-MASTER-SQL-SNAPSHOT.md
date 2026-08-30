---
version: "0.1.0b"
created_at: "2026-08-30T10:33:17+07:00,ATHER"
last_update: "2026-08-30T10:33:17+07:00,ATHER"
status: "candidate"
superseded_by: null
attributes:
  domain: "catalog-data"
  doc_type: "architecture-decision"
  scope: "local pricelist JSON projection from price-boss SQL snapshot"
  language: "th"
---

# ADR-002 — สัญญา pricelist_master.json จาก SQL snapshot

**Status:** Candidate — รออนุมัติ mapping ก่อนสร้าง exporter หรือ JSON จริง  
**Date:** 2026-08-30  
**Decided by:** ยังไม่ได้อนุมัติ  
**Complexity / Risk:** C-2 / MEDIUM — เปลี่ยน mapping หลาย entity แต่ไม่เปลี่ยนฐานข้อมูลหรือ runtime  
**Relates to:** [สถาปัตยกรรมหลัก](../SMARTGIFT_SYSTEM_ARCHITECTURE.md), [Data Pipeline](../DATA_PIPELINE_AND_VAULT_STRUCTURE.md), [ADR-001](ADR-001-ECO-FRIENDLY-CATEGORY-REFACTOR.md), [ontology v1.3.0](../../config/schema_genesisblock.yaml), [Price Boss migration](../../price-boss/sql/migrate_to_smartgift_db.sql), [Price Boss schema](../../price-boss/sql/schema.sql)

## Context

ผู้ใช้ขอ `pricelist_master.json` ซึ่งครอบคลุม ProductMaster, product family, pkg และ BOM โดยใช้ข้อมูลจาก `price-boss/sql` ได้

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

ทุกข้อด้านล่างเป็น **ข้อเสนอ** ยังไม่ใช่การอนุมัติ implementation

### D1 — สร้าง local projection แยกจาก master เดิม

เสนอไฟล์เป้าหมาย `data-pipeline/02_prepared/pricelist_master.json` ใช้ UTF-8 ไม่มี BOM และตั้ง `schema_version="0.1.0b"`, `status="review_required"` ใน metadata

ใช้ `price-boss/sql/smartgiftpricelist.postgres.sql` เป็น input เดียวสำหรับแถวสินค้า/ราคาในรอบนี้ MySQL copy ใช้ประกอบการตรวจเท่านั้น ไม่โหลดทั้งสองไฟล์รวมกัน และไม่เปิด connection ไปยังฐานข้อมูลหรือ upstream store

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
| `product_families` | **รออนุมัติความหมาย:** ใช้ 1 ต่อ `smartgift_type` เป็น family ตามประเภทสินค้า โดยเก็บ `source_semantics="product_type"`; ไม่อ้างว่าเป็น `catalogs` family ของเว็บ | 32 |
| `catalog_offers` | ทุก `smartgift_offer`; ใช้ code เดิม เก็บชนิด/ชื่อ/รายละเอียด/ราคาอ้างอิง/สถานะ ไม่เปลี่ยน set เป็น single จากการอ่านข้อความ | 1,110 |
| `pkg` | **รออนุมัติความหมาย:** index ของชุดเสนอขาย `offer_kind="set"`; record อ้าง `offer_code` ไปยัง catalog_offers และมี `bom_status="not_exported"` | 1,080 |
| `offer_product_links` | คลี่ `smartgift_model.offer_codes` เป็นคู่ source product ID–offer code; relation เป็น `source_association` ไม่ใช่ BOM | 3,200 |
| `bom` | array ของ BOM ที่มีหลักฐานและจำนวนจริงเท่านั้น; snapshot นี้ส่งออกเป็น `[]` พร้อม coverage=`not_exported` | 0 |
| `prices` | ทุก `smartgift_price` พร้อม source ID, offer_code, qty_tier, ราคา/VAT, missing flag, supplier group, FlowAccount code และวัน export | 669 |
| `metadata` | source/run/hash/scope/counts/coverage และข้อจำกัดการใช้งาน | 1 object |

ProductMaster ในไฟล์ใหม่นี้เป็น **source model projection** ไม่ใช่การ promote ให้เป็น canonical ProductMaster ที่อนุมัติแล้ว และไม่ใช่ replacement ของ ontology/vault contract เดิมที่ต้องมี base_cost ไม่สร้าง SKU หรือ stock value จากข้อมูลที่ไม่มี

รักษา `group_id` ตาม source (`home_travel`, `office`, `smart_tech`, `care_wellness`) โดยไม่แทนที่สี่หมวด portfolio ตาม ADR-001 ไม่ใช้ theme, gift tier, product family และ supplier group แทนกัน

ถ้าผู้ใช้หมายถึง **product family ของเว็บ (`catalogs`)** ให้เก็บช่อง family ว่างพร้อม `not_exported` จนมี export; ห้ามนำ 32 types มาอ้างว่าเป็นข้อมูล catalogs ถ้าหมายถึง **pkg=packaging หรือ corporate bundle** จะยังไม่มี master ที่พิสูจน์ครบจาก input นี้ และต้องแก้ mapping ก่อน implementation

### D3 — ราคาเป็น snapshot และ BOM ที่ขาดต้องเห็นได้ชัด

- เก็บราคาต้นทางและ `price_missing` ตามจริง ไม่เติมราคาที่หาย ไม่เปลี่ยน 0 ให้เป็นราคาขายที่ใช้ได้
- `price_tiers` เดิมของ models/offers เก็บใน `source_price_tiers` เพื่อรักษาหลักฐาน แต่ไม่รวมซ้ำกับตาราง prices และไม่ถือเป็นราคาชิ้นส่วน standalone เมื่อ source ระบุ `via_offer`
- `unit_price_with_vat` เป็น field จากต้นทาง ไม่คำนวณ VAT ใหม่; `rmb` เป็นค่าอ้างอิงจาก source ไม่ใช่ landed/base cost
- metadata ต้องบอก `quote_ready=false`, `inventory_ready=false`, `bom_coverage="not_exported"` จนผ่าน gate ที่เกี่ยวข้อง ไม่ยกระดับ price-boss snapshot ให้แทน price authority ตาม AGENTS.md
- ความสัมพันธ์ model–offer ไม่มี quantity: ห้ามใส่ `qty=1` หรือใช้การเดาจากชื่อเป็น BOM
- ห้ามผสม BOM/ต้นทุน 16 product masters และ 2 corporate bundles จากไฟล์เดิมโดยไม่มี identity reconciliation และการอนุมัติแยก

### D4 — ขอบเขตข้อมูลและไฟล์ที่อนุญาตหลังอนุมัติ

ขอบเขต implementation ที่เสนอมีเพียง exporter หนึ่งไฟล์, JSON เป้าหมาย, การตรวจ parser/reconciliation ที่จำเป็น และผลตรวจใน ADR นี้ ไม่เปลี่ยน application, price formula, inventory logic, schema, seed, UI หรือ vault state

อ่านเฉพาะตาราง export_run/type/model/offer/price และ field allowlist ไม่ดึง CRM, customer, contact, employee, quotation, supplier contact หรือ free-form sourcing notes ตรวจข้อความสินค้าที่ส่งออกด้วย หากพบข้อมูลส่วนบุคคลที่น่าสงสัยให้หยุดส่งออกเพื่อ review ไม่อ้างว่า allowlist เพียงอย่างเดียวพิสูจน์ Zero-PII ได้

ไม่รัน `run_pipeline.py`, sync, import SQL, embedding, migration หรือ write ไป repo อื่น การอนุมัติเอกสารนี้ไม่ใช่การอนุมัติ quote, publish, deploy หรือ upstream/vault promotion

## Consequences

- ได้ artifact ที่ตรวจย้อนกลับได้ครบตาม **SQL snapshot** แต่ยังไม่ใช่ BOM หรือ price list พร้อมขาย
- แยกข้อมูลที่มีจริงออกจากช่องว่าง โดยไม่ทำให้ consumer เก่าของ `smartgift_catalog_master.json` เปลี่ยนพฤติกรรม
- Product family และ pkg ต้องยืนยันความหมายตาม D2 ก่อนลงมือ เพราะ peer schema ใช้คำเหล่านี้ต่างกัน
- ProductMaster ชื่อเดียวกับ ontology ไม่ได้ทำให้ source IDs กลายเป็น UUIDv7 หรือ identity ใน GKS

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

**ผลตรวจรอบเอกสาร:** อ่านและ parse SQL snapshot ใน memory แล้ว; ตรวจจำนวน, unique IDs/pairs, price references และ missing data แล้ว ยังไม่มี exporter หรือ `pricelist_master.json` ถูกสร้าง และยังไม่ได้รัน regression suite

## Open questions / approval

ขออนุมัติให้ **product family = 32 product types**, **pkg = 1,080 ชุดเสนอขาย** ตาม D2 และให้ BOM ว่างพร้อมสถานะ `not_exported` ตามหลักฐาน SQL โดยยังไม่ดึง BOM จากแหล่งอื่น หากต้องการ family ของเว็บ, packaging หรือ corporate bundles ให้ระบุความหมายที่ต้องการก่อน implementation

## Version diff

- ไม่มีเอกสาร → `0.1.0b candidate`: เพิ่มข้อเสนอ schema, source mapping, provenance, missing-data gates และเกณฑ์ตรวจรับ
- ไม่มี code/data/runtime change ในรอบนี้; ไม่มีการเปลี่ยนเวอร์ชัน master เดิม

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---------|------|--------|---------|-------------|-------|
| 0.1.0b | 2026-08-30 | candidate | เสนอ local SQL snapshot projection และกำหนดคำถาม family/pkg ก่อน implementation | uncommitted | ATHER |
