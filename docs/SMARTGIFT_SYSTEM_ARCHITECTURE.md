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
│        ├─ Data Pipeline: FlowAccount Normalizer (Read-Only Intake ➔ Staging SQL)          │
│        ├─ Product Catalog Vault: vlt-catalog-product (Zero-PII UUIDv7)                    │
│        └─ Customer Client Vault: vlt-customer-client (PII-Gated Historical Suppression)  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 2. Four-Tier Cognitive Stack Architecture (Who Manages What)

ระบบแยกความรับผิดชอบออกเป็น 4 ระดับอย่างชัดเจนตามมาตรฐาน **ADR-041 ถึง ADR-044**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Scope Authority (zuri-ai / D:\zuri-ai)                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Scope Chain: Portfolio → Tenant (Org-EtohGroup) → Business (SmartGift) → Workspace    │
│  • Source of Truth: prisma/schema.prisma (PostgreSQL / Supabase / SQLite)                │
│  • Manages: Users, Memberships, Customer PII, Financial Transactions, Ledger Orders      │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-Resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Session, Memory & Vault Gatekeeper (MSP / D:\msp)                               │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Unified Thread ID, Episodic Memory, Token Budget, H0-H4 Access Ceilings     │
│  • API-010 (msp_vault_resolve): Maps server-owned workspace/project scope to Vault IDs   │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set: [vlt-catalog-product])
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Canonical Knowledge & GraphRAG Orchestrator (GKS / D:\gks)                      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Entity Canonicalization, Ontology Registry, Deduplication, Radius (R0-R6)    │
│  • GraphRAG Engine: Hybrid Dense Vector (bge-m3) + Graph HQL Traversal via query-ir.v1   │
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
│ Stage 1: Intake │ ───>  │ Stage 2: Preparation │ ───>  │ Stage 3: Staging SQL │
│    Raw Data     │       │  & Normalization     │       │    Generation        │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
 (FlowAccount xlsx,        (product_id_mapper,            (smartgift-portfolio.sql,
  Google Sheets, PDFs)      Regex Entity Extraction)       smartgift-clients.sql)
                                                                    │
                                                                    ▼
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Stage 5b: Edge  │ <───  │ Stage 5a: Upstream   │ <───  │ Stage 4: Review      │
│   Static DB     │       │   Postgres Sync      │       │   & Approval Gate    │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
 (GenesisBlockDB,          (Send to zuri-ai /             (Audit Diff Report,
  DuckDB, SQLite)           Supabase Cloud DB)             Human Verification)
```

1. **Stage 1 (Raw Intake):** เก็บไฟล์ต้นทาง `บริษัท เทราบิส จำกัด_product.xlsx` ในสถานะ **Read-Only / Immutable 100%**
2. **Stage 2 (Normalization):** ใช้ `product_id_mapper.py` สกัดรหัส Product ID, Model Code, และ Supplier Tag (`P-xx`) ที่ฝังอยู่ในชื่อสินค้า
3. **Stage 3 (Staging SQL):** ผลิตไฟล์ SQL มาตรฐาน `smartgift-portfolio.postgres.sql`
4. **Stage 4 (Review Gate):** ตรวจสอบผ่านรายงาน `product_id_mapping_report.json` ก่อน Approve
5. **Stage 5 (Dual Publishing):**
   * **5a. Upstream Cloud:** นำเข้า `zuri-ai` / Supabase Cloud DB
   * **5b. Local Edge Engine:** ซิงก์ลง GenesisBlockDB (`smartgift-genesis-db`) + Static SQLite (`projection.sqlite`) สำหรับ Edge Device & Offline Analytics (< 1ms Latency)

---

## 🔐 4. Multi-Vault RAG Architecture & Isolation Rules

| Vault ID | ประเภท Vault | ขอบเขตข้อมูลที่อนุญาต | กฎความปลอดภัย (Security Invariants) |
| :--- | :--- | :--- | :--- |
| **`vlt-catalog-product`** | Product Catalog & Sensory Vault | • สินค้ากายภาพ (`ProductMaster`)<br>• ชุดของขวัญ (`CatalogOffer`/BOM)<br>• หมวดหมู่ & เทียร์ราคา MOQ<br>• Unboxing Sensory Vectors (1024-dim) | ❌ **ห้ามเก็บข้อมูลลูกค้า (Zero-PII)**<br>❌ **ห้ามเก็บประวัติคำสั่งซื้อ/การเงิน** |
| **`vlt-customer-client`** | Corporate Client Profile Vault | • องค์กรลูกค้า (`CorporateClient`)<br>• ประวัติของขวัญที่เคยสั่งซื้อ<br>• Industry Segments & Preferences | 🔒 **ต้องผ่าน AuthContext Resolution**<br>🔒 **จำกัดสิทธิ์เฉพาะ Session Turn ของลูกค้ารายนั้น** |
| **`vlt-campaign-templates`**| Seasonal Campaign Templates | • แคมเปญวันแม่, ปีใหม่, ผู้บริหาร<br>• Mood & Tone Template Graph | ❌ ห้ามแก้ไขสูตรต้นทุน BOM สินค้าจริง |

---

## 🗂️ 5. โครงสร้างโฟลเดอร์เป้าหมาย (Target Directory Structure)

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
