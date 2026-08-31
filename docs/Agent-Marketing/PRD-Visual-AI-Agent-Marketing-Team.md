---
version: "0.3.0b"
created_at: "2026-08-09T18:00:00+07:00, ATHER, uncommitted"
last_update: "2026-08-10T00:10:00+07:00, ATHER"
status: "draft"
superseded_by: null
attributes:
  domain: "visual-ai-marketing"
  scope: "product-requirements"
  artifact_id: "PRD-VAMT-001"
---

# PRD — Visual AI Agent Marketing Team

## 1. เอกสารนี้คืออะไร

| รายการ | ค่า |
|---|---|
| Product ID | VAMT |
| เอกสารอ้างอิงระบบ | SRS-VAMT-001 และ SPEC-VAMT-001 |
| สถานะ | Draft — ห้ามถือว่าอนุมัติใช้งานจริง |
| Product owner ที่ต้องแต่งตั้ง | Marketing Owner |
| Technical owner ที่ต้องแต่งตั้ง | Runtime Owner |
| Governance owner ที่ต้องแต่งตั้ง | MSP Owner |
| กลุ่มผู้ใช้แรก | ทีมการตลาด, ทีมขาย, Brand Owner, Legal/Compliance |

Visual AI Agent Marketing Team คือสำนักงาน visual marketing แบบหลาย agent ที่สร้างและบริหาร creative สำหรับ B2B และ C2C โดยมีมนุษย์เป็นผู้ตัดสินใจในจุดเสี่ยง ระบบต้องสร้างภาพโฆษณา, social creative, product shot และ campaign visual ได้ แต่ต้องไม่ลดมาตรฐาน brand, claim, PDPA, ลิขสิทธิ์ หรือความสามารถในการตรวจสอบย้อนหลัง

ผลิตภัณฑ์นี้เป็น proposed subsystem ของ business operating environment ไม่ใช่การแทน CRM, accounting, price approval หรือ commerce settlement system ที่มีอยู่แล้ว ข้อมูลการขายและผลการตลาดยังมี source of truth ของตนเอง; VAMT รับเฉพาะ reference ที่ผ่านสิทธิ์และคืน campaign/asset/performance evidence กลับไป

## 2. ปัญหาที่แก้

### 2.1 ปัญหาธุรกิจ

1. งาน creative ใช้เวลานานเพราะ brief, ความรู้แบรนด์, ภาพสินค้า, feedback และ approval กระจายอยู่หลายที่
2. ภาพที่ผลิตเร็วมีความเสี่ยงไม่ตรง brand, ใช้ claim เกินหลักฐาน, ใช้ภาพอ้างอิงไร้สิทธิ์ หรือสูญเสียที่มาของไฟล์
3. ทีมขายได้ข้อมูลจากการประชุมและบทสนทนาลูกค้า แต่ความตั้งใจของลูกค้าไม่ถูกแปลงเป็น brief/evidence ที่ตรวจสอบได้
4. เมื่อ campaign เปลี่ยนคนดูแลหรือ runtime ล้มกลางงาน ไม่มีวิธีรู้แน่ชัดว่า asset ใดอนุมัติแล้ว, provider job ใดสร้างไปแล้ว หรือควร resume จุดใด
5. การ optimize มักเปลี่ยน creative จากตัวเลขที่ไม่มี attribution หรือเปลี่ยนเกินขอบเขตที่เจ้าของอนุมัติ

### 2.2 ผลกระทบหากไม่แก้

| มิติ | ผลกระทบ |
|---|---|
| Brand | tone และ visual identity ไม่สม่ำเสมอ ทำให้ความเชื่อมั่นลดลง |
| Compliance | claim, consent, personal data หรือ rights หลุดออกนอกขอบเขต |
| Cost | สร้างภาพซ้ำเมื่อ worker ล้ม หรือขาด history ว่าอะไรถูกปฏิเสธ |
| Sales | sales insight จาก FUNG ไม่เปลี่ยนเป็น action ที่ trace ได้ |
| Management | ไม่สามารถตอบได้ว่าใครอนุมัติอะไร จาก policy รุ่นใด และบนหลักฐานใด |

## 3. วิสัยทัศน์และคุณค่า

### วิสัยทัศน์

สร้าง Visual Office ที่ทำงานเร็วในระดับ agentic system แต่มีความรับผิดชอบเทียบเท่าทีม marketing ที่มี brand owner, legal review และ production control ครบถ้วน

### คุณค่าหลัก

| คุณค่า | ความหมายเชิงผลิตภัณฑ์ |
|---|---|
| Brand-consistent by design | ทุกงานสร้างภาพผูกกับ canonical brand atom ไม่ใช่ความจำของ model |
| Human-controlled | Agent เสนอและปฏิบัติตามขอบเขต; มนุษย์อนุมัติ, ยกเว้น และ release |
| Durable | งาน resume ได้หลัง crash โดยไม่สร้าง side effect ซ้ำ |
| Evidence-first | claim, product fact, metric และ decision ต้องมี source/reference |
| Reproducible | asset มี lineage, hash, model binding และ parameter history |
| Privacy-aware | FUNG และข้อมูลขายผ่าน consent, redaction, retention และ tenant isolation |

## 4. ผู้ใช้และสิทธิ์

| Persona | เป้าหมาย | สิทธิ์หลัก | ไม่มีสิทธิ์ |
|---|---|---|---|
| Marketing Owner | เปิด/ปิด campaign และตัดสินใจทิศทาง | อนุมัติ G0, G2, G3, G6, G7 ตาม policy | เปลี่ยน canonical brand/claim โดยลำพัง |
| Brand Owner | คุ้มครอง visual identity | อนุมัติ G1, G4 | ปล่อย campaign หรือแก้ rights policy |
| Sales Lead | แปลง discovery เป็น campaign request | submit brief, ยืนยัน business context | ถือ transcript เป็น approval |
| Legal/Compliance | อนุมัติ claim/rights/disclaimer | อนุมัติ G5, exception ตาม authority | สั่ง generate/release โดยไม่มี owner |
| Creative Operator | ดูงานและเสนอ revision | submit concept/revision request | bypass gate |
| Analyst | ดู performance และเสนอ experiment | อ่าน metric ที่ authorized | ปรับ live media โดยตรง |
| Runtime Operator | ดู health/recovery | retry/reconcile ตาม runbook | แก้ business decision หรือ asset content |
| Creator/Referral Partner | รับ creative kit และยอมรับสิทธิ์การใช้/ข้อเปิดเผย | submit acceptance ผ่าน UI ที่มี scope จำกัด | อนุมัติ campaign, เปลี่ยน copy/asset, publish นอก release scope |

## 5. Scope ของ V1

### 5.1 In scope

1. Campaign brief สำหรับ B2B และ C2C พร้อม reference ไปยัง product, brand, audience, channel และ evidence โดย C2C V1 จำกัดที่ creator/referral creative kit ที่ผ่านสิทธิ์แล้ว
2. Role-based agent team: Orchestrator, Brand Visual Guardian, Visual Research, Creative Concept Director, Visual Asset Generator, Copy-Visual Integrator, Performance & Optimization, Campaign Packager และ FUNG adapter
3. Human Gate G0 ถึง G7, interrupt/resume, signed decision, expiry และ audit trail
4. PersistentFlow campaign state, checkpoint, recovery และ reconciliation ของ provider job
5. Asset generation ผ่าน provider adapter พร้อม immutable revision, checksum, prompt/model lineage และ quarantine
6. GKS candidate/canonical knowledge workflow ผ่าน MSP, persisted/indexed by GenesisBlockDB
7. Campaign package manifest, approved rendition list, release handoff และ publish receipt
8. Performance ingestion จาก approved SoT พร้อม experiment proposal ที่มี guardrail
9. Operator views สำหรับ gate queue, campaign timeline, asset lineage, quarantine และ recovery status

### 5.2 Out of scope

1. Autonomous publication โดยไม่มี G6 release decision
2. Autonomous budget increase, ad-buying, bidding หรือ spend settlement
3. Payment, payout, creator settlement, tax และ invoice handling
4. การเปลี่ยน brand strategy, product truth, price, discount หรือ legal claim โดย agent
5. Training foundation image model จาก customer asset หรือ raw customer transcript
6. Face/voice cloning, celebrity likeness หรือ persona profiling ที่ไม่มี explicit consent
7. การนำ raw CRM/financial customer data เข้า prompt หรือ public image provider
8. การอ้างว่า performance เป็น causal result เมื่อ attribution/data quality ไม่พอ
9. การเลือก creator อัตโนมัติ, การส่งข้อความหา creator อัตโนมัติ, creator payout และ creator settlement

## 6. Canonical Gate Definitions

| Gate | Subject ที่อนุมัติ | Signer หลัก | Default expiry | เมื่อ reject/expire |
|---|---|---|---|---|
| G0 | brief, data authority, FUNG consent และ knowledge snapshot | Marketing Owner หรือ Sales Lead ตาม policy | 14 วัน หรือวันหมดอายุของ source ที่สั้นกว่า | BLOCKED จนแก้ missing authority |
| G1 | brand profile และ applicability ต่อ campaign | Brand Owner | 14 วัน | กลับไป planning พร้อม brand finding |
| G2 | concept route, message hierarchy และ asset spec draft | Marketing Owner + Brand Owner เมื่อ policy กำหนด | 14 วัน | สร้าง concept/spec revision ใหม่ |
| G3 | locked asset spec, provider/model binding, budget และ exception scope | Marketing Owner; Finance เมื่อเกิน threshold | 72 ชั่วโมง | ห้ามเรียก provider; กลับไป planning |
| G4 | final visual candidate ที่ผ่าน quality checks | Brand Owner | 14 วัน | quarantine/retire candidate หรือสร้าง revision ใหม่ |
| G5 | claim, disclaimer, rights และ creator usage-rights เมื่อมี | Legal + Marketing Owner | 14 วัน | package ไม่สมบูรณ์และย้อนกลับไป revision |
| G6 | immutable package manifest และ destination/schedule | Marketing Owner | 72 ชั่วโมง | ห้าม publish/schedule; package อยู่ READY_FOR_RELEASE |
| G7 | experiment, metric, guardrail และ stop condition | Marketing Owner | 7 วัน | คง control เดิมและปิด/ปรับ proposal |

ค่า expiry ข้างต้นเป็น default policy ของผลิตภัณฑ์; policy ที่เข้มกว่าใช้แทนได้ แต่ policy ที่ผ่อนกว่าต้องเป็น MSP exception ที่ลงนามและมีวันหมดอายุ

## 6.1 Product Principles และ Guardrails

1. ไม่มี evidence = ไม่มี claim
2. ไม่มี signed approval = ไม่มี irreversible side effect
3. ไม่มี provider reconciliation = ไม่มี retry create ใหม่
4. ไม่มี rights evidence = ไม่มี asset เข้า package
5. ไม่มี canonical/approved atom = ไม่มี brand/product fact ใน prompt
6. ไม่มี data quality status = ไม่มี optimization action
7. ไม่มี retention/consent = FUNG ต้อง block ก่อน transcription
8. ห้ามลบ/เขียนทับ asset, decision หรือ event เพื่อแก้ประวัติ; ใช้ revision/supersession

## 7. User Journeys

### 7.1 B2B Account-Based Campaign

1. Sales Lead ส่ง meeting evidence ที่ FUNG ตรวจ consent และ redaction แล้ว
2. Marketing Owner ทำ brief ด้วย account context, product truth และ objective
3. Orchestrator ตรวจความครบถ้วนและเปิด G0
4. Visual Research และ Creative Director สร้าง evidence packet กับ concept routes
5. Brand Owner อนุมัติ brand/concept scope ที่ G1/G2
6. Marketing Owner อนุมัติ model, provider และงบสร้างที่ G3
7. Generator ผลิต asset candidates; Guardian/Integrator ตรวจ
8. Brand Owner และ Legal อนุมัติ final creative, claim และ rights ที่ G4/G5
9. Packager ประกอบ deliverable; Marketing Owner อนุมัติ release ที่ G6
10. Performance Agent รายงานจาก SoT และเสนอ experiment ผ่าน G7

### 7.2 C2C Creator/Referral Campaign

1. Marketing Owner เลือก creator/referral partner ผ่านกระบวนการภายนอกระบบ; ระบบรับเฉพาะ consent และ usage-rights ที่ลงนามแล้ว
2. ผู้ดูแลเลือก micro-segment และ channel specification
3. ระบบสร้าง approved creative kit ที่มี template, disclosure, CTA และ rendition
4. Creator acceptance เป็น scoped human decision ที่ G5 ไม่ใช่ inferred transcript และไม่เป็นสิทธิ์ publish นอก G6
5. Release ผ่าน G6; performance ที่ attribution ครบเท่านั้นจึงเสนอ variation
6. Asset หรือ template ที่ถูก retire ยังคง audit ได้ แต่ reuse ไม่ได้

## 8. Functional Product Requirements

| ID | Requirement | Priority | Acceptance criteria |
|---|---|---|---|
| PRD-FR-001 | ผู้ใช้ต้องสร้าง campaign brief ที่อ้างอิง knowledge atom ได้ | P0 | brief ที่ขาด product/brand/channel ref submit ไม่ได้ |
| PRD-FR-002 | ระบบต้องแสดง campaign timeline ที่รวม agent, tool, gate และ human decision | P0 | ผู้ตรวจตาม run_id ย้อน timeline และ subject hash ได้ครบ |
| PRD-FR-003 | ระบบต้องเปิด human gate และ resume โดย signed decision เท่านั้น | P0 | decision หมดอายุ/subject เปลี่ยนแล้ว resume ไม่ได้ |
| PRD-FR-004 | Brand Guardian ต้อง block visual/claim ที่ขัด canonical rule | P0 | finding ชี้ rule/atom และ resolution ได้ |
| PRD-FR-005 | Generator ต้องสร้าง asset revision ที่มี lineage ครบ | P0 | asset ขาด checksum/model binding/rights ref เข้า package ไม่ได้ |
| PRD-FR-006 | ระบบต้อง reconcile provider job ก่อน retry | P0 | crash หลัง submit ไม่สร้าง provider job ซ้ำ |
| PRD-FR-007 | FUNG ต้อง block งานเมื่อ consent/retention ไม่ครบ | P0 | raw audio ไม่เข้าสู่ transcript workflow |
| PRD-FR-008 | Packager ต้องสร้าง immutable release manifest | P0 | manifest ขาด approval/asset/rights ไม่พร้อม release |
| PRD-FR-009 | Performance ต้องแสดง SoT source, time window, attribution และ quality | P1 | metric ไม่มี source อยู่ในสถานะ insufficient data |
| PRD-FR-010 | ระบบต้องเสนอ experiment พร้อม guardrail และ rollback trigger | P1 | experiment ไม่มี owner/gate/metric launch ไม่ได้ |
| PRD-FR-011 | Operator ต้องเห็น quarantine และ recovery queue | P1 | asset fail และ run crash ปรากฏใน queue พร้อม next action |
| PRD-FR-012 | ผู้ใช้ต้อง export audit package ต่อ campaign ได้ | P1 | export มี manifest, decision refs, event head hash และ retention notes |

| PRD-FR-013 | FUNG ต้อง enforce consent, retention และ deletion lifecycle แบบตรวจสอบได้ | P0 | ingest ที่ไม่มี consent record ถูก reject พร้อม audit event; redacted evidence ระบุ retention expiry; expiry/deletion สร้าง deletion evidence และเพิกถอน future retrieval |
| PRD-FR-014 | ทุกคำขอ external provider ต้องมีหลักฐาน PII scan ที่ผูกกับ payload จริง | P0 | payload hash, data class, scanner/policy, result, เวลาและ expiry ตรงกับคำขอก่อนสร้าง intent |
| PRD-FR-015 | External side effect ต้อง dispatch ผ่าน transactional outbox และ state-revision CAS | P0 | crash/retry/webhook ซ้ำไม่ทำ side effect หรือ ingest ผลซ้ำ |
| PRD-FR-016 | External result ต้องผ่าน admission validation ก่อนเข้า authoritative state | P0 | ผลที่ policy, approval หรือ knowledge stale ถูก quarantine และเข้า package/replay ไม่ได้ |
| PRD-FR-017 | G2 และ G5 ต้องบังคับ multi-authority quorum แบบตรวจสอบได้ | P0 | ลายเซ็นรายคน immutable; reject/revoke/expire ทำให้ aggregate approval ใช้ต่อไม่ได้ |
| PRD-FR-018 | ผลลัพธ์ APPROVE, REJECT, EXPIRE และ REQUEST_REVISION ของ G0-G7 ต้อง map ไป state เดียวที่กำหนด | P0 | ทุก outcome ผ่าน state validation; G6 reject/expire กลับ READY_FOR_RELEASE |

## 9. Non-functional Product Requirements

| ID | Requirement |
|---|---|
| PRD-NFR-001 | ข้อมูลและ action ทุกชนิดต้องแยก tenant และตรวจ authorization ทั้ง UI/API/adapter |
| PRD-NFR-002 | State ต้อง recover ได้โดยไม่สูญเสีย committed decision หรือทำ external side effect ซ้ำ |
| PRD-NFR-003 | ผู้ใช้ต้องเห็นสถานะ WAITING_FOR_HUMAN, BLOCKED, QUARANTINED และ RECOVERING อย่างตรงไปตรงมา |
| PRD-NFR-004 | Asset ที่ผ่าน approval ต้อง trace ย้อนถึง spec, atoms, model/provider และ decision ได้ |
| PRD-NFR-005 | ระบบต้อง fail closed เมื่อ schema, policy, evidence, consent หรือ rights ขาด |
| PRD-NFR-006 | ข้อมูล PII และ raw transcript ต้องไม่ปรากฏใน prompt log, event projection หรือ public asset manifest |

| PRD-NFR-007 | ก่อน Controlled Pilot ระบบต้องมี automated PII scan สำหรับ prompt log, event projection และ package manifest; พบ PII ที่ไม่อนุญาตต้อง block release |
| PRD-NFR-008 | ก่อนเรียก external image provider ทุก binding ต้องมี data-processing/right approval ที่ active ตาม data class และ geography |
| PRD-NFR-009 | GoVibe, MSP, GKS และ GenesisBlockDB ต้องมีขอบเขต authority แยกชัด และทุก run ต้องผูก GoVibe config snapshot ที่ตรวจ hash/version ได้ |

## 10. Success Metrics และ Guardrails

Metric ทุกตัวต้องมี approved metric definition และ SoT source; ไม่มี baseline ปัจจุบันจึงไม่กำหนดตัวเลขเป้าหมายลอย ๆ ใน PRD นี้

| กลุ่ม | Metric ที่จะวัด | Guardrail |
|---|---|---|
| Flow efficiency | เวลา brief ที่ครบถึง package ready | ห้ามลด gate เพื่อให้เร็ว |
| Brand quality | approval pass rate, violation class, revision count | pass rate สูงไม่ใช่เหตุให้ลด quality bar |
| Reliability | recovery success, duplicate side effect, provider reconciliation time | duplicate external create ต้องเป็น 0 |
| Governance | unsigned/expired decision rejection rate, exception count | exception เพิ่มต้อง review policy |
| Rights/PDPA | quarantine reason, consent block, retention compliance | rights/consent breach ต้องเป็น incident |
| Business | qualified lead, conversion, repeat/referral outcome | แสดง data quality และ attribution model เสมอ |

### Release-entry Metric Contract

Controlled Pilot ต้องถูก block จนกว่า Analytics Owner จะลงนาม baseline, target, measurement window, attribution method และ data-quality threshold ใน metric definition atom ต่อ objective ที่จะวัด ระบบห้ามใช้ตัวเลขธุรกิจสมมติแทนข้อมูลจริง

| Release stage | หลักฐานที่ต้องมี |
|---|---|
| Internal pilot ที่เรียก external image provider | active DPA/data-processing approval, provider/model binding ที่ G3 อนุมัติ, และ PII scan ของ request path ผ่าน |
| Controlled pilot | metric definition ที่มี baseline/target/owner/attribution/data-quality threshold ครบและลงนามแล้ว |
| Limited production | recovery test suite ผ่านทุก defined side-effect boundary, duplicate external create เท่ากับ 0 ใน test evidence, และมี active operational alert/runbook |

## 11. Dependencies

| Dependency | บทบาท | เงื่อนไขก่อนใช้งานจริง |
|---|---|---|
| GoVibe | governance control plane และ work tracking | execution authority/configuration ที่ approved |
| MSP | human decision, promotion, policy mediation | role mapping, signature และ policy contract |
| GKS | atomic knowledge authority | canonical atom registry และ version lookup |
| GenesisBlockDB | persist/index knowledge relation | tenant-aware access และ audit integration |
| PersistentFlow | durable workflow runtime | checkpoint, restore, state schema contract |
| FUNG | consented conversation intelligence | consent, redaction, retention, secure vault |
| Image provider | image generation/editing | data-processing/right/safety agreement |
| Object storage | immutable asset storage | versioning, encryption, lifecycle policy |
| Analytics/CRM SoT | performance facts | source contract, attribution, data-quality field |

### Provider Governance Prerequisite

Image provider เป็น dependency ที่ใช้ได้ต่อเมื่อมี data-processing/right/safety approval ที่ active ตาม class ของข้อมูลและ geography เท่านั้น การมี API credential หรือ non-production namespace ไม่ถือเป็น approval ให้ส่งข้อมูลไปยัง provider

### Authority Matrix

| ระบบ | Authority ที่ถือ | สิ่งที่ห้ามถือเป็น authority |
|---|---|---|
| GoVibe | approved execution configuration, workflow topology และ capability binding | human approval หรือ canonical business truth |
| MSP | signed decision, quorum, exception, promotion authorization และ revocation | เก็บหรือแก้ canonical atom โดยตรง |
| GKS | canonical/candidate atom registry, validity, supersession และ authorized mutation/read contract | workflow execution state |
| GenesisBlockDB | materialization และ index ของ GKS relation เพื่อค้นคืนแบบ tenant-aware | canonical mutation, promotion หรือ decision authority |

ทุก run ต้องเก็บ `config_snapshot_ref`, `config_hash` และ `config_version` ของ GoVibe ใน event, checkpoint และ audit export; การ materialize ใน GenesisBlockDB ห้ามเปลี่ยน status, content hash หรือ supersession ของ GKS atom และต้องตรวจย้อนกลับไปยัง GKS record ได้

## 12. Risks และ Mitigations

| Risk | Level | Mitigation |
|---|---|---|
| Brand drift จาก model creativity | High | canonical visual atoms + Guardian fail-closed + G4 |
| Duplicate generation after failure | High | outbox, idempotency key, provider reconciliation |
| Unapproved claim/price | High | claim evidence allowlist + G5; price อยู่ outside scope |
| Transcript/PII exposure | High | FUNG consent/redaction + secure vault + no raw prompt logging |
| Copyright/style imitation | High | rights policy, prohibited style rules, quarantine, legal gate |
| Stale approval ถูกนำกลับมาใช้ | High | subject hash + decision expiry + resume validation |
| Metric ขาด attribution | Medium | insufficient-data state และ block auto optimization |
| Provider model drift | Medium | versioned model binding + G3 reapproval for material change |

## 13. Release Strategy

1. Shadow mode: รับ brief และสร้าง state/audit โดยไม่เรียก image provider
2. Internal pilot: asset generation ใน non-production namespace, ไม่มี publish adapter
3. Controlled pilot: หนึ่ง tenant, หนึ่ง brand profile, human gate ทุกจุด
4. Limited production: เปิดเฉพาะ provider/model/channel ที่มี approved policy
5. Expansion: เพิ่ม channel/tenant ผ่าน separate change request และ acceptance evidence

### Release-entry Conditions

Internal pilot ที่เรียก external image provider ต้องผ่าน Provider Governance Prerequisite และ PII scan ก่อน Controlled pilot ต้องผ่าน Release-entry Metric Contract เพิ่มเติม หากข้อใดไม่ครบ campaign อยู่ BLOCKED โดยไม่มี auto-advance

## 14. Open Decisions

| ID | คำถาม | Owner | บล็อกอะไร |
|---|---|---|---|
| OD-001 | MSP signing และ identity provider ที่เป็น canonical คืออะไร | MSP Owner | G0-G7 production |
| OD-002 | PersistentFlow durable store ใช้ backend ใดและ retention เท่าใด | Runtime Owner | recovery SLO |
| OD-003 | provider ใดรับข้อมูลระดับใดได้ตาม PDPA/DPA | Legal + Security | G3/image generation |
| OD-004 | C2C หมายถึง creator/referral scope ใดบ้าง | Marketing Owner | C2C workflow detail |
| OD-005 | metric/attribution SoT และ owner ต่อ channel คือใคร | Analytics Owner | G7 optimization |

| OD-006 | ยืนยัน metric definition, baseline, target, attribution และ data-quality threshold สำหรับ Controlled Pilot | Analytics Owner | Controlled Pilot |

## 15. Traceability

ID-level normative matrix อยู่ใน SRS-VAMT-001 Section 12 และต้องครอบคลุม PRD requirement ทุก ID

| PRD IDs | SRS IDs | SPEC clauses | Verification |
|---|---|---|---|
| PRD-FR-001 ถึง 004 | SRS-FR-001 ถึง 012, 020 ถึง 030 | SPEC-BRIEF, SPEC-ROLE, SPEC-GATE, SPEC-ATOM | SRS-VER-001, 002, 005, 007 |
| PRD-FR-005 ถึง 006 | SRS-FR-013 ถึง 019, 031 ถึง 035 | SPEC-EVENT, SPEC-ASSET, SPEC-GENERATION | SRS-VER-003, 008, 009 |
| PRD-FR-007, 013 | SRS-FR-037 ถึง 041 | SPEC-FUNG, SPEC-SECURITY, SPEC-AUDIT | SRS-VER-006 |
| PRD-FR-008 ถึง 012 | SRS-FR-042 ถึง 049 | SPEC-PACKAGE, SPEC-RELEASE, SPEC-PERFORMANCE, SPEC-AUDIT | SRS-VER-008, 010, 011 |
| PRD-FR-014 ถึง 018 | SRS-FR-053 ถึง 061 | SPEC-EVENT, SPEC-GATE, SPEC-GENERATION, SPEC-SECURITY | SRS-VER-012 ถึง 016 |
| PRD-NFR-001 ถึง 006 | SRS-SEC-001 ถึง 008, SRS-FR-013 ถึง 019, 028 ถึง 045 | SPEC-STATE, SPEC-EVENT, SPEC-ASSET, SPEC-FUNG, SPEC-SECURITY | SRS-VER-003 ถึง 009 |
| PRD-NFR-007 ถึง 009 | SRS-FR-050, 062, SRS-SEC-009 ถึง 010 | SPEC-GENERATION, SPEC-SECURITY, SPEC-AUTHORITY, SPEC-AUDIT | SRS-VER-011, 012, 017 |
| C2C และ canonical gate outcomes | SRS-FR-051 ถึง 052, 060 ถึง 061 | SPEC-GATE, SPEC-AUDIT | SRS-VER-016, 018 |

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.3.0b | 2026-08-10 | draft | Added PII evidence, durable side effects, result admission, quorum, gate-state and authority contracts with repaired traceability | uncommitted | ATHER |
| 0.2.0b | 2026-08-09 | draft | Fable 5 review refinement: canonical gates, C2C boundary, pilot metrics and provider/PII prerequisites | uncommitted | ATHER |
| 0.1.0b | 2026-08-09 | draft | Initial product requirements for governed durable visual marketing team | uncommitted | ATHER |
