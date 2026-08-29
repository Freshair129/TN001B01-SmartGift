# 🎁 SmartGift B2B E-commerce & Intelligent Portfolio System

**Enterprise Scope:** `Wannapa Workspace` ➔ `Org-EtohGroup` (Tenant) ➔ `SmartGift` (Business 01)  
**Operating Entity:** บริษัท เทราบิส จำกัด (`Therabis Co., Ltd.`)  
**Architecture:** 100% Local Multi-Engine (PostgreSQL / SQLite + GenesisBlockDB Native Edge Engine)

---

## 📌 ภาพรวมระบบ (Overview)

**SmartGift** คือระบบจัดพอร์ตชุดของขวัญองค์กรอัจฉริยะ (B2B Corporate Gift Set & Intelligent Portfolio System) ที่ขับเคลื่อนด้วย **Hybrid GraphRAG Search Engine** (< 1ms Latency), **Inventory Cascade Waterfall Decomposition Engine**, และ **Advanced Landed Cost & Ladder Pricing Engine**

---

## 🏛️ สถาปัตยกรรม 4 ระดับ (Four-Tier Cognitive Stack)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Scope Authority (zuri-ai)                                         │
│  • Scope Chain: Portfolio → Tenant (Org-EtohGroup) → Business (SmartGift) → Workspace    │
│  • Manages: CRM, Client PII, Financial Ledger Orders, Row Level Security (RLS)           │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-Resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Session, Memory & Vault Gatekeeper (MSP)                                        │
│  • API-010 (msp_vault_resolve): Maps workspace/project scope to Authorized Vault IDs     │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set: [vlt-catalog-product])
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Canonical Knowledge & GraphRAG Orchestrator (GKS)                               │
│  • Governs: Entity Ontology, Schema Contracts (smartgift://b2b/portfolio/v1)             │
│  • GraphRAG Engine: Hybrid Dense Vector (bge-m3 1024-dim) + Graph Traversal (query-ir.v1)│
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (In-Process Native Rust C-ABI)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 4: Local Storage Substrate (GenesisBlockDB Native + Edge Static DB)                 │
│  • 6-Lane Substrate: Vector, Lexical, Graph, SQLite, Bitemporal, Provenance             │
│  • Invariant: Stores ONLY Product Masters, Gift Offers & Sensory Vectors (Zero-PII)      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ โครงสร้างโปรเจกต์ (Repository Structure)

```text
O:\Org-EtohGroup\SmartGift\
├── config/                  # ⚙️ สเปกสัญญาข้อมูล OpenAPI, GenesisBlock & Postgres DDL
├── data-pipeline/           # 🔄 5-Stage Data Governance Pipeline
│   ├── 01_raw/              # Stage 1: ไฟล์ดิบแยกหมวด + Immutable Archive + Registry
│   ├── 02_prepared/         # Stage 2: Master Catalog SSOT (smartgift_catalog_master.json)
│   ├── 03_staging_sql/      # Stage 3: ไฟล์ SQL ที่แปลงเสร็จแล้ว
│   └── 04_review_reports/   # Stage 4: รายงาน Audit, Diff & Provenance Log
├── docs/                    # 📚 เอกสารสถาปัตยกรรมและ Change Requests ทั้งหมด
├── vaults/                  # 🔐 Multi-Vault Storage (GenesisBlockDB Native + SQLite)
├── pipeline/                # 🛠️ สคริปต์ Intake, Mapper, Versioning, Sync, Orchestrator
├── src/                     # 💻 Business Logic (Cascade BOM, Pricing Calculator, UI)
├── tests/                   # 🧪 Automated Unit Tests
├── AGENTS.md                # 🛡️ กฎเหล็กและข้อกำหนดของ AI Agents
├── README.md                # 📖 เอกสารภาพรวมฉบับนี้
├── run_pipeline.py          # 🚀 คำสั่งรัน Master Data Pipeline 5 ขั้นตอน
└── demo_app.py              # 🎮 Interactive Terminal Demo
```

---

## 🚀 การเริ่มต้นใช้งาน (Quick Start)

### 1. ติดตั้ง Dependencies
```bash
npm install
```

### 2. รัน Master Data Pipeline (5 Stages)
```bash
py -3 run_pipeline.py
```

### 3. รัน Unit Tests ทั้งหมด
```bash
py -3 -m unittest discover tests
```

### 4. เปิด Interactive Demo Terminal
```bash
py -3 demo_app.py
```

---

## 📚 เอกสารเพิ่มเติม (Documentation in `/docs`)

* 🌐 [Zuri Ecosystem System Boundaries & Integration Blueprint](docs/ZURI_ECOSYSTEM_BOUNDARIES.md)
* 🏛️ [System Architecture Blueprint](docs/SMARTGIFT_SYSTEM_ARCHITECTURE.md)
* 📋 [Change Request (CR) for Zuri-AI, MSP & GKS Integration](docs/CR-GKS-MSP-VAULT-INTEGRATION.md)
* 📖 [Data Pipeline & Multi-Vault Structure Specification](docs/DATA_PIPELINE_AND_VAULT_STRUCTURE.md)
* 🛡️ [AI Agent Rules & Governance Invariants](AGENTS.md)
