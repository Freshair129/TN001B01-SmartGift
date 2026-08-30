---
version: "0.3.0b"
created_at: "2026-08-30T17:10:00+07:00,CLAUDE,uncommitted"
last_update: "2026-08-31T00:05:00+07:00,Claude"
status: "beta"
superseded_by: null
attributes:
  domain: "data-pipeline"
  doc_type: "architecture-decision"
  scope: "factory cost intake lane, lane renumbering, .xls support"
  language: "th"
---

# ADR-005 — Factory Cost Intake Lane (`08_factory_costs`) และการแก้เลข lane ซ้ำ

**สถานะ:** Beta — ดำเนินการใน working tree, ยังไม่ commit
**Complexity / Risk:** C-2 / MEDIUM
**ขอบเขต:** intake lane ใหม่สำหรับไฟล์ต้นทุนโรงงาน (supplier cost catalogs) + แก้เลขโฟลเดอร์ `02_` ที่ซ้ำกันใน `01_raw/`
**สัมพันธ์:** [ADR-002](ADR-002-PRICELIST-MASTER-SQL-SNAPSHOT.md), [ADR-003](ADR-003-SEASONAL-PKG-SCHEMA-PROFIT-GATE.md), [CR-006](../change-requests/CR-006-PII-IN-VERSION-CONTROL-AND-ZURI-FILE-INTAKE-READINESS.md), [source audit 2026-08-30](../../data-pipeline/04_review_reports/pricelist-factory-srp-source-audit-2026-08-30.md)

## Context

1. ไฟล์ต้นทุนโรงงาน 3 ไฟล์จาก
   `D:\workspace\Bussiness-01-SmartGift\businesses\smartgift\source\drive\2026-08-12`
   (Business Office Gift set / Power bank notebook / USB Flashdrive) ยังไม่เคยเข้า pipeline
   ขณะที่ source audit 2026-08-30 ระบุว่า factory cost ของ canonical PM ทั้ง 16 ตัว
   "ยังจับคู่ไม่ได้" และ seasonal package gate ทั้ง 11 รายการติด `missing_inputs`
2. Stage 1 archiver เดิม (`flowaccount_registry_archiver.py`) สแกนเฉพาะ
   `01_raw/01_flowaccount_exports/` และรับเฉพาะ `.xlsx`/`.csv`; การโยนไฟล์ต้นทุนลง lane นั้น
   จะบันทึก provenance ผิดประเภท (`FlowAccountExportSnapshot`)
3. `01_raw/` มี lane เลขซ้ำ: `02_factory_pricelists_pdf` และ `02_pricing_formulas`
4. ข้อจำกัดการ renumber: `05_crm_customer_data/` ถูก pin ไว้ใน `.gitignore` (กฎกัน PII จาก
   CR-006) และ path ของ `02_factory_pricelists_pdf` / `03_product_catalogs` ถูกอ้างใน
   `output/catalog-internal/production-manifest.json`, artwork JSON, spec และ RCA หลายฉบับ
   การ renumber lane เหล่านั้นมีความเสี่ยงทำกฎ PII พังหรือ manifest ชี้ path ผิด

## Decision

1. **แก้เลขซ้ำแบบ minimal:** ย้าย `02_pricing_formulas` → `07_pricing_formulas`
   (โฟลเดอร์นี้ว่างและมี reference จุดเดียวคือ `pipeline/pricing_formula_archiver.py`)
   **ไม่ renumber** lane 02–06 ที่เหลือ เพราะ path ถูก pin โดย `.gitignore` (PII rule),
   production manifest และเอกสาร audit ที่บันทึกหลักฐานตาม path เดิม
2. **เพิ่ม lane ใหม่ `01_raw/08_factory_costs/`** สำหรับ supplier cost catalog
   (ไฟล์ต้นทุน EXW/RMB จากโรงงาน) พร้อม archiver ของตัวเอง:
   `pipeline/factory_cost_archiver.py` — SHA-256 versioning, immutable archive ที่
   `01_raw/archive/factory_costs/`, registry ที่ `01_raw/factory_cost_registry.json`,
   audit event `FactoryCostSnapshot` ลง `provenance_audit_log.jsonl`
3. **รองรับ `.xls` (legacy BIFF)** ในขั้นอ่าน summary/extract ด้วย `xlrd`
   (ไฟล์ต้นฉบับเก็บตามเดิมไม่แปลงไฟล์ — โซน `01_raw` เป็น immutable)
4. **ขั้น extraction แยกจากการเติมราคา:** `pipeline/extract_factory_costs.py` แปลง
   workbook เป็น `02_prepared/factory_costs.json` (normalized cost rows + currency +
   MOQ + packing) และสร้างรายงาน `04_review_reports/factory-cost-intake-*.md` พร้อม
   **proposed** PM mapping เท่านั้น — ไม่เขียนต้นทุนเข้า `pricelist_master.json`
   จนกว่า mapping จะผ่านการยืนยันโดยมนุษย์ (คงหลักการเดียวกับ audit 2026-08-30 ที่ไม่เติม
   ต้นทุนเมื่อ exact match ไม่ได้)
5. **Zero-PII ยังคุมเหมือนเดิม:** ไฟล์ต้นทุนถูกตรวจเนื้อหาแล้ว — เป็นข้อมูลสินค้า/ราคาฝั่ง
   ซัพพลายเออร์ ไม่มีข้อมูลลูกค้า; บรรทัด contact ของซัพพลายเออร์ในหัวไฟล์จะไม่ถูกดึงเข้า
   prepared JSON

## Decision (extended 2026-08-31): apply confirmed cost to `ProductMaster.base_cost`

Decision 4 above deliberately kept extraction separate from *writing* cost, and the
2026-08-30 pass only wrote confirmed EXW cost into seasonal package BOM edges inside
`pricelist_master.json` — the standalone `data-pipeline/02_prepared/ProductMaster.json`
export's own `base_cost` field stayed `null` for all 16 records even after Boss's
confirmation, because nothing in the pipeline wrote to that file.

`pipeline/apply_factory_cost_to_product_master.py` closes that gap as its own write step,
gated the same way as the BOM path:

- Fails closed (raises, writes nothing) unless `factory_cost_pm_mapping.json`
  `metadata.status == "confirmed"`.
- Writes `base_cost` = EXW cost in THB for the 9 confirmed `pm_code` pairs only; the 7
  `unmatched_pm` records are left untouched (`base_cost` stays `null`,
  `factory_match_status` stays `missing_factory_match`).
- Every touched record keeps full provenance — factory item code/name, EXW price,
  currency, FX rate, confidence, source file/hash, the mapping's own hash, and the
  `cost_basis_note` reminder that this is EXW only, not landed cost.
- `contract_validation.promoted` never flips from this step; canonical promotion stays a
  separate, human-reviewed gate.
- Idempotent — a second run reports "already applied" and writes nothing.

Wired into `master_orchestrator.py` as **Stage 1.5**, right after the Stage 1 archivers,
since cost lineage begins there. Audit trail: `data-pipeline/04_review_reports/product_master_cost_apply_report.json`.

This does not change the profit gate: package-level profit still needs commercial inputs
(order quantity, package price, target recipients) beyond product cost, so all 11
packages remain `missing_inputs` as before.

## Consequences

- ไฟล์ต้นทุน 3 ไฟล์เข้าระบบพร้อม provenance ถูกประเภท และ pipeline มี lane ถาวรสำหรับ
  ไฟล์ต้นทุนรอบถัดไป
- เลข lane ใน `01_raw/` ไม่ซ้ำกันอีก (01–08 โดย 07=pricing formulas, 08=factory costs)
- profit gate ยังคง `missing_inputs` จนกว่า PM mapping จะถูกยืนยัน — ADR นี้ไม่อนุมัติราคา
- เอกสารโครงสร้าง `docs/DATA_PIPELINE_AND_VAULT_STRUCTURE.md` อัพเดทเป็น v1.1.0 ให้ตรง
  โครงจริง (`data-pipeline/` แทน `data/`, lane 01–08)

## Verification gates

- `git check-ignore -v data-pipeline/01_raw/05_crm_customer_data/<file>` ยังต้อง ignore ได้หลังการเปลี่ยนแปลง
- `py -3 pipeline/pricing_formula_archiver.py` ทำงานได้กับ path ใหม่
- `py -3 pipeline/factory_cost_archiver.py` ลงทะเบียน 3 ไฟล์ status `NEW_VERSION_ARCHIVED`
- extract ออก `factory_costs.json` โดยไม่มีชื่อบุคคล/email/skype จากหัวไฟล์
- `py -3 pipeline/apply_factory_cost_to_product_master.py` ปฏิเสธการเขียนเมื่อ mapping ยัง `status != confirmed`; เขียน `base_cost` ให้ 9 รหัสที่ยืนยันเท่านั้น; รันซ้ำแล้วไม่มีอะไรเปลี่ยน (idempotent); `contract_validation.promoted` ต้องยังเป็น `false` เสมอ

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.3.0b | 2026-08-31 | beta | เพิ่ม `apply_factory_cost_to_product_master.py` เติม `base_cost` เข้า ProductMaster.json 9/16 records พร้อม provenance; wire เป็น Stage 1.5 ใน orchestrator; tests 7 ตัวใหม่ผ่าน | 908b567 | Claude |
| 0.2.0b | 2026-08-30 | beta | Boss ยืนยัน mapping 9 คู่; exporter รับ `factory_cost_pm_mapping.json` เป็น input ที่ 6 (hash-pinned, ตรวจ status=confirmed) เติมต้นทุน EXW เข้า seasonal BOM 13/17 edges; field ต้นทุนใหม่ทั้งหมดถูกเพิ่มใน PUBLIC_FORBIDDEN_FIELDS; tests 61 ผ่าน | uncommitted | CLAUDE |
| 0.1.0b | 2026-08-30 | beta | ตั้ง lane 08_factory_costs, ย้าย 02_pricing_formulas→07, รองรับ .xls, extraction แบบ proposed mapping | uncommitted | CLAUDE |
