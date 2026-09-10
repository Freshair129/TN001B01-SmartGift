---
version: "1.0.0"
created_at: "2026-09-10T09:20:00+07:00,Antigravity"
status: "active"
attributes:
  domain: "catalog-data-pipeline"
  doc_type: "directory-readme"
  scope: "data-pipeline/01_raw"
---

# 📂 Data Pipeline: โครงสร้างโฟลเดอร์ข้อมูลดิบ (01_raw)

โฟลเดอร์ `01_raw/` คือ **Immutable Intake Substrate** (โซนรับเข้าข้อมูลดิบที่ไม่สามารถแก้ไขโดยตรงได้) ของระบบข้อมูล **Business 01: SmartGift (บริษัท เทราบิส จำกัด)** 

ข้อมูลในโซนนี้รวบรวมมาจากระบบบัญชี ERP (FlowAccount), โรงงานผู้ผลิตต่างประเทศ (จีน), แคตตาล็อกและใบเสนอราคาส่งลูกค้า, อัตราค่าขนส่งชิปปิ้ง, และพิมพ์เขียวกลยุทธ์ธุรกิจ เพื่อส่งต่อเข้าสู่กระบวนการสกัดข้อมูล (Stage 2 Normalize) ในขั้นตอนถัดไป

---

## 🗺️ สรุปภาพรวมโครงสร้าง 8 เลน (Lanes Overview)

| เลข Lane | ชื่อโฟลเดอร์ (Folder Name) | ประเภทข้อมูล | แหล่งที่มา (Source) | บทบาทในระบบ | ระดับความลับ (Security) |
|:---:|---|---|---|---|:---:|
| **01** | `01_flowaccount_exports/` | Spreadsheet (`.xlsx`) | FlowAccount ERP | ข้อมูลสินค้า, ประวัติการออกใบแจ้งหนี้/เสนอราคา | 🔒 กึ่งความลับ (ตาม ADR-006) |
| **02** | `02_catalog_srp_pricelists_pdf/` | เอกสาร PDF (13 เล่ม) | SmartGift Sales & Marketing | **แคตตาล็อกราคาขายส่งลูกค้า (Catalog SRP)**, สเปกไทย, รายการสี, Tiers 10–500 | 🟢 สาธารณะ/ส่งลูกค้า |
| **03** | `03_product_catalogs/` | เอกสาร PDF (2 เล่ม) | ผู้ผลิตต่างประเทศ (REEVES / จีน) | แคตตาล็อกสเปกอุปกรณ์อิเล็กทรอนิกส์และ Power Bank ภาษาอังกฤษ | ⚪ ข้อมูลอ้างอิง |
| **04** | `04_shipping_rates_cbm/` | รูปภาพตารางเรท (`.jpg`) | LK Cargo (ชิปปิ้ง) | อัตราค่าขนส่งทางรถ/เรือต่อ CBM และ KG จากกวางโจวและอี้อู | ⚪ ข้อมูลอ้างอิง |
| **05** | `05_crm_customer_data/` | Spreadsheet (`.xlsx`) | เซลส์ / FlowAccount | ข้อมูลลูกค้าองค์กร ประวัติการสั่งซื้อ และเบอร์ติดต่อ | 🚨 **ความลับสูงสุด (PDPA / PII)** |
| **06** | `06_business_pdf/` | เอกสาร PDF (5 เล่ม) | ผู้บริหาร / กลยุทธ์องค์กร | พิมพ์เขียวพอร์ตโฟลิโอ 2026, สถาปัตยกรรมโครงสร้างพื้นฐาน, Unboxing Engineering | 🔒 เอกสารภายในองค์กร |
| **07** | `07_pricing_formulas/` | YAML Rule Snapshots | ระบบคำนวณราคา | สแนปช็อตสูตรคำนวณราคา (ย้ายเลขมาจาก 02 ตาม ADR-005) | ⚪ ระบบภายใน |
| **08** | `08_factory_costs/` | Spreadsheet (`.xlsx`, `.xls`) | โรงงานจีน (Shenzhen Zhimei Shiji) | **ต้นทุนหน้าโรงงานจริง (Factory EXW USD/RMB)** | 🔒 ความลับทางการค้า |
| **-** | `archive/` | Timestamps + SHA-256 | Archivers อัตโนมัติ | ประวัติข้อมูลดิบย้อนหลังที่ถูกตรึงด้วย SHA-256 ไม่สามารถลบหรือแก้ได้ | 🔒 บันทึกการตรวจสอบ |

---

## 🔍 เจาะลึกรายละเอียดแต่ละโฟลเดอร์ (Detailed Directory Breakdown)

### 01. `01_flowaccount_exports/` — ข้อมูลดิบจากระบบ FlowAccount
* **ไฟล์ภายใน (4 ไฟล์):**
  1. `บริษัท เทราบิส จำกัด_product.xlsx` — ฐานข้อมูลสินค้าดิบ 1,319 แถว (ประกอบด้วยสินค้า, บริการสกรีน, กล่องบรรจุภัณฑ์, และแฟลชไดร์ฟสั่งทำ)
  2. `บริษัท เทราบิส จำกัด_QuotationReport_.xlsx` — รายงานใบเสนอราคาย้อนหลัง
  3. `บริษัท เทราบิส จำกัด_BillingNoteReport_.xlsx` — รายงานใบวางบิลย้อนหลัง
  4. `บริษัท เทราบิส จำกัด_contact.xlsx` — ทะเบียนรายชื่อติดต่อ
* **การนำไปใช้งาน:** สคริปต์ `flowaccount_registry_archiver.py` จะคำนวณ SHA-256 และบันทึกสแนปช็อตลง `archive/` และเป็นอินพุตหลักให้ `pipeline/normalize_flowaccount_catalog.py` สกัดรหัสโมเดล

---

### 02. `02_catalog_srp_pricelists_pdf/` — แคตตาล็อกราคาขายส่งลูกค้า (Catalog SRP)
*(เดิมมีชื่อว่า `02_factory_pricelists_pdf` ซึ่งเป็น Misnomer และได้รับการรีแฟกเตอร์ตามมติ 2026-09-10 พร้อมทำ Directory Junction เพื่อความเข้ากันได้ย้อนหลัง)*
* **ไฟล์ภายใน (13 เล่ม PDF):**
  - `01-ใบราคา-2025 POWER BANK.pdf`
  - `01-ใบเสนอราคา-update12กย68(แปลอังกฤษ to ไทยยังไม่เสร็จ).pdf` (เล่มหลัก 110 หน้า มี 793 รุ่นโมเดล)
  - `02-ตัวอย่างใบราคาส่งลูกค้า - BusinessOfficeGiftset-(แปล ไทย).pdf`
  - `02-ใบราคา2025-ชุดของขวัญธุรกิจ-ฺBusinessGift.pdf`
  - `03-ใบราคา-2025 POWER BANK-Fast Charging Series.pdf`
  - `04-ใบราคา-2025 NoteBook-POWER BANK-100W.pdf`
  - `04-ใบราคา2025-ชุดขวัญแปลกใหม่-NoveltyGift.pdf`
  - `05-ใบราคา-2025 POWER BANK-Wireless Charger - ชาร์จไร้สาย & แม็กเน็ต.pdf`
  - `06-ใบราคา-2025 NoteBook-POWER BANK-100W.pdf`
  - `Catalog-USBThailand.pdf`
  - `SmartGift-Premium_ใบราคาชุดของขวัญแปลไทย.pdf`
  - `SmartGift-ใบราคา-update.pdf` (136 หน้า)
  - `ใบราคาแฟลชไดร์ฟ - 4 ตค 67.pdf`
* **บทบาทสำคัญ:** เป็น **Single Source of Truth ของราคาขายแนะนำ (Catalog SRP)**, รายละเอียดสเปกสินค้าภาษาไทย, ภาพตัวอย่าง, สีของสินค้า และขั้นบันไดราคาขายตามจำนวน (Tier 10, 20, 50, 100, 300, 500 ชุด)

---

### 03. `03_product_catalogs/` — แคตตาล็อกสินค้าต้นทางต่างประเทศ
* **ไฟล์ภายใน (2 เล่ม PDF):**
  1. `2024_REEVES - Smart Electronics 2024 EN-OP.pdf` — แคตตาล็อกสินค้าอิเล็กทรอนิกส์แบรนด์ REEVES
  2. `2026 new catalogue of power banks&car charger&wireless charger.pdf` — แคตตาล็อกอุปกรณ์ชาร์จและพาวเวอร์แบงก์สากล
* **บทบาทสำคัญ:** ใช้อ้างอิงสเปกทางเทคนิคขั้นสูง ขนาด แบตเตอรี่ มิลลิแอมป์ และมาตรฐานความปลอดภัยสากล

---

### 04. `04_shipping_rates_cbm/` — อัตราค่าขนส่งชิปปิ้งนำเข้าจากจีน
* **ไฟล์ภายใน (2 รูปภาพ):**
  1. `LK-กวางโจว.jpg` — เรทค่าขนส่งทางรถ/เรือจากโกดังเมืองกวางโจว (Guangzhou) มาไทย
  2. `LK-อี้อู.jpg` — เรทค่าขนส่งจากโกดังเมืองอี้อู (Yiwu) มาไทย
* **บทบาทสำคัญ:** เป็นต้นทางของพารามิเตอร์อัตราค่าขนส่งต่อ CBM และต่อน้ำหนัก (กก.) ที่ใช้ใน `config/pricing_rules_formula.yaml` เพื่อคำนวณต้นทุนรวมส่งมอบ (Landed Cost)

---

### 05. `05_crm_customer_data/` — ข้อมูลลูกค้าและประวัติการสั่งซื้อ (PDPA / PII)
* **ไฟล์ภายใน (3 ไฟล์):**
  1. `2.1-รายชื่อลูกค้า-บริษัท เทราบิส จำกัด_contact.xlsx`
  2. `2.2 ประวัติการสั่งซื้อ-ลูกค้าแต่ละรายละซื้ออะไร – เมื่อใด - มูลค่าเท่าใด.xlsx`
  3. `บริษัท เทราบิส จำกัด_QuotationReport_.xlsx`
* ⚠️ **กฎความปลอดภัยสูงสุด (CR-006 & ADR-006):**
  - มีรายชื่อ เบอร์โทร อีเมล และประวัติการซื้อของลูกค้านิติบุคคล
  - **ห้าม** อัปโหลดไฟล์กลุ่มนี้ขึ้น GitHub สาธารณะ หรือนำไปรัน Embedding เข้าสู่ Vector Vault (`vlt-catalog-product`) โดยเด็ดขาด
  - อนุญาตให้เก็บเฉพาะใน Git Repository ส่วนตัว (Private) ภายใต้ข้อยกเว้นของ ADR-006 เท่านั้น

---

### 06. `06_business_pdf/` — พิมพ์เขียวและกลยุทธ์ธุรกิจ SmartGift
* **ไฟล์ภายใน (5 เล่ม PDF):**
  1. `SmartGift_2026_Portfolio_Blueprint.pdf` — แผนผังพอร์ตโฟลิโอผลิตภัณฑ์ปี 2026
  2. `Architecture_of_Appreciation.pdf` — ปรัชญาและโครงสร้างการมอบของขวัญองค์กร
  3. `Unboxing_Engineering.pdf` — ข้อกำหนดวิศวกรรมประสบการณ์การเปิดกล่อง (Sensory Unboxing Experience)
  4. `Sovereign_Group_Digital_Infrastructure.pdf` — โครงสร้างพื้นฐานดิจิทัลเครือบริษัท
  5. `Smart_Gift.pdf` — เอกสารแนะนำแบรนด์ SmartGift
* **บทบาทสำคัญ:** กำหนด Tier ของขวัญ (Executive, VIP, Corporate), สัดส่วนของขวัญ, และ Tag สำหรับการจัดกลุ่มหมวดหมู่

---

### 07. `07_pricing_formulas/` — สแนปช็อตสูตรราคา (Historical Snapshots)
* **บทบาทสำคัญ:** โฟลเดอร์นี้ได้รับการรีนัมเบอร์จากเลขเดิม `02_pricing_formulas` (ตามมติ ADR-005) เพื่อไม่ให้ซ้ำกับ Lane 02 โดยไฟล์สูตรหลักปัจจุบันอยู่ที่ `config/pricing_rules_formula.yaml` และประวัติย้อนหลังจัดเก็บที่ `archive/pricing_formulas/`

---

### 08. `08_factory_costs/` — ต้นทุนหน้าโรงงานจริงจากจีน (The Real Factory Costs)
* **ไฟล์ภายใน (3 ไฟล์หลัก + รูปภาพ):**
  1. `01-ต้นทุน-20260612 Business Office Gift set catalog.xlsx` — ต้นทุนชุดของขวัญจาก **Shenzhen Zhimei Shiji Industrial Co., Limited** คิดเป็นเงิน **USD (EXW Shantou)**
  2. `02-ต้นทุน-20260417 Power bank notebook catalog.xlsx` — ต้นทุนสมุดโน้ตและพาวเวอร์แบงก์ (USD)
  3. `ต้นทุน USB Flashdrive.xls` — ต้นทุนชิปและบอดี้แฟลชไดร์ฟ (RMB)
  4. `extracted_images/` — โฟลเดอร์เก็บภาพสินค้าที่สกัดออกจาก Excel โรงงาน
* **บทบาทสำคัญ:** เป็น **Single Source of Truth ของต้นทุนหน้าโรงงาน (Factory EXW Cost)** ที่แท้จริง สำหรับนำมาคิด Landed Cost และ Gross Margin ระดับ 50% – 70%

---

### `archive/` และไฟล์ Registry ทะเบียนคุมเวอร์ชัน
* `exports_registry.json` — บันทึก SHA-256 และประวัติเวอร์ชันของไฟล์ FlowAccount
* `factory_cost_registry.json` — บันทึก SHA-256 และประวัติเวอร์ชันของไฟล์ต้นทุนโรงงาน
* `pricing_formula_registry.json` — บันทึก SHA-256 และประวัติเวอร์ชันของสูตรคำนวณราคา
* `archive/` — เก็บไฟล์สแนปช็อตย้อนหลังแบบ Timestamped Hash (เช่น `20260829T225859Z_0d5acee8a0fe_...`) ห้ามแก้ไขหรือลบเด็ดขาด

---

## 🛡️ กฎเหล็กประจำโซนข้อมูลดิบ (Invariants for AI & Engineers)

1. **ห้ามแก้ไขไฟล์ดิบด้วยมือ (Raw Immutability):** ห้ามเปิดแก้ตัวเลขหรือสูตรในไฟล์ Excel หรือ PDF ใน `01_raw/` โดยตรง การแปลงค่าทั้งหมดต้องทำผ่านโค้ดใน `pipeline/` และบันทึกลง `02_prepared/` เท่านั้น
2. **รักษาความต่างระหว่าง Lane 02 และ Lane 08 (Zero Confusion):**
   - **Lane 02 = ราคาขายลูกค้า (Catalog SRP)** รวมสกรีนและกล่อง
   - **Lane 08 = ต้นทุนหน้าโรงงานจีน (Factory EXW)** สกุลเงิน USD/RMB
   - **ห้ามนำราคาจาก Lane 02 ไปใส่เป็นต้นทุนเด็ดขาด!**
3. **การรักษาความปลอดภัยข้อมูลลูกค้า (PDPA Invariant):** ข้อมูลใน Lane 05 และรายงานลูกค้าใน Lane 01 จะต้องไม่ถูกส่งออกนอกเครื่อง หรือถูกโหลดเข้าไปยัง AI Vector Substrate ที่ไม่มีการยืนยันสิทธิ์
