---
version: "0.1.0b"
created_at: "2026-08-30T17:35:19+07:00,CLAUDE"
last_update: "2026-08-30T17:35:19+07:00,CLAUDE"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-pricing"
  doc_type: "intake-review"
  scope: "factory cost lane 08 first ingest; proposed PM mapping awaiting human confirmation"
---

# Factory Cost Intake Review — lane 08_factory_costs

ไฟล์ต้นทุนโรงงาน 3 ไฟล์ (ชุดข้อมูล drive 2026-08-12) ถูก ingest พร้อม SHA-256 provenance
และ extract เป็น `02_prepared/factory_costs.json` — **ยังไม่มีการเขียนต้นทุนเข้า
`pricelist_master.json`** เพราะ PM mapping เป็นเพียง keyword candidates (ADR-005)

## Sources

| File | SHA-256 (12) | Records extracted |
|---|---|---:|
| 01-ต้นทุน-20260612 Business Office Gift set catalog.xlsx | `515ecf8464b5` | 1031 |
| 02-ต้นทุน-20260417 Power bank notebook catalog.xlsx | `9c8b51678f0a` | 71 |
| ต้นทุน USB Flashdrive.xls | `13e284c53bce` | 64 |

รวม 1166 records (มีราคา 1152); unmapped 38 records

## Proposed PM mapping candidates (ยังไม่ยืนยัน)

| PM code | จำนวน records ที่เข้าเกณฑ์ keyword |
|---|---:|
| PM-AROMA | 15 |
| PM-BOTTLE-LED | 71 |
| PM-CFMUG | 559 |
| PM-CUTLERY | 12 |
| PM-DESK-MAT | 3 |
| PM-FAN | 147 |
| PM-FLASH | 518 |
| PM-MSG | 209 |
| PM-NB | 283 |
| PM-PB10K | 428 |
| PM-PEN | 363 |
| PM-SPK | 120 |
| PM-TEA-INF | 66 |
| PM-UMB | 319 |

## เงื่อนไขก่อนใช้ราคา

- ราคาเป็น EXW (USD / RMB ตาม source) ยังไม่รวม freight, duty, FX — ต้องผ่าน
  `pricing_rules_formula.yaml` ก่อนเป็น landed cost
- สินค้าใน gift set catalog เป็นราคาต่อ **ชุด** ไม่ใช่ต่อชิ้นส่วน; การ map เข้า BOM
  ต้องตัดสินใจว่าจับที่ระดับ set หรือ component
- ไฟล์ USB flashdrive ไม่มี item code — จับคู่ได้เฉพาะระดับหมวด (PM-FLASH) + capacity
- ผู้อนุมัติต้องยืนยันคู่ mapping ทีละรายการก่อน จึงจะเติม `factory_cost_thb` ใน
  pricelist master ได้ (คงหลักการ audit 2026-08-30 ที่ไม่เติมต้นทุนเมื่อไม่มี exact match)

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | beta | first ingest of 3 factory cost files; extraction + proposed mapping only | uncommitted | CLAUDE |
