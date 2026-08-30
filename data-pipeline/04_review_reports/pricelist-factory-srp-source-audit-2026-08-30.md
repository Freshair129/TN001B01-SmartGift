---
version: "0.3.0b"
created_at: "2026-08-30T13:26:50+07:00,ATHER"
last_update: "2026-08-30T15:25:41+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-pricing"
  doc_type: "source-audit"
  scope: "SRP quantity comparison artifact; exact factory identity and CBM scenario"
---

# Pricelist: SRP และ quantity tiers ที่มีใน master

ตารางนี้เป็นผลตรวจแหล่งข้อมูลและชี้ไปยังผลเปรียบเทียบใน `pricelist_master.json` ไม่ได้เปลี่ยนราคาใน master หรือคำนวณ SRP ใหม่

- SRP ที่ประกาศใน master มี 16 รายการ; เป็นค่าจากตารางใน pipeline/enrich_review_catalog.py ไม่ใช่หลักฐานรับรองราคาตลาดหรือ quote approval
- ตรวจ source factory catalog price-boss/ราคา.sql แล้ว ไม่พบ code ตรงกับ 16 รายการนี้ จึงยังไม่เติมต้นทุน ไม่ใช้ base_cost ที่เท่ากับ SRP เป็นทุน
- คอลัมน์ qty แสดงครบ `1, 10, 20, 50, 100, 300, 500, 1000` ตามที่ผู้ใช้ยืนยัน โดย @1 คือราคา SRP ของชิ้นเดียว
- exporter สร้าง `srp_qty_comparisons` 128 แถว (16 สินค้า × 8 qty) และ `price_comparisons` จาก SQL snapshot อีก 669 แถว
- CBM ในแถว SRP เป็น estimate จาก carton dimensions/UPC ใน master ภายใต้ scenario กวางโจว–เซินเจิ้น รถ สินค้าทั่วไปหรืออิเล็กทรอนิกส์ GOLD; ยังไม่ใช่ measured freight
- เงื่อนไขกำไร pkg ขั้นต่ำ 25,000 บาทยังคงเดิม แต่ seasonal package gate ทั้ง 11 รายการเป็น
  `missing_inputs` เพราะต้นทุนโรงงาน/จำนวน/ฐานราคาไม่ครบ; ไม่ประกาศรายการใดว่าผ่าน

ผล artifact: `pricelist_master.json` SHA-256 `d0cde107f8351bf3e59487204987cfde5584817ccbc2f1bc31a100691fbe447a`; `price_comparisons` จับคู่ exact code ได้ 404/669 แถว แต่ canonical PM ได้ 0/16 จึงไม่คำนวณกำไรหรือประกาศผ่านเกณฑ์ 25,000 บาท. Artifact เดียวกันมี seasonal offers 6, packages 11 และ proposed BOM 17 edges

หน่วย: บาทต่อหน่วยตาม source; ยังต้องตรวจฐาน VAT/variant และที่มาราคาก่อนใช้จริง

| รหัส | ทุนโรงงาน | SRP / @1 | @10 | @20 | @50 | @100 | @300 | @500 | @1000 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PM-TMB | ยังจับคู่ไม่ได้ | 320.00 | 290.00 | 270.00 | 250.00 | 230.00 | 215.00 | 200.00 | 185.00 |
| PM-SPK | ยังจับคู่ไม่ได้ | 480.00 | 440.00 | 410.00 | 380.00 | 350.00 | 320.00 | 295.00 | 275.00 |
| PM-PB10K | ยังจับคู่ไม่ได้ | 690.00 | 620.00 | 580.00 | 540.00 | 490.00 | 450.00 | 420.00 | 390.00 |
| PM-CFMUG | ยังจับคู่ไม่ได้ | 299.00 | 270.00 | 250.00 | 230.00 | 210.00 | 195.00 | 180.00 | 165.00 |
| PM-UMB | ยังจับคู่ไม่ได้ | 250.00 | 220.00 | 200.00 | 185.00 | 170.00 | 155.00 | 140.00 | 130.00 |
| PM-MSG | ยังจับคู่ไม่ได้ | 850.00 | 780.00 | 720.00 | 660.00 | 600.00 | 550.00 | 500.00 | 460.00 |
| PM-NB | ยังจับคู่ไม่ได้ | 750.00 | 680.00 | 630.00 | 590.00 | 540.00 | 490.00 | 450.00 | 420.00 |
| PM-PEN | ยังจับคู่ไม่ได้ | 190.00 | 160.00 | 145.00 | 130.00 | 120.00 | 110.00 | 100.00 | 90.00 |
| PM-MUG-HEAT | ยังจับคู่ไม่ได้ | 350.00 | 310.00 | 290.00 | 270.00 | 245.00 | 225.00 | 210.00 | 195.00 |
| PM-FLASH | ยังจับคู่ไม่ได้ | 220.00 | 190.00 | 175.00 | 160.00 | 145.00 | 135.00 | 125.00 | 115.00 |
| PM-BOTTLE-LED | ยังจับคู่ไม่ได้ | 290.00 | 260.00 | 240.00 | 220.00 | 200.00 | 185.00 | 170.00 | 155.00 |
| PM-CUTLERY | ยังจับคู่ไม่ได้ | 165.00 | 140.00 | 130.00 | 120.00 | 110.00 | 100.00 | 92.00 | 85.00 |
| PM-TEA-INF | ยังจับคู่ไม่ได้ | 360.00 | 320.00 | 300.00 | 280.00 | 255.00 | 235.00 | 220.00 | 205.00 |
| PM-AROMA | ยังจับคู่ไม่ได้ | 550.00 | 490.00 | 460.00 | 420.00 | 380.00 | 350.00 | 320.00 | 295.00 |
| PM-FAN | ยังจับคู่ไม่ได้ | 260.00 | 230.00 | 210.00 | 195.00 | 175.00 | 160.00 | 148.00 | 138.00 |
| PM-DESK-MAT | ยังจับคู่ไม่ได้ | 590.00 | 530.00 | 490.00 | 450.00 | 410.00 | 375.00 | 345.00 | 320.00 |

## Source fingerprints

- smartgift_catalog_master.json SHA-256: `63f3e5668de6818cc3517543bdf0d1331bf7926d1769815290dbcd5f740c0ac7`
- ราคา.sql SHA-256: `d85e114018a4792d7a3aa8fc9b4f35475f40e9948bffd5aa04cf0171b5c9cb24`
- config/pricing_rules_formula.yaml SHA-256: `f4473230f10b59133936974a0cacf84bbe84865d61db76553d8cc2a58ba635fc`

## Version diff

0.1.0b → 0.2.0b: ยืนยัน qty 1 และทุก quantity tier; เขียน comparison rows ลง `pricelist_master.json` พร้อม exact-code factory matching, CBM scenario และ null เมื่อหลักฐานต้นทุนไม่ครบ
0.2.0b → 0.3.0b: อัปเดต hash หลัง seasonal projection; เพิ่ม package gate/BOM coverage note โดยคง factory identity ของ canonical PM เป็น missing

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.3.0b | 2026-08-30 | beta | อัปเดต hash และผล seasonal offers/packages/proposed BOM; package gate 25,000 ยัง missing_inputs จากต้นทุน PM ที่ไม่ยืนยัน | uncommitted | ATHER |
| 0.2.0b | 2026-08-30 | beta | เพิ่ม SRP/qty 128 แถว, SQL comparison 669 แถว และ CBM scenario; exact factory match ของ PM 0/16 จึงไม่เติมต้นทุน | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | ตรวจ SRP และ qty matrix จาก master; รอ scope และ cost identity | uncommitted | ATHER |
