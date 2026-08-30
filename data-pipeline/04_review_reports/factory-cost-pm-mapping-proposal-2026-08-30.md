---
version: "0.2.0b"
created_at: "2026-08-30T18:05:00+07:00,CLAUDE"
last_update: "2026-08-30T18:20:00+07:00,CLAUDE"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-pricing"
  doc_type: "mapping-proposal"
  scope: "PM ↔ factory cost item pairing — 9 คู่ confirmed โดย Boss 2026-08-30"
---

# ข้อเสนอจับคู่ PM ↔ Factory Cost Item — ✅ Boss ยืนยันแล้ว 9 คู่ (2026-08-30)

แหล่งข้อมูล: `02_prepared/factory_costs.json` (1,166 records, ingest 2026-08-30, lane 08)
อัตราแลกเปลี่ยนอ้างอิง `config/pricing_rules_formula.yaml`: USD→THB 32.50, CNY→THB 5.00
ราคาทุกตัวเป็น **EXW ต่อหน่วย ยังไม่รวม freight + duty** (landed cost ต้องผ่าน pricing formula)

คอลัมน์ `ยืนยัน`: ให้ Boss ใส่ ✅ / ❌ / รหัสอื่นที่ต้องการแทน — คู่ที่ยืนยันแล้วเท่านั้นจึงจะถูกเติมเข้า
`pricelist_master.json` (ADR-005)

## กลุ่ม A — ความมั่นใจสูง (สเปคตรงหลายจุด)

| PM | สินค้า canonical | Factory item | สเปคที่ตรง | EXW | ≈THB | ยืนยัน |
|---|---|---|---|---|---:|---|
| PM-MSG | เครื่องนวดคอ Low Pulse & ประคบร้อน | `TBY17-1` Neck massager | low pulse ✓, 15 levels, 2.5W, แขนยืดได้ | 3.60 USD | ฿117 | ✅ Boss |
| PM-MUG-HEAT | แก้วเซรามิก + แท่นอุ่น 55°C | `TN00-2` 55℃ Cup set | ceramic 350ml + heating pad 55℃ ✓✓ | 2.31 USD | ฿75 | ✅ Boss |
| PM-NB | สมุดโน้ต PU ฝังพาวเวอร์แบงก์ชาร์จไร้สาย | `TNA0014` (catalog powerbank-notebook) | A4 PU, wireless+cable, 8000mAh+จอ, แถม flash 32G + ปากกา | 18.77 USD | ฿610 | ✅ Boss |
| PM-CFMUG | แก้วกาแฟพกพาสแตนเลส 316 ฝา 3 ระบบ | `TJS00-1` Coffee Mug | 380ml, Ceramic Coated **316SUS** ✓, เก็บอุณหภูมิ 6 ชม. | 4.77 USD | ฿155 | ✅ Boss |
| PM-BOTTLE-LED | กระบอกน้ำบอกอุณหภูมิหน้าจอ Smart LED | `TDK01-1` Vacuum Cup | 450ml, 304 SS, **temperature display** ✓, กล่อง drawer+ถุงหิ้ว | 2.31 USD | ฿75 | ✅ Boss |

## กลุ่ม B — ความมั่นใจกลาง (ตรงบางส่วน / สเปคต่างเล็กน้อย — ระบุ gap ให้แล้ว)

| PM | สินค้า canonical | Factory item | Gap | EXW | ≈THB | ยืนยัน |
|---|---|---|---|---|---:|---|
| PM-UMB | ร่มพับออโต้ 6 ตอน UPF50+ | `TYS01-1` Umbrella | 8K auto open&close ✓ แต่ไม่ระบุ 6 ตอน/UPF50+ | 2.46 USD | ฿80 | ✅ Boss |
| PM-PB10K | พาวเวอร์แบงก์แม่เหล็กไร้สาย 10,000mAh + Stand | `TZJ00-1` Four cables power bank stand | 10000mAh ✓ stand ✓ แต่เป็นสาย 4 หัว **ไม่ใช่ MagSafe ไร้สาย** (ทางเลือกถูกกว่า: `TSX00-1` ฿166) | 7.15 USD | ฿232 | ✅ Boss (เลือก TZJ00-1) |
| PM-TMB | ทัมเบลอร์เก็บอุณหภูมิ SUS316 | `BW00-0` Vacuum cup | 450ml แต่เป็น **304** ไม่ใช่ 316 (ทางเลือก: `TBT12-0` ฿120 มีจออุณหภูมิ) | 2.31 USD | ฿75 | ✅ Boss (เลือก BW00-0) |
| PM-FLASH | แฟลชไดรฟ์โลหะหมุน Dual (Type-C/USB3.0) | composite: shell `Swivel usb` 1.3 RMB + chip PCBA 64G USB3.0 15.5 RMB (MOQ 500) | ราคา = shell+chip ต้องเลือก capacity; ตาราง chip ไม่ระบุ dual Type-C | 16.8 RMB | ฿84 | ✅ Boss (64G USB3.0) |

## กลุ่ม C — ไม่พบ single item ที่จับคู่ได้ (มีเฉพาะในชุด/ไม่มีเลย)

| PM | สินค้า canonical | สถานะหลักฐาน | ข้อเสนอ |
|---|---|---|---|
| PM-SPK | ลำโพงบลูทูธสเตอริโอคู่ 5W | มี speaker เป็นชิ้นส่วนในชุด (TDD03-2 ฯลฯ); single มีแต่ `TYD0060` ซึ่งเป็น desk clock multi-function คนละสินค้า | ขอ quote แยกชิ้นจากโรงงาน |
| PM-PEN | ปากกาไม้วอลนัทหัวทองเหลือง | มีแต่ปากกาพลาสติกแถมในชุดสมุด | ขอ quote / หา supplier อื่น |
| PM-FAN | พัดลมพกพาจอดิจิทัล 4000mAh | Turbo Handheld Fan มีเฉพาะเป็นชิ้นส่วนชุด (แยกราคาไม่ได้) | ขอ quote แยกชิ้น |
| PM-TEA-INF | กระบอกชงชาแก้ว Borosilicate 2 ชั้น | glass bottle + tea infuser มีเฉพาะในชุด TJS24/25xx | ขอ quote แยกชิ้น |
| PM-AROMA | เครื่องอโรมาเปลวไฟ | ไม่พบทั้ง 3 ไฟล์ (humidifier มีในชุดเท่านั้น) | หา supplier / ไฟล์ต้นทุนเพิ่ม |
| PM-CUTLERY | ชุดช้อนส้อมมีดพกพา | ไม่พบ | หา supplier / ไฟล์ต้นทุนเพิ่ม |
| PM-DESK-MAT | แผ่นรองโต๊ะหนังชาร์จไร้สาย | wireless mouse pad มีเฉพาะในชุด TRM05/03xx | ขอ quote แยกชิ้น |

## หมายเหตุการตัดสินใจ

1. `TDK01-1`/`TBT12-0` มี temperature display จึงถูกเสนอเข้า PM-BOTTLE-LED แทน PM-TMB
   (แม้ keyword แรกจะชี้ไป tumbler) — ถ้า Boss เห็นต่างให้สลับได้
2. ราคา MOQ: catalog gift set ระบุ "MOQ 1 pc สำหรับ stock items"; USB flashdrive MOQ 500
3. เมื่อยืนยันแล้ว ขั้นถัดไป: เติม `factory_cost_thb`/`factory_unit_cny`/`supplier` ลง
   pricelist master ผ่าน exporter (เฉพาะแถว confirmed) แล้วรัน profit gate ใหม่

## ผลการ integrate เข้า pricelist master (2026-08-30)

Exporter รับ `factory_cost_pm_mapping.json` เป็น input hash-pinned แล้วเติมต้นทุน EXW:

- **BOM: 13/17 edges ได้ต้นทุน** (4 edges ที่เหลือติด PM-PEN ×2, PM-AROMA, PM-TEA-INF)
- **Package ครบทุกชิ้น 3 ชุด:**
  - `PKG-XMAS-2026-REACH-OPS` — EXW ฿230/ชุด (SRP รวม ฿860)
  - `PKG-XMAS-2026-SELECT-MID` — EXW ฿230/ชุด; indicative profit ฿320/ชุด ที่ราคา offer @qty10 ฿550 (ยังไม่รวม freight/duty/VAT)
  - `PKG-NY-2027-REACH-OPS` — EXW ฿150/ชุด (SRP รวม ฿610)
- **Partial 3 ชุด:** XMAS-SIGNATURE (ขาด PM-PEN), NY-SELECT-MID (ขาด PM-AROMA), NY-SIGNATURE (ขาด PM-PEN, PM-TEA-INF)
- **Profit gate ฿25,000:** ทุก package ยังสถานะ `missing_inputs` ตามนโยบาย — `factory_identity`/`factory_cost` ถูกปลดแล้วสำหรับ 3 ชุดที่ครบ แต่ยังรอ **quote_quantity, package_price, target_recipients, freight evidence, VAT basis** ซึ่งเป็น commercial input จาก company order brief
- Public projection ตรวจแล้วไม่มี field ต้นทุนหลุด; unit tests 61 ตัวผ่าน; `--check` determinism ผ่าน

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.3.0b | 2026-08-30 | beta | integrate mapping เข้า exporter: BOM 13/17 costed, 3 pkg full coverage, gate ปลด factory inputs แล้วเหลือ commercial inputs | uncommitted | CLAUDE |
| 0.2.0b | 2026-08-30 | beta | Boss ยืนยันครบ 9 คู่ (A ทั้ง 5, PB10K=TZJ00-1, TMB=BW00-0, UMB=TYS01-1, FLASH=shell+chip 64G USB3.0); บันทึกลง 02_prepared/factory_cost_pm_mapping.json | uncommitted | CLAUDE |
| 0.1.0b | 2026-08-30 | beta | ข้อเสนอจับคู่ 9 PM (A:5, B:4) + 7 PM ไม่มี single match; รอ Boss ยืนยัน | uncommitted | CLAUDE |
