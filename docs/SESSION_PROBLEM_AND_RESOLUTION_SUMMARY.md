# 📑 รายงานสรุปปัญหาที่พบและแนวทางแก้ไข (Session Problem & Resolution Summary)

**หัวข้อ:** การจัดระเบียบโครงสร้างแคตตาล็อกสินค้า, Data Governance Pipeline, และ Multi-Business Architecture  
**วันที่บันทึก:** 30 สิงหาคม 2026  
**ขอบเขตระบบ:** `Wannapa Workspace` ➔ `Org-EtohGroup` (Tenant) ➔ 4 ธุรกิจในเครือ  

---

## 🔍 1. ปัญหาด้านคุณภาพข้อมูลต้นทาง & การสกัดรหัสสินค้า (Data Quality & Normalization)

### **ปัญหาที่ 1: รหัสสินค้าฝังอยู่ในข้อความชื่อสินค้า (Embedded Product IDs)**
* **อาการ:** ข้อมูลดิบจาก FlowAccount Excel (`บริษัท เทราบิส จำกัด_product.xlsx`) ขาดรหัสสินค้าในคอลัมน์ Code แต่ไปฝังอยู่ในชื่อสินค้าภาษาไทย เช่น `Model : MC00-1`, `THB03-2(P-20)`, `TYD0762(P-PT)`, `444`/`445`
* **แนวทางแก้ไข:** พัฒนา Entity Extraction Engine ด้วย Regex ใน [`pipeline/02_normalize_mapper.py`](file:///O:/Org-EtohGroup/SmartGift/pipeline/02_normalize_mapper.py) เพื่อดึงรหัสสินค้า, รหัสซัพพลายเออร์ (`P-xx`), และ Model Code ออกมาสร้างเป็นตารางข้อมูลสะอาดโดย **ไม่แก้ไขไฟล์ Excel ต้นฉบับเด็ดขาด**

---

### **ปัญหาที่ 2: ความเสี่ยงไฟล์ FlowAccount Export ถูกเขียนทับ (Identical Filename Overwrite)**
* **อาการ:** การส่งออกไฟล์จาก FlowAccount ในแต่ละรอบจะได้ชื่อไฟล์เดิมซ้ำกันเสมอ ทำให้ประวัติข้อมูลเดิมเสี่ยงสูญหายและไม่สามารถย้อนดูประวัติ Diff ได้
* **แนวทางแก้ไข:** พัฒนาระบบ [`pipeline/flowaccount_registry_archiver.py`](file:///O:/Org-EtohGroup/SmartGift/pipeline/flowaccount_registry_archiver.py) คำนวณ SHA-256 ของเนื้อหาไฟล์, ทำการข้ามไฟล์ที่เนื้อหาซ้ำ (`UNCHANGED_DUPLICATE_SKIPPED`), และบันทึกไฟล์ใหม่เข้าคลังถาวร `data-pipeline/01_raw/archive/YYYYMMDDTHHMMSSZ_{sha256[:12]}_{filename}` พร้อมบันทึกประวัติการเปลี่ยนแปลงของแถวใน `exports_registry.json`

---

### **ปัญหาที่ 3: ความจริงของราคาต้องไม่ยึดจาก PDF (Price Authority Invariant)**
* **อาการ:** เดิมมีความเข้าใจว่าราคาอ้างอิงจาก PDF Blueprint แต่ในความเป็นจริง PDF เป็นเพียงเอกสารนำเสนอ (Presentation Material) และมีสินค้า 102 จาก 669 รายการที่มี `unit_price = 0` พร้อม Flag `price_missing = true`
* **แนวทางแก้ไข:** บังคับใช้กฎ Invariant ให้ยึดราคาจาก FlowAccount Export SQL (`smartgift-portfolio.postgres.sql`) เป็น Source of Truth และต้องกรอง `price_missing = false` ก่อนคำนวณ Margin เสมอ

---

## 🏛️ 2. ปัญหาด้านขอบเขตความปลอดภัย & การแยก Vault (Security Boundaries)

### **ปัญหาที่ 4: ความสับสนเรื่องข้อมูลลูกค้าปนใน Catalog Data Pipeline (PII Leak Risk)**
* **อาการ:** ในไฟล์ดิบมีข้อมูลรายชื่อลูกค้า (`contact.xlsx`) และประวัติการเสนอราคา (`QuotationReport_.xlsx`) ปนอยู่กับไฟล์สินค้า
* **แนวทางแก้ไข:** กำหนดขอบเขต **Zero-PII Invariant** อย่างเคร่งครัด:
  * `vlt-catalog-product` (GenesisBlockDB / Vector Vault) เก็บเฉพาะข้อมูลสินค้า, BOM, และ Sensory Vectors เท่านั้น
  * ข้อมูลลูกค้า (PII) และคำสั่งซื้อทั้งหมดถูกตัดออกจาก Edge Vault และจัดเก็บเฉพาะใน PostgreSQL Tier 1 (`zuri-ai` DB) ภายใต้ระบบ Row Level Security (RLS)

---

### **ปัญหาที่ 5: การแยกคลังความรู้ระหว่าง Zuri Edge Device กับ SmartGift**
* **อาการ:** ความเสี่ยงที่สคริปต์จะไปเปิดหรือเขียนทับคลังส่วนกลาง `D:\workspace\zuri-edge-device\data\genesis_smartgift_store_v4\` ซึ่งถูกควบคุมการสลับรอบด้วยพอยน์เตอร์ `CURRENT`
* **แนวทางแก้ไข:** ให้ SmartGift รันฐานข้อมูล GenesisBlockDB ใน Substrate ของตัวเอง (`vaults/vlt-catalog-product/genesis-db/`) อย่างอิสระ และห้ามสร้าง Prefix `gks:` ขึ้นมาเองนอกระบบ GKS

---

## 💻 3. ปัญหาด้านการคำนวณราคา & Logic (Pricing Engine Parity)

### **ปัญหาที่ 6: ความซับซ้อนของสูตรคำนวณ Landed Cost & Ladder Pricing**
* **อาการ:** อัลกอริทึมการคำนวณราคาบนเว็บ `smartgift-pricing.vercel.app` มีความซับซ้อนสูง: การสลับโหมด Volume vs Weight ตาม Density ($\ge 400$ kg/CBM), ค่าเผื่อ Small Order Factor ($1.0\times$ ถึง $1.5\times$), ค่าสกรีนโลโก้, และขั้นบันไดราคาขายตาม Profit Floor $\ge 5,000$ THB
* **แนวทางแก้ไข:** ทำการถอดรหัส Logic และเขียนเป็น Python Engine ใน [`src/cascade_engine/pricing_calculator.py`](file:///O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py) พร้อมสร้าง Automated Unit Tests ตรวจสอบความถูกต้องได้ผลลัพธ์ตรงกับหน้าเว็บ 100%

---

## 🗂️ 4. ปัญหาด้านโครงสร้างโปรเจกต์ & การจัดการเอกสาร (Project Architecture & CRs)

### **ปัญหาที่ 7: ไฟล์ตกค้างใน Root Directory (Root Cluttering)**
* **อาการ:** สคริปต์ Sync เดิมสร้างโฟลเดอร์ชั่วคราว (`smartgift-genesis-db/`, `test-db/`) และไฟล์ JSON ไว้ใน Root Directory
* **แนวทางแก้ไข:** จัดระเบียบย้ายไฟล์ทั้งหมดเข้า `vaults/` และ `data-pipeline/` และย้ายเอกสารเข้า `docs/` ทำให้ Root Directory สะอาดสมบูรณ์ มีเฉพาะ `README.md`, `AGENTS.md`, และ Entry Scripts เท่านั้น

---

### **ปัญหาที่ 8: Change Request รวมหลายเรื่องในไฟล์เดียว**
* **อาการ:** เอกสาร CR รวมทั้งเรื่อง Scope Chain, Data Pipeline UI, และ GitHub Explorer ไว้ในฉบับเดียว ทำให้ยากต่อการ Review และ Implement
* **แนวทางแก้ไข:** ตรวจสอบสารบบใน `D:\zuri-ai\docs\change-requests/` และแยกเป็น 3 ฉบับตามมาตรฐานสากล:
  * **`CR-002`**: Scope Chain to GKS, MSP & Zuri Edge Device Catalog Vault Resolution
  * **`CR-003`**: Data Pipeline Governance Dashboard & Approval Gates UI
  * **`CR-004`**: GitHub Integration & "Files" Tab File Tree Explorer
