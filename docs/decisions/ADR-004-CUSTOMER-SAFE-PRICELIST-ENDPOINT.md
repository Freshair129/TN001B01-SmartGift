---
version: "0.1.0b"
created_at: "2026-08-30T16:40:00+07:00,ATHER,uncommitted"
last_update: "2026-08-30T16:40:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "public-api"
  doc_type: "architecture-decision"
  scope: "customer-safe pricelist endpoint and Expo deployment"
  language: "th"
---

# ADR-004 — Customer-safe Pricelist API และ Expo deployment

**สถานะ:** Beta — Boss อนุมัติให้ commit/deploy/เปิด endpoint เมื่อ 2026-08-30
**Complexity / Risk:** C-3 / HIGH
**ขอบเขต:** public read-only Expo surface สำหรับ SmartGift; ไม่ใช่ quote หรือ production pricing
**สัมพันธ์:** [ADR-003](ADR-003-SEASONAL-PKG-SCHEMA-PROFIT-GATE.md), [TDD Seasonal PKG](../specs/TDD-SEASONAL-PKG-PROFIT-GATE-EXPO-2026-08-30.md)

## Context

`pricelist_master.json` มี factory cost, CBM, profit gate, FlowAccount evidence และ source
provenance ซึ่งใช้ใน local internal review เท่านั้น การ deploy ทั้ง repository หรือเปิด
`/api/pricelist` แบบ local projection ออกสาธารณะจะส่งข้อมูลภายในและไฟล์ raw/customer ไปด้วย

## Decision

1. สร้าง `public/data/pricelist_public.json` จาก exporter เดิมด้วย field allowlist เดียวที่
   ตรวจซ้ำด้วย `validate_public_projection` ก่อนเขียนไฟล์
2. เปิด Vercel read-only endpoints:
   - `GET /api/pricelist` — customer-safe catalog, SRP quantity ladder, seasonal package,
     BOM identity/quantity และ ad creative
   - `GET /api/catalog` — contract เดียวกันเพื่อให้ Expo โหลด catalog ได้
   - `GET /api/health` — status/schema/counts ที่ไม่มีราคาโรงงานหรือต้นทุน
3. response สาธารณะห้ามมี factory cost/identity, CBM/freight, profit/margin, supplier,
   FlowAccount, source path/hash, provenance, audit, CRM หรือ PII; endpoint รับเฉพาะ GET
4. deploy เฉพาะ `public/`, `api/` และ `vercel.json` ผ่าน `.vercelignore`; local internal
   endpoint `http://localhost:5180/api/pricelist` ยังคงเป็นทางดูต้นทุนและ evidence
5. package status, quote readiness และ profit gate ยังคงเป็น candidate/missing-inputs;
   deployment นี้ไม่ทำให้ package ใดกลายเป็น quote หรืออนุมัติการผลิต

## Consequences

- ลูกค้าเปิด Expo ได้จาก URL ที่ deploy แล้วโดยไม่เห็น factory cost, profit หรือ CBM
- ทีมภายในยังตรวจราคา/ต้นทุน/CBM ได้จาก local server และ master artifact เต็ม
- public data เป็น snapshot; เมื่อ master เปลี่ยนต้องรัน exporter, ตรวจ privacy และ deploy ใหม่
- SSO/auth สำหรับ internal cost endpoint ไม่ถูกทำให้เป็น public; การ quote/CRM ยังอยู่นอก scope

## Verification gates

- exporter `--check`, unit tests และ public allowlist scan ต้องผ่านก่อน deploy
- Vercel dry-run ต้องไม่รวม `data-pipeline/01_raw`, full master, vault, CRM หรือ source code
- หลัง deploy ต้องตรวจ `GET /api/health`, `GET /api/pricelist`, `GET /api/catalog`, หน้า `/#/expo`
  และทดสอบว่า forbidden fields ไม่ปรากฏใน response

## Version diff

`0.1.0b`: เพิ่ม customer-safe allowlist artifact, read-only API endpoints, upload boundary และ
verification gates แยกจาก internal local pricing evidence

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | beta | ออกแบบและอนุมัติ customer-safe pricelist endpoints กับ Expo deployment boundary | uncommitted | ATHER |
