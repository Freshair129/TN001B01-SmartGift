# 🧠 Session Memory: SmartGift Pricing Engine & FlowAccount Standardization

- **Date:** 2026-09-10
- **Workspace:** `c:\Users\pc\workspace\business-01-smart-gift` (Remote: `Freshair129/TN001B01-SmartGift`)
- **System Integration:** Zuri-AI Procurement & FlowAccount Data Pipeline
- **Core Topics:** B2B Pricing Calculation, Direct Single-Drop Shipping Absorption, FlowAccount SKU Naming Standard, Catalog vs Price List Architecture, and Cost Reconciliation.

---

## 📌 1. กฎและบรรทัดฐานทางธุรกิจที่กำหนดขึ้นใน Session นี้ (Key Invariants)

### 1.1 นโยบายค่าขนส่งจุดเดียว (Direct Single Drop Policy)
- **เงื่อนไข:** การจัดส่งสินค้าตรงจากท่าเรือไทย (คลองเตย/แหลมฉบัง) สู่คลังสินค้าของลูกค้าปลายทางเพียงจุดเดียว (Single Destination)
- **อัตราค่าขนส่งในประเทศ:** อัตราเหมามาตรฐานรถบรรทุก **2,500 บาท / เที่ยว**
- **วิธีคิดต้นทุน:** รวมค่าจัดส่งเหมาเฉลี่ยเข้าไปในต้นทุนรวมส่งมอบต่อหน่วย ($\text{Landed Cost per Unit} = \text{ต้นทุนสินค้า} + \text{ค่าเรือ} + \text{ค่าสกรีน} + \frac{2,500}{\text{จำนวนสั่งผลิต}}$)
- **การแสดงผลในใบเสนอราคา (Quotation):** แสดงรายการค่าจัดส่งเป็น **`0.00 บาท (ฟรีค่าจัดส่ง)`** เพื่อเป็นจุดเด่นทางการค้า

### 1.2 สถาปัตยกรรมการตั้งรหัสสินค้าใน FlowAccount
ตามกฎข้อกำหนดของผู้ใช้ รหัสสินค้าใน FlowAccount สำหรับชุดของขวัญและสินค้าพรีเมียมต้องประกอบด้วย 3 ส่วนอย่างเคร่งครัด:
$$\mathbf{[รหัสโมเดลโรงงาน]} + \mathbf{[-จำนวนชิ้นในชุด]} + \mathbf{[(รหัสแพ็กเกจกล่อง)]}$$

- **ชุด 3 ชิ้น (P-06):** รหัสโรงงาน `TMS06` + 3 ชิ้น `-3` + กล่อง `(P-06)` = **`TMS06-3(P-06)`**
- **ชุด 4 ชิ้น (P-16):** รหัสโรงงาน `TMS06` + 4 ชิ้น `-4` + กล่อง `(P-16)` = **`TMS06-4(P-16)`**
- **แก้วเดี่ยว (P-BAG):** รหัสโรงงาน `BW00` + ชิ้นเดี่ยว `-0` + ถุงของขวัญ `(P-BAG)` = **`BW00-0(P-BAG)`**

### 1.3 ความแตกต่างระหว่าง Catalog กับ Price List
- **Catalog (แคตตาล็อกสินค้า):** เน้นการนำเสนอคุณค่า ดีไซน์ รูปภาพ ความสวยงาม สเปกทางเทคนิค ตัวเลือกสี และโมเดล 3D เหมาะสำหรับลูกค้าและผู้บริหารใช้เลือกดูสินค้า (ไม่เน้นแสดงราคา หรือระบุเพียงราคาเริ่มต้น)
- **Price List (ใบแสดงรายการราคา):** เน้นโครงสร้างพาณิชย์ ขั้นบันได Tier จำนวนสั่งซื้อ ต้นทุน Landed Cost ราคาขายทั่วไป ราคาขายองค์กร อัตรากำไร (Margin) และยอดประหยัด สำหรับจัดซื้อ ฝ่ายขาย และการออกเอกสารบัญชี

### 1.4 การสอบทานอัตราแลกเปลี่ยนและต้นทุนโรงงานจริง (FX & Factory Cost Audit)
- ไฟล์ต้นทุนจริงของบริษัท (`01-ต้นทุน-20260612 Business Office Gift set catalog.xlsx` แถว 5846):
  - ราคา USD คำนวณจาก: `=15/6.5` = **$2.307692 USD (US$ 2.31)**
  - คอลัมน์ **"บาท"** คูณด้วยอัตราแลกเปลี่ยนฟิกซ์: **34.00 บาท / USD** (`=E5846*34`)
  - **ต้นทุนบาทที่แท้จริงคือ:** **`78.4615385` บาท (78.46 ฿)** (ห้ามใช้อัตราสปอตอื่นโดยพลการหากไม่ได้รับคำสั่งปรับฐาน FX ทั้งระบบ)

---

## ⏱️ 2. ลำดับเหตุการณ์และไทม์ไลน์การดำเนินงาน (Chronological Timeline)

| ลำดับ | กิจกรรม / คำสั่ง | การดำเนินการและผลลัพธ์ |
| :---: | :--- | :--- |
| **1** | ค่าขนส่งจุดเดียว ท่าเรือไปจุดหมายเดียว | กำหนดโมเดล Direct Single Drop อัตราเหมา 2,500 บาท/เที่ยว และนำมาหารเฉลี่ยเข้าสู่สูตร Landed Cost ต่อชุด |
| **2** | วาด Flowchart การคำนวณราคาเป็น .md และ Infographic | สร้าง Flowchart การคำนวณราคาตั้งแต่โรงงานจีนจนถึงราคาขายองค์กร พร้อม Render ภาพประกอบ Infographic |
| **3** | ชี้แจงที่มาตัวคูณส่วนลด | อธิบายกลไกตัวคูณส่วนลดตาม Volume Discount และการรักษาระดับ Safety Gross Margin |
| **4** | คำนวณราคาชุด `TMS06-4` (4 ชิ้น) | สกัดต้นทุนโรงงาน (\$14.46 USD), คำนวณราคา Tiers 100-1,000, สร้าง JSON, ออกแบบ Infographic Catalog และเขียนเอกสาร Spec |
| **5** | วางโครงสร้างรหัส FlowAccount และเปรียบเทียบต้นทุน | กำหนดรูปแบบ `Model-Number(Package)`, คำนวณราคาขายทั่วไป (Retail SRP) จากผลรวมราคาแยกชิ้นใน ProductMaster |
| **6** | คำนวณราคาชุด `TMS06-3` (3 ชิ้น) | จัดทำชุด 3 ชิ้น `TMS06-3(P-06)` (ต้นทุนโรงงาน \$11.00 USD), คำนวณตารางเปรียบเทียบกำไร และสร้าง Infographic |
| **7** | รวมเล่ม Master Excel (4 แท็บ) + Master JSON | รวมทั้ง TMS06-3 และ TMS06-4 เข้าด้วยกันใน `SmartGift_TMS06_Series_Pricing_Master.xlsx` และ JSON |
| **8** | วิเคราะห์ % Margin ราคาขายทั่วไป 2 รุ่น | เปรียบเทียบ Margin ขายทั่วไป (39.7%–51.5%) vs ขายองค์กร (24.1%–32.2%) และสรุปยอดที่องค์กรประหยัดได้ |
| **9** | คำนวณรุ่นแก้วเดี่ยว `BW00-0` | สกัดข้อมูลแถว 5846 (Vacuum cup 450ml จอ LED), สร้างรหัส `BW00-0(P-BAG)`, จัดทำ Excel และ JSON |
| **10** | ชี้แจงความแตกต่าง Catalog vs Price List | สรุปบทบาทหน้าที่ระหว่างสื่อแสดงสินค้า (Catalog) กับตารางเงื่อนไขการค้า (Price List) |
| **11** | สอบทานและแก้ไขต้นทุนจริง `BW00-0` | ผู้ใช้ส่งภาพแถว 5846 (`US$2.31` -> `78.4615385` บาท), ตรวจพบว่าไฟล์บริษัทใช้ FX 34.00, ดำเนินการปรับแก้ฐานทุนจาก 83.08 บาท เป็น **78.4615385 บาท** ใน Excel, CSV และ JSON ทั้งหมด |

---

## 📊 3. ตารางสรุปราคาและมาร์จิ้นทุกรุ่น (Master Price Summary)

### 3.1 ชุดของขวัญพรีเมียม TMS06 Series

| ช่วงสั่งซื้อ | TMS06-3(P-06) ทุนรวม | TMS06-3 ราคาขายองค์กร (Margin) | TMS06-4(P-16) ทุนรวม | TMS06-4 ราคาขายองค์กร (Margin) | ราคาขายทั่วไปอ้างอิง |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **100 ชุด** | 470.85 ฿ | **620.00 ฿** *(24.1%)* | 662.42 ฿ | **880.00 ฿** *(24.7%)* | 970 ฿ / 1,300 ฿ |
| **300 ชุด** | 428.98 ฿ | **590.00 ฿** *(27.3%)* | 610.08 ฿ | **850.00 ฿** *(28.2%)* | 840 ฿ / 1,130 ฿ |
| **500 ชุด** | 396.85 ฿ | **580.00 ฿** *(31.6%)* | 565.99 ฿ | **830.00 ฿** *(31.8%)* | 740 ฿ / 1,000 ฿ |
| **1,000 ชุด** | 379.95 ฿ | **560.00 ฿** *(32.2%)* | 543.10 ฿ | **800.00 ฿** *(32.1%)* | 670 ฿ / 900 ฿ |

### 3.2 แก้วทัมเบลอร์เดี่ยวจอ LED `BW00-0(P-BAG)` (ฐานทุนโรงงาน 78.4615385 บาท)

| ช่วงสั่งซื้อ | ต้นทุนรวมส่งมอบ (Landed Cost) | ราคาขายทั่วไป (Margin) | ราคาขายองค์กร (Margin) | องค์กรประหยัดได้/ชิ้น |
| :---: | :---: | :---: | :---: | :---: |
| **50 ชิ้น** | **145.48 ฿** | 250.00 ฿ *(41.8%)* | **189.00 ฿** *(23.0%)* | 61.00 ฿ |
| **100 ชิ้น** | **120.48 ฿** | 230.00 ฿ *(47.6%)* | **169.00 ฿** *(28.7%)* | 61.00 ฿ |
| **300 ชิ้น** | **103.81 ฿** | 215.00 ฿ *(51.7%)* | **149.00 ฿** *(30.3%)* | 66.00 ฿ |
| **500 ชิ้น** | **100.48 ฿** | 200.00 ฿ *(49.8%)* | **139.00 ฿** *(27.7%)* | 61.00 ฿ |
| **1,000 ชิ้น** | **97.98 ฿** | 185.00 ฿ *(47.0%)* | **129.00 ฿** *(24.0%)* | 56.00 ฿ |

---

## 📁 4. ทะเบียนไฟล์และ Artifacts ที่ถูกสร้างและอัปเดต (Artifacts Registry)

### 4.1 ชุด Master รวม (TMS06 Series)
* **Excel Workbook (4 แท็บ):** [SmartGift_TMS06_Series_Pricing_Master.xlsx](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/SmartGift_TMS06_Series_Pricing_Master.xlsx)
* **Master JSON:** [SmartGift_TMS06_Series_Pricing.json](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/SmartGift_TMS06_Series_Pricing.json)

### 4.2 ชุด 3 ชิ้น `TMS06-3(P-06)`
* **Excel Workbook:** [TMS06-3_P-06_pricing_comparison_sheet.xlsx](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-3_P-06_pricing_comparison_sheet.xlsx)
* **CSV:** [TMS06-3_pricing_comparison_sheet.csv](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-3_pricing_comparison_sheet.csv)
* **Extended JSON:** [TMS06-3_pricing_and_catalog_extended.json](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-3_pricing_and_catalog_extended.json)
* **Infographic Catalog (PNG):** [TMS06-3_catalog_infographic.png](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-3_catalog_infographic.png)
* **Spec Markdown:** [TMS06-3-PRICING-CATALOG-INFOGRAPHIC-2026-09-10.md](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-3-PRICING-CATALOG-INFOGRAPHIC-2026-09-10.md)

### 4.3 ชุด 4 ชิ้น `TMS06-4(P-16)`
* **Excel Workbook:** [TMS06-4_P-16_pricing_comparison_sheet.xlsx](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-4_P-16_pricing_comparison_sheet.xlsx)
* **CSV:** [TMS06-4_pricing_comparison_sheet.csv](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-4_pricing_comparison_sheet.csv)
* **Extended JSON:** [TMS06-4_pricing_and_catalog_extended.json](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-4_pricing_and_catalog_extended.json)
* **Infographic Catalog (PNG):** [TMS06-4_catalog_infographic.png](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-4_catalog_infographic.png)
* **Spec Markdown:** [TMS06-4-PRICING-CATALOG-INFOGRAPHIC-2026-09-10.md](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/TMS06-4-PRICING-CATALOG-INFOGRAPHIC-2026-09-10.md)

### 4.4 แก้วเดี่ยวจอ LED `BW00-0(P-BAG)`
* **Excel Workbook (แก้ไขฐานทุน 78.46 ฿):** [BW00-0_pricing_comparison_sheet.xlsx](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/BW00-0_pricing_comparison_sheet.xlsx)
* **Catalog & Pricing JSON:** [BW00-0_pricing_and_catalog.json](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/BW00-0_pricing_and_catalog.json)
* **CSV:** [BW00-0_pricing_comparison_sheet.csv](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/BW00-0_pricing_comparison_sheet.csv)

### 4.5 เอกสารพิมพ์เขียวกลยุทธ์ธุรกิจ (`06_business_pdf`)
* **Markdown Spec:** [docs/specs/SPEC-BUSINESS-PDF-BLUEPRINTS-2026-09-10.md](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/SPEC-BUSINESS-PDF-BLUEPRINTS-2026-09-10.md)
* **JSON Registry:** [docs/specs/business_pdf_blueprints_registry.json](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/business_pdf_blueprints_registry.json)
* **Directory README:** [data-pipeline/01_raw/06_business_pdf/README.md](file:///c:/Users/pc/workspace/business-01-smart-gift/data-pipeline/01_raw/06_business_pdf/README.md)
* **Prepared Dataset:** [data-pipeline/02_prepared/business_pdf_blueprints.json](file:///c:/Users/pc/workspace/business-01-smart-gift/data-pipeline/02_prepared/business_pdf_blueprints.json)

### 4.6 สเปกและสัญญาโครงสร้างข้อมูลฉบับสมบูรณ์ (Full Enterprise Master Schema)
* **Contract Schema:** [contracts/smartgift-full-master.schema.json](file:///c:/Users/pc/workspace/business-01-smart-gift/contracts/smartgift-full-master.schema.json)
* **Enterprise Spec (.md):** [docs/specs/SPEC-FULL-ENTERPRISE-SCHEMA-2026-09-10.md](file:///c:/Users/pc/workspace/business-01-smart-gift/docs/specs/SPEC-FULL-ENTERPRISE-SCHEMA-2026-09-10.md)
