---
version: "0.1.2b"
created_at: "2026-08-31T00:09:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T03:10:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "knowledge-provenance"
  doc_type: "architecture-decision"
  scope: "local knowledge registry, asset identities and retrospective provenance; approved with phase gates"
  language: "th"
---

# ADR-007 — Knowledge Registry และการสืบย้อนแหล่งข้อมูล

**Status:** Approved / beta — Boss อนุมัติ frozen manifest และ publish P2 pilot แล้ว; P3 exact evidence ยังไม่ทำ
**Date:** 2026-08-31<br>
**Decided by:** Boss — ข้อความ `approve` วันที่ 2026-08-31<br>
**Complexity / Risk:** C-3 / HIGH — เพิ่ม identity contract, registry storage และ provenance graph<br>
**Relates to:** [AGENTS.md](../../AGENTS.md), [Data Pipeline](../DATA_PIPELINE_AND_VAULT_STRUCTURE.md), [schema authority](../../config/schema_genesisblock.yaml), [vault manifest](../../config/vaults_manifest.json), [ADR-002](ADR-002-PRICELIST-MASTER-SQL-SNAPSHOT.md), [ADR-004](ADR-004-CUSTOMER-SAFE-PRICELIST-ENDPOINT.md), [ADR-005](ADR-005-FACTORY-COST-INTAKE-LANE.md), [ADR-006](ADR-006-PRIVATE-REPOSITORY-SOURCE-DATA-EXCEPTION.md), [รายละเอียดสัญญา](../specs/SPEC-KNOWLEDGE-REGISTRY-2026-08-31.md)

## Context

ผู้ใช้ขอ Knowledge Registry สำหรับ `doc_id`, `pic_id`, `media_id`, `attachment_id` และการลงทะเบียนย้อนหลังเพื่อทราบว่าข้อมูลมาจากไหน การลงทะเบียนต้องไม่เริ่มจากสินค้าที่มี SRP เพียง 16 ตัว เพราะจะทำให้รายการต้นทุนและภาพที่ยังไม่จับคู่หายไปจาก coverage อีกครั้ง

หลักฐานจาก checkout ณ 2026-08-31 (ไม่ใช่ผลทดสอบ runtime):

- มี `exports_registry.json` 4 file entries/4 versions, `pricing_formula_registry.json` 1 entry/1 version และ `factory_cost_registry.json` 3 entries/3 versions; identity เดิมอิงชื่อไฟล์, version และ SHA-256 แยกตาม lane
- `factory_costs.json` มี 1,166 records, มีราคา 1,152; ทั้งหมดมี source_file, 64 records มี sheet, แต่ไม่พบ source row/cell ใน records ปัจจุบัน จึงพิสูจน์ได้ระดับไฟล์/แถว prepared JSON ไม่ใช่เซลล์ Excel ทุกตัว
- `catalog_media.json` มี sets 153 records, products 6 records และ hero แยกต่างหาก; นี่เป็นจำนวน references ไม่ใช่จำนวนภาพไม่ซ้ำ Metadata ที่สุ่มตรวจมี code/image/source_label/visual_status แต่ไม่มี registry IDs สี่ชนิด
- หลักฐานภาพแบบ page + source code + image object + hash กระจายอยู่ใน image-first spec และ internal production manifest ต้องย้ายความสัมพันธ์เข้าสัญญาที่ตรวจอัตโนมัติได้ โดยไม่ย้ายไฟล์ต้นฉบับ
- YAML canonical ontology ปัจจุบันยังไม่มี Document/Picture/Media/Attachment; vault manifest ยังไม่มี knowledge-registry vault
- package.json ประกาศ `@freshair129/gks-genesis-block-native: ^0.2.5`; seed ใช้ `GenesisDatabase.open/addNode/addEdge` จริง แต่หลักฐานนี้ไม่ยืนยัน transaction, unique index หรือ query API สำหรับ registry ใหม่

## Decision

### D1 — ทะเบียนกลางเป็น metadata/lineage ไม่ใช่ price master ใหม่

Registry ตอบ “ไฟล์อะไร / เวอร์ชันไหน / ภาพไหน / แถวหรือเซลล์ไหน / ผ่านขั้นตอนอะไร / ถูกใช้ที่ไหน” ไม่แก้ราคา, BOM, stock, ProductMaster หรือสิทธิ์ใช้ภาพ การลงทะเบียนสำเร็จไม่เท่ากับข้อมูลได้รับการอนุมัติทางธุรกิจ

### D2 — IDs สี่ชนิดมีความหมายต่างกัน

| Field | Proposed prefix | ความหมาย |
|---|---|---|
| doc_id | doc: | เอกสารเชิงตรรกะ เช่น PDF, Excel, JSON report, Markdown |
| pic_id | pic: | ภาพต้นฉบับหรือภาพที่แปลงแล้ว แยกสถานะจริง/crop/generated |
| media_id | media: | เสียงหรือวิดีโอ ไม่รวมรูปนิ่งซ้ำกับ pic_id |
| attachment_id | att: | การแนบหนึ่งครั้งระหว่างเวอร์ชันเจ้าของกับเวอร์ชันไฟล์ที่ถูกแนบ ไม่ใช่สำเนา bytes อีกชุด |

ใช้ UUIDv7 ที่ registry ออกและเก็บถาวร; SHA-256 ระบุเนื้อหา, path ระบุตำแหน่ง, business code ระบุรหัสธุรกิจ — ทั้งสามอย่างไม่แทน registry ID และไม่แทน canonical `pm:`/`offer:` IDs

### D3 — แยก logical identity, byte version และ source occurrence

ไฟล์เดิมเปลี่ยนเนื้อหา → เวอร์ชันใหม่; ไฟล์ถูกย้าย → บันทึก location/alias หลังพิสูจน์ความต่อเนื่อง ไม่เปลี่ยน ID เอง; bytes ซ้ำ → รายงาน duplicate และใช้ content hash ร่วมได้ แต่ไม่รวม logical document หรือความหมายสินค้าเอง ภาพเดียวแนบหลายหน้าได้หลาย attachment IDs

เพิ่ม supporting records เท่าที่ใช้ตรวจย้อนจริง: AssetVersion, FileLocation, ProcessingRun, EvidenceRecord และ CatalogEntityReference รายละเอียด field/edge อยู่ใน spec ไม่สร้าง catalog ProductMaster สำเนา

### D4 — Canonical ledger + graph projection ที่ rebuild ได้

เสนอ registry ledger ที่ `data-pipeline/00_knowledge_registry/` และ graph projection แยก `vaults/vlt-knowledge-registry/genesis-db/` ด้วย engine เดิม หลังผ่าน capability gate ในฐานทดลองเท่านั้น ไม่ใช้ seed catalog เดิมเปิด registry และไม่เพิ่ม Neo4j/บริการภายนอก

Ledger เป็น authority ของการลงทะเบียน/ID; graph เป็น read projection ที่ hash-pin กับ ledger generation ไม่เป็น writer อีกตัว หาก graph capability ยังไม่ผ่าน ให้รายงาน graph phase ว่ายังไม่เสร็จ ห้ามสลับ backend หรือแตะ product vault โดยพลการ

### D5 — เพิ่ม contract แบบแยก namespace หลังอนุมัติ

หลัง Boss อนุมัติ ได้เพิ่ม `smartgift://knowledge/registry/v1` เป็น registry contract/node/edge sections แยกใน `config/schema_genesisblock.yaml` ไม่เปลี่ยน semantics ของ catalog ontology v1.3.0 หรือ prefixes เดิม ตรวจ equality ของ catalog sections กับ HEAD และทดสอบ export consumers ผ่านแล้ว ส่วน registry data จริงได้ publish เฉพาะ frozen manifest ที่ Boss อนุมัติตาม §Approval boundary

### D6 — Backfill ครบตาม source inventory ไม่กรองด้วยการจับคู่ SRP

เริ่มจากไฟล์และแถวที่มีอยู่ทั้งหมดใน allowlist รวม records ที่ไม่มีราคา, ไม่มีรหัส, ยังไม่จับคู่ และภาพที่ยังไม่ยืนยันสินค้า รักษา unknown/orphan/conflict เป็นสถานะที่ตรวจเห็นได้ ไม่สร้าง source page/cell/วันที่ย้อนหลังจากการคาดเดา

เริ่ม pilot ที่ต้นทุน 3 ไฟล์ + archives + prepared cost records 1,166 รายการ และภาพ/manifest ที่มี provenance เดิม ก่อนขยายสู่เอกสาร/สื่ออื่นใน workspace ห้ามนับ factory price row, product model, physical file และ unique content เป็นจำนวนเดียวกัน

### D7 — ขอบเขตความปลอดภัยไม่ขยายตามคำว่า registry

Registry รุ่นแรกเป็น local internal metadata สำหรับแหล่งสินค้า/ธุรกิจที่ผ่าน classification เท่านั้น ไม่มี raw customer contents, contact metadata, quotation history หรือ customer file paths ในทะเบียนนี้ ไม่คัดลอกเนื้อหา supplier-contact headers จากเอกสารต้นทุน

- CRM/PII/unknown sources: hold/exclude พร้อม aggregate counts ที่ไม่ระบุบุคคล; การเข้าถึงและทะเบียนส่วน CRM ต้องผ่าน owner/consent scope ของ zuri-ai แยกต่างหาก
- ADR-006 อนุมัติไฟล์เฉพาะชุด ไม่อนุมัติ derived customer registry หรือการ push registry ใหม่
- ไม่เขียน catalog product vault, customer vault, governed edge store หรือ `gks:` namespace; ชื่อ package ไม่ได้ทำให้ GenesisBlockDB กลายเป็น GKS service
- ไม่ deploy, commit/push, fetch cloud sources, execute attachments/macros, ทำ OCR/embedding หรือเปลี่ยน public API โดยอัตโนมัติ
- source paths/hashes/cost lineage ไม่ส่งเข้า public catalog; สิทธิ์อ่าน source ต้องไม่กว้างขึ้นเพราะ deduplicate หรือสร้างภาพ derivative

## Alternatives considered

1. เพิ่ม array ของ file names ใน ProductMaster: ไม่พอสำหรับหลายเวอร์ชัน หลาย source และ evidence ราย field; ยังผูก coverage กับ ProductMaster โดยไม่จำเป็น
2. ใช้ hash เป็น doc_id: ระบุ bytes ได้แต่แยก logical version/location/owner ไม่ได้ และ merge เอกสารคนละบริบทได้ผิด
3. เปลี่ยนไป Neo4j ทันที: เพิ่ม infrastructure และ migration โดยยังไม่พิสูจน์ความจำเป็น; ใช้ graph-modeling principles ของ skill กับ engine boundary เดิมก่อน

## Consequences

- ต้องมี schema validation, identity map, atomic generation commit, bounded lineage queries และ rollback tests ก่อน backfill จริง
- การกู้ sheet/row/cell ย้อนหลังต้องเพิ่ม extraction provenance adapters หลังอนุมัติ; แค่มี registry ไม่ได้ทำให้ source locators ที่ขาดกลับมาเอง
- graph-modeling skill กำหนดให้ใช้ typed relationships, stable version history และ bounded traversal ไม่ใช่การอนุมัติ vendor migration หรือ unbounded graph query
- เอกสาร Data Pipeline รุ่นเก่าที่ระบุ CRM ว่า untracked ทั้งหมดไม่ใช่ current storage authority; AGENTS.md + ADR-006 เป็นตัวตัดสินข้อยกเว้นปัจจุบัน ไม่แก้เอกสารอื่นนอกงานโดยอัตโนมัติ

## Approval boundary

อนุมัติ ADR นี้ร่วมกับ spec จึงเริ่ม P0–P3 ตาม phase gates ได้: local capability test, registry contract/ledger, dry-run แล้ว publish backfill เฉพาะ manifest ที่ผ่าน review หากรายการ scope/PII/แหล่งภายนอกเปลี่ยนต้องถามใหม่ ไม่มี approval ใดในเอกสารนี้แทนผลตรวจ runtime

Boss อนุมัติ frozen plan `44b356aa4e1d9c098e69ad34515ae4679c882acb103121ab7bd2f418ee94ab21` ด้วยข้อความ “อนุมัติ” วันที่ 2026-08-31; P2 publish เป็น generation `gen-01a05448-25ef-775c-9891-938b8ac9757b` และตรวจ idempotency/lineage/Genesis readback ผ่านแล้ว ดู SPEC §13 ไม่แก้ frozen plan เดิมเพื่อรักษา hash; approval receipt และผลตรวจแยกอยู่ใน internal review reports

## Version diff

ไม่มีเอกสาร → `0.1.0b candidate`: เสนอ identity/provenance registry และแผนลงทะเบียนย้อนหลัง ยังไม่เปลี่ยน schema, code, ledger, vault หรือข้อมูลต้นฉบับ

`0.1.0b candidate` → `0.1.1b beta`: บันทึก approval; เพิ่ม registry namespace แยกใน YAML, local ledger + read queries, isolated Genesis projection และ source-first dry-run ตาม [implementation evidence ใน SPEC](../specs/SPEC-KNOWLEDGE-REGISTRY-2026-08-31.md#12-implementation-evidence--2026-08-31) ยังไม่ publish backfill/P3 exact adapters และไม่ commit/push/deploy

## CHANGELOG

Version diff `0.1.1b` → `0.1.2b`: บันทึก frozen-manifest approval, current generation และ P2 publish verification; ไม่มี ontology/runtime changes ในรอบนี้

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.2b | 2026-08-31 | beta | Approved frozen manifest published locally; 1,166 record traces and native projection verified; P3 pending | uncommitted | ATHER |
| 0.1.1b | 2026-08-31 | beta | Boss approved design; implement P0/P1 and test isolated ledger/projection; real backfill gated on frozen manifest | uncommitted | ATHER |
| 0.1.0b | 2026-08-31 | candidate | ตรวจทะเบียน/locator เดิมและเสนอ local registry + graph provenance | uncommitted | ATHER |
