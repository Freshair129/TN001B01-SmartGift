---
version: "0.1.1b"
created_at: "2026-08-10T00:00:00+07:00, ATHER, uncommitted"
last_update: "2026-08-10T16:30:00+07:00, ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "product-requirements"
  domain: "smartgift-zuri-line-copilot"
  scope: "visual-office-mvp-rbac-group-policy-reporting"
  artifact_id: "REQ-CR-012-VISUAL-OFFICE-MVP"
---

# REQ-CR-012 — Visual Office MVP Requirement Baseline

**สถานะ:** `beta` — Boss อนุมัติ requirement baseline แล้ว แต่ยังไม่อนุญาตให้เชื่อม endpoint, เขียน functional UI หรือ deploy จนกว่า API/policy/runtime contract ที่ระบุในเอกสารนี้จะผ่าน gate

## 1. วัตถุประสงค์

กำหนด MVP สำหรับ Visual Office ของ Zuri LINE Group Copilot ให้ Tenant Owner จัดการ RBAC, กลุ่ม LINE, capability ของ Copilot, reviewer, รายงาน และ alert ได้เองในลักษณะ SaaS โดยยังคง tenant isolation, PII masking, auditability, human-gate สำหรับ side effect, fail-closed และ recovery visibility เป็นข้อบังคับ

## 2. สถานะหลักฐานและขอบเขตการตัดสินใจ

| รายการ | สถานะ |
|---|---|
| Baseline สถาปัตยกรรม | ใช้ draft `CR-012`, `SPEC-CR-012`, `ADR-CR-012` จาก commit `d603a9e` บน branch `docs/vamt-tdd` เป็นฐานชั่วคราว |
| Worktree ปัจจุบัน | branch `codex/fontend` ไม่มีเอกสาร CR/SPEC/ADR ดังกล่าว; เอกสารนี้ไม่อ้างว่าเป็นการ restore หรือ merge เอกสารเหล่านั้น |
| ความเสี่ยง | HIGH — กระทบข้อความ LINE, CRM, PII, policy, approval และรายงานผู้บริหาร |
| ขอบเขต | Requirement baseline ของ UI/control plane เท่านั้น; ไม่ออกแบบ secret store, durable state, LINE ingress หรือ PersistentFlow implementation |

## 3. Confirmed Requirements

### 3.1 RBAC และขอบเขต tenant

| ID | Requirement | สถานะ |
|---|---|---|
| RQ-01 | ระบบใช้ RBAC; ผู้ใช้ไม่ได้ผูกสิทธิ์ตายตัวตามชื่อบุคคล | Confirmed |
| RQ-02 | Tenant Owner มอบและถอนทุก role ภายใน tenant ได้ รวมถึง role ระดับกำกับดูแล | Confirmed |
| RQ-03 | Tenant Owner อนุมัติทุก role/การกระทำภายใน tenant ได้เอง | Confirmed; ต้อง supersede human-quorum ที่ระบุใน baseline draft |
| RQ-04 | Tenant Owner กำหนดการเห็นและการจัดการแต่ละ LINE group ได้ทั้งตาม role และรายบุคคล | Confirmed |
| RQ-05 | ผู้รับการ์ดรายงานกด Dashboard ต้อง login Zuri และผ่าน server-side RBAC ทุกครั้ง | Confirmed |

### 3.2 LINE group และ Copilot policy

| ID | Requirement | สถานะ |
|---|---|---|
| RQ-06 | ทุกกลุ่มเริ่มต้นเป็น disabled; Tenant Owner ต้องลงทะเบียนและเปิดใช้ทีละกลุ่ม | Confirmed |
| RQ-07 | Tenant Owner ลงทะเบียน/เปิดกลุ่มได้ทุกประเภท ไม่จำกัดเฉพาะ internal group | Confirmed; ต้อง supersede V1 scope ใน baseline draft |
| RQ-08 | กลุ่มใหม่ไม่มี capability เริ่มต้น; Tenant Owner เปิด/ปิด capability เองรายกลุ่ม | Confirmed |
| RQ-09 | Tenant Owner กำหนด trigger แยกตามกลุ่มได้: `@mention/command`, ตรวจคำถาม/หัวข้อ, หรือทุกข้อความใหม่ | Confirmed |
| RQ-10 | เมื่อเปิด capability แล้ว Copilot ตอบ LINE อัตโนมัติได้ทันที เฉพาะสิทธิ์ read-only ของกลุ่มนั้น | Confirmed; ต้อง supersede shadow-first gate ใน baseline draft |
| RQ-11 | Tenant Owner เปิด/ปิด Answer, Summary Candidate และ Task Candidate แยกตามกลุ่มได้ | Confirmed |
| RQ-12 | Summary/Task Candidate เป็นร่างเสมอ; ห้ามสร้าง task, เขียน CRM, ส่ง หรือ publish เอง | Confirmed |
| RQ-13 | Tenant Owner แต่งตั้ง Reviewer/Approver แยกตาม group ได้ | Confirmed |

### 3.3 ลำดับคุณค่าทางธุรกิจ

1. ผู้บริหารเห็นสรุปสถานการณ์และความเสี่ยงของแต่ละกลุ่มทันเวลา
2. ข้อมูลลูกค้า/CRM ที่ตอบในกลุ่มถูกต้องและค้นหาได้
3. ไม่พลาด follow-up, งานค้าง หรือคำตัดสินใจ

### 3.4 Reporting และ alert

| ID | Requirement | สถานะ |
|---|---|---|
| RQ-14 | รายงานเป็นการ์ดใน LINE ตามตัวอย่างที่ให้: หัวข้อ, ช่วงเวลา, KPI หลัก, รายการย่อย และปุ่มเปิด Dashboard | Confirmed |
| RQ-15 | Tenant Owner เลือกปลายทางรายงานได้ทั้ง LINE group และข้อความส่งตรง แยกตามรายงาน | Confirmed |
| RQ-16 | มี Template V1 ครบ: Group Operations Summary, CRM/Customer Status, Risk & Escalation Alert, Custom KPI Card | Confirmed |
| RQ-17 | รายงานเริ่มจาก Template แล้ว Tenant Owner เปิด/ปิด KPI, จัดลำดับ และกำหนดเกณฑ์ alert ได้ | Confirmed |
| RQ-18 | รองรับ schedule รายวัน/สัปดาห์/เดือน, เงื่อนไข KPI/risk และตารางแบบอิสระ | Confirmed |
| RQ-19 | ตารางแบบอิสระต้องตั้งผ่าน UI Builder (วัน, เวลา, ความถี่, วันยกเว้น); ห้ามบังคับให้ผู้ใช้เขียน Cron | Confirmed |
| RQ-20 | Alert ส่งทันที แยกการ์ดต่อเหตุการณ์ | Confirmed |
| RQ-21 | Tenant Owner ตั้ง alert cap แยกตามรายงาน/เงื่อนไขได้ แต่ระบบมี hard cap ที่ข้ามไม่ได้ | Confirmed |
| RQ-22 | เหตุการณ์ที่เกิน cap ต้องรวมเป็นการ์ดเดียวที่บอกจำนวนที่ถูกพัก พร้อมลิงก์/ปุ่มดูรายละเอียด | Confirmed |
| RQ-23 | Tenant Owner ตั้งระดับข้อมูลต่อรายงานได้ แต่ระบบต้องบังคับ policy ของกลุ่ม, role ผู้รับ และ PII masking เสมอ | Confirmed |

## 4. ข้อบังคับที่ห้ามลดทอน

- ไม่มี secret/token แสดง, log, echo หรืออ่านกลับจาก UI ได้
- ทุกการเข้าถึงข้อมูลต้อง scoped ตาม tenant และตรวจสิทธิ์ฝั่ง server; การปฏิเสธต้องไม่เปิดเผยว่ามีข้อมูล/ลูกค้านั้นอยู่หรือไม่
- PII ต้อง mask ตาม policy และ recipient role แม้ Tenant Owner จะตั้งรายงานเอง
- ทุก side effect (task creation, CRM write, send, publish) ต้องเป็น explicit action หลังการตรวจ/อนุมัติ; Candidate ไม่ใช่ side effect
- UI ต้องแสดง loading, empty, error, denied, expired, revoked, stale, offline และ permission-denied state
- Disable/revoke ต้องหยุด Copilot อย่าง fail-closed โดยไม่ทำให้ Zuri Inbox เดิมหยุดทำงาน
- ตัวเลข/KPI ทุกตัวต้องมี source reference และ `as_of`; หากไม่มีข้อมูลต้องแสดงว่าไม่มีข้อมูล ไม่เดา

## 5. ความขัดแย้งที่ต้องแก้ใน CR/SPEC/ADR ฐานงาน

| ID | Baseline draft | การตัดสินใจใหม่นี้ | ผลที่ต้องทำหลังอนุมัติ |
|---|---|---|---|
| CF-01 | Boss + Privacy/Brand quorum เป็น authority สำหรับ auto-reply/pilot | Tenant Owner assign/approve ทุก role ได้เอง | แก้ gate authority, audit model และ threat model |
| CF-02 | V1 เฉพาะ registered `INTERNAL_SALES` และเริ่ม `ACTIVE_SHADOW` | Owner เปิดกลุ่มได้ทุกประเภทและ auto-reply read-only ได้ทันที | เพิ่ม group policy/consent/retention สำหรับ external/customer/public groups |
| CF-03 | capability ถูกจำกัดตาม classification template | Owner เปิด/ปิด capability รายข้อรายกลุ่ม | นิยาม capability catalog, validation และ fail-closed defaults |

## 6. Open Decisions — ไม่หยุดการจัดทำ UI spec แต่ห้ามเดาใน implementation

| ID | เรื่องที่ต้องตัดสินใจ | เหตุผล |
|---|---|---|
| OD-01 | Canonical Zuri design system และ visual token source | เอกสารแผนระบุว่ายังไม่มี canonical pick |
| OD-02 | API contract/source of truth สำหรับ group policy, role assignment, report template, schedule, recipient และ alert state | UI ต้องไม่แสดงหรือส่งข้อมูลจำลองเป็นข้อมูลจริง |
| OD-03 | ค่า hard cap สูงสุด, rate limit และ retention/consent ต่อประเภทกลุ่ม | เป็นค่าควบคุมความเสี่ยงและ PDPA ไม่ควรเดา |
| OD-04 | รายการ capability ที่ Owner เลือกได้จริง และ field-level mask ของ CRM ต่อกลุ่ม/recipient | ต้องเชื่อม policy engine และ CRM authority จริง |
| OD-05 | สัญญารูปแบบการ์ด LINE และ lifecycle ของปุ่ม Open Dashboard | ภาพตัวอย่างกำหนด intent/UI pattern แต่ไม่ใช่ API contract |

## 7. Acceptance Criteria สำหรับเริ่ม implementation

1. Boss ตอบ `APPROVED` ต่อเอกสารนี้ และยอมรับว่าต้องแก้ CR/SPEC/ADR ฐานงานตาม CF-01 ถึง CF-03
2. ก่อน code ที่เชื่อมข้อมูลจริง ต้อง freeze OD-02 และ OD-04 อย่างน้อยในระดับ API/policy contract
3. ก่อนเปิดใช้รายงานจริง ต้อง freeze OD-03 และ OD-05 พร้อม evidence ว่า KPI มี source/as_of และ PII mask ทำงาน
4. Implementation ต้องเริ่มจาก vertical slice ที่ตรวจ RBAC/tenant scope ฝั่ง server ได้ ไม่ใช่ UI ที่แค่ซ่อนด้วย CSS

## Contract Lock — 2026-08-10

Zuri Team/Employee RBAC is the only surface that may assign or revoke a tenant user's global role. Visual Office may select an existing tenant user as a group reviewer and may request control-plane changes only; it has no role-administration endpoint and must render role administration as managed by Zuri Team until the canonical RBAC contract proves the required Owner flow.

Group configuration and capabilities are configuration-only. Neither a valid record nor an enabled `answer` capability authorizes LINE runtime until canonical server-verified binding, consent/retention, immutable policy snapshot, PersistentFlow runtime gate, effective kill switch, and audit evidence have all admitted the group. This lock supersedes any prior immediate-activation wording, including RQ-10.

The browser submits only an opaque `groupBindingId` issued by the server from the same tenant's canonical Zuri LINE OA connection. It must never submit or derive `externalGroupRef`, LINE group ID, OA ID, or a tenant selector as authority.

An active report configuration is not delivery live. No report may be represented as sent or live until a governed outbox, idempotency, runtime policy gate, recipient revalidation, delivery receipt, retry/recovery contract, and audit evidence are present.

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.1b | 2026-08-10 | beta | Added contract lock for role authority, config-only group admission, canonical group binding, and config-only report delivery | uncommitted | ATHER |
| 0.1.0b | 2026-08-10 | beta | Recorded Boss approval of the requirement baseline; functional integration remains blocked by API, policy, runtime, and delivery gates | uncommitted | ATHER |
| 0.1.0b | 2026-08-10 | candidate | Consolidated MVP decisions gathered from Boss; records supersession conflicts and remaining implementation-blocking decisions | uncommitted | ATHER |
