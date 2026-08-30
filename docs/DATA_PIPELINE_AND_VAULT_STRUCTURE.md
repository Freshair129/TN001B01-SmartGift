# 🏛️ Data Pipeline, Multi-Vault RAG & Static DB Architecture

**Document Version:** 1.1.0  
**Project:** SmartGift B2B E-commerce & Intelligent Portfolio System (`O:\Org-EtohGroup\SmartGift`)  
**Scope:** Multi-Vault RAG, Data Governance Pipeline, Review Gates, Edge Static DB & Upstream Sync

> **v1.1.0 (2026-08-30):** อัพเดทโครงสร้างโฟลเดอร์ให้ตรงกับ repo จริง (`data-pipeline/` แทน `data/`,
> root ที่ `O:\Org-EtohGroup\SmartGift` แทน `o:\cat`), เพิ่ม intake lane 01–08 ใน `01_raw/`
> (แก้เลข lane ซ้ำ `02_pricing_formulas` → `07_pricing_formulas` และเพิ่ม `08_factory_costs`)
> — ดู [ADR-005](decisions/ADR-005-FACTORY-COST-INTAKE-LANE.md)

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
1. **Stage 1: Intake Raw Data (`data-pipeline/01_raw/`):**
   * เก็บไฟล์ต้นฉบับแยกเป็น lane 01–08 (FlowAccount exports, ใบราคาโรงงาน PDF, แคตตาล็อก, เรทส่ง CBM, CRM, เอกสารธุรกิจ, สูตรราคา, ต้นทุนโรงงาน)
   * ทุก lane ที่มี archiver จะทำ SHA-256 versioning + immutable archive + registry + audit log
   * **กฎเหล็ก:** เป็นโซน **Read-Only / Immutable** ห้ามแก้ไขไฟล์ต้นฉบับโดยเด็ดขาด
2. **Stage 2: Preparation & Normalization (`pipeline/02_normalize_mapper.py`):**
   * ใช้ Regular Expression สกัด Product ID, Model Code, และ Supplier Tag (`P-xx`) ที่ฝังอยู่ในชื่อสินค้า
   * แปลงข้อมูลให้อยู่ในโครงสร้างมาตรฐาน (Canonical Schema)
3. **Stage 3: Staging SQL Generation (`data-pipeline/03_staging_sql/`):**
   * ผลิตไฟล์ SQL พร้อมนำเข้า เช่น `smartgift-portfolio.postgres.sql`, `smartgift-customers.postgres.sql`
4. **Stage 4: Review & Approval Gate (`data-pipeline/04_review_reports/`):**
   * สร้างรายงานตรวจสอบความถูกต้อง [product_id_mapping_report.json](file:///o:/cat/product_id_mapping_report.json)
   * แสดง Diff และความผิดปกติเพื่อรอการ Review + Approve
5. **Stage 5: Dual Distribution (แยก 2 ปลายทาง):**
   * **5a. Upstream Production:** ส่งไฟล์ `.sql` ที่ผ่านการ Approve เข้าสู่ `zuri-ai` / Supabase Cloud DB
   * **5b. Local Static DB & Edge Engine:** แปลงข้อมูลลง **GenesisBlockDB Substrate + SQLite/DuckDB** ประจำ Vault ในเครื่องสำหรับ Edge Device, Analytics และ GraphRAG

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
│   │   ├── 02_factory_pricelists_pdf/    #   ใบราคาโรงงาน PDF (path ถูกอ้างใน production manifest — ห้าม renumber)
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
│   ├── 03_staging_sql/                   # Stage 3: ไฟล์ SQL ที่แปลงเสร็จแล้ว
│   └── 04_review_reports/                # Stage 4: รายงาน Audit & Approval Gates
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
│   ├── master_orchestrator.py            # รัน pipeline 5 stage ตามลำดับ
│   ├── flowaccount_registry_archiver.py  # Stage 1: FlowAccount exports (SHA-256 versioning)
│   ├── pricing_formula_archiver.py       # Stage 1: pricing formula YAML (lane 07)
│   ├── factory_cost_archiver.py          # 🆕 Stage 1: factory cost files (lane 08, รองรับ .xls/.xlsx)
│   ├── extract_factory_costs.py          # 🆕 Stage 2: normalize supplier costs + proposed PM mapping
│   ├── 02_normalize_mapper.py            # Stage 2: สกัดรหัสสินค้า & ทำ Entity Mapping
│   ├── enrich_review_catalog.py          # Stage 3: review catalog + BOM enrichment
│   ├── export_pricelist_master.py        # Stage 3/4: pricelist master artifact
│   ├── 04_audit_review.py                # Stage 4: ตรวจสอบ Diff และสร้างรายงาน Review
│   └── 05_sync_edge_vaults.py            # Stage 5: ซิงก์ข้อมูลลง GenesisBlockDB & Static DBs
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
