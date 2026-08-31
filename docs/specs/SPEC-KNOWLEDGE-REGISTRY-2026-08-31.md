---
version: "0.1.2b"
created_at: "2026-08-31T00:09:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T03:10:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "knowledge-provenance"
  doc_type: "specification"
  scope: "document, picture, media, attachment registry and retrospective source lineage"
  language: "th"
---

# SPEC — Knowledge Registry / ลงทะเบียนย้อนหลังและสืบย้อนแหล่งข้อมูล

**สถานะ:** Approved / beta — Boss อนุมัติ frozen manifest; P2 pilot publish และตรวจครบตาม §13 แล้ว ส่วน P3 ยังไม่ทำ
**Complexity / Risk:** C-3 / HIGH<br>
**Decision:** [ADR-007](../decisions/ADR-007-KNOWLEDGE-REGISTRY-AND-PROVENANCE.md)<br>
**Authority:** [GenesisBlock schema](../../config/schema_genesisblock.yaml), [AGENTS](../../AGENTS.md), [ADR-004](../decisions/ADR-004-CUSTOMER-SAFE-PRICELIST-ENDPOINT.md), [ADR-005](../decisions/ADR-005-FACTORY-COST-INTAKE-LANE.md), [ADR-006](../decisions/ADR-006-PRIVATE-REPOSITORY-SOURCE-DATA-EXCEPTION.md)

## 1. ผลลัพธ์ที่ผู้ใช้ต้องได้

- ค้น `doc_id` แล้วเห็นไฟล์ต้นฉบับ ทุก version/location และภาพ/สื่อ/attachment ที่มาจากเอกสารนั้น
- ค้น `pic_id` หรือ `media_id` แล้วเห็น source version, page/sheet/cell/time range, วิธี extract/transform และรายการที่นำไปใช้
- ค้นแถวต้นทุนหรือค่ากำไรแล้วเดินกลับไปหาแถว prepared, source workbook และ source locator จริงได้; หาก locator ยังไม่มี ต้องเห็น `source_locator_missing`
- แยก “มีข้อมูลในแหล่ง” / “ลงทะเบียนแล้ว” / “สกัดแล้ว” / “มีหลักฐานตำแหน่ง” / “จับคู่แล้ว” / “อนุมัติใช้แล้ว” อย่างอิสระ
- Coverage ครอบคลุม source inventory แม้ไม่มี SRP หรือไม่มี ProductMaster mapping; 1,166 records ไม่ถูกย่อเหลือ 9 records อีก

[ASSUMPTIONS]

1. ข้อความที่พิมพ์สลับภาษาในคำขอหมายถึงการไล่ลงทะเบียนย้อนหลังเพื่อทราบที่มาข้อมูล
2. `pic_id` หมายถึง picture ไม่ใช่ Person In Charge; รุ่นนี้ไม่สร้างทะเบียนบุคคล
3. รุ่นแรกอยู่ใน SmartGift workspace, เป็น local/internal metadata, ไม่ย้ายต้นฉบับ ไม่เชื่อม cloud/CRM อัตโนมัติ
4. เอกสารต้นทุน/ภาพเดิมคงสิทธิ์เข้าถึงเดิม; การสร้างทะเบียนไม่อนุมัติการเผยแพร่หรือ commercial use

## 2. Current-state evidence และสิ่งที่ยังขาด

| แหล่งที่ตรวจ | สิ่งที่มี | สิ่งที่ registry ต้องเติม |
|---|---|---|
| exports_registry.json | 4 entries/4 versions; มีข้อมูลที่ต้องแยก CRM ก่อน | bridge legacy identity โดย import เฉพาะ records ที่ผ่าน classification |
| pricing_formula_registry.json | 1 entry/1 version, hash/archive | doc/version identity และ lineage ของสูตร |
| factory_cost_registry.json | 3 entries/3 versions, hash/size/archive/sheets | stable doc IDs, locations, bridge version_id เดิม |
| factory_costs.json | 1,166 records / 1,152 priced; source_file 1,166, sheet 64, row/cell 0 | evidence identity ต่อ source record, ตำแหน่งจริงเมื่อพิสูจน์ได้ |
| catalog_media.json | sets 153 + products 6 + hero | IDs/attachment occurrences; อย่านับจำนวน refs ว่าเป็น unique pics |
| production-manifest + image-first spec | provenance ภาพกระจายใน source/page/code/object/hash | structured verified links, preserve conflicts/generated flags |
| schema_genesisblock.yaml | catalog ontology 1.3.0 | registry namespace ที่ผ่าน review; ไม่แทน catalog IDs |
| package.json + seed_genesisblock.mjs | ใช้ GenesisBlockDB native binding เดิม | capability test ของ registry adapter; ไม่อนุมาน Cypher/transaction support |

ฐานไฟล์นี้เป็น evidence snapshot จาก checkout ณ 2026-08-31 ไม่อ้างว่า source สภาพนี้จะคงเดิมในวัน backfill ต้อง freeze path/hash/size ใหม่ก่อนรันจริง

## 3. Entity และ ID contract ที่เสนอ

### 3.1 IDs ที่ผู้ใช้ขอ

| Entity | Primary field | รูปแบบเสนอ | identity / version rule |
|---|---|---|---|
| Document | doc_id | doc:<UUIDv7> | logical document: PDF/XLSX/XLS/CSV/JSON/MD/DOCX ฯลฯ; เปลี่ยน bytes ไม่เปลี่ยน logical ID |
| Picture | pic_id | pic:<UUIDv7> | ภาพนิ่ง; source photo, crop, resized และ generated แยก origin/derivation |
| Media | media_id | media:<UUIDv7> | audio/video; เก็บ metadata duration/tracks ถ้าพิสูจน์ได้ |
| Attachment | attachment_id | att:<UUIDv7> | หนึ่งการแนบใน owner version + locator/role + target version; หลายหน้าหรือหลายเจ้าของ = หลาย IDs |

Document/Picture/Media มี AssetVersion; Attachment เป็น occurrence ที่ pin owner/target versions ไม่สร้างสำเนาไฟล์ และไม่ต้องมี version chain อีกชุด การแก้ binding ต้องสร้าง occurrence ใหม่พร้อม supersedes event ไม่ rewrite ประวัติเดิม

### 3.2 Supporting records

| Entity / prefix | หน้าที่ / required fields เพิ่มจาก common scope |
|---|---|
| AssetVersion / ver: | owner_asset_id, sha256 เต็ม 64 hex, size_bytes, detected_mime, observed_at, ordinal; version_id pin bytes หนึ่งชุด |
| FileLocation / loc: | workspace-relative path หรือ source URI ที่มีหลักฐาน, storage_scope, first_seen_at, last_seen_at, availability; ไม่ฝัง credentials ใน URI |
| ProcessingRun / run: | operation, implementation/version หรือ unknown, configuration_sha256 ถ้ามี, input version refs, started/finished time ที่ทราบ, status |
| EvidenceRecord / ev: | record_kind, prepared/source locator, source record key ที่พิสูจน์ได้, evidence_status; ไม่เก็บ customer rows หรือสร้างราคาใหม่ |
| CatalogEntityReference / eref: | target_entity_type, target_vault_id, canonical_id หรือ null, business_code หรือ null, resolution_status, authority_schema_hash |

CatalogEntityReference เป็น pointer ไม่ใช่ ProductMaster/CatalogOffer อีกสำเนา Canonical ID ต้อง resolve จาก authority จริง; business code อย่าง PM-TMB หรือ code ในภาพไม่ถูกแปลงเป็น canonical primary key โดยคาดเดา unresolved refs เก็บเพื่อ review แต่ห้ามใช้เป็น verified product binding

**Common scope:** tenant_id=`Org-EtohGroup`, business_id=`SmartGift`, registry_contract_version, registered_at, updated_at, classification, lifecycle_status, access_scope_ref<br>
**เวลา:** registered_at เป็นเวลาลงทะเบียนจริงวันนี้; source_created_at/ingested_at เป็นเวลาที่มีหลักฐานและอาจ null ห้ามย้อน UUID/เวลาให้ดูเหมือนลงทะเบียนตั้งแต่อดีต<br>
**Content vs file:** bytes เดียวกันมี SHA-256 เดียวกัน แต่ไม่รวม logical assets, supplier identity, product model หรือสิทธิ์ใช้ไฟล์เอง

### 3.3 Idempotency และ duplicate policy

- Persist identity_map: (scope, source-system namespace, trusted provider object ID / legacy alias / normalized local origin key) → logical asset ID
- ใช้ legacy registry + archive history ยืนยัน current/archive ว่าเป็น version เดียวกัน; ถ้าพิสูจน์ไม่ได้ให้ candidate_duplicate แม้ hash เท่ากัน
- Version uniqueness: (scope, owner_asset_id, full_sha256); observed locations แยกจาก version และประวัติการพบ path
- Attachment uniqueness: (scope, owner_version_id, normalized locator, attachment role, target_version_id)
- Evidence uniqueness: (scope, source_version_id, locator, record_kind, extractor contract version); ไม่มี locator ที่เสถียรใช้ prepared JSON pointer ที่ pin hash พร้อมสถานะ partial ไม่ใช้ SKU เป็น row primary key
- รัน manifest เดิมซ้ำต้องได้ IDs/edges เดิม; no-op run ไม่สร้าง version/attachment เพิ่ม แม้มี audit event ของการตรวจซ้ำ
- รูปเหมือนกันจากหลายเอกสารไม่แปลว่าเป็นสินค้ารุ่นเดียวกัน; exact-byte duplicates กับ semantic candidates เป็นคนละสถานะ
- ย้าย/rename path ไม่ทำเอง ถ้ามีการย้ายที่อนุมัติแล้ว บันทึก alias/move evidence โดยคง ID; path reuse ที่ไม่ทราบว่าเอกสารเดิมหรือไม่ต้อง review
- UUID collision หรือ unique-key conflict ต้อง fail closed ไม่ merge/overwrite เงียบ ๆ; รองรับ single-writer lock

## 4. Graph contract

ความสัมพันธ์เป็น typed edges แยกจาก node arrays; JSON export อาจมี list เพื่อแสดงผลได้ แต่ writer/query ต้องตรวจ endpoint types และ scope

| Edge | Source → Target | ข้อกำหนด |
|---|---|---|
| HAS_VERSION | Document/Picture/Media → AssetVersion | version มี owner เดียว |
| STORED_AT | AssetVersion → FileLocation | มี observed hash/time; หนึ่ง path มีหลาย version ตามเวลาได้ |
| HAS_ATTACHMENT | AssetVersion → Attachment | owner version ต้องมีอยู่ |
| ATTACHES_VERSION | Attachment → AssetVersion | pin target bytes/version ไม่ใช้ latest โดยนัย |
| GENERATED_BY | AssetVersion/EvidenceRecord → ProcessingRun | ใช้เมื่อทราบ process จริง; historical unknown ไม่แต่ง model/tool |
| USED_INPUT | ProcessingRun → AssetVersion | input versions pin hash |
| DERIVED_FROM | AssetVersion → AssetVersion | crop/render/convert/generated output → input; ไม่มี self/cycle |
| EXTRACTED_FROM | EvidenceRecord → AssetVersion | มี locator + evidence level; prepared row ไม่อ้างว่าเป็น raw Excel cell |
| DEPENDS_ON | EvidenceRecord → EvidenceRecord | เช่นกำไรขึ้นกับราคา, ทุน, FX; ทุก input ต้องอ้างอิงได้และ graph ไม่มี cycle |
| ABOUT_ENTITY | EvidenceRecord → CatalogEntityReference | verified link ต้องมี authority-resolved canonical ID |
| ILLUSTRATES | AssetVersion(kind=picture) → CatalogEntityReference | ต้องตรวจ source code/target และ visual evidence; generated ไม่เท่ากับ source-photo |

```text
Document(doc_id) ──HAS_VERSION──> source version ──STORED_AT──> raw/archive path
                                      │
                                      ├─HAS_ATTACHMENT─> attachment_id ─ATTACHES_VERSION─> picture version
                                      │                                                       ▲
                                      │                                          Picture(pic_id)─HAS_VERSION
                                      │
EvidenceRecord(ราคา/แถว) ─EXTRACTED_FROM┘
           │
           └─ABOUT_ENTITY─> CatalogEntityReference ── logical reference ──> canonical pm:/offer:

EvidenceRecord(กำไร) ─DEPENDS_ON─> EvidenceRecord(ราคาขาย / ทุน / สูตร / FX)
output version ─GENERATED_BY─> run ─USED_INPUT─> exact input versions
```

Logical reference สุดท้ายไม่ใช่ cross-vault physical edge หรือการ copy ProductMaster เข้า registry; ตัว reader resolve ตาม scope และตรวจ schema ก่อนเสมอ

## 5. Source locator และระดับความน่าเชื่อถือ

Locator เป็น tagged object; validate type และพิกัดตาม parent MIME:

| kind | ตัวระบุตำแหน่ง |
|---|---|
| file | version_id + whole-file scope; ใช้ได้แต่ไม่ใช่ row-level proof |
| pdf | page_number (1-based), object_ref/xref ถ้ามี, bbox พร้อม unit/origin/page dimensions/rotation |
| spreadsheet | sheet_name ตามจริง, row_number (1-based), cell_ref/range เช่น E42; ระบุ formula/value mode |
| spreadsheet_picture | sheet_name, OOXML media part + drawing relationship/anchor หรือหลักฐาน BIFF ที่รองรับจริง |
| json | JSON pointer + parent file version hash; pointer เดิมใน bytes คนละ version ถือเป็นคนละหลักฐาน |
| text | line_start/line_end (1-based) หรือ character offsets + encoding ที่ประกาศ |
| media_time | time_start_ms/time_end_ms, track/channel หากทราบ |
| embedded_file | container member path / relationship ID พร้อม sanitized path ไม่ extract traversal path |

**สถานะแยกกัน:** registration_status (registered/blocked), locator_status (file_only/prepared_record_only/exact/unknown), identity_status (unresolved/candidate/confirmed/conflict), source_integrity (verified/missing/hash_mismatch), usage_rights (unknown/internal_only/approved_for_public), visual_origin (source_photo/crop/render/generated/unknown)

คำว่า registered ไม่เปลี่ยน candidate เป็น confirmed และคำว่า exact locator ไม่ยืนยันว่าใช้ภาพเพื่อการค้าได้

- ราคา EXW ทั้งชุดไม่ใช่ราคาชิ้นส่วน; evidence ต้องเก็บ unit/currency/basis ที่ source กล่าว ไม่แยกทุน BOM เอง
- 14 cost records ไม่มีราคาเป็นหลักฐาน source missing ไม่แทน 0 และไม่ลบ record
- USB shell/chip/capacity เป็นคนละ evidence records; การประกอบ 84 บาทต้อง DEPENDS_ON inputs ที่ยืนยัน ไม่เอาราคา chip เป็นราคาสินค้าสำเร็จ
- Generated picture บันทึก model/version/prompt reference เท่าที่มีหลักฐาน ไม่เก็บ prompt ที่มี PII/secrets และไม่ใช้ภาพ generated ยืนยัน physical product
- row/page/cell ที่ขาดเป็น null พร้อม reason; การเก็บ legacy reference ไม่ยืนยันว่าต้นทางยังเปิดอ่านได้

## 6. Storage, consistency และ query boundary

### 6.1 ที่เก็บตามสัญญา (runtime และ P2 pilot publish แล้ว)

```text
config/schema_genesisblock.yaml
  registry_contract / registry_node_ontology / registry_edge_ontology   [proposed isolated sections]

data-pipeline/00_knowledge_registry/
  generations/<generation_id>/
    nodes.jsonl
    edges.jsonl
    identity_map.jsonl
    manifest.json                # contract hash, inputs, counts, checksums
  CURRENT                        # atomic reference to validated generation
  audit/events.jsonl             # scope-safe events, no raw PII/payload

vaults/vlt-knowledge-registry/genesis-db/
  <engine-managed projection of one validated generation>

data-pipeline/04_review_reports/
  knowledge-registry-backfill-<run_id>.json  # internal audit
```

- Ledger generation + identity_map เป็น canonical registration state; ไม่มี graph-only mutations
- Stage candidate generation แยก, validate ทุก file/ref/hash, publish CURRENT แบบ atomic ภายใต้ writer lock ที่ตรวจแล้ว; filesystem ที่รองรับ atomicity ไม่ได้ต้องหยุดก่อน publish
- Graph โหลดจาก immutable generation และประกาศ projected_generation_id; ห้ามเสิร์ฟผลว่า current ถ้า generation ไม่ตรง ให้ stale/unavailable ชัดเจน
- Graph atomic swap/rebuild เป็น capability gate ของ engine ที่ต้องทดสอบ ห้ามสมมติจากการมี addNode/addEdge
- Rollback ด้วยการเลือก prior validated generation และ rebuild projection; ไม่ลบ raw, ไม่ rewrite audit หรือ reuse retired IDs
- เก็บ checksum/checkpoint ตรวจ audit integrity ได้ แต่ไม่อ้างว่า local files เป็น tamper-proof/WORM
- Registry outputs และ vault ใหม่ต้อง ignore จาก Git โดย default และอยู่ใน deployment denylist ก่อนเขียนข้อมูลจริง; การ push/export ต้องมี scope review แยก

### 6.2 Queries ที่ต้องรองรับ

| Query contract | ผลลัพธ์ |
|---|---|
| lookup_asset(id, scope) | identity, pinned/current version ที่ระบุชัด, locations, availability |
| trace_origin(id, scope, depth<=6) | bounded backward path พร้อม exact/partial/conflict และ source locators |
| find_usages(id, scope, depth<=6) | forward consumers/evidence/attachments ที่เข้าถึงได้ |
| list_attachments(doc_version_id, cursor, limit<=100) | รูป/สื่อ/เอกสารแนบของ document version นั้น |
| audit_coverage(run_id, scope) | registered/excluded/blocked/orphan/missing locator/candidate mapping แยกจำนวน |

ค่าเริ่มต้น depth=4, สูงสุด 6; limit node=500, edge=1,000, page=100 และ time budget=1,000 ms เป็นข้อกำหนดการออกแบบที่ต้องทดสอบ ไม่ใช่ benchmark ปัจจุบัน ผลที่ถูกตัดต้อง `truncated=true` + reason/cursor ไม่ตีความว่าไม่มี source

Indexes/validation keys: scoped node ID; scoped version owner+sha256; normalized location; legacy identity key; typed adjacency ทั้งสองทิศ; source locator; canonical target ref ไม่ใช้ unbounded full graph scan หรือรวมทุก asset ไว้ที่ supernode เดียว สำหรับ engine ที่ไม่มี unique/composite index ต้องมี validated writer-side indexes และ parity tests ไม่กล่าวว่า engine enforce แล้ว

## 7. Backfill phases และ reconciliation

| Phase | งานหลังอนุมัติ | Gate |
|---|---|---|
| P0 — contract + capability | ตรวจ consumers ของ YAML, prototype read/write/query ใน temporary isolated DB, idempotency/lock/recovery tests | ไม่เปิด product/customer vault, ไม่เรียก embeddings; capability ไม่ผ่านต้องหยุด graph phase |
| P1 — frozen inventory | เลือก allowlist ตาม content classification, hash/size/MIME/legacy refs, ทำ dry-run plan | counts/file hashes/review status ชัด; user review manifest ก่อน publish |
| P2 — registry pilot | register 3 cost docs + same-version archives เป็น locations, ทั้ง 1,166 cost records; register media references ที่ผ่าน classification โดยไม่เดา mapping | preserve duplicates/missing prices; IDs stable; no source modifications |
| P3 — exact evidence backfill | เพิ่ม adapters เพื่อเก็บ Excel row/cell, PDF page/object/bbox, existing output image hashes และ processing lineage | reconcile extracted values และภาพต่อ version; ambiguous/mismatch เข้า review |
| P4 — wider registry | ขยายเอกสาร/สื่อ non-PII อื่นใน workspace ตาม manifest ที่ตรวจแล้ว | ไม่มี implicit cloud fetch/CRM ingest/public publish; unknown source ไม่หายจาก coverage summary |

ทุก phase ใช้ source-first inventory ไม่เริ่มจาก SRP/approved PM subset:

1. อ่าน legacy registries เป็น bridge; ไม่เรียก archivers/orchestrator เดิมที่อาจเขียน archive, database หรือ audit ของงานอื่น
2. ตรวจ raw file SHA-256 กับ registry; mismatch/missing/corrupt file เป็น blocked ไม่ใช้ latest มาทับประวัติเดิม
3. แยกจำนวน physical files, logical assets, versions, unique content hashes, attachment occurrences และ evidence rows
4. Freeze รายการ file paths/hash เป็น approval manifest; detect symlink/junction escape และ path traversal ก่อนอ่านตาม reference
5. ตรวจ format โดยไม่ execute workbook macros/PDF scripts/embedded executables; ไม่ตาม external links ภายในเอกสาร
6. ลงทะเบียน snapshot ที่ผ่าน scope; ไม่แก้หรือย้ายต้นฉบับ เก็บ old path/legacy version ID เป็น aliases
7. รายงาน reconciliation: input total = eligible + excluded_by_policy + blocked; eligible = registered + failed; registered lineage = exact + partial + orphan (กลุ่มไม่ซ้ำ)
8. สำหรับ known factory baseline ตรวจ expected records 1,166 / priced 1,152 / missing price 14 แต่ต้องตรวจใหม่ถ้า source hash เปลี่ยน; ไม่อ้าง unique product models จากจำนวนนี้
9. สินค้า/ภาพที่ไม่มี canonical mapping ลงทะเบียนได้ แต่ `ABOUT_ENTITY/ILLUSTRATES` ไม่ได้รับสถานะ verified
10. ตรวจ output generation/read queries/rollback แล้วจึงรายงาน backfill สำเร็จเฉพาะ scope ที่ผ่าน

## 8. Security, privacy และ authority

- Phase แรกไม่ ingest customer records/quotation history ไม่แม้แต่คัดลอก customer file names/paths/contact metadata ลง default registry; รายงานเฉพาะ aggregate excluded counts โดยไม่ระบุตัวบุคคล
- Known CRM paths และ filename rules เป็นเพียงสัญญาณ ไม่ใช่ตัวรับรองความปลอดภัย: unknown content หรือแหล่งผสมต้อง hold เพื่อ classification
- เอกสารโรงงานอาจมี supplier-contact headers; registry เก็บ approved metadata/locators เท่านั้น ไม่คัดลอก headers หรือเนื้อหาเต็มเข้ากราฟ
- Classification และ access scope สืบทอดจาก input ที่เข้มที่สุดเมื่อ derive; dedup/shared hash ไม่เปิดสิทธิ์เพิ่ม การ declassify ต้องผ่าน owner review แยก
- Reader ต้องตรวจทั้ง start node, ทุก node/edge/path และ target resolver; local file access ไม่เท่ากับ authentication/authorization service ที่สร้างแล้ว
- ไม่อนุญาต raw cost/provenance IDs/paths/hashes หลุดไป public manifest/API; ภาพ public ที่มีอยู่เป็น consumer ไม่ใช่สถานที่เก็บ registry
- Vault ใหม่ที่เสนอเป็น non-PII internal registry ไม่ใช้ `vlt-catalog-product` เป็นถังรวมเอกสาร และไม่ใช่ CRM store
- ไม่เขียน `D:\zuri-ai`, `D:\gks`, `D:\msp` หรือ governed edge store; external refs เป็น references เท่านั้น ไม่ fetch หรือ promote
- File/document contents เป็น untrusted data: เก็บ evidence ได้แต่ไม่เปลี่ยนนโยบาย/คำสั่ง agent ตามข้อความที่พบในเอกสาร
- No OCR/embedding/model calls ในรอบแรก; หากต้องใช้เพื่อกู้ locator ต้องเสนอ scope/tool/privacy/cost เพิ่มก่อน

## 9. Verification / acceptance / exit

| ID | Test / acceptance |
|---|---|
| KR-01 | 4 external IDs มี type/prefix/uniqueness ถูกต้อง; UUIDv7 และ scope validation ผ่าน |
| KR-02 | manifest เดิมรันซ้ำไม่เพิ่ม logical assets/versions/attachments/evidence; IDs เดิมตรงทั้งหมด |
| KR-03 | file version ใหม่คง logical ID, hash ต่าง; ย้อนดู version เก่าได้; rollback ไม่แก้ raw |
| KR-04 | bytes ซ้ำคนละ path/owner ไม่ merge entity หรือสิทธิ์โดยอัตโนมัติ; attachment occurrences แยกตามเจ้าของ/ตำแหน่ง |
| KR-05 | source-first pilot เก็บ cost records ครบ 1,166 รวม 14 ไม่มีราคา; counts ไม่ถูกจำกัดด้วย 9 confirmed PM |
| KR-06 | Excel formula/cached value, merged rows, two-sided USB tables และ duplicate item code แยก locator ที่ถูกต้อง; unsupported เป็น partial ไม่ fabricated |
| KR-07 | รูปเดียวหลายหน้า/crop/generated มี lineage/rights ต่างกัน; อย่างน้อยหนึ่ง exact source image trace ผ่านโดยไม่ถือว่า generated เป็นของจริง |
| KR-08 | ราคา/กำไร trace กลับ inputs ที่ pin version ได้; หากยังมีเพียง prepared pointer ต้องระบุ partial ไม่ประกาศ raw-cell exact |
| KR-09 | ไม่มี dangling edge, endpoint type ผิด, derive/dependency cycle, cross-scope leak หรือ unbounded traversal; pagination/truncation ทดสอบครบ |
| KR-10 | source path traversal/junction escape, hash mismatch, missing source, malformed metadata และ registry-ID conflict fail closed |
| KR-11 | crash ระหว่าง generation publish/rebuild และสอง writers ไม่ทำ state ครึ่งชุดเป็น current; stale graph ถูกระบุและ rollback ผ่าน |
| KR-12 | PII/unknown source ถูก hold; outputs ไม่ track/deploy โดย default; ไม่เพิ่ม cost/private fields ใน public API; customer/product vault hashes ไม่เปลี่ยน |
| KR-13 | capability ของ Genesis adapter ผ่านใน isolated store; ไม่ใช้ตัวอย่าง Cypher ใน skill เป็นหลักฐานว่า engine นี้รองรับ Cypher |
| KR-14 | documentation/schema/manifest/consumer contracts ตรงกัน; application regression tests ที่ได้รับผลกระทบผ่านก่อน landing |

**Exit รอบออกแบบ:** เอกสาร candidate ได้รับ approval แล้ว; ผล implementation และสิ่งที่ยังไม่ผ่านดู §12<br>
**Exit implementation:** ทุก KR ที่อยู่ใน phase scope ผ่านพร้อม coverage/remaining gaps ที่ตรวจได้ ไม่ใช้คำว่า “ลงทะเบียนครบทั้งหมด” ถ้ายังมี exclusions/orphans ที่ไม่แสดงในผล

## 10. Proposed changes หลังอนุมัติ / ownership

- `config/schema_genesisblock.yaml`: เพิ่มแยก registry namespace และ constraints โดยไม่เปลี่ยน catalog identity/edges เดิม
- `config/vaults_manifest.json`: เพิ่ม internal registry projection เฉพาะเมื่อ adapter gate ผ่าน
- `pipeline/knowledge_registry/` + `tests/test_knowledge_registry_*.py`: writer, validators, legacy adapters และ read/query parity; exact runtime language แยก adapter ตาม binding เดิม
- `docs/DATA_PIPELINE_AND_VAULT_STRUCTURE.md`: เพิ่ม registry lifecycle และแก้เฉพาะข้อความที่เกี่ยวข้องกับ source authority/current privacy exception
- `.gitignore` / deployment exclusions: ป้องกัน registry generation/audit/vault ก่อนเริ่ม publish
- ไม่แก้ `pipeline/master_orchestrator.py` หรือรวมเป็น automatic pipeline ใน phase แรก; explicit scoped command เท่านั้น
- ไม่แตะ dirty ProductMaster/cost-apply/orchestrator/tests/report ของอีกงาน และไม่ถือว่าคำขอนี้อนุมัติ apply costs หรือสร้างรายงาน SRP ทั้งหมด
- ไม่มี source Excel edits, schema change, backfill, database creation, commit/push หรือ deploy ในรอบเอกสารนี้

## 11. Review / approval

Boss อนุมัติ ADR-007 + spec นี้ด้วยข้อความ `approve` วันที่ 2026-08-31 การอนุมัติออกแบบไม่แทน review ของ frozen backfill manifest และไม่รวมข้อมูล CRM/PII หรือแหล่งภายนอก

## 12. Implementation evidence — 2026-08-31

### สถานะที่ตรวจจริง

- P0/P1: เพิ่ม `pipeline/knowledge_registry/` และ schema sections แยกจาก catalog; ไม่เปลี่ยน `pm:`/`offer:`/BOM/ราคา
- Ledger: UUIDv7, typed edges, origin identity, version/hash/location, attachment occurrence, partial evidence, bounded origin/usage queries และ pagination
- Publish: single-writer lock + compare generation + staged immutable files/checksums + read-back validation + input hash recheck + atomic CURRENT replace; ใช้ pattern ที่ตรวจจาก `export_master()` และเพิ่ม multi-file ledger boundary
- Audit เป็น hash-chained **publish intent** เขียนก่อน pointer swap: intent ไม่ใช่หลักฐานว่าการ publish สำเร็จ ให้ตรวจ CURRENT/manifest ประกอบ ไม่อ้าง WORM หรือ power-loss durability บนทุก filesystem
- Genesis projection: separate worker exit ปิด native handles; สร้าง database path ใหม่แล้วทดสอบ node/edge readback ก่อนเปลี่ยน pointer; stale เมื่อ generation ต่างจาก ledger ไม่เปิด vault เดิม ไม่สร้าง embeddings
- Offline projection parity มี degree cap 5,000 และ worker timeout 60 วินาที (แยกจาก reader limits); synthetic fanout 1,166 rows ผ่าน ไม่ตัดเหลือ 1,000 โดยเงียบ
- Local CLI จงใจมีเพียง `dry-run` / `verify-plan` ในรอบนี้ ไม่มี auto-publish, orchestrator integration หรือ public API

### Frozen manifest ที่ได้รับอนุมัติและ publish แล้ว

`data-pipeline/04_review_reports/knowledge-registry-backfill-44b356aa4e1d9c09.json`

Plan SHA-256: `44b356aa4e1d9c098e69ad34515ae4679c882acb103121ab7bd2f418ee94ab21`

| รายการ | จำนวนที่ตรวจจาก source ปัจจุบัน |
|---|---:|
| Physical paths | 169 |
| เอกสารต้นทุนหลัก / archive locations | 3 / 3 |
| Metadata documents (legacy/prepared/catalog_media) | 3 |
| รูปภาพ / attachment occurrences | 160 / 160 |
| Unique content hashes | 166 |
| Cost records / มีราคา / ไม่มีราคา | 1,166 / 1,152 / 14 |
| Prepared-pointer evidence / raw-cell exact | 1,166 / 0 |
| Staged in-memory nodes / edges | 1,830 / 2,990 |

ID ใน in-memory rehearsal เดิมไม่ได้ใช้เป็น identity จริง; generation ที่ publish หลังอนุมัติใน §13 เป็นแหล่งอ้างอิงปัจจุบัน เฉพาะ pilot allowlist นี้ ไม่ใช่ทั้ง workspace

### Reproduce

```powershell
# ใช้ Python ที่มี PyYAML; เครื่องนี้ py -3 ไม่พบ runtime จึงใช้ executable โดยตรง
& 'C:\Users\freshair\AppData\Local\Programs\Python\Python313\python.exe' -X utf8 -m pipeline.knowledge_registry dry-run
& 'C:\Users\freshair\AppData\Local\Programs\Python\Python313\python.exe' -X utf8 -m pipeline.knowledge_registry verify-plan --plan data-pipeline/04_review_reports/knowledge-registry-backfill-44b356aa4e1d9c09.json
& 'C:\Users\freshair\AppData\Local\Programs\Python\Python313\python.exe' -X utf8 -m unittest tests.test_knowledge_registry tests.test_knowledge_registry_backfill tests.test_knowledge_registry_projection tests.test_pricelist_master_export -q
node --test tests/knowledge_registry_genesis.test.cjs
```

- Targeted final run: 51 tests, 50 pass / 1 skip; native capability 1 pass
- Full-suite checkpoint ก่อนเพิ่ม common-field regression: 118 tests, 117 pass / 1 skip; มี ResourceWarnings จาก font/SQLite fixtures เดิม ไม่แก้ไฟล์นอกขอบเขต
- Symlink fixture skip เพราะสิทธิ์ Windows ไม่อนุญาตสร้าง symlink: มี path/scope/hash checks แต่ **ยังไม่ถือว่ามี live junction/symlink escape proof บนเครื่องนี้**
- Full suite เดิมสร้าง product manifest ที่ workspace จริงและเปลี่ยน generated_at; คืนเฉพาะผลข้างเคียงจาก test ให้ตรงก่อนรันแล้ว ไม่ถือเป็น catalog change

### Remaining gates / ไม่อ้างว่าเสร็จแล้ว

1. P2 gate ผ่านแล้วตาม §13; manifest อื่นหรือขยาย scope ยังต้อง review ก่อน publish
2. P3: exact Excel row/cell/formula/cached-value reconciliation, PDF object/bbox/drawing adapters, image source-to-crop proof และ margin input decomposition ยังไม่ทำ; ไม่ยกระดับ `prepared_record_only` เป็น `exact`
3. ProcessingRun/CatalogEntityReference ontology สำรองไว้ แต่ยังไม่มี verified resolver/ILLUSTRATES writer; physical product mapping และ usage rights คง unknown/unresolved
4. Reader ปัจจุบันใช้ validated ledger adjacency; Genesis เป็น verified projection ยังไม่ใช่ replacement query service/authentication layer
5. Source availability/observed/last-seen richness และ `audit_coverage(run_id)` เต็มรูปแบบยังเป็นงานถัดไป; ตอนนี้มี registration timestamps กับ frozen coverage report เท่านั้น
6. Metadata MIME detection เป็น signature gate ไม่ใช่ full parser/malware scan; malformed containers ต้องตรวจด้วย exact adapters ก่อนอ้าง extraction proof
7. No commit/push/deploy; ไม่มี OCR/LLM/embedding/cloud fetch หรือแก้ raw Excel; skill graph-databases ใช้ typed relations/identity/bounded traversal ไม่ได้ติดตั้ง Neo4j หรือใช้ Cypher กับ Genesis
8. Native engine เปิด UDP gossip socket ตาม runtime เดิมระหว่าง isolated tests; ไม่ได้ตั้ง peer หรือเรียก external ingestion และไม่อ้างว่ารันภายใต้ network-isolation proof

## 13. P2 publish evidence — 2026-08-31

Boss อนุมัติ manifest ด้วยข้อความ “อนุมัติ”; receipt: `data-pipeline/04_review_reports/knowledge-registry-approval-44b356aa4e1d9c09.json` คง frozen plan เดิมทุก byte รวม status ณ เวลา dry-run ไม่ rewrite ให้ hash เปลี่ยน

- Current ledger: `gen-01a05448-25ef-775c-9891-938b8ac9757b`
- Current Genesis projection: `proj-01a05448-36f1-76d8-a382-6d3405b300f1`; generation ตรง ledger, native node/edge readback และ file checksums ผ่าน
- 1,830 nodes / 2,990 edges: Document 6 (ต้นทุน 3 + metadata 3), Picture 160, Attachment 160, AssetVersion 166, FileLocation 169, EvidenceRecord 1,169 (ต้นทุนรายแถว 1,166 + file-level source 3)
- `media:` ไม่มีรายการใน pilot เพราะ manifest นี้ไม่มี audio/video ไม่ได้ตีความว่าทั้ง workspace ไม่มี media
- ตรวจต้นทุน **ทุกแถว** 1,166 รายการย้อนหลังถึง workbook ที่ถูกต้อง รวม 14 รายการไม่มีราคา โดยยังเป็น prepared-pointer/file-level proof ไม่ใช่ raw-cell exact
- ภาพ 160 รายการ trace ถึง `catalog_media.json` และ pagination attachments 100+60 ผ่าน; 6 ภาพมี generated claim และ 154 ยังเป็น unknown ตามหลักฐานเดิม ไม่ยกระดับเป็นภาพสินค้าจริงหรือ approved-for-public
- รัน stage/commit ซ้ำแล้ว ID sets, generation count (=1), current generation และ audit hash คงเดิม ไม่สร้างซ้ำ
- `find_usages` จากเอกสารใหญ่หยุดที่ 500 nodes พร้อม `truncated=true / node_limit`; bounded per-record trace ทุกแถวผ่าน (max observed 1.701 ms ในรอบนี้ ไม่ใช่ SLA/production benchmark)
- ตรวจ source hashes 169 paths หลัง publish ตรง frozen plan; hash ของ schema, public product manifest, audit manifest, รายงาน profit เดิม และ vault เดิมไม่เปลี่ยน
- Tests รอบ publish: 26 run / 25 pass / 1 Windows symlink-fixture skip; ไม่รัน full suite ที่มีผลข้างเคียงสร้าง public manifests ซ้ำ และไม่แก้ runtime code ในรอบ publish
- ใช้ existing Python API `stage_plan(...).commit()` / `project(...)` ภายใต้ approval นี้; CLI ยังเป็น dry-run/verify-only ไม่มี auto-sync

รายงาน machine-readable พร้อม doc IDs และ checksum evidence: `data-pipeline/04_review_reports/knowledge-registry-published-44b356aa4e1d9c09.json` (internal/ignored)

Ledger generation pin hash ของ source paths 169 รายการ + frozen plan + approval receipt รวม 171 input references; approval ไม่อนุญาต commit/push/deploy และไม่แก้ raw Excel/customer/product vault

## Version diff

ไม่มี spec → `0.1.0b candidate`: เพิ่ม ID/typed graph contract, source locators, scoped ledger/projection, backfill และ verification gates; schema/runtime/data ยังไม่เปลี่ยน

`0.1.0b candidate` → `0.1.1b beta`: บันทึก approval, P0/P1 implementation/test evidence และ frozen manifest; แยก remaining P2/P3 gates จากสิ่งที่ตรวจผ่านแล้ว

## CHANGELOG

Version diff `0.1.1b` → `0.1.2b`: เพิ่มผล P2 publish/IDs/checksums/idempotency และแยก remaining P3 gates โดยไม่แก้ frozen manifest หรือ runtime code

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.2b | 2026-08-31 | beta | Publish approved P2 pilot, verify all source-row/file traces and idempotency; record actual IDs and remaining P3 gaps | uncommitted | ATHER |
| 0.1.1b | 2026-08-31 | beta | Approved design; local registry/projection tests and 169-path frozen pilot plan; no real publish | uncommitted | ATHER |
| 0.1.0b | 2026-08-31 | candidate | กำหนด knowledge registry และหลักฐานย้อนหลังจาก source inventory ครบ ไม่ผูกกับ SRP subset | uncommitted | ATHER |
