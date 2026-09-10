# 🏛️ Data Pipeline, Multi-Vault RAG & Static DB Architecture

**Document Version:** 1.3.1b
**Project:** SmartGift B2B E-commerce & Intelligent Portfolio System (`O:\Org-EtohGroup\SmartGift`)  
**Scope:** Multi-Vault RAG, Data Governance Pipeline, Review Gates, Edge Static DB & Upstream Sync

> **v1.2.0 (2026-08-31):** แก้ Stage 3 ให้ตรงกับ `pipeline/master_orchestrator.py` จริง — Stage 3
> คือ Review Catalog Enrichment (`enrich_review_catalog.py`) ไม่ใช่ "Staging SQL Generation";
> `data-pipeline/03_staging_sql/` ไม่มีสคริปต์ใดเขียนเข้าไปเลยและว่างมาตั้งแต่ต้น ไม่ใช่ dead code
> ที่เพิ่งเกิด เพิ่ม Stage 1.5 (apply confirmed factory cost mapping) และ Stage 4.5 (public web
> manifest) ที่ orchestrator รันจริงแต่เอกสารรุ่นก่อนไม่ได้พูดถึง และชี้แจงว่า Stage 5's Supabase/
> zuri-ai cloud path เป็น opt-in ผ่าน env var (`SUPABASE_URL`/`SUPABASE_KEY`) — ถ้าไม่ตั้งค่า
> ระบบทำงานแบบ local-only (`⚠️ Operating in Local Master Sync mode`) ไม่ใช่ pipeline ที่อัปโหลด
> คลาวด์อัตโนมัติเสมอไปตามที่ v1.1.0 บอกไว้
>
> **v1.1.0 (2026-08-30):** อัพเดทโครงสร้างโฟลเดอร์ให้ตรงกับ repo จริง (`data-pipeline/` แทน `data/`,
> root ที่ `O:\Org-EtohGroup\SmartGift` แทน `o:\cat`), เพิ่ม intake lane 01–08 ใน `01_raw/`
> (แก้เลข lane ซ้ำ `02_pricing_formulas` → `07_pricing_formulas` และเพิ่ม `08_factory_costs`)
> — ดู [ADR-005](decisions/ADR-005-FACTORY-COST-INTAKE-LANE.md)

---

## 📌 1. วงจรชีวิตของข้อมูล (5-Stage Data Pipeline Lifecycle)

ข้อมูลในระบบ SmartGift จะไหลผ่านกระบวนการ 5 ขั้นตอนอย่างเป็นลำดับ โดยมี **Human-in-the-Loop Review Gate** ก่อนส่งขึ้น Cloud เสมอ:

```
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Stage 1: Intake │ ───>  │ Stage 2: Preparation │ ───>  │ Stage 3: Review      │
│    Raw Data     │       │  & Normalization     │       │  Catalog Enrichment  │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
 (FlowAccount xlsx,        (product_id_mapper,            (sub-catalogs, price
  factory costs,           regex entity extraction)        tiers, SRP, package
  pricing formulas —                                       BOM breakdown)
  + Stage 1.5 confirmed
  cost apply, below)
                                                                    │
                                                                    ▼
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Stage 5: Local  │ <───  │ Stage 4.5: Public    │ <───  │ Stage 4: Review &    │
│  Vault Sync     │       │  Web Manifest        │       │  Approval Gate       │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
 (GenesisBlockDB +         (category slices,              (catalog_version_diff_
  SQLite; Supabase          integrity hashes for            report.json, Human
  cloud path is opt-in,     public/data/)                   Verification)
  env-var gated — see
  Stage 5 note below)
```

### รายละเอียด 5 ขั้นตอน (+ 1.5 / 4.5 ที่ orchestrator แทรกไว้):
1. **Stage 1: Intake Raw Data (`data-pipeline/01_raw/`):**
   * เก็บไฟล์ต้นฉบับแยกเป็น lane 01–08 (FlowAccount exports, ใบราคาโรงงาน PDF, แคตตาล็อก, เรทส่ง CBM, CRM, เอกสารธุรกิจ, สูตรราคา, ต้นทุนโรงงาน)
   * ทุก lane ที่มี archiver จะทำ SHA-256 versioning + immutable archive + registry + audit log
   * **กฎเหล็ก:** เป็นโซน **Read-Only / Immutable** ห้ามแก้ไขไฟล์ต้นฉบับโดยเด็ดขาด
   * **Stage 1.5 (`pipeline/apply_factory_cost_to_product_master.py`):** เติม `ProductMaster.base_cost`
     ให้เฉพาะรหัสที่มี `factory_cost_pm_mapping.json` status `confirmed` เท่านั้น (fail-closed,
     idempotent) — ดู [ADR-005](decisions/ADR-005-FACTORY-COST-INTAKE-LANE.md)
2. **Stage 2: Preparation & Normalization (`pipeline/02_normalize_mapper.py`):**
   * ใช้ Regular Expression สกัด Product ID, Model Code, และ Supplier Tag (`P-xx`) ที่ฝังอยู่ในชื่อสินค้า
   * แปลงข้อมูลให้อยู่ในโครงสร้างมาตรฐาน (Canonical Schema)
3. **Stage 3: Review Catalog Enrichment (`pipeline/enrich_review_catalog.py`):**
   * รวม sub-catalog สินค้า/ชุดของขวัญ, quantity tiers, SRP และ package BOM breakdown เข้า
     `smartgift_catalog_master.json`
   * **`data-pipeline/03_staging_sql/` ไม่ได้ถูกใช้งาน** — ไม่มีสคริปต์ใดใน `pipeline/` เขียนไฟล์ลง
     โฟลเดอร์นี้เลย (ตรวจ git history แล้วว่างมาตั้งแต่ commit แรก) ไม่มีการผลิตไฟล์
     `smartgift-portfolio.postgres.sql`/`smartgift-customers.postgres.sql` ตามที่เอกสารรุ่นก่อนอ้างไว้
     — ราคาปัจจุบันอ่านจาก `price-boss/sql/smartgiftpricelist.postgres.sql` ที่มีอยู่แล้ว (input, ไม่ใช่
     output ของ stage นี้) ผ่าน `pipeline/export_pricelist_master.py` ซึ่งเป็นสคริปต์แยกที่ยังไม่ได้ผูก
     เข้า orchestrator (รันเองด้วย `python pipeline/export_pricelist_master.py`)
4. **Stage 4: Review & Approval Gate (`pipeline/04_audit_review.py`):**
   * สร้าง `catalog_version_diff_report.json` และ version snapshot ใหม่ใน `data-pipeline/04_review_reports/`
   * แสดง Diff และความผิดปกติเพื่อรอการ Review + Approve
   * **Stage 4.5 (`pipeline/generate_product_manifest.py`):** สร้าง customer-safe manifest
     (`public/data/product_manifest.json`), category slices และ integrity hashes สำหรับหน้าเว็บ —
     ดู [ADR-004](decisions/ADR-004-CUSTOMER-SAFE-PRICELIST-ENDPOINT.md)
5. **Stage 5: Local Vault Sync (`pipeline/05_sync_edge_vaults.py`):**
   * แปลงข้อมูลลง **GenesisBlockDB Substrate + SQLite** ประจำ Vault ในเครื่องสำหรับ Edge Device,
     Analytics และ GraphRAG เสมอ
   * **Cloud sync เป็น opt-in:** สคริปต์นี้พยายามเชื่อม Supabase ก็ต่อเมื่อตั้งค่า env var
     `SUPABASE_URL`/`SUPABASE_KEY` ไว้เท่านั้น — ถ้าไม่ตั้งค่า (สภาพปัจจุบันของ repo นี้) จะรันแบบ
     `⚠️ Operating in Local Master Sync mode` คือ local-only ล้วน ไม่มีการอัปโหลดขึ้น
     `zuri-ai`/Supabase อัตโนมัติ

**สคริปต์ที่มีอยู่แต่ orchestrator ไม่ได้เรียก (รันแยกด้วยมือ):** `extract_factory_costs.py`
(แปลงไฟล์ต้นทุนดิบ lane 08 → `factory_costs.json`; ต้องรันก่อนถ้าไฟล์ต้นทุนใหม่เข้ามา),
`export_pricelist_master.py` (สร้าง `pricelist_master.json`/`pricelist_public.json`),
`build_offline_catalog.py` (สร้าง offline customer catalog), `add_dimensions_weight.py`,
`add_material_color.py`, `auto_quote_service.py` — ไม่มีสคริปต์เหล่านี้ใน 5-stage run ของ
`master_orchestrator.py`

---

## 🗄️ 2. Multi-Vault RAG Directory Structure (โครงสร้างโฟลเดอร์)

เพื่อรองรับ Vault ใหม่ๆ ในอนาคต (เช่น Catalog Vault, Customer Client Vault, Campaign Vault) ระบบจัดโครงสร้างโฟลเดอร์ดังนี้:

```text
O:\Org-EtohGroup\SmartGift\
├── config/                               # ⚙️ สเปกสัญญาข้อมูล & Vault Manifest
│   ├── schema_genesisblock.yaml          # GenesisBlock Engine Schema (query-ir.v1)
│   ├── schema_postgresql.sql             # Supabase PostgreSQL DDL & pgvector
│   ├── openapi_spec.yaml                 # OpenAPI 3.0 Standard Endpoint Spec
│   ├── pricing_rules_formula.yaml        # สูตรราคา (source of truth ของ formula lane)
│   └── vaults_manifest.json              # ทะเบียนกำกับ Vault ทั้งหมดในระบบ
│
├── data-pipeline/                        # 📥 Data Pipeline Workspace (แยกตาม Stage)
│   ├── 01_raw/                           # Stage 1: ไฟล์ต้นฉบับ Read-Only / Immutable
│   │   ├── 01_flowaccount_exports/       #   FlowAccount xlsx (product/contact/quotation/billing)
│   │   ├── 02_catalog_srp_pricelists_pdf/ #   🆕 แคตตาล็อกราคาขายส่งลูกค้า (Catalog SRP) PDF (legacy alias: 02_factory_pricelists_pdf)
│   │   ├── 03_product_catalogs/          #   แคตตาล็อกสินค้า PDF
│   │   ├── 04_shipping_rates_cbm/        #   เรทค่าส่ง CBM (ภาพ)
│   │   ├── 05_crm_customer_data/         #   ⚠️ PII — untracked+ignored ตาม CR-006, path ถูก pin ใน .gitignore ห้าม rename/renumber
│   │   ├── 06_business_pdf/              #   เอกสารธุรกิจ PDF (blueprint ฯลฯ)
│   │   ├── 07_pricing_formulas/          #   สูตรราคา YAML snapshot (เดิมชื่อ 02_pricing_formulas — ย้ายตาม ADR-005)
│   │   ├── 08_factory_costs/             #   🆕 ไฟล์ต้นทุนโรงงาน supplier cost catalogs (.xlsx/.xls) — ADR-005
│   │   ├── archive/                      #   immutable snapshots (SHA-256 prefixed)
│   │   ├── exports_registry.json         #   ทะเบียน version ของ FlowAccount exports
│   │   ├── pricing_formula_registry.json #   ทะเบียน version ของ pricing formulas
│   │   └── factory_cost_registry.json    #   🆕 ทะเบียน version ของ factory cost files
│   ├── 02_prepared/                      # Stage 2: ข้อมูล JSON สะอาดหลัง Normalize
│   │   ├── smartgift_catalog_master.json
│   │   ├── pricelist_master.json
│   │   └── factory_costs.json            #   🆕 normalized supplier costs + proposed PM mapping
│   ├── 03_staging_sql/                   # ⚠️ ว่างเปล่า — ไม่มีสคริปต์ใดเขียนเข้ามา (ดูหมายเหตุ Stage 3 ด้านบน)
│   └── 04_review_reports/                # Stage 4 / 4.5: รายงาน Audit, Diff & Public Manifest
│
├── vaults/                               # 🔐 Multi-Vault Storage (Local Edge Engine Substrates)
│   │
│   ├── vlt-catalog-product/              # 📦 Vault 1: Product Catalog & Sensory (Zero-PII)
│   │   ├── genesis-db/                   # GenesisBlockDB Native Rust Substrate (Vectors + Graph)
│   │   ├── projection.sqlite             # Static SQLite DB สำหรับ Edge Device & Offline Query
│   │   └── analytics.duckdb              # DuckDB Substrate สำหรับ OLAP / Margin Analytics
│   │
│   ├── vlt-customer-client/              # 👥 Vault 2: Corporate Clients & Segments (PII-Gated)
│   │   ├── genesis-db/                   # Knowledge Graph ความสัมพันธ์ลูกค้าองค์กร
│   │   └── client-policy.json            # นโยบายของขวัญและข้อห้าม (Suppression Rules)
│   │
│   └── vlt-campaign-templates/           # 🎁 Vault 3: แคมเปญและแม่แบบชุดของขวัญ
│       └── genesis-db/
│
├── pipeline/                             # 🛠️ สคริปต์ Data Pipeline Engine
│   ├── master_orchestrator.py            # รัน pipeline 1/1.5/2/3/4/4.5/5 ตามลำดับ (ดู §1)
│   ├── flowaccount_registry_archiver.py  # Stage 1: FlowAccount exports (SHA-256 versioning)
│   ├── pricing_formula_archiver.py       # Stage 1: pricing formula YAML (lane 07)
│   ├── factory_cost_archiver.py          # Stage 1: factory cost files (lane 08, รองรับ .xls/.xlsx)
│   ├── apply_factory_cost_to_product_master.py # Stage 1.5: เติม ProductMaster.base_cost (confirmed mapping เท่านั้น)
│   ├── 02_normalize_mapper.py            # Stage 2: สกัดรหัสสินค้า & ทำ Entity Mapping
│   ├── enrich_review_catalog.py          # Stage 3: review catalog + BOM enrichment
│   ├── 04_audit_review.py                # Stage 4: ตรวจสอบ Diff และสร้างรายงาน Review
│   ├── generate_product_manifest.py      # Stage 4.5: public web manifest + category slices
│   ├── 05_sync_edge_vaults.py            # Stage 5: ซิงก์ข้อมูลลง GenesisBlockDB & SQLite (local-only ถ้าไม่ตั้ง Supabase env var)
│   ├── extract_factory_costs.py          # แยก, ไม่อยู่ใน orchestrator: normalize supplier costs → proposed PM mapping
│   ├── export_pricelist_master.py        # แยก, ไม่อยู่ใน orchestrator: pricelist_master.json/pricelist_public.json
│   └── build_offline_catalog.py          # แยก, ไม่อยู่ใน orchestrator: offline customer catalog bundle
│
├── src/                                  # 💻 Business Domain & Application Logic
│   ├── cascade_engine/                   # Inventory Cascade & On-Demand BOM Decomposition
│   ├── graphrag_agent/                   # Hybrid GraphRAG Agent & Local LLM Connector
│   └── analytics/                        # Analytics Engine (Cost/Margin, COGS, Top Selling)
│
├── tests/                                # 🧪 Automated Unit & Integration Tests
│   └── test_cascade_inventory.py
│
├── AGENTS.md                             # 🛡️ กฎเหล็กและการทำงานของ AI Agent
├── SMARTGIFT_ARCHITECTURE_STACK.md       # 🏛️ สเปกสถาปัตยกรรมและเทคโนโลยีเต็มรูปแบบ
├── CR-GKS-MSP-VAULT-INTEGRATION.md       # 📋 เอกสาร Change Request สำหรับ zuri-ai, MSP, GKS
└── README.md                             # 📖 เอกสารแนะนำโปรเจกต์
```

---

## 🔒 3. กฎความปลอดภัยและการแยกขอบเขต Vault (Security & Isolation Rules)

| Vault ID | ชื่อและประเภท Vault | ขอบเขตข้อมูลที่อนุญาต | ข้อห้ามเด็ดขาด (Invariants) |
| :--- | :--- | :--- | :--- |
| **`vlt-catalog-product`** | Catalog & Sensory Vault | • สินค้ากายภาพ (ProductMaster)<br>• ชุดของขวัญ (CatalogOffer/BOM)<br>• หมวดหมู่ & เทียร์ราคา<br>• Unboxing Sensory Vectors | ❌ **ห้ามเก็บข้อมูลลูกค้า (PII)**<br>❌ **ห้ามเก็บประวัติคำสั่งซื้อ/การเงิน** |
| **`vlt-customer-client`** | Customer Profile Vault | • องค์กรลูกค้า (CorporateClient)<br>• ประวัติของขวัญที่เคยสั่งซื้อ<br>• Industry Segments & Preferences | 🔒 **ต้องผ่าน AuthContext Gate**<br>🔒 **จำกัดสิทธิ์เฉพาะ Turn ของลูกค้ารายนั้น** |
| **`vlt-campaign-templates`** | Seasonal Campaign Vault | • แคมเปญวันแม่, ปีใหม่, ผู้บริหาร<br>• Mood & Tone Template Graph | ❌ ห้ามดัดแปลง BOM สินค้าจริง |

---

## ⚡ 4. ประโยชน์ของสถาปัตยกรรมนี้

1. **รองรับ Edge Device 100%:** ไฟล์ `projection.sqlite` และ GenesisBlockDB ทำงานแบบ Offline อ่านข้อมูลได้เร็ว < 1ms โดยไม่ต้องต่อ Cloud
2. **รองรับ Data Analytics:** มี Static DB (`projection.sqlite` / DuckDB) ให้ฝ่ายวิเคราะห์รันคำนวณ Gross Margin, BOM Cost, และสถิติยอดสั่งซื้อได้ทันที
3. **Data Quality & Governance สูงสุด:** ผ่านการเตรียมข้อมูลและตรวจสอบ (Review + Approve) ก่อนใช้งานเสมอ — การส่งเข้า `zuri-ai` / Supabase Cloud DB เป็น opt-in ที่ยังไม่ได้เปิดใช้ในสภาพปัจจุบันของ repo นี้ (ดู Stage 5 ใน §1)

## 5. Knowledge Registry — local provenance sidecar (ADR-007)

[ADR-007](decisions/ADR-007-KNOWLEDGE-REGISTRY-AND-PROVENANCE.md) และ [SPEC](specs/SPEC-KNOWLEDGE-REGISTRY-2026-08-31.md) ได้รับ approval ทั้ง design และ frozen pilot manifest แล้ว; P2 publish ในเครื่องและตรวจ lineage/idempotency/native projection ผ่านตาม SPEC §13:

- `doc:` / `pic:` / `media:` / `att:` ใช้ UUIDv7 ใน registry namespace แยกจาก catalog IDs; `pic:` หมายถึงภาพ ไม่ใช่บุคคล
- Canonical registration ledger: `data-pipeline/00_knowledge_registry/generations/` + atomic `CURRENT`; graph เป็น rebuildable projection ใน `vaults/vlt-knowledge-registry/genesis-db/` เท่านั้น
- Source-first pilot ที่ publish: 3 cost documents, 3 archive locations, 1,166 cost records (14 ไม่มีราคา), 160 รูป/160 attachment references; raw-cell exact ยังเป็น 0 ไม่เท่ากับข้อมูลสูญหาย
- คำสั่ง `python -m pipeline.knowledge_registry dry-run` / `verify-plan --plan <relative-path>` ไม่แก้ raw files และไม่ publish CURRENT; registry ไม่ได้เชื่อมเข้า master orchestrator อัตโนมัติ
- Outputs/registry vault ถูก ignore และอยู่ใน deployment denylist; ไม่ ingest CRM/customer metadata ไม่เพิ่ม price authority หรือสร้าง canonical ProductMaster จากชื่อไฟล์
- `lookup_asset`, `trace_origin`, `find_usages`, `list_attachments` อ่าน validated local ledger; scope checks ไม่ใช่ authentication service ที่ติดตั้งแล้ว
- Exact Excel/PDF locator recovery, verified image-to-product resolver และ backfill นอก pilot เป็น gate ถัดไปตาม SPEC ไม่อ้าง production-ready

## Version diff / CHANGELOG

`1.2.0` → `1.3.0b`: เพิ่มเฉพาะ knowledge-registry lifecycle แยกจาก pipeline เดิม; รักษาการแก้ Stage 3 และ price-authority filename จากอีก session

`1.3.0b` → `1.3.1b`: บันทึก approved P2 pilot publish ใน local ledger/graph โดยไม่เปลี่ยน automatic pipeline หรือ source authority

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 1.3.1b | 2026-08-31 | beta | Record approved local pilot publication and verified lineage; exact P3 locators pending | uncommitted | ATHER |
| 1.3.0b | 2026-08-31 | beta | Add approved ADR-007 isolated registry and frozen-backfill gate; no automatic sync | uncommitted | ATHER |
