---
version: "1.0.0"
created_at: "2026-09-10T13:28:00+07:00,Antigravity,uncommitted"
last_update: "2026-09-10T13:28:00+07:00,Antigravity"
status: "approved"
superseded_by: null
attributes:
  domain: "pricing-financial-provenance"
  doc_type: "root-cause-analysis"
  scope: "BW00-0 factory cost discrepancy, FX rate drift, and financial provenance schema enforcement"
  language: "th"
---

# RCA: ความคลาดเคลื่อนของฐานต้นทุนโรงงาน BW00-0 และอัตราแลกเปลี่ยน (FX Rate Drift Incident)

## 📌 1. ข้อมูลเหตุการณ์ (Incident Overview)

- **รหัสเหตุการณ์:** `INC-20260910-BW00-COST-DRIFT`
- **วันที่เกิดเหตุการณ์:** 2026-09-10 เวลาประมาณ 12:51 ICT
- **ระบบที่ได้รับผลกระทบ:** SmartGift Pricing Engine, Data Pipeline, และตารางเปรียบเทียบราคา (`BW00-0_pricing_comparison_sheet.xlsx`, `BW00-0_pricing_and_catalog.json`)
- **ผู้ตรวจพบ (Reported By):** ผู้ใช้งาน (User / Boss) — ผ่านคำถาม *"BW00-0 เอาราคามาจากไหน ทำไมผิด"* พร้อมภาพแคปเจอร์หน้าจอ Excel
- **ระดับความรุนแรง (Severity):** **SEV-2 / HIGH (Financial & Quotation Accuracy Risk)** — มีความเสี่ยงต่อการออกใบเสนอราคาผิดพลาดหากนำฐานต้นทุนที่สูงเกินจริงไปใช้คำนวณราคาขายและมาร์จิ้น

---

## 🔍 2. อาการที่พบ (Symptoms & Discrepancy)

ในการจัดทำเอกสารราคาและสเปกรุ่น `BW00-0` (แก้วทัมเบลอร์เก็บอุณหภูมิ 450ml พร้อมจอสัมผัส LED ในถุงของขวัญ Dark Blue):
1. **ตัวเลขที่ระบบ AI ส่งมอบในรอบแรก:**
   - ต้นทุนโรงงาน: **`83.08 บาท`** (\$2.31 USD @ FX 36.00 ฿/USD)
   - ต้นทุนรวมส่งมอบ (Landed Cost 100 ชิ้น): `125.10 บาท`
   - ราคาขายองค์กร: `169.00 บาท` (Margin 25.99%)
2. **ตัวเลขจริงในหน้าจอ Excel ของผู้ใช้งาน:**
   - แถวที่ 5846 ในไฟล์ `01-ต้นทุน-20260612 Business Office Gift set catalog.xlsx`
   - คอลัมน์ราคา USD: แสดง `US$2.31` (สูตร `=15/6.5` = $2.307692 USD)
   - คอลัมน์ **"บาท"**: แสดงค่า **`78.4615385` บาท** (สูตร `=E5846*34`)
3. **ส่วนต่างความคลาดเคลื่อน:**
   - ต้นทุนโรงงานของระบบ AI สูงกว่าความเป็นจริง **`+4.62 บาท / ชิ้น`** (+5.89%) ทำให้มาร์จิ้นและฐานการคำนวณผิดเพี้ยนไปจากเอกสารต้นฉบับของบริษัท

---

## 🧾 3. หลักฐานเชิงประจักษ์ (Empirical Evidence)

### หลักฐานภาพหน้าจอ Excel ของผู้ใช้งาน (Row 5846)
- **Cell A5846:** `BW00-0`
- **Cell C5846:** `Vacuum cup in simple dark blue gift bag packing`
- **Cell E5846:** `=15/6.5` (ได้ค่า `2.30769230769231` แสดงผล `US$2.31`)
- **Cell G5846 (Header "บาท"):** `=E5846*34` (ได้ค่า `78.4615385`)

### หลักฐานในฐานข้อมูลเดิม (`ProductMaster.json`)
- พบว่ามีรายการ `PM-TMB` บันทึกค่า `base_cost: 75.00 บาท` (ซึ่งคำนวณจาก $15/6.5 	imes 32.50 = 75.00$ บาท อัตราแลกเปลี่ยนในอดีต) ทำให้เกิดตัวเลข 3 ชุดที่ไม่ตรงกัน (75.00 vs 78.46 vs 83.08)

---

## 🔬 4. การวิเคราะห์หาสาเหตุที่แท้จริง (Root Cause Analysis — 5 Whys)

1. **Why 1: ทำไมระบบถึงคำนวณต้นทุนโรงงานได้ 83.08 บาท?**  
   *ตอบ:* เพราะสคริปต์คำนวณนำตัวเลข $2.307692 USD ไปคูณด้วยอัตราแลกเปลี่ยน **36.00 บาท/USD**
2. **Why 2: ทำไมสคริปต์ถึงใช้อัตราแลกเปลี่ยน 36.00 บาท/USD?**  
   *ตอบ:* เพราะ AI นำอัตราแลกเปลี่ยน Spot ปัจจุบันของตลาด (ซึ่งเคยใช้ในชุด TMS06) มาใช้เป็นค่า Default โดยคิดว่าเป็นค่ากลางของระบบ
3. **Why 3: ทำไม AI ไม่ตรวจดูคอลัมน์ "บาท" ในไฟล์ต้นทุนก่อนคำนวณ?**  
   *ตอบ:* เพราะตัวสคริปต์อ่านค่าเฉพาะคอลัมน์ A (รหัส), C (ชื่อ), และ E (ราคา USD) โดยละเลยคอลัมน์สูตรคำนวณเงินบาทถัดไป (`=E5846*34`) ซึ่งบริษัทได้ล็อกสูตรตายตัวไว้แล้ว
4. **Why 4: ทำไมในระบบมีทั้ง 75.00, 78.46 และ 83.08 บาท?**  
   *ตอบ:* เพราะขาด **Financial Provenance Single Source of Truth (SSOT)** ข้อมูลเก่าใน ProductMaster อิง FX 32.5, ในไฟล์ต้นทุนอิง FX 34.0, และโมเดลใหม่ดึง FX 36.0 ทำให้ไม่มีการล็อก Baseline ทางบัญชี
5. **Why 5: ทำไมระบบถึงปล่อยให้ข้อมูลที่ไม่มี Provenance ผ่านออกมาได้?**  
   *ตอบ:* **(Root Cause)** ขาด Schema Contract ที่บังคับระบุ `source_file`, `source_row`, `currency_exchange_formula` และ `factory_cost_thb_exact` ทำให้ตัวเลขราคาลอยตัวได้โดยไม่มีการตรวจสอบย้อนกลับ (Unanchored Financial Data)

---

## ⚡ 5. การแก้ไขเฉพาะหน้า (Immediate Remediation)

1. **ปรับแก้ฐานต้นทุนโรงงาน `BW00-0`:**
   - ปรับจาก 83.08 บาท ➔ **`78.4615385` บาท (78.46 ฿)** ตามสูตรจริง `=E5846*34`
2. **คำนวณ Landed Cost และตารางราคาใหม่ทั้งหมด:**
   - คำนวณ Landed Cost ทุก Tier (145.48 ฿, 120.48 ฿, 103.81 ฿, 100.48 ฿, 97.98 ฿)
   - ปรับตาราง % Margin ขายทั่วไป (41.8% – 51.7%) และขายองค์กร (23.0% – 30.3%)
3. **อัปเดตไฟล์ผลลัพธ์ทั้งหมด:**
   - อัปเดต [BW00-0_pricing_comparison_sheet.xlsx](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/BW00-0_pricing_comparison_sheet.xlsx)
   - อัปเดต [BW00-0_pricing_and_catalog.json](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/BW00-0_pricing_and_catalog.json)
   - อัปเดต [BW00-0_pricing_comparison_sheet.csv](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/BW00-0_pricing_comparison_sheet.csv)

---

## 🛡️ 6. มาตรการป้องกันระยะยาว (Corrective & Preventative Actions — CAPA)

| มาตรการ | รายละเอียดการดำเนินงาน | สถานะ |
| :--- | :--- | :---: |
| **CAPA 1: บันทึกข้อผูกพันใน ADR-009** | ประกาศข้อตัดสินใจ **D4 (FX Baseline Governance)** ใน `ADR-009` บังคับใช้อัตรา 34.00 บาท/USD สำหรับแคตตาล็อกชุดนี้ | ✅ เสร็จสิ้น |
| **CAPA 2: บังคับใช้ Financial Provenance ใน Schema** | กำหนดใน `contracts/smartgift-full-master.schema.json` ว่าทุก Payload ต้องมีบล็อก `cost_and_financial_provenance` ระบุไฟล์, แถว, สูตร และค่าต้นทุนบาทเป๊ะๆ | ✅ เสร็จสิ้น |
| **CAPA 3: Automated Schema Validation Gate** | ใช้ `jsonschema.validate()` ตรวจสอบ Payload ราคาทุกชุดก่อนนำไป Generate แคตตาล็อกหรือส่งให้ฝ่ายขาย | ✅ เสร็จสิ้น |
| **CAPA 4: ปรับปรุง Session Memory** | บันทึกประวัติและบทเรียนความคลาดเคลื่อนนี้ลงใน `session_memory.md` เพื่อเป็นบริบทถาวรของโครงการ | ✅ เสร็จสิ้น |

---

## 📌 7. เอกสารและสัญญาที่เกี่ยวข้อง

- **ADR อ้างอิง:** [docs/decisions/ADR-009-B2B-PRICING-LOGISTICS-AND-FLOWACCOUNT-SKU-ARCHITECTURE.md](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/decisions/ADR-009-B2B-PRICING-LOGISTICS-AND-FLOWACCOUNT-SKU-ARCHITECTURE.md)
- **สัญญา Schema:** [contracts/smartgift-full-master.schema.json](file:///c:/Users/pc/workspace/business-01-smart-gift/contracts/smartgift-full-master.schema.json)
- **สเปก Master Schema:** [docs/specs/SPEC-FULL-ENTERPRISE-SCHEMA-2026-09-10.md](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/SPEC-FULL-ENTERPRISE-SCHEMA-2026-09-10.md)
