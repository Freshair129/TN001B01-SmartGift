# 🎁 SmartGift B2B E-commerce & Intelligent Portfolio System

**Enterprise Scope:** `Wannapa Workspace` ➔ `Org-EtohGroup` (Tenant) ➔ `SmartGift` (Business 01)  
**Operating Entity:** บริษัท เทราบิส จำกัด (`Therabis Co., Ltd.`)  
**Architecture:** 100% Local Multi-Engine (PostgreSQL / SQLite + GenesisBlockDB Native Edge Engine)  
**Contract Authority:** `smartgift://b2b/portfolio/v1` (Schema Authority: [`config/schema_genesisblock.yaml`](config/schema_genesisblock.yaml))

---

## 📌 1. ภาพรวมระบบ (System Overview)

**SmartGift** คือระบบจัดพอร์ตชุดของขวัญองค์กรอัจฉริยะ (B2B Corporate Gift Set & Intelligent Portfolio System) ที่เปลี่ยนกระบวนทัศน์จากการนำเสนอแบบ *"ร้านรวมสินค้าพรีเมียมทั่วไป"* ไปสู่ **"ระบบออกแบบของขวัญองค์กรตามกลุ่มผู้รับ (Recipient-first Corporate Gifting)"** ขับเคลื่อนด้วย:

* ⚡ **Hybrid GraphRAG Search Engine:** ค้นหาสินค้าและเซ็ตของขวัญตามประสาทสัมผัส (Sensory), ธีม (Theme), และระดับการดูแล (Gift Tier) ด้วย Sub-millisecond Latency
* 💧 **BOM Waterfall Inventory Cascade Engine:** ตัดสต็อกและคำนวณความพร้อมของชุดของขวัญตามส่วนประกอบย่อยแบบไม่ติดลบ (`inventory_qty >= 0`)
* 💰 **Landed Cost & Ladder Pricing Engine:** คำนวณราคาขายตามขั้นบันได (Tier Pricing) สะท้อนต้นทุนนำเข้า ค่าขนส่ง และอัตรากำไรขั้นต่ำ (Profit Gate)
* 🎨 **Interactive 3D / Web Catalog:** แคตตาล็อกสำหรับลูกค้าและฝ่ายขาย แสดงภาพเสมือนจริง 3D Model (`.glb`) และมุมมองแยกชิ้นส่วนของขวัญ (Gift Anatomy)

---

## 🏛️ 2. สถาปัตยกรรม 4 ระดับ (Four-Tier Cognitive Stack)

ระบบแยกขอบเขตความรับผิดชอบและความปลอดภัยออกเป็น 4 ระดับอย่างเคร่งครัดตามมาตรฐาน **ADR-041 ถึง ADR-044**:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Scope Authority (zuri-ai / Cloud Layer)                            │
│  • Scope Chain: Portfolio → Tenant (Org-EtohGroup) → Business (SmartGift) → Workspace    │
│  • Manages: CRM, Client PII, Financial Ledger Orders, Row Level Security (RLS)           │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-Resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Session, Memory & Vault Gatekeeper — Memory-and-Soul-Passport (MSP)             │
│  • Contract: API-009 (Persistent Memory) & Scope-to-Vault Resolution                     │
│  • Gatekeeper: ตรวจสอบสิทธิ์การเข้าถึง Vault ID ประจำโปรเจกต์ [vlt-catalog-product]       │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set: [vlt-catalog-product])
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Canonical Knowledge & GraphRAG Orchestrator — Genesis-Knowledge-System (GKS)    │
│  • Governs: Entity Ontology, Canonical Data Contract (schema_genesisblock.yaml)          │
│  • GraphRAG Engine: Hybrid Dense Vector (bge-m3 1024-dim) + Graph Traversal              │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (In-Process Native Rust C-ABI)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 4: Local Storage Substrate (GenesisBlockDB Native + Edge Static DB)                 │
│  • 6-Lane Substrate: Vector, Lexical, Graph, SQLite, Bitemporal, Provenance             │
│  • Invariant: เก็บเฉพาะ Product Master, Gift Offer, BOM Edges (Zero-PII เคร่งครัด)       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ 3. โครงสร้างโปรเจกต์จริง (Repository Structure & Directory Index)

```text
.
├── AGENTS.md                  # 🛡️ กฎเหล็ก ธรรมาภิบาล และข้อกำหนดการทำงานของ AI Agents (v1.0.1b)
├── PRODUCT.md                 # 🎯 วิสัยทัศน์ผลิตภัณฑ์ บุคลิกแบรนด์ และหลักการออกแบบ Customer Catalog
├── README.md                  # 📖 สารบัญและเอกสารภาพรวมโปรเจกต์ฉบับนี้
├── run_pipeline.py            # 🚀 สคริปต์รัน Master Data Pipeline ครบวงจร 5 ขั้นตอน
├── demo_app.py                # 🎮 Interactive CLI Demo: ค้นหา GraphRAG, จำลองจัดเซ็ต, ตัดสต็อก Cascade
├── run_e2e_flowaccount_demo.py# 🧪 สคริปต์รัน E2E Pipeline จาก FlowAccount Export สู่ Catalog
├── seed_genesisblock.mjs      # ⚡ สคริปต์ Seed ข้อมูลแคตตาล็อกเข้า GenesisBlockDB
├── test_genesis.mjs           # 🧪 ทดสอบการเชื่อมต่อและการอ่านข้อมูล GenesisBlockDB
├── package.json / vercel.json # ⚙️ การตั้งค่า Node.js dependencies และการ Deploy Web API
│
├── api/                       # 🌐 Vercel Serverless Functions / Web APIs
│   ├── _public_data.js        # Data Loader ปลอดภัย (Zero-PII) สำหรับ Web APIs
│   ├── catalog.js             # API ดึงรายการแคตตาล็อกสินค้าและชุดของขวัญ
│   ├── pricelist.js           # API ดึงรายการราคาขั้นบันไดและ Tier Pricing
│   ├── media.js               # API ส่งคืนรูปภาพและสื่อประกอบสินค้า
│   └── health.js              # API ตรวจสอบสถานะความพร้อมของระบบ
│
├── asset/                     # 🎨 แหล่งเก็บ 3D Assets (.glb) และสื่อดิจิทัลต้นฉบับ
│
├── config/                    # ⚙️ สัญญาข้อมูลและสเปกโครงสร้าง (Data Contracts & Schemas)
│   ├── schema_genesisblock.yaml # 👑 Canonical Authority Schema (ID Prefixes, Entities, Edges)
│   ├── openapi_spec.yaml      # สเปก OpenAPI v3 สำหรับ B2B Catalog API
│   ├── schema_postgresql.sql  # DDL สคริปต์โครงสร้างฐานข้อมูล PostgreSQL
│   ├── schema_neo4j.cypher    # Cypher Query สคริปต์โครงสร้าง Graph Database
│   ├── pricing_rules_formula.yaml # สูตรและกฎการคำนวณราคา/Margin
│   ├── shipping_rate_matrix.json/yaml # ตารางอัตราค่าขนส่งตามระยะทางและขนาด
│   ├── vaults_manifest.json   # รายการลงทะเบียน Vaults ประจำโปรเจกต์
│   └── agent_automation_manifest.json # การตั้งค่า Automation triggers ของ Agent
│
├── data-pipeline/             # 🔄 5-Stage Data Governance Pipeline
│   ├── 01_raw/                # Stage 1: ไฟล์ดิบ (Excel, SQL Export) + Immutable Snapshot
│   ├── 02_prepared/           # Stage 2: Master SSOT (smartgift_catalog_master.json / pricelist)
│   ├── 03_staging_sql/        # Stage 3: ผลลัพธ์จากการ Enrich & Staging
│   └── 04_review_reports/     # Stage 4: รายงาน Audit, Diff Log และ Provenance Metadata
│
├── docs/                      # 📚 แหล่งรวบรวมเอกสารการออกแบบ สถาปัตยกรรม และสเปกทั้งหมด
│   ├── business/              # 🏢 ยุทธศาสตร์ธุรกิจ, GTM, Sales Playbook, Taxonomy (มี INDEX.md)
│   ├── decisions/             # 🏛️ Architecture Decision Records (ADR-001 ถึง ADR-008)
│   ├── specs/                 # 📐 สเปกเทคนิค (3D Viewer, Image-First Catalog, Knowledge Registry)
│   ├── change-requests/       # 📋 Change Requests สำหรับ Zuri-AI Integration (CR-002 ถึง CR-006)
│   ├── Agent-Marketing/       # 🤖 สเปก Visual AI Agent Marketing Team (PRD, SRS, SPEC, TDD)
│   └── references/            # 📑 เอกสารอ้างอิงสถาปัตยกรรม Zuri และ Ecosystem
│
├── output/                    # 📤 ไฟล์ผลลัพธ์จากการ Build Catalog (JSON, HTML, Bundles)
│
├── pipeline/                  # 🛠️ โมดูลและสคริปต์การแปลงข้อมูล (Pipeline Execution Modules)
│   ├── 01_intake.py           # นำเข้าไฟล์ดิบเข้าสู่ Pipeline
│   ├── 02_normalize_mapper.py # แปลงข้อมูลดิบเป็น Canonical GenesisBlock Schema
│   ├── 04_audit_review.py     # ตรวจสอบความถูกต้องและสร้างรายงาน Audit
│   ├── 05_sync_edge_vaults.py # ซิงค์ข้อมูล Master Catalog เข้าสู่ GenesisBlockDB
│   ├── export_pricelist_master.py # สกัดราคาและสร้าง Pricelist Master จาก FlowAccount SQL
│   ├── extract_factory_costs.py # สกัดต้นทุนโรงงาน (Factory Cost Lane)
│   ├── build_offline_catalog.py # ประกอบแคตตาล็อกฉบับ Offline/Static
│   ├── enrich_review_catalog.py # เติมเต็มข้อมูลรูปภาพ มิติ และประสาทสัมผัส
│   ├── master_orchestrator.py # ตัวควบคุมการทำงานของ Pipeline ทุกขั้นตอน
│   └── knowledge_registry/    # ระบบ Registry ติดตามที่มาของข้อมูล (Provenance)
│
├── price-boss/                # 💰 Price Boss Submodule (ระบบคำนวณราคาและซิงค์ฐานข้อมูล)
│   ├── sql/                   # สคริปต์ SQL ฐานราคา FlowAccount (`smartgiftpricelist.postgres.sql`)
│   ├── pricing.html           # หน้าจอคำนวณและเปรียบเทียบราคา
│   ├── sync_smartgift.py      # ซิงค์ข้อมูลราคาระหว่าง Price Boss กับ SmartGift Catalog
│   └── server/                # Web Server ประจำโมดูล Price Boss
│
├── public/                    # 🌐 Web Application & Interactive Customer Catalog
│   ├── index.html             # หน้าหลัก Customer Catalog (Image-First & 3D Viewer)
│   ├── internal.html          # หน้าจอภายในสำหรับตรวจเช็กรายการสินค้าและราคา
│   ├── customer-catalog.js    # Logic แสดงผลแคตตาล็อก การค้นหา และการกรอง
│   ├── gift-anatomy-3d.js     # Three.js 3D Viewer สำหรับดูโมเดลและการแยกชิ้นส่วนของขวัญ
│   ├── customer-catalog.css   # ดีไซน์และสไตล์ชีทแบบ Responsive & Modern Dark/Light
│   └── serve.py               # Local Development Server สำหรับทดสอบ Web Catalog
│
├── scripts/                   # 🔧 สคริปต์เครื่องมือเสริม (Utility Scripts)
│   ├── extract_customer_catalog_photos.py # สกัดรูปภาพสำหรับใช้งานบน Web Catalog
│   └── catalog3d/             # สคริปต์ประมวลผล 3D Assets และ Preview
│
├── src/                       # 💻 Core Business Logic & Engines
│   ├── cascade_engine/        # 💧 BOM Cascade Waterfall Stock & Pricing Calculator
│   ├── graphrag_agent/        # ⚡ Unboxing Sensory GraphRAG Search Engine
│   └── ui/                    # โมดูล UI Console & Helpers
│
├── tests/                     # 🧪 ชุดการทดสอบอัตโนมัติ (Automated Unit & Integration Tests)
│   ├── test_pricing_calculator.py
│   ├── test_cascade_engine.py
│   ├── test_graphrag_search.py
│   ├── test_zero_pii_vault.py
│   └── test_schema_genesisblock.py
│
└── vaults/                    # 🔐 Multi-Vault Local Storage Substrates
    └── vlt-catalog-product/   # Zero-PII Canonical Product & Offer Master (GenesisBlockDB)
        └── genesis-db/        # Native Storage Files (Vector, Lexical, Graph, SQLite)
```

---

## 📚 4. สารบัญเอกสารโครงการ (Master Documentation Index)

| หมวดหมู่ | ไดเรกทอรี / เอกสารสำคัญ | คำอธิบายสาระสำคัญ |
|---|---|---|
| **ยุทธศาสตร์ธุรกิจ & การขาย** | [**`docs/business/INDEX.md`**](docs/business/INDEX.md) | **ดัชนีรวมเอกสารธุรกิจ:** สถาปัตยกรรมแบรนด์, แผนเข้าตลาด (GTM), คู่มือการขาย (Sales Playbook), กฎจัดเซ็ตสินค้า (Taxonomy & Offer Rules) และแม่แบบ Brief ผู้รับ (Recipient Matrix) |
| **การตัดสินใจเชิงสถาปัตยกรรม** | [**`docs/decisions/`**](docs/decisions/) | **ADR-001 ถึง ADR-008:** บันทึกการตัดสินใจทางเทคนิค เช่น Eco-Friendly Category, Snapshot ราคา SQL, กำไรขั้นต่ำ Seasonal PKG, และ Private Repo Source Data Exception (ADR-006) |
| **สเปกทางเทคนิค (Technical Specs)** | [**`docs/specs/`**](docs/specs/) | สเปก 3D Assets/Viewer ([`SPEC-PRODUCT-3D-ASSETS`](docs/specs/SPEC-PRODUCT-3D-ASSETS-2026-08-31.md), [`SPEC-PRODUCT-3D-VIEWER`](docs/specs/SPEC-PRODUCT-3D-VIEWER-2026-08-31.md)), แคตตาล็อกฉบับรูปภาพ ([`SPEC-CUSTOMER-CATALOG-IMAGE-FIRST`](docs/specs/SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30.md)), Knowledge Registry ([`SPEC-KNOWLEDGE-REGISTRY`](docs/specs/SPEC-KNOWLEDGE-REGISTRY-2026-08-31.md)), และ ERD GenesisBlock |
| **Change Requests (Zuri-AI)** | [**`docs/change-requests/`**](docs/change-requests/) | ข้อเสนอการเชื่อมต่อกับระบบหลัก Zuri-AI: CR-002 (Vault Resolution), CR-003 (Governance Gates), CR-004 (Files Tab), CR-005 (Shipping Matrix), CR-006 (Zero-PII & File Intake) |
| **Visual AI Agent Marketing** | [**`docs/Agent-Marketing/`**](docs/Agent-Marketing/) | ชุดเอกสารพัฒนาระบบ Visual AI Marketing: [`PRD`](docs/Agent-Marketing/PRD-Visual-AI-Agent-Marketing-Team.md), [`SRS`](docs/Agent-Marketing/SRS-Visual-AI-Agent-Marketing-Team.md), [`SPEC`](docs/Agent-Marketing/SPEC-Visual-AI-Agent-Marketing-Team.md), [`TDD`](docs/Agent-Marketing/TDD-Visual-AI-Agent-Marketing-Team.md) |
| **เอกสารอ้างอิง Ecosystem** | [**`docs/references/`**](docs/references/) | สถาปัตยกรรมและ Schema การเชื่อมต่อภาพรวม: [`ZURI_ECOSYSTEM_BOUNDARIES.md`](docs/ZURI_ECOSYSTEM_BOUNDARIES.md), [`DATA_PIPELINE_AND_VAULT_STRUCTURE.md`](docs/DATA_PIPELINE_AND_VAULT_STRUCTURE.md), [`SMARTGIFT_SYSTEM_ARCHITECTURE.md`](docs/business/SMARTGIFT_SYSTEM_ARCHITECTURE.md) |

---

## 🔄 5. วงจรการทำงานของ Data Pipeline (5-Stage Data Governance)

```text
[Stage 1: 01_raw] ───► [Stage 2: 02_prepared] ───► [Stage 3: 03_staging] ───► [Stage 4: 04_reports] ───► [Stage 5: vaults]
  • FlowAccount SQL       • smartgift_catalog_master.json • Enrich Media/Dims     • Audit Diff Log         • vlt-catalog-product
  • Factory Costs         • smartgift_pricelist_master.json • Profit Gate Calc     • Provenance Record      • GenesisBlockDB Sync
  • Immutable Archive     • Canonical ID Mappings         • Ladder Pricing                                  • Zero-PII Verified
```

1. **Stage 1 (Raw Intake):** รับไฟล์ดิบจาก FlowAccount และไฟล์ต้นทุนโรงงาน บันทึกสำเนาแบบไม่แก้ไข (Immutable Archive)
2. **Stage 2 (Prepared Master):** แปลงข้อมูลเข้าสู่ Canonical Schema (`cat:`, `pm:`, `offer:`, `bundle:`, `tier:`, `seg:`) สร้าง Master SSOT JSON
3. **Stage 3 (Enrichment & Profit Gate):** เติมเต็มข้อมูลรูปภาพ มิติ น้ำหนัก และตรวจสอบเกณฑ์กำไรขั้นต่ำ (Profit Margin Gate)
4. **Stage 4 (Audit & Provenance):** ตรวจสอบความถูกต้อง บันทึกประวัติการเปลี่ยนแปลง (Diff) และสร้าง Audit Report
5. **Stage 5 (Vault Synchronization):** บันทึกข้อมูลลงสู่ GenesisBlockDB Native Vault (`vlt-catalog-product`) สำหรับการสืบค้นความเร็วสูง

---

## 🛡️ 6. กฎเหล็กด้านความปลอดภัยและธรรมาภิบาล (Non-Negotiable Invariants)

ตามที่ระบุไว้ใน [**`AGENTS.md`**](AGENTS.md):

1. 🔒 **Zero-PII in Vector Vault:** `vlt-catalog-product` ต้องมีเฉพาะข้อมูลแคตตาล็อกสินค้า ห้ามบันทึกชื่อลูกค้า เบอร์ติดต่อ หรือประวัติการเสนอราคาเด็ดขาด
2. 🏷️ **Price Authority:** ห้ามแก้ไขไฟล์ Excel ดิบโดยตรง สิทธิ์ราคาต้องอ้างอิงจาก FlowAccount SQL Export (`price-boss/sql/smartgiftpricelist.postgres.sql`) และคำนวณผ่าน [`src/cascade_engine/pricing_calculator.py`](src/cascade_engine/pricing_calculator.py)
3. 📦 **Inventory Non-Negative:** ห้ามปรับแก้เงื่อนไขสต็อกติดลบ (`inventory_qty >= 0`) และต้องใช้ตรรกะ Waterfall Decomposition ในการตัดสต็อกเสมอ
4. 📜 **GenesisBlock Schema is Canon:** ทุก Entity และ Edge ต้องเป็นไปตาม [`config/schema_genesisblock.yaml`](config/schema_genesisblock.yaml) อย่างเคร่งครัด
5. 🔏 **Private Repository Boundary (ADR-006):** อนุญาตเฉพาะไฟล์ที่ได้รับการยกเว้นตาม Allowlist ใน `.gitignore` บน Private Repo เท่านั้น ห้ามนำ PII ขึ้น Public Repositories

---

## 🚀 7. คำสั่งเริ่มต้นใช้งาน (Quick Start & Commands)

### 1. ติดตั้ง Dependencies
```bash
npm install
```

### 2. รัน Master Data Pipeline 5 ขั้นตอน
```bash
py -3 run_pipeline.py
```

### 3. รัน Unit Tests ทั้งหมด
```bash
py -3 -m unittest discover tests
```

### 4. รัน Web Catalog Development Server (ดูหน้าเว็บ 3D Catalog)
```bash
python public/serve.py
# เปิดเบราว์เซอร์ไปที่: http://localhost:8080
```

### 5. รัน Interactive Demo CLI ใน Terminal
```bash
py -3 demo_app.py
```
