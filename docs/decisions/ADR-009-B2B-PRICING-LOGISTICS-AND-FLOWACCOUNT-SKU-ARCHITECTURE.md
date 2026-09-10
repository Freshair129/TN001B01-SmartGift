---
version: "1.0.0"
created_at: "2026-09-10T13:26:00+07:00,Antigravity,uncommitted"
last_update: "2026-09-10T13:26:00+07:00,Antigravity"
status: "approved"
superseded_by: null
attributes:
  domain: "b2b-pricing-and-procurement"
  doc_type: "architecture-decision"
  scope: "B2B pricing calculation, direct single-drop shipping absorption, and FlowAccount SKU naming convention"
  language: "th"
---

# ADR-009 — สถาปัตยกรรมโครงสร้างราคา B2B, การกระจายค่าขนส่ง Single Drop และมาตรฐานรหัสสินค้า FlowAccount

**Status:** Approved / Binding Invariant — มีผลบังคับใช้กับระบบ SmartGift (Business 01), ERP FlowAccount Adapter, Catalog Generator และ Zuri-AI Procurement Integration<br>
**Date:** 2026-09-10<br>
**Proposed by:** Antigravity; อนุมัติขอบเขต: Boss / User<br>
**Complexity / Risk:** C-2 / MEDIUM — สัญญาข้อกำหนดการตั้งรหัสสินค้า (SKU) ข้ามระบบ และสูตรคำนวณต้นทุนรวมส่งมอบ (Landed Cost)<br>
**Relates to:** [AGENTS.md](../../AGENTS.md), [SPEC-FULL-ENTERPRISE-SCHEMA-2026-09-10](../specs/SPEC-FULL-ENTERPRISE-SCHEMA-2026-09-10.md), [contracts/smartgift-full-master.schema.json](../../contracts/smartgift-full-master.schema.json), [ADR-006](ADR-006-PRIVATE-REPOSITORY-SOURCE-DATA-EXCEPTION.md), [ADR-007](ADR-007-KNOWLEDGE-REGISTRY-AND-PROVENANCE.md), [06_business_pdf](../../data-pipeline/01_raw/06_business_pdf/README.md)

---

## 1. บริบทและปัญหา (Context & Problem Statement)

ในกระบวนการจัดทำข้อมูลสินค้าและราคาสำหรับลูกค้านิติบุคคล (B2B Corporate Gifts) ของบริษัท เทราบิส จำกัด (`Therabis Co., Ltd.`) ภายใต้ระบบ **SmartGift (Business 01)** พบปัญหาความไม่ชัดเจนเชิงสถาปัตยกรรม 5 ประการ:

1. **ความกำกวมของรหัสสินค้า (SKU Ambiguity):** ข้อมูลดิบจากโรงงานจีนบันทึกเพียงรหัสโมเดลเดี่ยว เช่น `TMS06-4` หรือ `BW00-0` ซึ่งไม่ระบุรหัสกล่องบรรจุภัณฑ์และจำนวนชิ้น ทำให้เมื่อนำเข้าสู่ระบบบัญชี FlowAccount เกิดความสับสนว่าชุดดังกล่าวบรรจุในกล่องประเภทใด (เช่น กล่องสั้น P-06, กล่องยาว P-16 หรือถุง P-BAG)
2. **การจัดการต้นทุนค่าขนส่งในประเทศ (Domestic Logistics Cost):** ค่าขนส่งในไทยแบบเหมาคันรถ (Direct Single Drop) ไม่เคยถูกนิยามให้ชัดเจนว่าจะแสดงเป็นค่าบริการแยกต่างหาก หรือรวมเข้าไปในราคาสินค้าต่อหน่วย
3. **การปะปนระหว่าง Catalog กับ Price List:** แคตตาล็อกสินค้าหน้าร้านและตารางราคาเชิงพาณิชย์เคยผูกติดกัน ทำให้เมื่อราคาต้นทุนหรืออัตราแลกเปลี่ยนผันผวน ส่งผลให้ต้องรื้อแคตตาล็อกใหม่ทั้งหมด
4. **ความคลาดเคลื่อนของอัตราแลกเปลี่ยน (FX Baseline Drift):** การใช้ Spot Rate ปัจจุบัน (เช่น 36.00 ฿/USD) ไปคำนวณต้นทุนสินค้าที่โรงงานล็อกราคาไว้ด้วยเรทคงที่ในไฟล์ต้นทุน (34.00 ฿/USD) ส่งผลให้เกิดความคลาดเคลื่อนทางบัญชี
5. **การขาดสัญญาโครงสร้างข้อมูลกลาง (Schema Contract):** ขาด JSON Schema มาตรฐานในการตรวจสอบความถูกต้องของข้อมูลราคาก่อนออกใบเสนอราคา (Quotation)

---

## 2. ข้อตัดสินใจเชิงสถาปัตยกรรม (Architectural Decisions)

ที่ประชุมสถาปัตยกรรมระบบได้มีมติเห็นชอบข้อกำหนดมาตรฐานถาวร (Binding Invariants) 5 ข้อดังนี้:

### D1. มาตรฐานการตั้งรหัส FlowAccount SKU (FlowAccount Naming Invariant)
กำหนดให้รหัสสินค้าหลักในระบบ FlowAccount สำหรับสินค้าพรีเมียมและชุดของขวัญ ต้องประกอบด้วย 3 องค์ประกอบหลักตามรูปแบบ:
$$\mathbf{[รหัสโมเดลโรงงาน]} + \mathbf{[-จำนวนชิ้นในชุด]} + \mathbf{[(รหัสแพ็กเกจกล่อง)]}$$
- **Pattern RegEx:** `^[A-Z0-9]+-[0-9]+\(P-[A-Z0-9]+\)$`
- **ตัวอย่าง:**
  - `TMS06-4(P-16)` = โมเดลโรงงาน `TMS06` + ชุด 4 ชิ้น `-4` + กล่องยาวพรีเมียม `(P-16)`
  - `TMS06-3(P-06)` = โมเดลโรงงาน `TMS06` + ชุด 3 ชิ้น `-3` + กล่องสี่เหลี่ยมพรีเมียม `(P-06)`
  - `BW00-0(P-BAG)` = โมเดลโรงงาน `BW00` + ชิ้นเดี่ยว `-0` + ถุงของขวัญหูหิ้ว `(P-BAG)`

### D2. นโยบายการกระจายค่าขนส่งจุดเดียว (Direct Single Drop Absorption)
- โลจิสติกส์ในประเทศสำหรับลูกค้าองค์กร กำหนดให้ใช้โมเดล **Direct Single Drop** (ท่าเรือไทย คลองเตย/แหลมฉบัง ตรงสู่โกดังลูกค้าปลายทางจุดเดียว) ในอัตราเหมามาตรฐาน **2,500 บาท / เที่ยว**
- บังคับใช้สูตรกระจายค่าขนส่งเข้าไปในต้นทุนรวมส่งมอบต่อหน่วย (Landed Cost per Unit):
  $$	ext{domestic\_freight\_thb} = rac{2,500}{	ext{quantity}}$$
  $$	ext{total\_landed\_cost\_thb} = 	ext{factory\_exw\_thb} + 	ext{sea\_freight\_thb} + 	ext{customization\_thb} + 	ext{domestic\_freight\_thb}$$
- **ผลลัพธ์เชิงพาณิชย์:** ในใบเสนอราคา (Quotation) รายการค่าจัดส่งจะแสดงเป็น **`0.00 บาท (ฟรีค่าจัดส่ง)`** โดยถูกดูดซับเข้าไปในมาร์จิ้นของสินค้าแล้ว

### D3. การแยกสถาปัตยกรรม Catalog ออกจาก Price List (Decoupling Policy)
- **Catalog (Presentation Layer):** มีหน้าที่แสดงความสวยงาม สเปกทางเทคนิค ตัวเลือกสี และภาพจัดเซ็ตตามปรัชญา `Recipient-First` และ `Unboxing Engineering` จากเอกสาร `06_business_pdf` **ห้ามระบุราคาตายตัวหรือ Margin ภายใน** (แสดงสถานะเป็น 'สอบถามราคา' หรือ 'ราคาเริ่มต้น')
- **Price List (Commercial & Accounting Layer):** บริหารจัดการแยกต่างหากตามขั้นบันไดจำนวนสั่งซื้อ (Tiers 50, 100, 300, 500, 1,000+) ควบคุม Gross Margin ให้อยู่ในเกณฑ์ปลอดภัย:
  - **ราคาขายทั่วไป (Retail SRP):** Target Gross Margin **39% – 52%**
  - **ราคาขายองค์กร (Corporate B2B):** Target Gross Margin **20% – 35%**

### D4. การล็อกฐานต้นทุนโรงงานจริงและอัตราแลกเปลี่ยน (FX Baseline Governance)
- ในไฟล์ต้นทุนโรงงานจริงของบริษัท (`01-ต้นทุน-20260612 Business Office Gift set catalog.xlsx` แถว 5846) กำหนดให้อัตราแลกเปลี่ยนคงที่ที่ **`34.00 บาท / USD`**
- ต้นทุนบาทโรงงานต้องคำนวณจากสูตรตรงของเซลล์ เช่น `BW00-0`: `=15/6.5 * 34` = **`78.4615385` บาท (78.46 ฿)**
- ห้ามนำอัตราแลกเปลี่ยน Spot ลอยตัวมาปรับแก้ฐานทุนโดยไม่ผ่านมติ Commercial Approval

### D5. การประกาศใช้ Full Enterprise Master Schema
- ประกาศให้ไฟล์ [`contracts/smartgift-full-master.schema.json`](../../contracts/smartgift-full-master.schema.json) เป็นสัญญากลางที่ผูกพันการทำงานระหว่าง:
  1. ตัวแปลงข้อมูลดิบ (FlowAccount Normalizer / Stage 2)
  2. ตัวสร้างใบเสนอราคา (Quotation Engine)
  3. ระบบจัดซื้อและใบรับสินค้าของ Zuri-AI Procurement Module

---

## 3. ผลกระทบและการบังคับใช้ (Consequences & Enforcement)

### ด้านบวก (Positive):
1. **ความถูกต้องระดับบัญชี 100%:** ฝ่ายจัดซื้อและคลังสินค้าทราบทันทีจากรหัส SKU ว่าต้องเบิกกล่องบรรจุภัณฑ์รหัสใด (เช่น P-16 หรือ P-06)
2. **จุดขายส่งฟรีที่คุ้มทุนจริง:** ลูกค้าองค์กรประทับใจที่ได้ฟรีค่าจัดส่ง ในขณะที่บริษัทรักษา Margin ปลอดภัยไว้แล้วทุก Tier
3. **ความปลอดภัยของข้อมูล (Zero-PII):** ไม่มีต้นทุนจริง มาร์จิ้น หรือข้อมูลส่วนบุคคลหลุดรอดไปยังหน้าเว็บแคตตาล็อกสาธารณะ

### ข้อจำกัดและการเฝ้าระวัง (Trade-offs & Operational Guards):
1. **กรณีส่งหลายจุด (Multi-Drop):** หากลูกค้าต้องการให้กระจายสินค้าหลายสาขาหรือจัดส่งรายบุคคลถึงบ้าน (Home Fulfillment) ต้องคิดค่าบริการเสริมแยกต่างหากตาม Option B, C, D ในสเปกโลจิสติกส์
2. **การตรวจสอบความสอดคล้องของ Schema:** ทุก Payload ข้อมูลสินค้าก่อนขึ้นสู่ระบบ Production ต้องผ่านการ Validate ด้วย `jsonschema.validate()` เทียบกับ `smartgift-full-master.schema.json`
