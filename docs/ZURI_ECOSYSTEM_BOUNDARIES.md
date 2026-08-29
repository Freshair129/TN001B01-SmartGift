# 🌐 Zuri Ecosystem System Boundaries & Integration Blueprint

**Document Version:** 1.0.0  
**Enterprise Scope:** `Wannapa Workspace` ➔ `Org-EtohGroup` (Tenant) ➔ `SmartGift` (Business 01)  
**Operating Legal Entity:** บริษัท เทราบิส จำกัด (`Therabis Co., Ltd.`)  
**Target Systems:** `zuri-ai`, `zuri-edge-device`, `MSP`, `GKS`, and `SmartGift`  

---

## 🏛️ 1. ภาพรวมขอบเขตสถาปัตยกรรม (System Boundary Overview)

เอกสารฉบับนี้กำหนด **ขอบเขตความรับผิดชอบ (Separation of Concerns)**, **กรรมสิทธิ์ในข้อมูล (Data Ownership)**, และ **ส่วนต่อประสาน (Interfaces & Contracts)** ระหว่างระบบ **SmartGift (Business 01)** กับระบบต่างๆ ใน **Zuri Ecosystem**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Business Authority (zuri-ai & zuri-edge-device)                   │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • zuri-ai (D:\zuri-ai): Cloud PostgreSQL / Supabase, Users, CRM, Orders, Invoices (PII) │
│  • zuri-edge-device (D:\workspace\zuri-edge-device): Local Host Runtime & Local LLM Hub │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-Resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Memory & Vault Gatekeeper (MSP / D:\msp)                                        │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Unified Thread ID, Episodic Memory, Token Budget, H0-H4 Ceilings             │
│  • API-010 (msp_vault_resolve): Resolves Workspace Scope ➔ [vlt-catalog-product]        │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Canonical Knowledge & GraphRAG Orchestrator (GKS / D:\gks)                      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Canonical Ontology Registry, Radius (R0-R6) GraphRAG Routing, Deduplication │
│  • Contract: smartgift://b2b/portfolio/v1 (v1.3.0) via Query IR (query-ir.v1)            │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (In-Process Native Rust C-ABI NAPI)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 4: Dedicated Storage Substrate (SmartGift Engine / O:\Org-EtohGroup\SmartGift)     │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Substrate: GenesisBlockDB Native (v0.2.5) + Static SQLite (projection.sqlite)         │
│  • Invariant: Zero-PII Product Catalog & Sensory Vectors Only (< 1ms Latency)            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ 2. ตารางผูกความสัมพันธ์ (Domain & Scope Binding Matrix)

| Entity ใน Zuri Ecosystem | SmartGift Domain Mapping | กรรมสิทธิ์และการจัดเก็บข้อมูล (Data Ownership) |
| :--- | :--- | :--- |
| **`Portfolio`** | `Wannapa Workspace` (Portfolio Root) | Tier 1 (`zuri-ai` DB) |
| **`Tenant` / `Organization`** | **`Org-EtohGroup`** (`tenantId`) | Tier 1 (`zuri-ai` DB) |
| **`Business`** | **`SmartGift`** (`businessId` / Business 01) | Tier 1 & SmartGift Repo |
| **`LegalEntity`** | **บริษัท เทราบิส จำกัด** (`Therabis Co., Ltd.`) | Tier 1 (ทะเบียนนิติบุคคล / ผู้ถือคลัง) |
| **`Workspace` / `Project`** | SmartGift 2026 Portfolio Campaign | Tier 1 (ผูก `catalogVaultId`) |
| **`Product Catalog Vault`** | **`vlt-catalog-product`** (UUIDv7) | **SmartGift Tier 4 (Zero-PII)** |
| **`Customer CRM Vault`** | **`vlt-customer-client`** (PII-Gated) | Tier 1 & Tier 2 Gated Auth |
| **`Orders & Ledger`** | คำสั่งซื้อ, ใบเสนอราคา, ใบวางบิล | Tier 1 (`zuri-ai` PostgreSQL / FlowAccount) |

---

## 🛡️ 3. กฎเหล็กขอบเขตระบบ (System Boundaries & Invariants)

### 1. **ขอบเขตความปลอดภัยของข้อมูลลูกค้า (Zero-PII Invariant ใน Vector Vault)**
* **กฎ:** โฟลเดอร์ `vaults/vlt-catalog-product/genesis-db/` **เก็บได้เฉพาะข้อมูลสินค้าเท่านั้น** (ProductMaster, CatalogOffer, BOM, Sensory Vectors)
* ❌ **ห้ามเก็บรายชื่อลูกค้า (`Customer`), เบอร์โทร, ที่อยู่ หรือประวัติการเงินใน Vector Vault โดยเด็ดขาด**
* ข้อมูลลูกค้า (PII) ทั้งหมดต้องถูกเก็บไว้ใน **PostgreSQL / Supabase Tier 1 (`zuri-ai`)** ที่มีระบบ Row Level Security (RLS) ล็อกสิทธิ์เท่านั้น

---

### 2. **ขอบเขตการเข้าถึงคลังข้อมูล (Zuri Edge Device Isolation)**
* **กฎ:** SmartGift จะรันฐานข้อมูล GenesisBlockDB ในโฟลเดอร์ของตัวเอง (`O:\Org-EtohGroup\SmartGift\vaults\vlt-catalog-product\genesis-db`)
* ❌ **ห้ามเข้าไปเขียนหรือเปิดไฟล์ใน `D:\workspace\zuri-edge-device\data\genesis_smartgift_store_v4\` โดยตรง** เนื่องจากเป็นคลังที่ถูกดูแลโดย Ingestion Pipeline ส่วนกลางของ Zuri Edge Device ที่มีการควบคุมการสลับรอบด้วยพอยน์เตอร์ `CURRENT`

---

### 3. **ขอบเขตการสร้างรหัสเอกลักษณ์ (GKS Canonical Identity Boundary)**
* **กฎ:** การออกรหัสที่เป็น Canonical Entity กลางระดับองค์กร ต้องทำผ่าน **GKS (`D:\gks`)**
* ❌ **ห้ามสร้างรหัส Prefix `gks:` ขึ้นมาเองใน SmartGift** ให้ใช้ Namespace เฉพาะของโดเมนตัวเอง เช่น `offer:`, `pm:`, `cat:`, `tier:` ตามสัญญา `smartgift://b2b/portfolio/v1`

---

### 4. **ขอบเขตการระบุสิทธิ์และ Memory (MSP Boundary)**
* **กฎ:** **MSP (`D:\msp`)** เป็นผู้คุมเซสชัน และเป็นคนเรียก API-010 (`msp_vault_resolve`) เพื่อแปลง `workspaceId` เป็น `vault_id` (`vlt-catalog-product`)
* SmartGift ให้บริการสืบค้น GraphRAG ข้อมูลสินค้า โดยปฏิบัติตาม Context Token Budget และ Security Ceilings (H0-H4) ที่ MSP กำหนด

---

### 5. **ขอบเขตความถูกต้องของราคา (Price Authority Invariant)**
* **กฎ:** ราคาขายส่งและต้นทุนสินค้าให้อิงจากไฟล์ส่งออกของ FlowAccount (`smartgift-portfolio.postgres.sql`) และระบบคำนวณราคา [pricing_calculator.py](file:///O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py)
* ไฟล์ดิบ `บริษัท เทราบิส จำกัด_product.xlsx` ใน `data-pipeline/01_raw/` เป็น **Read-Only 100%** ห้ามดัดแปลงแก้ไข

---

## 🔌 4. ส่วนต่อประสานระหว่างระบบ (Interfaces & Communication Protocols)

```text
┌──────────────┐                               ┌──────────────┐
│   zuri-ai    │ ─── (1) AuthContext Envelope ──> │     MSP      │
└──────────────┘                               └──────────────┘
                                                       │
                                      (2) Authorized Vault Set: [vlt-catalog-product]
                                                       ▼
┌──────────────┐                               ┌──────────────┐
│  SmartGift   │ <── (3) query-ir.v1 Query ─── │     GKS      │
│ Vector Vault │                               │ Orchestrator │
└──────────────┘                               └──────────────┘
```

1. **`zuri-ai` ➔ `MSP`:** ส่ง AuthContext พร้อมระบุ `catalogVaultId: "vlt-catalog-product"`
2. **`MSP` ➔ `GKS`:** ทำการ Resolve Scope และส่ง Authorized Vault Set พร้อมจัดสรร Token Budget
3. **`GKS` ➔ `SmartGift GenesisBlockDB`:** ส่งคำสั่งสืบค้นผ่านโปรโตคอล **Query IR (`query-ir.v1`)** เพื่อดึงเวกเตอร์สัมผัสแกะกล่องและ Traversing BOM Edges (< 1ms)
