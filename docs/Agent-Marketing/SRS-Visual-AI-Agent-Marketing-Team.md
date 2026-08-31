---
version: "0.3.0b"
created_at: "2026-08-09T18:10:00+07:00, ATHER, uncommitted"
last_update: "2026-08-10T00:10:00+07:00, ATHER"
status: "draft"
superseded_by: null
attributes:
  domain: "visual-ai-marketing"
  scope: "system-requirements"
  artifact_id: "SRS-VAMT-001"
---

# SRS — Visual AI Agent Marketing Team

## 1. Purpose

เอกสารนี้กำหนดข้อกำหนดเชิงระบบสำหรับ VAMT ตาม PRD-VAMT-001 โดยใช้คำว่า MUST/SHALL หมายถึงบังคับ, SHOULD หมายถึงข้อกำหนดที่ต้องมีเหตุผลและ approval หากไม่ทำ, และ MAY หมายถึงทางเลือกที่ไม่กระทบ invariant

ระบบเป็น workflow runtime แบบ durable และ governed ไม่ใช่ chatbot ที่สร้างภาพทันที ทุก transition, asset, knowledge reference และ human decision ต้องมี contract ที่ตรวจสอบได้

## 2. System Context และ Boundaries

~~~mermaid
flowchart LR
    UI["Visual Office UI"] --> GOV["GoVibe Control Plane"]
    GOV --> PF["PersistentFlow Runtime"]
    GOV --> MSP["MSP Decision Service"]
    PF --> GKS["GKS / GenesisBlockDB"]
    PF --> FUNG["FUNG Secure Adapter"]
    PF --> IMG["Image Provider Adapter"]
    PF --> OBJ["Immutable Object Storage"]
    PF --> ANA["Analytics / CRM SoT Adapter"]
    PF --> PUB["Publishing / CRM Handoff Adapter"]
    PF --> LEDGER["Audit Event Ledger"]
~~~

| Component | ความรับผิดชอบ | Boundary |
|---|---|---|
| Visual Office UI | submit, review, approval, operator view | ไม่มี authority bypass |
| GoVibe | governance/work tracking/context routing | ไม่เก็บ asset bytes หรือ raw PII |
| PersistentFlow | node execution, state, checkpoint, resume | ไม่ถือ canonical business truth |
| MSP | human authorization, exception, promotion mediation | ไม่สร้าง creative |
| GKS/GenesisBlockDB | knowledge identity, provenance, relation, persistence/index | ไม่ publish campaign |
| FUNG | consented speech-to-evidence | raw media อยู่ secure boundary |
| Image adapter | provider-neutral generation lifecycle | ไม่มี direct UI/provider credential exposure |
| Object storage | immutable media payload | ต้องไม่มี authority assertion อยู่ใน filename |
| SoT adapter | metric/CRM facts | VAMT ห้ามแก้ source data |
| Publishing adapter | external release/scheduling receipt | เรียกได้เมื่อ G6 passed เท่านั้น |

## 3. System-wide Invariants

| ID | Invariant |
|---|---|
| SRS-INV-001 | ทุก request ต้องมี tenant_id, campaign_id, run_id, correlation_id และ actor/principal context |
| SRS-INV-002 | ทุก asset revision, decision, event และ checkpoint เป็น append-only; การแก้ไขใช้ superseding revision |
| SRS-INV-003 | คำขอที่ไม่มี schema version หรือ schema ที่ไม่รองรับต้อง reject ก่อนทำงาน |
| SRS-INV-004 | knowledge candidate ห้ามใช้เป็น truth/prompt input เว้นแต่ policy ระบุชัดและ MSP อนุมัติ scope |
| SRS-INV-005 | external side effect ต้องมี idempotency key และ intent event ก่อนเรียก adapter |
| SRS-INV-006 | ไม่มี gate decision ที่ลงนามและตรง subject hash = ไม่มี resume/release/exception |
| SRS-INV-007 | raw PII/raw transcript/secret ห้ามอยู่ใน campaign state, model prompt log หรือ public manifest |
| SRS-INV-008 | metric ที่ไม่มี SoT source, as-of time, attribution basis และ data quality ต้องไม่ขับ optimization action |
| SRS-INV-009 | asset ที่ rights/brand/technical check ไม่ครบต้องอยู่ CANDIDATE หรือ QUARANTINED และเข้า release ไม่ได้ |
| SRS-INV-010 | live run ต้องใช้ policy/atom/model binding snapshot ที่ระบุรุ่นได้ |

## 4. Functional Requirements

### 4.1 Campaign Intake และ Knowledge

| ID | Requirement |
|---|---|
| SRS-FR-001 | ระบบ SHALL validate Campaign Brief ตาม SPEC-BRIEF ก่อนสร้าง run |
| SRS-FR-002 | ระบบ SHALL resolve GKS reference ทุกตัว, ตรวจ tenant, status, validity window และ content hash |
| SRS-FR-003 | เมื่อ reference ไม่ resolve, expired, unauthorized หรือ conflicting ระบบ SHALL transition เป็น BLOCKED พร้อม missing requirement ที่อ่านได้ |
| SRS-FR-004 | ระบบ SHALL สร้าง immutable knowledge snapshot ก่อน Visual Research เริ่ม |
| SRS-FR-005 | ระบบ SHALL แยก candidate atom จาก canonical/approved atom ใน UI และ agent context |
| SRS-FR-006 | ระบบ SHALL ไม่ promote knowledge candidate; การ promote ต้องสร้าง MSP decision และ GKS supersession event |

### 4.2 Agent Orchestration

| ID | Requirement |
|---|---|
| SRS-FR-007 | Orchestrator SHALL route งานให้ agent ตาม capability manifest และ dependency graph |
| SRS-FR-008 | agent output SHALL validate ตาม role-specific schema ก่อน merge เข้า state |
| SRS-FR-009 | agent ที่ output BLOCKED SHALL ระบุ missing references, policy หรือ authority ที่ขาด |
| SRS-FR-010 | Orchestrator SHALL ไม่ merge free-form prose เข้าสู่ authoritative campaign state |
| SRS-FR-011 | parallel execution SHALL ทำได้เฉพาะ node ที่ไม่มี write conflict และต้องใช้ isolated task state |
| SRS-FR-012 | model/provider fallback ที่มีผลต่อ brand, data class, cost หรือ reproducibility SHALL เปิด approval ใหม่ตาม G3 |

### 4.3 PersistentFlow State และ Recovery

| ID | Requirement |
|---|---|
| SRS-FR-013 | ระบบ SHALL persist a checkpoint ก่อนและหลัง node ที่มี side effect |
| SRS-FR-014 | checkpoint SHALL contain state revision, event-head hash, knowledge snapshot hash, pending gate และ in-flight operation references |
| SRS-FR-015 | runtime SHALL write NODE_INTENT ก่อนเรียก external adapter |
| SRS-FR-016 | runtime SHALL reconcile in-flight provider job ด้วย idempotency key/provider job ID ก่อน retry |
| SRS-FR-017 | recovery SHALL restore จาก last consistent checkpoint และ append recovery event; ห้าม rewrite history |
| SRS-FR-018 | ถ้า event chain/schema/state hash ไม่ผ่าน ระบบ SHALL enter MANUAL_REVIEW และ block side effect |
| SRS-FR-019 | runtime SHALL make resume idempotent เมื่อใช้ decision_id เดิม |

### 4.4 Human Gate และ MSP

| ID | Requirement |
|---|---|
| SRS-FR-020 | ระบบ SHALL เปิด G0 เมื่อ brief/data authority พร้อม และ block downstream execution จนอนุมัติ |
| SRS-FR-021 | G1/G2 SHALL protect brand applicability และ concept selection ก่อน generation binding |
| SRS-FR-022 | G3 SHALL bind provider, model, policy, cost ceiling และ approved generation scope |
| SRS-FR-023 | G4/G5 SHALL approve final visual quality, claim, disclaimer และ rights ก่อน package |
| SRS-FR-024 | G6 SHALL be mandatory ก่อน publish, schedule, CRM handoff หรือ external release |
| SRS-FR-025 | G7 SHALL be mandatory เมื่อ experiment เกิน pre-approved optimization policy |
| SRS-FR-026 | ทุก decision SHALL contain authorized principal, role, policy ref, subject hash, timestamp, signature และ expiry when applicable |
| SRS-FR-027 | subject revision หรือ policy version ที่เปลี่ยนจน invalidates scope SHALL reopen affected gate |

### 4.5 Brand, Creative และ Asset

| ID | Requirement |
|---|---|
| SRS-FR-028 | Brand Visual Guardian SHALL evaluate concept/spec/candidate against canonical brand atoms และ report rule-level findings |
| SRS-FR-029 | Brand finding SHALL have severity BLOCKER, MAJOR, MINOR หรือ ADVISORY พร้อม required resolution |
| SRS-FR-030 | BLOCKER และ MAJOR SHALL fail closed; exception ต้องผ่าน MSP and authorized human decision |
| SRS-FR-031 | Generator SHALL accept only LOCKED asset specification and active generation decision |
| SRS-FR-032 | Generator SHALL record provider/model binding, prompt/negative prompt hash, parameter hash, source asset refs, seed if available และ cost reference |
| SRS-FR-033 | Generator SHALL generate a new revision, never overwrite existing asset object |
| SRS-FR-034 | asset SHALL pass MIME, checksum, dimensions, EXIF sanitization, malware, watermark and policy checks before candidate registration |
| SRS-FR-035 | asset with unresolved right, safety or technical issue SHALL be QUARANTINED and unreachable by normal release routing |
| SRS-FR-036 | Copy-Visual Integrator SHALL use only approved copy/claim/disclaimer atoms and SHALL provide accessibility metadata |

### 4.6 FUNG, PDPA และ Sensitive Information

| ID | Requirement |
|---|---|
| SRS-FR-037 | FUNG adapter SHALL validate consent, participant scope, jurisdiction and retention policy before transcription |
| SRS-FR-038 | FUNG output SHALL be a redacted evidence package with timestamped source spans and retention expiry |
| SRS-FR-039 | transcript statement SHALL not be treated as approval without a corresponding MSP decision |
| SRS-FR-040 | raw audio, raw transcript and PII mapping SHALL stay in secure vault and SHALL not enter GKS canonical atom automatically |
| SRS-FR-041 | deletion/expiry request SHALL revoke future retrieval access and generate audit proof according to policy |

### 4.7 Packaging, Release และ Performance

| ID | Requirement |
|---|---|
| SRS-FR-042 | Packager SHALL verify each included asset, rights ref, brand decision, copy/disclaimer and required approval before manifest creation |
| SRS-FR-043 | release manifest SHALL be immutable, versioned and content-hashed |
| SRS-FR-044 | publishing adapter SHALL verify active G6 decision and scope match before external call |
| SRS-FR-045 | publishing adapter SHALL persist external receipt, timestamp, destination and correlation ID |
| SRS-FR-046 | Performance Agent SHALL ingest metrics only through approved SoT adapter |
| SRS-FR-047 | metric record SHALL include source ref, as_of, measurement window, attribution method and data-quality state |
| SRS-FR-048 | experiment proposal SHALL include hypothesis, variants, primary metric, guardrail, stop condition and approval requirement |

| SRS-FR-049 | Controlled Pilot SHALL remain blocked until an Analytics Owner-signed metric definition supplies baseline, target, measurement window, attribution method and data-quality threshold for each primary objective |
| SRS-FR-050 | G3 SHALL reject an external image-provider binding without active data-processing/right/safety approval applicable to the request data class and geography |
| SRS-FR-051 | C2C V1 SHALL accept only externally selected creator/referral partners with scoped consent and usage-rights; automated creator selection, outreach and settlement SHALL be rejected as out of scope |
| SRS-FR-052 | gate expiry and reject behavior SHALL conform to the canonical G0-G7 definitions in PRD-VAMT-001 Section 6; resume SHALL revalidate the active policy and referenced knowledge snapshot |
| SRS-FR-053 | ก่อนสร้าง intent หรือ dispatch external provider ระบบ SHALL verify PII scan evidence ที่ bind กับ canonical outgoing payload hash, data class, scanner version, policy ref/version, result, finding count, scanned_at และ expires_at |
| SRS-FR-054 | PII scan ที่ missing, expired, payload hash ไม่ตรง, result ไม่ผ่าน หรือมี unapproved finding SHALL fail closed ก่อน NODE_INTENT, GENERATION_REQUESTED และ external dispatch |
| SRS-FR-055 | side effect intent, state revision CAS, idempotency reservation และ outbox record SHALL commit ใน transaction เดียวก่อน worker dispatch |
| SRS-FR-056 | idempotency key SHALL unique ต่อ tenant, adapter, operation class และ canonical input hash; key เดิมกับ input hash ต่างกัน SHALL enter MANUAL_REVIEW โดยห้าม dispatch |
| SRS-FR-057 | dispatcher/webhook SHALL persist provider acknowledgement/result ด้วย dedupe key และ state-revision CAS; duplicate delivery SHALL return prior outcome without second state mutation |
| SRS-FR-058 | recovery SHALL classify operation เป็น ACCEPTED, PENDING, NOT_FOUND หรือ AMBIGUOUS ตาม SPEC-EVENT และ SHALL NOT create replacement operation outside that truth table |
| SRS-FR-059 | ก่อน authoritative ingest ระบบ SHALL revalidate result payload/subject hash, active gate/approval, policy version และ knowledge atom validity/supersession; stale result SHALL enter immutable quarantine และ SHALL NOT package, publish หรือ replay |
| SRS-FR-060 | G2/G5 SHALL collect immutable per-signer decisions under a versioned quorum policy and derive one aggregate hash/status with deterministic reject, revoke and expiry precedence |
| SRS-FR-061 | ทุก G0-G7 outcome SHALL use the outcome-to-state mapping in SPEC-GATE; G6 REJECT/EXPIRE SHALL return the unchanged package to READY_FOR_RELEASE |
| SRS-FR-062 | runtime SHALL persist GoVibe config snapshot ref/hash/version in every run checkpoint and audit export; GenesisBlockDB SHALL be treated only as GKS materialization/index and SHALL NOT authorize canonical mutation |

## 5. State Machine Requirements

~~~mermaid
stateDiagram-v2
    [*] --> INTAKE
    INTAKE --> PLANNING: G0 approved
    INTAKE --> BLOCKED: missing authority
    PLANNING --> WAITING_FOR_HUMAN: gate opened
    WAITING_FOR_HUMAN --> PLANNING: G1/G2 approved
    PLANNING --> GENERATING: G3 approved
    GENERATING --> REVIEWING: candidates registered
    REVIEWING --> WAITING_FOR_HUMAN: G4/G5 opened
    WAITING_FOR_HUMAN --> PACKAGING: G4/G5 approved
    PACKAGING --> READY_FOR_RELEASE: manifest complete
    READY_FOR_RELEASE --> WAITING_FOR_HUMAN: G6 opened
    WAITING_FOR_HUMAN --> LIVE: G6 approved
    LIVE --> OPTIMIZING: verified performance available
    OPTIMIZING --> GENERATING: G7 experiment approved
    OPTIMIZING --> CLOSED: no further action
    BLOCKED --> PLANNING: missing requirement resolved
    GENERATING --> RECOVERING: runtime or provider fault
    RECOVERING --> GENERATING: reconciled
    RECOVERING --> MANUAL_REVIEW: integrity failure
    MANUAL_REVIEW --> PLANNING: owner remediation
    CLOSED --> [*]
~~~

Allowed transitions must be defined in SPEC-STATE. Any unlisted transition SHALL be rejected and audit logged.

## 6. Data Requirements

### 6.1 Data Classification

| Class | Examples | Storage and log rule |
|---|---|---|
| Public | approved public campaign asset | manifest/object store under tenant namespace |
| Internal | brand token, concept, approved copy | GKS/object store; least privilege |
| Confidential | commercial strategy, unreleased campaign | encrypted, role-scoped; never sent to unauthorized provider |
| Restricted | PII, raw audio, transcript, credentials | secure vault/secret manager only; no generic event/prompt log |

### 6.2 Retention

1. Event/decision/asset manifest retention MUST follow audit policy and legal hold.
2. Raw FUNG media MUST follow consent/retention atom and be unavailable after expiry.
3. Quarantined artifact retention MUST preserve minimum forensic evidence but not enable reuse.
4. Purge MUST create an auditable tombstone, not silently delete reference history.
5. A valid consent/retention atom MUST define a retention duration, deletion authority, legal-hold exception and deletion-evidence format before ingestion is accepted.

## 7. Interface Requirements

| Interface | Required behavior |
|---|---|
| GKS resolver | resolve immutable atom version/status/hash and return no secret content |
| MSP decision service | validate principal, policy, scope and signature; issue immutable decision ref |
| PersistentFlow persistence | save/load checkpoint atomically with revision and event head |
| Image provider adapter | accept idempotency key; expose job status/retrieve-by-key; return provider version/cost when available |
| FUNG adapter | require consent ref; redact before returning evidence package |
| Object store | immutable object keys, versioning, checksum, encryption and lifecycle |
| SoT analytics adapter | return source-stamped metric snapshots, never unqualified raw numbers |
| Publishing adapter | verify release decision, perform one side effect, return receipt/reconciliation state |

Exact request/response contracts are declared in SPEC-VAMT-001.

## 8. Security Requirements

| ID | Requirement |
|---|---|
| SRS-SEC-001 | Authorization SHALL be enforced server side in every adapter, not only UI |
| SRS-SEC-002 | Secrets SHALL be sourced from secret manager and redacted from logs/errors |
| SRS-SEC-003 | All durable stores and object storage SHALL encrypt in transit and at rest |
| SRS-SEC-004 | Provider access SHALL be data-class-aware and tenant-scoped |
| SRS-SEC-005 | Decision signature SHALL be bound to exact subject hash and policy scope |
| SRS-SEC-006 | Audit log SHALL be tamper-evident through chained hashes or equivalent verifiable integrity |
| SRS-SEC-007 | UI asset review SHALL not expose raw transcript, provider secret or cross-tenant URI |
| SRS-SEC-008 | Asset uploads/reference images SHALL undergo rights and malware validation before provider use |
| SRS-SEC-009 | Prompt logs, event projections and package manifests SHALL pass an automated PII scan before Controlled Pilot/release; unapproved finding SHALL block the relevant transition |
| SRS-SEC-010 | GoVibe configuration, MSP decisions, GKS atoms and GenesisBlockDB projections SHALL be tenant-scoped and authority-separated; projection mismatch SHALL fail closed and audit log |

## 9. Reliability, Performance และ Observability

### 9.1 Service Targets

ตัวเลขเป้าหมายต้องกำหนดหลัง capacity test และ provider SLA review; requirements ที่บังคับก่อนกำหนดตัวเลขมีดังนี้

| Area | Requirement |
|---|---|
| Durability | committed checkpoint และ signed decision ต้องไม่สูญหายเมื่อ worker restart |
| Idempotency | duplicate external asset/publish request ต้องไม่สร้าง side effect ใหม่ |
| Integrity | hash mismatch ต้อง fail closed และเปิด manual review |
| Visibility | operator เห็น run phase, in-flight job, pending gate, retry count และ recovery reason |
| Degradation | provider timeout ต้อง state เป็น WAITING_EXTERNAL/RECOVERING ไม่ใช่ FAILED เงียบ ๆ |

### 9.2 Required Observability Events

- CAMPAIGN_CREATED
- KNOWLEDGE_SNAPSHOT_BOUND
- NODE_INTENT
- NODE_COMPLETED
- NODE_FAILED
- CHECKPOINT_COMMITTED
- GATE_OPENED
- HUMAN_DECISION_ACCEPTED
- GENERATION_REQUESTED
- GENERATION_RECONCILED
- ASSET_QUARANTINED
- PACKAGE_CREATED
- RELEASE_REQUESTED
- RELEASE_RECEIPT_RECORDED
- RECOVERY_STARTED
- RECOVERY_COMPLETED
- INCIDENT_OPENED

## 10. Error Handling และ Recovery

| Condition | Required state/action |
|---|---|
| missing atom/permission | BLOCKED, no downstream node |
| invalid agent output | NODE_FAILED, preserve raw output in secured diagnostic store, no state merge |
| provider timeout | WAITING_EXTERNAL then reconcile; no blind re-create |
| provider duplicate webhook | deduplicate by provider job/receipt ID |
| stale/expired approval | WAITING_FOR_HUMAN with new gate |
| asset safety/right failure | QUARANTINED |
| object checksum mismatch | MANUAL_REVIEW, freeze release |
| state/event integrity mismatch | MANUAL_REVIEW, start incident |
| analytics source unavailable | INSUFFICIENT_DATA, block optimization action |

## 11. Verification Requirements

| ID | Verification |
|---|---|
| SRS-VER-001 | contract tests for all schemas and negative inputs |
| SRS-VER-002 | role prompt tests that prove scope boundaries and BLOCKED behavior |
| SRS-VER-003 | recovery tests at every external side-effect boundary |
| SRS-VER-004 | authorization and cross-tenant isolation tests |
| SRS-VER-005 | golden brand tests for logo, palette, safe zone, prohibited visual and claim checks |
| SRS-VER-006 | FUNG consent/redaction/expiry integration tests |
| SRS-VER-007 | release gate bypass/adversarial tests |
| SRS-VER-008 | audit replay from event ledger to final manifest |
| SRS-VER-009 | load/chaos test for concurrent gate resume, provider webhook and worker restart |
| SRS-VER-010 | human acceptance test with Marketing, Brand, Legal and Runtime owners |
| SRS-VER-011 | Controlled Pilot release check proves active DPA/data-processing approval, successful request-path PII scan and signed metric definition contract |
| SRS-VER-012 | request-path PII tests mutate payload/hash/data class/scanner policy/time and prove every mismatch blocks before intent and dispatch |
| SRS-VER-013 | crash-point tests cover transaction commit, dispatch, provider accept, ack persist and webhook replay with zero duplicate side effect/state ingest |
| SRS-VER-014 | recovery truth-table tests cover ACCEPTED, PENDING, NOT_FOUND and AMBIGUOUS including idempotency hash conflict |
| SRS-VER-015 | stale admission tests revoke/expire gate, policy and atom after dispatch and prove immutable quarantine with no package/replay reachability |
| SRS-VER-016 | concurrent G2/G5 signing tests prove quorum, partial state, reject precedence, revocation, expiry and duplicate signature idempotency |
| SRS-VER-017 | authority tests prove GenesisBlockDB cannot promote/mutate GKS truth and replay binds the original GoVibe config snapshot |
| SRS-VER-018 | table-driven tests cover APPROVE, REJECT, EXPIRE and REQUEST_REVISION for G0-G7 and validate every resulting lifecycle transition |

## 12. Requirement Traceability Matrix

| PRD ID | SRS requirements | SPEC clauses | Verification ID |
|---|---|---|---|
| PRD-FR-001 | SRS-FR-001 ถึง 006 | SPEC-BRIEF, SPEC-ATOM | SRS-VER-001, 002 |
| PRD-FR-002 | SRS-FR-007 ถึง 010 | SPEC-ROLE, SPEC-EVENT | SRS-VER-002, 008 |
| PRD-FR-003 | SRS-FR-019 ถึง 027 | SPEC-GATE, SPEC-EVENT | SRS-VER-007, 009, 018 |
| PRD-FR-004 | SRS-FR-028 ถึง 030 | SPEC-ROLE, SPEC-ATOM | SRS-VER-005 |
| PRD-FR-005 | SRS-FR-031 ถึง 035 | SPEC-ASSET, SPEC-GENERATION | SRS-VER-001, 005 |
| PRD-FR-006 | SRS-FR-013 ถึง 019, 055 ถึง 058 | SPEC-EVENT | SRS-VER-003, 009, 013, 014 |
| PRD-FR-007 | SRS-FR-037 ถึง 040 | SPEC-FUNG, SPEC-SECURITY | SRS-VER-006 |
| PRD-FR-008 | SRS-FR-042 ถึง 045 | SPEC-PACKAGE, SPEC-RELEASE | SRS-VER-007, 008 |
| PRD-FR-009 | SRS-FR-046 ถึง 047, 049 | SPEC-PERFORMANCE | SRS-VER-010, 011 |
| PRD-FR-010 | SRS-FR-048 | SPEC-PERFORMANCE, SPEC-GATE | SRS-VER-010, 018 |
| PRD-FR-011 | SRS-FR-018, 035, 058 ถึง 059 | SPEC-STATE, SPEC-EVENT | SRS-VER-003, 014, 015 |
| PRD-FR-012 | SRS-SEC-006, SRS-FR-043, 045, 062 | SPEC-AUDIT | SRS-VER-008, 017 |
| PRD-FR-013 | SRS-FR-037 ถึง 041 | SPEC-FUNG, SPEC-AUDIT | SRS-VER-006 |
| PRD-FR-014 | SRS-FR-053 ถึง 054 | SPEC-GENERATION, SPEC-SECURITY | SRS-VER-012 |
| PRD-FR-015 | SRS-FR-055 ถึง 058 | SPEC-EVENT | SRS-VER-013, 014 |
| PRD-FR-016 | SRS-FR-059 | SPEC-EVENT, SPEC-ATOM, SPEC-GATE | SRS-VER-015 |
| PRD-FR-017 | SRS-FR-060 | SPEC-GATE | SRS-VER-016 |
| PRD-FR-018 | SRS-FR-052, 061 | SPEC-GATE, SPEC-STATE | SRS-VER-018 |
| PRD-NFR-001 | SRS-SEC-001, 004, 010 | SPEC-STATE, SPEC-SECURITY, SPEC-AUTHORITY | SRS-VER-004, 017 |
| PRD-NFR-002 | SRS-FR-013 ถึง 019, 055 ถึง 059 | SPEC-EVENT, SPEC-STATE | SRS-VER-003, 009, 013 ถึง 015 |
| PRD-NFR-003 | SRS-FR-003, 018, 035, 058 ถึง 059 | SPEC-STATE, SPEC-EVENT | SRS-VER-003, 014, 015 |
| PRD-NFR-004 | SRS-FR-014, 032 ถึง 034, 042 ถึง 045 | SPEC-ASSET, SPEC-AUDIT | SRS-VER-005, 008 |
| PRD-NFR-005 | SRS-FR-003, 018, 030, 035, 050, 054, 059 | SPEC-14, SPEC-SECURITY | SRS-VER-001, 007, 012, 015 |
| PRD-NFR-006 | SRS-FR-040, SRS-SEC-002, 007, 009 | SPEC-FUNG, SPEC-SECURITY | SRS-VER-004, 006, 012 |
| PRD-NFR-007 | SRS-FR-053 ถึง 054, SRS-SEC-009 | SPEC-GENERATION, SPEC-SECURITY | SRS-VER-011, 012 |
| PRD-NFR-008 | SRS-FR-050, 053 ถึง 054 | SPEC-GENERATION, SPEC-SECURITY | SRS-VER-011, 012 |
| PRD-NFR-009 | SRS-FR-062, SRS-SEC-010 | SPEC-AUTHORITY, SPEC-AUDIT | SRS-VER-017 |
| C2C V1 boundary | SRS-FR-051 | SPEC-GATE, SPEC-AUDIT | SRS-VER-010, 018 |

## 13. Approval Criteria

เอกสาร SRS นี้ผ่าน review ได้เมื่อ:

1. ทุก P0 requirement มี implementation owner, test owner และ acceptance evidence plan
2. OD-001 ถึง OD-005 ใน PRD มี owner และ target decision date
3. MSP, GKS, PersistentFlow, FUNG และ provider contract ถูกตรวจเทียบกับ implementation จริง
4. ไม่มี requirement ใดอนุญาตให้ agent bypass policy/gate หรือ mutate canonical truth
5. Security/PDPA/Legal review ยืนยัน data classification และ provider data-processing boundary

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.3.0b | 2026-08-10 | draft | Added durable side-effect, result admission, quorum, authority and complete ID-level verification traceability | uncommitted | ATHER |
| 0.2.0b | 2026-08-09 | draft | Added pilot-release, provider approval, C2C boundary, retention and PII scan requirements | uncommitted | ATHER |
| 0.1.0b | 2026-08-09 | draft | Initial system requirements and traceability for VAMT | uncommitted | ATHER |
