# 🏛️ SmartGift B2B System & Data Architecture Specification

**Document Version:** 2.0.0  
**Status:** APPROVED ARCHITECTURE BLUEPRINT  
**Enterprise Hierarchy:** `Wannapa Workspace` ➔ `Org-EtohGroup` (Tenant) ➔ `SmartGift` (Business 01)  
**Operating Entity:** บริษัท เทราบิส จำกัด (`Therabis Co., Ltd.`)  
**Scope:** 4-Tier Cognitive Stack, 5-Stage Data Pipeline, Multi-Vault RAG, Edge Static DB & Folder Structure  

---

## 📌 1. Executive Summary & Enterprise Hierarchy

ระบบ **SmartGift B2B Intelligent Portfolio & GraphRAG System** เป็นหน่วยธุรกิจ (Business 01) ภายใต้เครือองค์กร **`Org-EtohGroup`** บนแพลตฟอร์ม **`Wannapa Workspace`**

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Workspace: Wannapa Workspace (Operational Environment)                                  │
│  └─ Organization (Tenant): Org-EtohGroup (Enterprise Group Boundary)                    │
│     └─ Business 01: SmartGift (B2B Gift Set & Portfolio Engine)                          │
│        ├─ Legal Entity: บริษัท เทราบิส จำกัด (Therabis Co., Ltd.)                         │
│        ├─ Data Pipeline: FlowAccount Normalizer (Read-Only Intake ➔ Review Catalog)       │
│        ├─ Product Catalog Vault: vlt-catalog-product (Zero-PII UUIDv7)                    │
│        └─ Customer Client Vault: vlt-customer-client (PII-Gated Historical Suppression)  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 2. Four-Tier Cognitive Stack Architecture (Who Manages What)

ระบบแยกความรับผิดชอบออกเป็น 4 ระดับอย่างชัดเจนตามมาตรฐาน **ADR-041 ถึง ADR-044**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Scope Authority (zuri-ai & zuri-edge-device)                      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • zuri-ai (D:\zuri-ai): Cloud PostgreSQL / Supabase, Users, CRM, Orders, Invoices (PII) │
│  • zuri-edge-device (D:\workspace\zuri-edge-device): Host Runtime & Local LLM Gateway    │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-Resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Session, Memory & Vault Gatekeeper                                              │
│          (MSP / Memory-and-Soul-Passport: D:\Memory-and-Soul-Passport [alias: D:\msp])    │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Unified Thread ID, Episodic Memory, Token Budget, H0-H4 Ceilings             │
│  • API-010 (msp_vault_resolve): Maps Workspace Scope ➔ [vlt-catalog-product]             │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Canonical Knowledge & GraphRAG Orchestrator                                     │
│          (GKS / Genesis-Knowledge-System: D:\Genesis-Knowledge-System [alias: D:\gks])   │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Canonical Ontology Registry, Radius (R0-R6) GraphRAG Routing, Deduplication │
│  • Contract: smartgift://b2b/portfolio/v1 (v1.3.0) via Query IR (query-ir.v1)            │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (In-Process Native Rust C-ABI)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 4: Storage Substrate (GenesisBlockDB Native + Edge Static DB)                      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • 6-Lane Substrate: Vector, Lexical, Graph, SQLite, Bitemporal, Provenance             │
│  • Static DBs: projection.sqlite (Edge Offline Search) & analytics.duckdb (OLAP Margin)  │
│  • Invariant: Stores ONLY Product Masters, Gift Offers & Sensory Vectors (Zero-PII)      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 3. Five-Stage Data Pipeline & Governance Flow

เพื่อรักษาความถูกต้องของข้อมูลบัญชีต้นทางและความปลอดภัยสูงสุด ข้อมูลจะไหลผ่าน 5 ขั้นตอน:

```
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Stage 1: Intake │ ───>  │ Stage 2: Preparation │ ───>  │ Stage 3: Review      │
│    Raw Data     │       │  & Normalization     │       │  Catalog Enrichment  │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
 (FlowAccount xlsx,        (product_id_mapper,            (sub-catalogs, price
  factory costs, +         Regex Entity Extraction)        tiers, SRP, package
  Stage 1.5 confirmed                                       BOM breakdown)
  cost apply)
                                                                    │
                                                                    ▼
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Stage 5: Local  │ <───  │ Stage 4.5: Public    │ <───  │ Stage 4: Review      │
│  Vault Sync     │       │  Web Manifest        │       │   & Approval Gate    │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
 (GenesisBlockDB,          (category slices,              (Audit Diff Report,
  SQLite; Supabase          integrity hashes)               Human Verification)
  path opt-in, see #5)
```

1. **Stage 1 (Raw Intake):** เก็บไฟล์ต้นทาง `บริษัท เทราบิส จำกัด_product.xlsx` ในสถานะ **Read-Only / Immutable 100%**; ตามด้วย **Stage 1.5** (`pipeline/apply_factory_cost_to_product_master.py`) ที่เติม `ProductMaster.base_cost` เฉพาะรหัสที่ผ่านการยืนยัน mapping แล้ว
2. **Stage 2 (Normalization):** ใช้ `pipeline/02_normalize_mapper.py` สกัดรหัส Product ID, Model Code, และ Supplier Tag (`P-xx`) ที่ฝังอยู่ในชื่อสินค้า
3. **Stage 3 (Review Catalog Enrichment):** `pipeline/enrich_review_catalog.py` รวม sub-catalog, quantity tiers, SRP และ package BOM เข้า `smartgift_catalog_master.json` — **ไม่ผลิตไฟล์ SQL** `data-pipeline/03_staging_sql/` ว่างเปล่าและไม่มีสคริปต์ใช้งาน (ดูรายละเอียดใน [DATA_PIPELINE_AND_VAULT_STRUCTURE.md §1](DATA_PIPELINE_AND_VAULT_STRUCTURE.md))
4. **Stage 4 (Review Gate):** `pipeline/04_audit_review.py` สร้าง `catalog_version_diff_report.json` ก่อน Approve; ตามด้วย **Stage 4.5** (`pipeline/generate_product_manifest.py`) ที่สร้าง customer-safe manifest สำหรับหน้าเว็บ
5. **Stage 5 (Local Vault Sync):** `pipeline/05_sync_edge_vaults.py` ซิงก์ลง GenesisBlockDB + Static SQLite (`projection.sqlite`) เสมอสำหรับ Edge Device & Offline Analytics (< 1ms Latency) — เชื่อม Supabase/`zuri-ai` ก็ต่อเมื่อตั้งค่า `SUPABASE_URL`/`SUPABASE_KEY`; ถ้าไม่ตั้งค่า (สภาพปัจจุบัน) จะรัน local-only

---

## 🔐 4. Multi-Vault RAG Architecture & Isolation Rules

| Vault ID | ประเภท Vault | ขอบเขตข้อมูลที่อนุญาต | กฎความปลอดภัย (Security Invariants) |
| :--- | :--- | :--- | :--- |
| **`vlt-catalog-product`** | Product Catalog & Sensory Vault | • สินค้ากายภาพ (`ProductMaster`)<br>• ชุดของขวัญ (`CatalogOffer`/BOM)<br>• หมวดหมู่ & เทียร์ราคา MOQ<br>• Unboxing Sensory Vectors (1024-dim) | ❌ **ห้ามเก็บข้อมูลลูกค้า (Zero-PII)**<br>❌ **ห้ามเก็บประวัติคำสั่งซื้อ/การเงิน** |
| **`vlt-customer-client`** | Corporate Client Profile Vault | • องค์กรลูกค้า (`CorporateClient`)<br>• ประวัติของขวัญที่เคยสั่งซื้อ<br>• Industry Segments & Preferences | 🔒 **ต้องผ่าน AuthContext Resolution**<br>🔒 **จำกัดสิทธิ์เฉพาะ Session Turn ของลูกค้ารายนั้น** |
| **`vlt-campaign-templates`**| Seasonal Campaign Templates | • แคมเปญวันแม่, ปีใหม่, ผู้บริหาร<br>• Mood & Tone Template Graph | ❌ ห้ามแก้ไขสูตรต้นทุน BOM สินค้าจริง |

---

## 🗂️ 5. โครงสร้างโฟลเดอร์เป้าหมาย (Target Directory Structure)

> **หมายเหตุ (2026-08-31):** ผังนี้เป็น blueprint เป้าหมาย ไม่ใช่ snapshot ของไฟล์จริงในปัจจุบัน —
> ชื่อไฟล์ตัวอย่างด้านล่าง (เช่น `flowaccount-product-raw.xlsx`, `smartgift-portfolio.postgres.sql`)
> ไม่ตรงกับไฟล์จริงใน repo และ `03_staging_sql/` ยังไม่มีสคริปต์ใดเขียนเข้าไปเลย ดูโครงสร้างจริง
> ปัจจุบันที่ [DATA_PIPELINE_AND_VAULT_STRUCTURE.md](DATA_PIPELINE_AND_VAULT_STRUCTURE.md)

```text
O:\Org-EtohGroup\                         # 🏢 Organization Root (Tenant: Org-EtohGroup)
│
└── SmartGift\                            # 💼 Business 01 (Business: SmartGift)
    │
    ├── config/                           # ⚙️ สเปกสัญญาข้อมูล & ทะเบียน Vault
    │   ├── schema_genesisblock.yaml      # Contract: smartgift://b2b/portfolio/v1
    │   ├── schema_postgresql.sql         # Supabase PostgreSQL DDL & pgvector
    │   ├── openapi_spec.yaml             # OpenAPI 3.0 Standard Endpoint Spec
    │   └── vaults_manifest.json          # ทะเบียนกำกับ Vault ทั้งหมด
    │
    ├── data-pipeline/                    # 🔄 5-Stage Data Governance Pipeline
    │   ├── 01_raw/                       # Stage 1: ไฟล์ต้นฉบับ Read-Only (FlowAccount, Sheets)
    │   │   ├── flowaccount-product-raw.xlsx
    │   │   └── google-sheet-catalog-raw.csv
    │   ├── 02_prepared/                  # Stage 2: ข้อมูล JSON สะอาดหลัง Normalize
    │   │   └── smartgift_catalog_master.json
    │   ├── 03_staging_sql/               # Stage 3: ไฟล์ SQL ที่แปลงเสร็จแล้ว
    │   │   ├── smartgift-portfolio.postgres.sql
    │   │   └── smartgift-customers.postgres.sql
    │   └── 04_review_reports/            # Stage 4: รายงาน Audit & Approval Gates
    │       └── product_id_mapping_report.json
    │
    ├── vaults/                           # 🔐 Multi-Vault Storage (Local Substrates)
    │   │
    │   ├── vlt-catalog-product/          # 📦 Vault 1: Product Catalog & Sensory (Zero-PII)
    │   │   ├── genesis-db/               # GenesisBlockDB Substrate (Vectors + Graph < 1ms)
    │   │   ├── projection.sqlite         # Static SQLite DB สำหรับ Edge Device & Offline
    │   │   └── analytics.duckdb          # DuckDB สำหรับ OLAP / Margin Analytics
    │   │
    │   ├── vlt-customer-client/          # 👥 Vault 2: Corporate Clients & Segments (PII-Gated)
    │   │   ├── genesis-db/               # Knowledge Graph ประวัติของขวัญลูกค้าองค์กร
    │   │   └── client-policy.json        # นโยบายและข้อห้าม (Suppression Rules)
    │   │
    │   └── vlt-campaign-templates/       # 🎁 Vault 3: แคมเปญและแม่แบบชุดของขวัญ
    │       └── genesis-db/
    │
    ├── pipeline/                         # 🛠️ สคริปต์ Data Pipeline Engine
    │   ├── 01_intake.py                  # ดึงข้อมูลจากแหล่งต้นทาง
    │   ├── 02_normalize_mapper.py        # สกัดรหัสสินค้า & Entity Extraction
    │   ├── 03_export_sql.py              # ผลิตไฟล์ SQL พร้อมนำเข้า
    │   ├── 04_audit_review.py            # ตรวจสอบ Diff และสร้างรายงาน Review
    │   └── 05_sync_edge_vaults.py        # ซิงก์ข้อมูลลง GenesisBlockDB & Static DB
    │
    ├── src/                              # 💻 Business Domain & Application Logic
    │   ├── cascade_engine/               # BOM Cascade & Profit Margin Engine
    │   ├── graphrag_agent/               # GraphRAG Agent & Local LLM Connector
    │   └── analytics/                    # Static Analytics Engine (COGS, Margin %)
    │
    ├── tests/                            # 🧪 Automated Unit & Integration Tests
    │   └── test_cascade_inventory.py
    │
    ├── AGENTS.md                         # 🛡️ กฎเหล็กประจำ Business 01 (SmartGift)
    ├── SMARTGIFT_SYSTEM_ARCHITECTURE.md  # 🏛️ สเปกสถาปัตยกรรมฉบับนี้
    ├── CR-GKS-MSP-VAULT-INTEGRATION.md   # 📋 เอกสาร Change Request สำหรับ zuri-ai, MSP, GKS
    └── package.json                      # Node dependencies (@freshair129/gks-genesis-block-native)
```
