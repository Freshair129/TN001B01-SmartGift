---
version: "0.1.0b"
created_at: "2026-08-31T06:18:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T06:18:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-3d"
  doc_type: "rca"
  scope: "local viewer asset allowlist"
---

# RCA — viewer โหลด W502 ไม่พบเพราะ version ถูกตรึง

## Symptom

หลังเพิ่ม W502 v001 ลง allowlist, `tests/catalog3d-viewer.test.mjs` ล้มเหลวด้วย `ENOENT` ที่ `output/catalog-3d/W502/v004/model.glb`.

## Evidence

- W502 ที่ผ่าน build อยู่ `W502/v001/model.glb` เพราะเป็นรุ่นสร้างแรก
- S1033 และ DW03 ใช้ v004 อยู่เดิม
- `viewer-server.mjs` สร้าง path ด้วย `code, 'v004'` สำหรับทุก code

## Root Cause

local viewer มี hash allowlist ต่อรหัส แต่ไม่เก็บ asset version ต่อรหัส จึงใช้ version เดียวกับทุกโมเดลโดยปริยาย.

## Why it escaped detection

test เดิมมีแต่ S1033/DW03 ซึ่งบังเอิญอยู่ v004 เหมือนกัน; ไม่มี test model ที่ version ต่างกัน.

## Proposed prevention

allowlist ต้องเก็บ `{ version, sha256 }` ต่อ code และ tests ต้องเปิด model ทุก allowlisted code. ไม่อ่าน version จาก request หรือ directory เพื่อคง fail-closed/static-file boundary.

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-31 | beta | RCA hard-coded v004 จาก W502 v001 test failure | uncommitted | ATHER |
