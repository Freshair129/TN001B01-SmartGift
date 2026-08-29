# 📋 Change Request (CR): Multi-Tier Scope Chain to GKS/MSP Catalog Vault Resolution

**Document ID:** `CR-2026-08-30-GKS-MSP-VAULT-01`  
**Target Repositories:** `D:\zuri-ai` (Tier 1), `D:\msp` (Tier 2), `D:\gks` (Tier 3), `O:\cat` (SmartGift B2B Domain)  
**Author:** SmartGift B2B Portfolio & Data Architecture Team  
**Status:** PROPOSED / READY FOR AGENT HANDOVER  
**Related ADRs:** ADR-022, ADR-041 (Zuri Edge Device), ADR-042 (Standalone GraphRAG), ADR-043 (Four-Tier Cognitive Stack), ADR-044 (Unified Thread ID)  
**Related Features:** FR-057 (Authorized Agent Context & Vault Resolution), FR-079 (Model Connection Cut-over), FR-098 (Agent/Tool/MSP Authorization)

---

## 🏛️ 1. Architecture Topology: 4-Tier Cognitive Stack

ก่อนส่งต่อให้ Agent ใน `D:\zuri-ai`, `D:\msp`, และ `D:\gks` ดำเนินการ สรุปลำดับสแต็กการทำงาน (Who manages what) ไว้ดังนี้:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Scope Authority (zuri-ai / D:\zuri-ai)                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Scope Chain: Portfolio → Tenant → Business → Workspace → Project (BR-001)            │
│  • Source of Truth: prisma/schema.prisma (Postgres / Supabase / SQLite)                  │
│  • Manages: Users, Memberships, Customer PII, Financial Transactions, Orders             │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Session, Memory & Vault Gatekeeper (MSP / D:\msp)                               │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • Governs: Unified Thread ID, Episodic Memory, Token Budget, H0-H4 Access Ceilings     │
│  • API-010 (msp_vault_resolve): Maps server-owned workspace/project scope to Vault IDs   │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set: [vlt-smartgift-2026])
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
│  Tier 4: Storage Substrate (GenesisBlockDB Native / smartgift-genesis-db)                │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  • 6-Lane Substrate: Vector, Lexical, Graph, SQLite, Bitemporal, Provenance             │
│  • Invariant: Stores ONLY Product Masters, Gift Offers & Sensory Vectors (Zero-PII)      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ 2. Domain Entity Mapping (SmartGift B2B ↔ zuri-ai Scope Chain)

ตารางเปรียบเทียบการแมปความสัมพันธ์ระหว่างระบบ **SmartGift B2B E-commerce (`O:\cat`)** กับ **`schema-zuri-ai.md` (`D:\zuri-ai`)**:

| `schema-zuri-ai.md` (Scope Chain) | Zuri Production Scope | SmartGift B2B Domain Mapping | หน้าที่ / ขอบเขตความรับผิดชอบ |
| :--- | :--- | :--- | :--- |
| **`Workspace`** | `Wannapa Workspace` | Operational Environment | พื้นที่ทำงานหลักระดับบนสุด |
| **`Tenant` / `Organization`** | `Org-EtohGroup` | Organization Boundary | ขอบเขตองค์กร / เครือธุรกิจ (`tenantId: Org-EtohGroup`) |
| **`Business`** | `SmartGift` (Business01) | B2B Gift Business Unit | ธุรกิจจัดชุดของขวัญ B2B (`businessId: SmartGift`) |
| **`LegalEntity`** | บริษัท เทราบิส จำกัด | Operating Corporation | นิติบุคคลผู้ดำเนินธุรกิจและเจ้าของคลังสินค้า |
| **`Project`** | SmartGift 2026 Portfolio | Catalog Campaign | แคมเปญจัดชุดของขวัญ / แคตตาล็อก (`projectId`) |
| **`KnowledgeVault` (ขอเพิ่ม)** | `vlt-smartgift-2026` | Catalog & Sensory Vault | คลังความรู้ Vector & Graph สินค้า (Zero-PII UUIDv7) |
| **`Customer` / `Session`** | Corporate Client / PIC | B2B Procurement Buyers | ผู้สั่งซื้อ (เก็บเฉพาะใน Tier 1 PostgreSQL) |

---

## 📝 3. รายละเอียด Change Request (CR Specifications)

### 🎯 วัตถุประสงค์
1. เปิดทางให้ **Tier 1 (`zuri-ai`)** สามารถผูก **`vault_id` / `catalogVaultRef`** เข้ากับ `Workspace` หรือ `Project` ได้
2. ให้ **Tier 2 (`MSP`)** ฟังก์ชัน `msp_vault_resolve` (API-010) สามารถแปลงสิทธิ์ Workspace/Project ไปเป็น `vault_id` ของ SmartGift Catalog ได้
3. ให้ **Tier 3 (`GKS`)** รับสืบค้นข้อมูลสินค้าผ่าน Query IR (`query-ir.v1`) จาก Substrate **Tier 4 (`GenesisBlockDB`)** โดยยังคงกฎเหล็ก **Zero-PII (ห้ามเก็บข้อมูลลูกค้า/คำสั่งซื้อใน Vector Vault)**

---

### 📦 รายการสิ่งที่ขอแก้ไขในแต่ละ Repository (Action Items for Agents):

#### **A. ฝั่ง Tier 1: `D:\zuri-ai` (`prisma/schema.prisma` & `schema-zuri-ai.md`)**
1. **เพิ่มฟิลด์ใน Model `Workspace` หรือ `Project`:**
   ```prisma
   // prisma/schema.prisma
   model Workspace {
     // ... existing fields ...
     catalogVaultId   String?   // UUIDv7 / vlt-{tenant_code} (เช่น vlt-smartgift-2026)
     vaultNamespace   String?   // e.g. "smartgift://b2b/portfolio/v1"
   }
   ```
2. **อัปเดต AuthContext Resolver (`src/modules/agent/auth-context.js`):**
   * ให้แนบ `catalogVaultId` เข้าไปใน Request Envelope เมื่อเรียกใช้งาน Agent ในบริบท B2B Gift Catalog

---

#### **B. ฝั่ง Tier 2: `D:\msp` (Memory Service Provider & Vault Resolution)**
1. **อัปเดต API-010 `msp_vault_resolve`:**
   * ตรวจสอบว่าหาก Scope มีการผูก `catalogVaultId` ให้เพิ่ม Vault ID นั้นเข้าสู่ **Authorized Vault Set** สำหรับ Turn การสนทนานั้น
   * บังคับใช้ Security Ceilings (H0-H4) และ Token Budget ไม่ให้ Memory ของลูกค้าข้ามไปปนเปื้อนใน Catalog Vault

---

#### **C. ฝั่ง Tier 3: `D:\gks` (Genesis Knowledge System & RAG Orchestrator)**
1. **ลงทะเบียน Schema Contract ใน GKS Registry:**
   * ลงทะเบียน `schema_ref: "smartgift://b2b/portfolio/v1"` (Version `1.3.0`)
   * ผูก Vector Spaces: `unboxing_sensory` (1024-dim `bge-m3`) และ `product_features` (1024-dim `bge-m3`)
2. **Query IR Router (`query-ir.v1`):**
   * เชื่อมโยง Query IR ไปยัง Local Substrate Path `./smartgift-genesis-db`

---

#### **D. กฎความปลอดภัยและข้อห้าม (Security Invariants & Non-Negotiables)**
1. **Zero-PII Invariant ใน Vault:**
   * `vault_id` ใน GenesisBlockDB / GKS **ต้องเก็บเฉพาะข้อมูลสินค้า (ProductMaster, CatalogOffer, BOM, Sensory Vectors) เท่านั้น**
   * ห้ามเก็บชื่อลูกค้า (`Customer`), เบอร์โทร, LINE ID หรือประวัติคำสั่งซื้อ (`Orders/Transactions`) ลงใน Vault โดยเด็ดขาด ข้อมูลส่วนบุคคลทั้งหมดต้องอยู่ที่ Tier 1 (`zuri-ai` DB) เท่านั้น
2. **Price Authority Invariant:**
   * ข้อมูลราคาสินค้าใน Catalog ให้ยึดจากไฟล์ส่งออก `smartgift-portfolio.postgres.sql` (จาก FlowAccount) เป็นหลักเสมอ ห้ามดัดแปลงไฟล์ต้นทาง Excel

---

## 🚀 4. Execution & Verification Checklist

- [ ] **Tier 1 (`D:\zuri-ai`):** Run `npx prisma validate` และอัปเดต `schema-zuri-ai.md`
- [ ] **Tier 2 (`D:\msp`):** รัน Integration Test `tests/integration/msp-vault-memory-port.test.js`
- [ ] **Tier 3 (`D:\gks`):** ตรวจสอบ GKS Schema Registry `smartgift://b2b/portfolio/v1`
- [ ] **Tier 4 (`O:\cat`):** รัน `py -3 -m unittest discover tests` และ `node test_genesis.mjs` (ผ่าน 100%)
