---
version: "0.2.1b"
created_at: "2026-08-31T04:02:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T10:45:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "product-3d-assets"
  doc_type: "architecture-decision"
  scope: "approved local canonical ProductMaster coverage with evidence gates"
  language: "th"
---

# ADR-008 — โมเดลสินค้า 3D แยกไฟล์จากภาพ catalog

**Status:** Approved / beta — สร้าง local coverage register สำหรับ 16 canonical ProductMaster; ยังสร้าง GLB ได้เฉพาะรุ่นที่หลักฐานครบและผ่าน owner review<br>
**Date:** 2026-08-31<br>
**Proposed by:** ATHER; ผู้อนุมัติขอบเขต: Boss<br>
**Complexity / Risk:** C-3 / MEDIUM — สัญญา asset และ provenance สำหรับ consumer ในอนาคต; ไม่มี schema migration ใน pilot<br>
**Relates to:** [AGENTS.md](../../AGENTS.md), [schema authority](../../config/schema_genesisblock.yaml), [customer image-first spec](../specs/SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30.md), [ADR-007](ADR-007-KNOWLEDGE-REGISTRY-AND-PROVENANCE.md), [สเปกและเกณฑ์ตรวจรับ](../specs/SPEC-PRODUCT-3D-ASSETS-2026-08-31.md)

## Context

Boss ขอ “render model Product 3D โดยแกะจากภาพใน catalog เก็บเป็นไฟล์แยก เพื่อเอามาสร้าง 3d catalog” ก่อนหน้านี้ระบุให้สินค้าทรงเดียวกันต่างสีใช้โมเดลร่วมกัน และ catalog มีลูกค้าเป็นผู้ใช้หลัก

การตรวจ checkout พบ product source projections 427 รายการ, product families 32 กลุ่ม และ canonical ProductMaster 16 รายการ ตัวเลขเหล่านี้ไม่ใช่จำนวนรูปทรงไม่ซ้ำที่ยืนยันแล้ว ภาพเดี่ยวที่มี source crop แยกชัดเจนมี 6 รหัส; ภาพชุดของขวัญไม่ใช่หลักฐานจำนวน/รูปทรงของสินค้าแต่ละชิ้นโดยอัตโนมัติ

`public/gift-anatomy-3d.js` สร้างรูปทรงพื้นฐานใน scene เดียว จึงยังไม่ใช่คลังไฟล์โมเดลที่เทียบกับแต่ละรุ่นจริง ส่วน registry ตาม ADR-007 กำหนด Media สำหรับเสียง/วิดีโอ ไม่ได้อนุมัติประเภทโมเดล 3D

## Decision — อนุมัติขอบเขต pilot

### D1 — ส่งมอบ geometry จริง ไม่ใช้ภาพแบนแทนโมเดล

ใช้ glTF 2.0 binary (`.glb`) แบบ self-contained เป็นไฟล์ส่งต่อสำหรับ catalog; มี mesh ที่หมุนดูด้านข้าง/ด้านหลังได้ เก็บ preview ที่ render จากไฟล์ export แล้วแยกต่างหาก ภาพ AI แบบ 3D-looking ไม่ถือว่าเป็น `.glb` ที่ตรวจรับได้

นี่คือการสร้างรูปทรงอ้างอิงภาพสำหรับงานแสดงสินค้า ไม่ใช่ factory CAD, photogrammetry ที่พิสูจน์ครบทุกมุม หรือแบบผลิตที่ยืนยันความเที่ยงตรง

### D2 — หนึ่ง geometry ต่อรูปทรงที่พิสูจน์ว่าเหมือนกัน

แยกสี/ผิว/ลายเป็น material variants ที่อ้าง mesh เดิม ไม่สร้างไฟล์ geometry ซ้ำทุกสี การเปลี่ยนฝา หูจับ ช่องเสียบ สัดส่วน หรือขนาดที่ไม่พิสูจน์ว่า scale เดียวกันได้ ต้องแยกพิจารณา ห้ามใช้ family เดียวกันหรือชื่อคล้ายกันเป็นเหตุให้รวมรุ่นเอง

### D3 — Source-first canonical ProductMaster coverage

เป้าหมายคือ canonical ProductMaster 16 รายการที่มี `pm:` และ `IN_CATEGORY` ไป `cat:` ถูกต้องตาม schema ตามลำดับ Category: eco-friendly, classic-oriental, novelty-self-care, executive-smart-tech. ไม่ขยายไป 427 source projections, CatalogOffer หรือ BundleOffer ใน decision นี้

แต่ละ `pm:` ต้องมี (1) owner-verified source-code cross-reference, (2) ภาพต้นฉบับที่ hash/locator ตรวจได้ และ (3) ขนาดและมุมที่พอสำหรับขึ้นรูปก่อนเริ่ม GLB. หากไม่ครบต้องคง hold พร้อม evidence request matrix; ห้ามใช้ family hint, code คล้าย หรือภาพ generated/fallback เป็น identity proof.

หากภาพไม่พอให้เก็บสถานะ needs-reference/estimated ไม่ประดิษฐ์รายละเอียดแล้วอ้างว่ามาจากโรงงาน จำนวนโมเดลทั้งหมดใน catalog ยังไม่สรุปจนกว่าจะจัดกลุ่ม geometry โดยตรวจหลักฐานทีละรายการ

### D4 — Sidecar ภายใน ไม่ขยาย canonical namespace

เก็บ model, variants, metadata และ preview แยกใต้ `output/catalog-3d/` โดยมี index ภายในสำหรับโหลดตรวจทาน Asset key เป็นเพียงชื่อ artifact ในแพ็กเกจ ไม่ใช่ `pm:` หรือ registry ID

metadata เก็บ source code, image/PDF hashes, source locator และ registry references เฉพาะที่ resolve ได้จริง ProductMaster ที่ยังไม่ยืนยันให้เป็น null พร้อม mapping status; ไม่สร้าง `pm:` จาก business code ไม่บังคับ `.glb` เป็น `pic:`/`media:` และไม่เพิ่ม ontology ใน pilot

### D5 — Generated local viewer index, not public catalog promotion

viewer local อ่าน generated index ที่รวม Category coverage, hold reason และเฉพาะ asset ที่ local-ready/review-ready ตาม lifecycle; route ยังคง loopback allowlist และไม่ expose raw PDF, metadata หรือ source directory. Review candidates ที่ canonical identity unresolved ต้องติดป้ายชัดและไม่นับเป็น ProductMaster completion.

งานนี้ยังไม่แก้หน้า catalog, API, schema, BOM, ราคา หรือ product vault. Local-ready ไม่เท่ากับ public/customer-ready; การเผยแพร่และ registry promotion ต้องมี approval แยก และห้ามส่ง internal provenance/source paths ไปกับ customer payload

## Alternatives considered

1. Render ภาพนิ่งมุม 3D อย่างเดียว: ส่งต่อง่าย แต่หมุนดูสินค้าไม่ได้ ไม่ตอบโจทย์ geometry catalog
2. Export โมเดลกล่อง/ทรงกระบอกเดิมทุก SKU: ทำเร็ว แต่ไม่มีหลักฐานว่ารูปทรงตรงรุ่น
3. External image-to-3D service: อาจช่วยงานขึ้นรูป แต่มีการส่งภาพออกนอกเครื่อง ค่าใช้จ่าย และความคลาดเคลื่อนที่ต้อง review; ไม่อยู่ใน approval นี้
4. Factory CAD/multi-view capture: ให้หลักฐานรูปทรงดีกว่า แต่ยังไม่มีไฟล์ในชุดอ้างอิงที่ตรวจ จึงเป็นทางเลือกสำหรับรุ่นที่ต้องการความแม่นยำสูง ไม่ใช่ข้ออ้างว่าภาพเดี่ยวกู้รายละเอียดครบได้

## Consequences

- มีไฟล์โมเดลที่นำไปใช้ซ้ำได้พร้อมหลักฐานและสถานะความแม่นยำ แต่ยังไม่ใช่ catalog 3D ที่ deploy แล้ว
- ต้อง re-import GLB และตรวจภาพเทียบ reference จริง ไม่ใช้เพียง export สำเร็จเป็นหลักฐานความเหมือน
- รูปทรงบางด้าน/วัสดุบางชนิดเป็นการประมาณ ต้องเปิดเผยใน metadata และขอ review ก่อน public use
- การลงทะเบียนโมเดลใน Knowledge Registry เป็นงานต่อเนื่องที่ต้องเสนอประเภท/ความสัมพันธ์ให้ชัดก่อนแก้ schema

## Approval boundary

Boss อนุมัติให้ทำตาม 16 ProductMaster coverage plan โดยมี gates ข้างต้น. ไม่อนุมัติการสร้างครบ 427 รายการโดยอัตโนมัติ การซื้อบริการ ส่งภาพออกภายนอก ติดตั้งเครื่องมือระดับระบบ commit/push หรือ deploy

## Version diff

`0.2.0b beta` → `0.2.1b beta`: สร้าง coverage register, blank evidence input template, evidence request matrix และ generated local viewer index แล้ว. Baseline เป็น 16 held/0 local-ready ตาม evidence gate ไม่ใช่การอ้างว่าครบ 16 โมเดล.

`0.1.2b beta` → `0.2.0b beta`: ขยายจาก pilot 6 source codes เป็น local coverage program สำหรับ 16 canonical ProductMaster, เพิ่ม evidence/owner gates และ generated local viewer index; ไม่เปลี่ยน schema, graph, public exposure หรือ approval boundary อื่น.

`0.1.1b beta` → `0.1.2b beta`: บันทึก P1 สอง GLBs และ local verification ใน SPEC §9; ไม่มี ontology/public scope change และไม่อ้างว่า owner อนุมัติ assets แล้ว

`0.1.0b candidate` → `0.1.1b beta`: บันทึก approval สำหรับ P0–P1 และ gates เดิม; ไม่ขยาย public/schema/registry scope

ไม่มีเอกสาร → `0.1.0b candidate`: เพิ่มข้อเสนอ file-based 3D asset contract และ source-first pilot เท่านั้น; runtime/schema/source data ไม่เปลี่ยน

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.2.1b | 2026-08-31 | beta | local coverage artifacts พร้อม; ทั้ง 16 ยังรอหลักฐาน | uncommitted | ATHER |
| 0.2.0b | 2026-08-31 | beta | อนุมัติ 16 ProductMaster coverage พร้อม evidence gates | uncommitted | ATHER |
| 0.1.2b | 2026-08-31 | beta | P1 สองโมเดลพร้อมตรวจ; P2–P3 รอ review | uncommitted | ATHER |
| 0.1.1b | 2026-08-31 | beta | Boss อนุมัติ pilot โดยตรวจสองรุ่นแรกก่อนขยาย | uncommitted | ATHER |
| 0.1.0b | 2026-08-31 | candidate | เสนอ geometry/material/provenance separation และขอบเขต pilot | uncommitted | ATHER |
