---
version: "0.2.0b"
created_at: "2026-08-30T16:20:00+07:00,ATHER,uncommitted"
last_update: "2026-08-30T15:25:41+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "portfolio-blueprint"
  doc_type: "architecture-decision"
  scope: "seasonal package identity, cost/profit gate, and expo projection"
  language: "th"
---

# ADR-003 — Seasonal PKG ใช้ schema BundleOffer PK และ gate กำไร ฿25,000

**สถานะ:** Beta — Boss อนุมัติ local implementation เมื่อ 2026-08-30; ยังไม่ promote quote/production
**วันที่:** 2026-08-30
**ผู้ตัดสินใจ:** Boss ยืนยันให้ดำเนินการตาม schema และ package gate
**Complexity / Risk:** C-3 / HIGH
**เอกสารรายละเอียด:** [TDD Seasonal PKG และ Expo View](../specs/TDD-SEASONAL-PKG-PROFIT-GATE-EXPO-2026-08-30.md)
**Schema authority:** [`config/schema_genesisblock.yaml`](../../config/schema_genesisblock.yaml)
**Relates to:** [ADR-002](ADR-002-PRICELIST-MASTER-SQL-SNAPSHOT.md), [factory/SRP audit](../../data-pipeline/04_review_reports/pricelist-factory-srp-source-audit-2026-08-30.md)

## Context

คำขอล่าสุดต้องการสร้างชุด package จาก ProductMaster/CatalogOffer ที่มี สำหรับ Christmas
และ New Year โดยแสดงราคาขาย, ต้นทุนโรงงาน, CBM, ราคา 1 ชิ้น, โฆษณา และมุมมอง Expo ที่
ถอดชิ้นส่วนได้ พร้อมบังคับกำไรไม่น้อยกว่า ฿25,000 ต่อ package

ขอบเขตองค์กรคือ tenant `Org-EtohGroup` → business `SmartGift` → บริษัท เทราบิส จำกัด
(`Therabis Co., Ltd.`) การอ้างโครงสร้างบริษัทใน package หมายถึงระดับผู้รับตาม schema
ไม่ใช่การเก็บข้อมูลลูกค้าหรือรายชื่อพนักงาน

Schema v1.3.0 นิยาม package เป็น `BundleOffer` (`bundle:`) ซึ่งชี้ไปยัง CatalogOffer
ด้วย `INCLUDES_OFFER` และ CatalogOffer ชี้ ProductMaster ด้วย `CONTAINS`; schema ไม่ได้
นิยาม `pkg:` node ใหม่ จึงไม่ควรสร้าง identity คู่ขนานที่ทำให้ FK สับสน

หลักฐานรอบปัจจุบันพบว่า canonical ProductMaster 16 รายการยังจับคู่ factory code แบบ exact
ได้ 0/16 และ CBM เป็น declared scenario ไม่ใช่ measured freight นอกจากนี้ catalog offer
ปัจจุบันมี Select/Signature แต่ไม่มี Reach/Bespoke จึงต้องแยก derived offer ที่ยังไม่อนุมัติ
ออกจาก offer source เดิม

## Decision (approved locally; beta)

1. ใช้ `bundle:<stable-slug>` เป็น immutable graph/projection primary keyของ package
   และเก็บ `pkg_code = PKG-...` เป็น unique alternate/business key เท่านั้น
2. ให้ทุก `pkg_items`, `pkg_costs`, `pkg_creatives` อ้าง `bundle_id` เป็น FK ไปยัง schema PK;
   resolver รับ `pkg_code` ได้แต่ต้องแปลงเป็น `bundle_id` ก่อนเขียน
3. ใช้ `GiftTier` (`Reach`, `Select`, `Signature`, `Bespoke`) แยกจาก
   `RecipientSegment` (`C-Level`, `Mid-Management`, `Operations`) และไม่สร้าง customer
   tier ใหม่ใน product vault
4. สร้าง package candidates สำหรับ Christmas 2026 / New Year 2027 ตาม TDD โดยใช้
   existing offer codes `TDD03-2`, `TWL01-8`, `TGC06-4`, `TMK0215` เมื่อ tier/source
   ตรงกัน และสร้าง derived CatalogOffer จาก PM ที่มีได้เฉพาะหลังอนุมัติกรณี Reach/Bespoke
5. ให้ package gate คิดจาก order quantity และ direct cost ครบทุกหมวด โดย `profit_thb >= 25000`
   เท่านั้นจึงเป็น `pass`; ข้อมูลขาดให้ `cost_pending`/`mapping_pending` และไม่ถือว่าผ่าน
6. เก็บราคา `qty=1` เป็น reference แยกจาก package quote quantity; ถ้า CatalogOffer ไม่มี
   ราคา qty 1 ให้ null/price pending ห้ามอนุมานจากผลรวม component SRP
7. แยก Internal Expo View (ต้นทุน/CBM/profit/evidence) ออกจาก Customer-safe Ad Preview
   (ชื่อ, ภาพ, use case, tier/segment) และไม่ส่ง PII หรือข้อมูล supplier ไปยัง customer view

## Consequences

### Positive

- graph IDs, FK และ legacy `PKG-...` ไม่ปะปนกัน และ query `bundle_cascade` ของ schema ใช้ได้
- package ที่ไม่มีต้นทุนโรงงานจริงจะไม่ถูกแสดงเป็น quote หรือโฆษณาว่าผ่าน gate
- โครงสร้างบริษัทแสดงด้วย schema segments โดยไม่เก็บรายชื่อบุคคลใน `vlt-catalog-product`
- Expo สามารถแสดง BOM chain เดียวกับข้อมูลที่คำนวณราคา ลดความเสี่ยงภาพ/รายการไม่ตรงกัน

### Trade-offs

- Operations Reach และ Bespoke ยังทำเป็น sellable offer ไม่ได้จนกว่าจะสร้าง/อนุมัติ derived offer
- ต้องมี factory/PO/invoice identity, freight/CBM, branding, packing, assembly, delivery และ
  VAT basis เพิ่มก่อนประเมินกำไรจริง
- การเปิด customer view จริงต้องทำ response allowlist/server-side gate เพิ่ม ไม่ใช่เพียงซ่อน field

## Guardrails

- ห้ามใช้ `ProductMaster.base_cost` ที่เท่ากับ SRP เป็น factory cost
- ห้ามใช้ fuzzy code match, hardcoded freight estimate หรือ corporate bundle เก่าเป็นหลักฐานผ่าน
- ห้ามแก้ raw Excel/SQL, จอง stock, เขียน CRM/PII, seed vault หรือ deploy/public release ใน ADR นี้
- ราคาที่มีอยู่เป็น snapshot/reference; quote readiness, inventory readiness และ production approval
  ต้องผ่าน workflow แยก

## Approval gates ที่ยังค้างสำหรับการ promote

ต้องตอบ open questions ใน TDD เรื่องปี/วันส่ง, จำนวนแต่ละ segment, derived offer policy,
factory cost owner, freight/VAT/direct-cost rate card, creative language/channel และรูปแบบ
segment-only หรือ corporate mixed parent package ก่อนเริ่ม implementation

## Decision status and exit

Boss อนุมัติขอบเขต local implementation แล้ว จึงสร้าง exporter, JSON และ Expo view ตาม decision นี้
ผลลัพธ์รอบนี้เป็น beta projection: seasonal offers 6, packages 10 (+ legacy reference 1), และ
proposed BOM 17 edges; package gate ของทั้ง 11 รายการเป็น `missing_inputs` เพราะ exact factory
identity, order quantity, direct cost และ VAT basis ยังไม่ครบ จึงไม่มีรายการใดประกาศว่า `pass`
หรือพร้อมขายได้

ยังไม่มีการแก้ raw Excel/SQL, calculator เดิม, vault, inventory, CRM หรือ public deployment.
การตอบ open questions ในหัวข้อ Approval gates เป็นเงื่อนไขแยกก่อน quote/production promotion.

## Version diff

`0.1.0b → 0.2.0b`: Boss อนุมัติ decision และสร้าง local seasonal projection ตาม schema; เพิ่ม
offer/package/BOM validation, gate fail-closed, qty-1/ladder comparison และ Expo customer-safe
presentation. ยังไม่มี quote หรือ runtime/public promotion.

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.2.0b | 2026-08-30 | beta | Boss อนุมัติและสร้าง BundleOffer PK, PKG alias/FK, gate ฿25,000, BOM projection และ seasonal Expo | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | เสนอ BundleOffer PK, PKG alias/FK, gate ฿25,000 และ seasonal Expo | uncommitted | ATHER |
