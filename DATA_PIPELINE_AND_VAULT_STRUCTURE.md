# 🏛️ Data Pipeline, Multi-Vault RAG & Static DB Architecture

**Document Version:** 1.0.0  
**Project:** SmartGift B2B E-commerce & Intelligent Portfolio System (`O:\cat`)  
**Scope:** Multi-Vault RAG, Data Governance Pipeline, Review Gates, Edge Static DB & Upstream Sync

---

## 📌 1. วงจรชีวิตของข้อมูล (5-Stage Data Pipeline Lifecycle)

ข้อมูลในระบบ SmartGift จะไหลผ่านกระบวนการ 5 ขั้นตอนอย่างเป็นลำดับ โดยมี **Human-in-the-Loop Review Gate** ก่อนส่งขึ้น Cloud เสมอ:

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

### รายละเอียด 5 ขั้นตอน:
1. **Stage 1: Intake Raw Data (`data/01_raw/`):**
   * เก็บไฟล์ต้นฉบับ เช่น `บริษัท เทราบิส จำกัด_product.xlsx`, Google Sheet CSV, PDF Blueprint
   * **กฎเหล็ก:** เป็นโซน **Read-Only / Immutable** ห้ามแก้ไขไฟล์ต้นฉบับโดยเด็ดขาด
2. **Stage 2: Preparation & Normalization (`pipeline/02_normalize_mapper.py`):**
   * ใช้ Regular Expression สกัด Product ID, Model Code, และ Supplier Tag (`P-xx`) ที่ฝังอยู่ในชื่อสินค้า
   * แปลงข้อมูลให้อยู่ในโครงสร้างมาตรฐาน (Canonical Schema)
3. **Stage 3: Staging SQL Generation (`data/03_staging_sql/`):**
   * ผลิตไฟล์ SQL พร้อมนำเข้า เช่น `smartgift-portfolio.postgres.sql`, `smartgift-customers.postgres.sql`
4. **Stage 4: Review & Approval Gate (`data/04_review_reports/`):**
   * สร้างรายงานตรวจสอบความถูกต้อง [product_id_mapping_report.json](file:///o:/cat/product_id_mapping_report.json)
   * แสดง Diff และความผิดปกติเพื่อรอการ Review + Approve
5. **Stage 5: Dual Distribution (แยก 2 ปลายทาง):**
   * **5a. Upstream Production:** ส่งไฟล์ `.sql` ที่ผ่านการ Approve เข้าสู่ `zuri-ai` / Supabase Cloud DB
   * **5b. Local Static DB & Edge Engine:** แปลงข้อมูลลง **GenesisBlockDB Substrate + SQLite/DuckDB** ประจำ Vault ในเครื่องสำหรับ Edge Device, Analytics และ GraphRAG

---

## 🗄️ 2. Multi-Vault RAG Directory Structure (โครงสร้างโฟลเดอร์)

เพื่อรองรับ Vault ใหม่ๆ ในอนาคต (เช่น Catalog Vault, Customer Client Vault, Campaign Vault) ระบบจัดโครงสร้างโฟลเดอร์ดังนี้:

```text
o:\cat\
├── config/                               # ⚙️ สเปกสัญญาข้อมูล & Vault Manifest
│   ├── schema_genesisblock.yaml          # GenesisBlock Engine Schema (query-ir.v1)
│   ├── schema_postgresql.sql             # Supabase PostgreSQL DDL & pgvector
│   ├── openapi_spec.yaml                 # OpenAPI 3.0 Standard Endpoint Spec
│   └── vaults_manifest.json              # ทะเบียนกำกับ Vault ทั้งหมดในระบบ
│
├── data/                                 # 📥 Data Pipeline Workspace (แยกตาม Stage)
│   ├── 01_raw/                           # Stage 1: ไฟล์ต้นฉบับ Read-Only (FlowAccount, Sheets)
│   │   ├── flowaccount-product-raw.xlsx
│   │   └── google-sheet-catalog-raw.csv
│   ├── 02_prepared/                      # Stage 2: ข้อมูล JSON สะอาดหลัง Normalize
│   │   └── smartgift_catalog_master.json
│   ├── 03_staging_sql/                   # Stage 3: ไฟล์ SQL ที่แปลงเสร็จแล้ว
│   │   ├── smartgift-portfolio.postgres.sql
│   │   └── smartgift-customers.postgres.sql
│   └── 04_review_reports/                # Stage 4: รายงาน Audit & Approval Gates
│       └── product_id_mapping_report.json
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
│   ├── 01_intake.py                      # ดึงข้อมูลจากแหล่งต้นทาง
│   ├── 02_normalize_mapper.py            # สกัดรหัสสินค้า & ทำ Entity Mapping
│   ├── 03_export_sql.py                  # สรุปผลเป็นไฟล์ SQL มาตรฐาน
│   ├── 04_audit_review.py                # ตรวจสอบ Diff และสร้างรายงาน Review
│   └── 05_sync_edge_vaults.py            # ซิงก์ข้อมูลลง GenesisBlockDB & Static DBs
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
3. **Data Quality & Governance สูงสุด:** ผ่านการเตรียมข้อมูลและตรวจสอบ (Review + Approve) ก่อนส่งเข้า `zuri-ai` / Supabase Cloud DB เสมอ
