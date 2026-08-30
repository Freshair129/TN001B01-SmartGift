# 🏛️ SmartGift B2B Architecture & Tech Stack Specification
**Option B: Supabase Cloud PostgreSQL + GenesisBlock Edge Engine**

เอกสารฉบับนี้สรุปสถาปัตยกรรมและเทคโนโลยี (Tech Stack) ของระบบ **SmartGift B2B E-commerce & Intelligent Portfolio System** ทั้งในปัจจุบัน (Development Stage) และการเตรียมพร้อมสู่อนาคต (Production Cloud Stage)

---

## 📌 Executive Summary

ระบบ SmartGift ในปัจจุบันทำงานในรูปแบบ **100% Local Multi-Engine Architecture (ไม่ต้องพึ่งพา Cloud)** โดยรันระบบ Local คู่ขนานกันทั้ง 2 ส่วนในเครื่อง:

* **Read / Search Path (GraphRAG):** ประมวลผลผ่าน **GenesisBlockDB Local Edge Engine** ในเครื่องเพื่อความเร็วระดับ Microsecond (< 1ms Latency)
* **Write / Transaction / BOM Path:** ประมวลผลผ่าน **Local PostgreSQL / Local Master Storage (`smartgift_catalog_master.json`)** ภายในเครื่องโดยไม่มีการต่อเชื่อมไป Supabase Cloud ในขณะนี้

*(หมายเหตุ: Supabase Cloud PostgreSQL ถูกจัดวางไว้เป็นทางเลือกสำหรับการสเกลระบบขึ้นคลาวด์ในอนาคตเท่านั้น)*

---

## 🛠️ 1. Current Tech Stack (ปัจจุบัน - โหมดการพัฒนา Local Dev)

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Local Development Stack                                  │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ • Master Catalog SSOT  : smartgift_catalog_master.json & schema_genesisblock.yaml       │
│ • Local AI Engine      : Ollama (bge-m3:1024dim Embedding + Local Thai LLM qwen3.5:4b)   │
│ • Local Search Engine  : GenesisBlockDB Native Addon (@freshair129/gks-genesis-block-native)│
│ • Query Protocol       : Query IR Specification (query-ir.v1)                            │
│ • Inventory Cascade    : inventory_cascade_engine.py (Non-Stock Tracked / On-Demand BOM Decomposition) │
│ • Application Interface: demo_app.py (Python Interactive CLI Terminal)                   │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### รายละเอียดส่วนประกอบในปัจจุบัน:

1. **Single Source of Truth (SSOT):**
   * [smartgift_catalog_master.json](file:///o:/cat/smartgift_catalog_master.json) — Master Data เก็บข้อมูลหมวดหมู่ สินค้ากายภาพ ข้อเสนอ และชุดของขวัญองค์กร
   * [schema_genesisblock.yaml](file:///o:/cat/schema_genesisblock.yaml) — สเปกสัญญาข้อมูล (`smartgift://b2b/portfolio/v1`)

2. **Embedded Native Engine (GenesisBlockDB v0.2.5):**
   * ติดตั้งผ่าน npm package: `@freshair129/gks-genesis-block-native`
   * ทำงานแบบ In-Process Native C-ABI / Node Addon 
   * เก็บข้อมูลลงดิสก์ผ่านไฟล์ Binary (`nodes.bin`, `edges.bin`, `vec_default.bin`) และมี SQLite (`projection.sqlite`) ทำหน้าที่เป็น Storage Substrate เบื้องหลัง

3. **GraphRAG & Local LLM Integration:**
   * สกัดความหมาย Sensory / Unboxing Experience ด้วยโมเดล Embedding `bge-m3` (1024 dimensions) ผ่าน Ollama Local API
   * ประมวลผลคำตอบภาษาไทยผ่าน Local LLM (Pathumma / Typhoon-S / Qwen)

---

## 🚀 2. Future Tech Stack (อนาคต - โหมด Production Cloud Deployment)

```
                                 ┌─────────────────────────────────────────────────────────┐
                                 │                   Supabase Cloud Tier                   │
                                 │                 (Managed PostgreSQL)                    │
                                 ├─────────────────────────────────────────────────────────┤
                                 │ • Master Catalog Tables & Relational Constraints        │
                                 │ • Granular Physical Stock Inventory & Cascade Engine    │
                                 │ • `pgvector` Extension (Cloud Vector Backup)            │
                                 │ • Row Level Security (RLS) & Financial Ledger           │
                                 └────────────────────────────┬────────────────────────────┘
                                                              │
                                            Catalog Sync      │ (Webhook / Polling Sync)
                                            Bridge Engine     │ (supabase_genesis_sync.py)
                                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             Edge / Local AI Search Tier                                  │
│                              (GenesisBlockDB Native)                                     │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ • In-Process Native Rust Embedded Hybrid Graph + Vector Search (`query-ir.v1`)           │
│ • Ultra-low Latency HNSW Vector Index (`bge-m3` 1024-dim)                                │
│ • Serves Real-time GraphRAG Context directly to LLM Agents (< 1ms Latency)              │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### รายละเอียดส่วนประกอบในอนาคต (Production Architecture):

### ☁️ **A. Cloud Storage & Transaction Tier (Supabase PostgreSQL)**
* **Database Platform:** Supabase Managed PostgreSQL
* **Schema DDL:** [schema_postgresql.sql](file:///o:/cat/schema_postgresql.sql)
* **Extension:** `pgvector` (เปิดใช้งานแล้ว `CREATE EXTENSION IF NOT EXISTS vector;`)
* **หน้าที่หลัก:**
  * **Master Catalog Tables:** `categories`, `product_masters`, `catalog_offers`, `attributes`
  * **On-Demand BOM Decomposition & Pricing Engine:** เนื่องจากสินค้าเป็นแบบ **ไม่นับสต็อก (Non-Stock Tracked / Made-to-Order)** ระบบจะแตกชิ้นส่วน BOM (Bill of Materials) ตามจำนวนที่สั่งเพื่อคำนวณต้นทุนชิ้นส่วนจริง (COGS) และกำไรขั้นต้น (Gross Profit Margin %) แบบ Real-Time
  * **Audit Log & Invoicing:** บันทึกประวัติคำสั่งซื้อและรายการชิ้นส่วนจริงที่ต้องจัดซื้อ/สั่งผลิตลง `inventory_deduction_logs`
  * **Row Level Security (RLS):** ควบคุมสิทธิ์การเข้าถึงข้อมูลขององค์กรลูกค้าแต่ละเจ้า

---

### ⚡ **B. Edge AI Search & GraphRAG Tier (GenesisBlockDB Engine)**
* **Runtime Deployment:** รันเป็น In-Process Engine บน Backend API Server / Edge Worker (เช่น Render, Docker Container, หรือ AWS ECS)
* **หน้าที่หลัก:**
  * โหลดข้อมูล Master Catalog มาไว้ใน RAM + Local Disk Storage (`smartgift-genesis-db`)
  * ให้บริการค้นหาข้อมูลความรู้สึก (Unboxing Sensory Vectors) และท่องความสัมพันธ์ของชุดของขวัญ (Graph Traversal) 
  * ให้ผลลัพธ์การค้นหา Context แก่ AI LLM ด้วยความเร็วสูงปรี๊ด **< 1ms** โดยไม่ต้องยิง Network Hit ไปที่เซิร์ฟเวอร์ Supabase

---

### 📊 **C. Static DB for Offline Operations & Data Analytics (DuckDB / SQLite Substrate)**
* **Database Platforms:** SQLite (`projection.sqlite` ใน GenesisBlockDB) / DuckDB / Static Parquet Snapshots
* **หน้าที่หลัก:**
  * **Offline Mode (การทำงานแบบ Offline 100%):** ทำหน้าที่เป็น Static Embedded Replica ช่วยให้การค้นหา AI GraphRAG และการคำนวณราคาชุดของขวัญสามารถทำงานต่อไปได้ในเครื่อง Local/Desktop/Mobile แม้ขาดการเชื่อมต่ออินเทอร์เน็ตไปยัง Supabase Cloud
  * **Data Analytics & Executive Dashboards (OLAP Engine):** ใช้ DuckDB อ่านไฟล์ Static Parquet / SQLite เพื่อวิเคราะห์ข้อมูลเชิงลึก (Analytics) เช่น เทรนด์ความนิยมของหมวดหมู่ของขวัญ (Theme Popularity), การวิเคราะห์กำไรขั้นต้นรายไตรมาส (Portfolio Profitability Analysis) และรายงานพฤติกรรมลูกค้า โดยไม่รบกวนประสิทธิภาพของ Cloud Database หลัก

---

### 🔄 **D. Sync Bridge Engine (ตัวเชื่อมโยงข้อมูล)**
* **ไฟล์ระบบ:** [supabase_genesis_sync.py](file:///o:/cat/supabase_genesis_sync.py)
* **หน้าที่หลัก:**
  * คอยดึงข้อมูลอัปเดต Master Catalog จาก Supabase Cloud ลงมาอัปเดตที่ GenesisBlockDB Edge Engine และ Static Offline DB
  * รันสคริปต์ [seed_genesisblock.mjs](file:///o:/cat/seed_genesisblock.mjs) เพื่อ rebuild/flush HNSW Index อัตโนมัติเมื่อมีการเพิ่มสินค้าใหม่

---

### 💻 **E. Frontend & API Layer (อนาคต)**
* **REST API Specification:** [openapi_spec.yaml](file:///o:/cat/openapi_spec.yaml) (OpenAPI 3.0 Standard Spec)
* **Framework:** Next.js (TypeScript) / React
* **Database Client:** `@supabase/supabase-js` Direct Client (พร้อม Auto-generated TypeScript Types จาก Supabase CLI)
* **Authentication:** Supabase Auth (Magic Link, OAuth, Enterprise SAML)

---

### ⚡ **F. Multi-Level Caching Strategy (กลยุทธ์การทำ Caching)**

เพื่อประสิทธิภาพสูงสุด ระบบแบ่ง Caching ออกเป็น 3 ระดับ:

1. **Level 1: In-Memory Native Vector & Graph Cache (GenesisBlockDB)**
   * **สิ่งที่ Cache:** HNSW Vector Index (`bge-m3`) และ Graph Topology Nodes/Edges
   * **กลไก:** GenesisBlockDB โหลดข้อมูลทั้งหมดขึ้น Native RAM ของ Backend Server ทำให้การทำ GraphRAG ค้นหาบริบทเซ็ตของขวัญทำได้เร็วสุดขีด **< 1ms** โดยไม่ต้องยิง Network ไปที่ Supabase Cloud
2. **Level 2: Semantic LLM Response Cache (Redis / In-Memory LRU)**
   * **สิ่งที่ Cache:** คำตอบสำเร็จรูปที่ LLM เคยประมวลผล (Semantic Query Hash)
   * **กลไก:** ใช้ Redis หรือ In-Memory LRU Cache เก็บคำตอบคำถามยอดฮิต หากมีคำถามเดิมเข้ามา AI สามารถดึงคำตอบจาก Cache ตอบกลับได้ทันที ปรับลดค่าใช้จ่ายการเรียก LLM API
3. **Level 3: Master Catalog Static Cache & Invalidation**
   * **สิ่งที่ Cache:** ข้อมูล Master Catalog, MOQ Price Tiers, และโครงสร้าง BOM สินค้า
   * **กลไก Invalidation:** เมื่อมีการแก้ไขข้อมูลสินค้าหรือราคาใน Supabase Cloud ตัวระบบจะยิง Webhook มาสั่งสคริปต์ [supabase_genesis_sync.py](file:///o:/cat/supabase_genesis_sync.py) ให้ Rebuild/Flush Cache ใน GenesisBlockDB อัตโนมัติ

---

### 🧠 **G. Standard Enterprise GraphRAG Pipeline Architecture (มาตรฐานระบบ RAG)**

ตามมาตรฐานสากลของระบบ **Enterprise GraphRAG** ระบบจะต้องมี 5 เลเยอร์สำคัญในการประมวลผลคำถามจนถึงคำตอบ:

1. **Ingestion & Knowledge Graph Extraction Layer**
   * **Vector Embedding:** แปลงข้อความ Unboxing Experience & สเปกสินค้าด้วยโมเดล `bge-m3` (1024-dim)
   * **Graph Knowledge Base:** สกัดความสัมพันธ์ของสินค้า, หมวดหมู่, เทียร์งบประมาณ, และกลุ่มผู้รับลงใน Knowledge Graph
2. **Hybrid Retrieval Layer (สืบค้นลูกผสม)**
   * **Dense Vector Search (HNSW Cosine Similarity):** สืบค้นความหมายความรู้สึก (Sensory Vibe)
   * **Sparse / Lexical Search:** ค้นด้วย Keyword รหัสสินค้า (`PM-PB10K`, `PKG-SME-ELITE`)
   * **Graph Traversal (2-Hop Expansion):** ท่องความสัมพันธ์ดึงชิ้นส่วน BOM (`:CONTAINS`) และเทียร์ราคา (`:BELONGS_TO_TIER`)
3. **Post-Retrieval & Filtering Layer**
   * **History Suppression Filter:** กรองรายการชุดของขวัญที่ลูกค้าองค์กรรายนั้นเคยสั่งซื้อไปแล้วในปีที่แล้วออก
   * **Re-ranking & Reciprocal Rank Fusion (RRF):** หลอมรวมคะแนนจาก Vector + Keyword + Graph เพื่อจัดลำดับ Top Candidates
4. **Generation & Guardrails Layer**
   * **System Persona & Prompt Engineering:** AI Consultant สร้างคำตอบพร้อมจัดรูปแบบใบเสนอราคาภาษาไทย
   * **Grounding & Hallucination Guardrail:** ตรวจสอบว่าคำตอบของ LLM อ้างอิงจากข้อมูลจริงใน Knowledge Graph 100%
5. **Observability & Evaluation Layer**
   * **RAG Metrics (Faithfulness, Answer Relevance, Context Precision):** บันทึก Trace การสืบค้นและวัดผลคุณภาพคำตอบ

---

### 🔐 **H. Product Catalog Vault Architecture (UUIDv7 Isolation)**

เพื่อความเป็นสัดส่วน ความปลอดภัยสูงสุด และการคุ้มครองข้อมูลส่วนบุคคล (Zero PII & Data Privacy) ระบบกำหนดขอบเขตของ **`vault_id` (vlt- UUIDv7)** ไว้อย่างเข้มงวดดังนี้:

1. **เก็บเฉพาะข้อมูลสินค้า & Knowledge Graph (Product & Sensory Data Only)**
   * `vault_id` แต่ละอันทำหน้าที่เป็น **Catalog Product Vault** เก็บเฉพาะข้อมูลชุดของขวัญ (`CatalogOffer`), ชิ้นส่วนสินค้า (`ProductMaster`), หมวดหมู่ (`Category`), เทียร์ราคา (`GiftTier`) และ Unboxing Sensory Vectors
2. **ห้ามเก็บรายชื่อลูกค้าและประวัติคำสั่งซื้อ (Zero PII / Zero Transaction Storage)**
   * รายชื่อองค์กรลูกค้า (`CorporateClient`), ผู้ติดต่อ (`Customer`), บัญชีการเงิน และประวัติการสั่งซื้อธุรกรรมทั้งหมด **จะไม่ถูกเก็บลงใน Vault หรือ GenesisBlock Edge Engine เด็ดขาด**
   * ข้อมูลลูกค้าและการเงินทั้งหมดจะถูกจำกัดวงและควบคุมความปลอดภัยไว้อยู่เฉพาะใน **Supabase Cloud PostgreSQL** ที่มี Row Level Security (RLS) และ Data Encryption เท่านั้น
3. **Audit Trail & UUIDv7 Timestamping**
   * ใช้รูปแบบ **UUIDv7** ที่มี Time-ordered Timestamp ในตัว ช่วยให้จัดเรียงและสืบค้นรุ่นของ Catalog สินค้าตามเวลาได้อย่างแม่นยำ

---

## 📊 3. เปรียบเทียบข้อดีของ Tech Stack ที่เลือก (Why Option B?)

| คุณสมบัติ | Supabase All-in-One (ทั่วไป) | **Option B (ของเรา: Supabase + GenesisBlock Edge)** |
| :--- | :---: | :---: |
| **Search Latency (GraphRAG)** | 50ms - 200ms (ผ่าน Cloud) | ⚡ **< 1ms (In-Process Execution)** |
| **ภาระของ Cloud Database** | 🔴 สูง (โดนยิง Search Traffic ตลอดเวลา) | 🟢 **ต่ำมาก** (Database Cloud รับเฉพาะงาน Write/Orders) |
| **ความเสถียรของคลังสินค้า** | 🔒 ACID Compliant 100% | 🔒 **ACID Compliant 100%** (ตัดสต็อกที่ Supabase) |
| **การรองรับ Offline / Edge** | ❌ ไม่รองรับ | ✅ **รองรับ 100%** (ค้นหาต่อได้แม้ไม่มีอินเทอร์เน็ต) |

---

## 🧪 4. การทดสอบและการรันระบบ (Verification & Commands)

```bash
# 1. ทดสอบการรัน Unit Tests สำหรับสถาปัตยกรรมคลังสินค้า
py -3 -m unittest discover tests

# 2. ทดสอบการเปิดเอนจิน GenesisBlockDB Native NAPI Binding
node test_genesis.mjs

# 3. ทดสอบสคริปต์ซิงก์ข้อมูล Supabase ➔ GenesisBlockDB Edge
py -3 supabase_genesis_sync.py

# 4. เปิดหน้าต่างจำลองระบบ SmartGift B2B (Option B Architecture)
py -3 demo_app.py
```
