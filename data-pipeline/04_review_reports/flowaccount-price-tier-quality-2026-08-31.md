---
version: "0.1.0b"
created_at: "2026-08-31T00:40:00+07:00,Claude"
last_update: "2026-08-31T00:40:00+07:00,Claude"
status: "candidate"
superseded_by: null
attributes:
  domain: "catalog-pricing"
  doc_type: "data-quality-review"
  scope: "smartgift_price (FlowAccount export 2026-06-21) — tier/price anomalies found 2026-08-30/31"
---

# smartgift_price — รายการ tier/ราคาที่ต้องยืนยันกับ FlowAccount

พบระหว่างตรวจสอบข้าม session (cross-session review, 2026-08-30/31) ว่าตัวเลข "offer ที่มีราคาจริง"
ที่เคยรายงานไว้ (221/1,110) นับรวมแถวที่ `price_missing=true` ปนอยู่ด้วย ตัวเลขที่ถูกต้องคือ
**122/1,110 offers (11%) มีราคาจริงอย่างน้อย 1 tier** ไม่ใช่ 221 (20%)

ราคาทั้งหมดมาจาก FlowAccount export วันเดียว `2026-06-21` (`price-boss/sql/smartgiftpricelist.postgres.sql`,
sha256 `26355664...`) — ณ วันที่ทำรายงานนี้ (2026-08-31) ข้อมูลเก่าไปแล้ว ~10 สัปดาห์

**สำคัญ:** ค่าที่ผิดปกติด้านล่างนี้ยืนยันแล้วว่า**มีอยู่ในไฟล์ SQL ต้นทางจริง** (ตรวจ raw INSERT
statement โดยตรง) ไม่ใช่บั๊กจากการ parse ของ `pipeline/export_pricelist_master.py` — ตามกฎ AGENTS.md
ข้อ 2 (ห้ามแก้ไฟล์ราคาต้นทาง) เอกสารนี้จึง **ไม่แก้ค่าใด ๆ ในต้นทาง** มีแต่ทำให้ exporter มองเห็นและ
แยกแยะกรณีเหล่านี้ชัดเจนขึ้น (ผ่าน `data_quality_issues` ใหม่ 2 ประเภท) แล้วบันทึกไว้ให้คนตรวจสอบต่อกับ
FlowAccount

## กลุ่ม A — qty_tier ผิดปกติ (`non_standard_qty_tier`, 5 แถว)

ค่าเหล่านี้ไม่อยู่ใน tier ที่ใช้บ่อย (10/20/50/100/500/1000 ~107-110 แถวต่อค่า) และไม่ใช่ tier ที่มี
ความหมายทางธุรกิจที่ประกาศไว้แล้ว (`SRP_QTY_TIERS` = 1/10/20/50/100/300/500/1000) — สงสัยว่าเป็นการ
กรอกข้อมูลผิดพลาดฝั่ง FlowAccount (เช่น เอารหัส/เลขอื่นมาใส่ช่อง tier)

| offer_code | qty_tier | unit_price | flow_account_code | ข้อสงสัย |
|---|---:|---:|---|---|
| TDS07-2 | 5012 | ฿1,100 | `TDS07-2(P-02)-5012` | 5012 ไม่เข้าพวกกับ ladder ปกติของสินค้านี้เอง (10/20/50/100 อยู่แล้ว) |
| TYD0262 | 11 | ฿1,180 | `TYD0262(P-2D)-11` | 4 แถวติดกัน (11-14) ห่างกันทีละ 1 — ไม่ตรงรูปแบบ ladder แบบคูณ (10→20→50) |
| TYD0262 | 12 | ฿1,110 | `TYD0262(P-2D)-12` | เช่นเดียวกัน |
| TYD0262 | 13 | ฿1,050 | `TYD0262(P-2D)-13` | เช่นเดียวกัน |
| TYD0262 | 14 | ฿980 | `TYD0262(P-2D)-14` | เช่นเดียวกัน |

**ผลกระทบที่แก้ไปแล้ว:** ทั้ง TDS07-2 และ TYD0262 เป็นชุดของขวัญที่อยู่ใน customer catalog media
allowlist จริง — ก่อนแก้ offline catalog build (`pipeline/build_offline_catalog.py`) จะโชว์ราคาที่
qty "5012+"/"11+"-"14+" ให้ลูกค้าเห็นตรง ๆ ตอนนี้ตัดออกจาก ladder ที่แสดงลูกค้าแล้ว (ใช้
`data_quality_issues` แทนการเดา/แก้ตัวเลข)

**สิ่งที่ต้องทำต่อ:** สอบถาม FlowAccount/ทีมขายว่า TDS07-2 ควรมี tier 5012 จริงหรือควรเป็นค่าอื่น
(เช่น 500 หรือ 12) และ TYD0262's 11-14 เป็น custom ladder เฉพาะสินค้านี้จริงหรือกรอกผิด

## กลุ่ม B — มีราคาจริงแต่ไม่มี qty_tier (`priced_without_qty_tier`, 16 แถว)

แถวเหล่านี้ **ไม่ใช่ราคาที่ขาดหาย** — `price_missing=false` และมี `unit_price` จริง เพียงแต่ไม่ผูกกับ
quantity tier ใด ๆ (อาจเป็นราคาเดี่ยวแบบไม่มีบันไดราคา หรือราคาประจำกลุ่ม `price_list_group` ที่ไม่ระบุ
จำนวน) — ก่อนหน้านี้แถวเหล่านี้ถูกนับรวมกับแถว "ราคาหาย" แบบไม่แยกแยะ ทำให้เข้าใจผิดว่าเป็นข้อมูล
เสีย

| offer_code | unit_price | price_list_group |
|---|---:|---|
| TBH03-3 | ฿850 | — |
| TBH04-1 | ฿570 | P-02 |
| TBH11-2 | ฿1,380 | — |
| TCC00-2 | ฿640 | — |
| TCS00-2 | ฿940 | — |
| TCS40-3 | ฿1,980 | — |
| TCZ003 | ฿1,430 | P-04 |
| TCZ0033 | ฿1,430 | — |
| TFB00-2 | ฿620 | — |
| TPH00-4 | ฿1,180 | P-06 |
| TSB02-2 | ฿600 | — |
| TSQ06-4 | ฿1,210 | P-16 |
| TTT30-1 | ฿220 | — |
| TWR21-7 | ฿720 | P-PT |
| TYD0364 | ฿1,570 | P-2D |
| TYZ02-2 | ฿390 | — |

**สิ่งที่ต้องทำต่อ:** ยืนยันกับ FlowAccount ว่าราคาเดี่ยวเหล่านี้คือ SRP มาตรฐาน (ไม่มีบันไดราคาตาม
จำนวนสั่งจริง) หรือควรมี tier ที่ export มาไม่ครบ

## การเปลี่ยนแปลงในโค้ด (0.1.0b)

- `pipeline/export_pricelist_master.py`: เพิ่ม `_standard_qty_tiers()` (คำนวณจากข้อมูลจริงในแต่ละรอบ
  export + `SRP_QTY_TIERS` ที่ประกาศไว้แล้ว ไม่ hardcode ตัวเลขจาก snapshot วันนี้) และเพิ่มเหตุผลใหม่
  2 แบบใน `data_quality_issues`: `priced_without_qty_tier`, `non_standard_qty_tier`
- เพิ่ม `quality_summary.priced_without_qty_tier_count` (16), `non_standard_qty_tier_count` (5),
  `standard_qty_tiers`, `offers_with_confirmed_price_count` (122 — ตัวเลขที่ถูกต้อง แทน
  `priced_offer_count` เดิม 221 ที่นับรวม row-present ไม่ใช่ real-price)
- `build_public_projection`: เพิ่ม `price_missing`, `data_quality_issues` เข้า `prices` ที่ deploy
  จริง (ปลอดภัย ไม่ใช่ cost/PII — ไม่กระทบ `PUBLIC_FORBIDDEN_FIELDS`) เพื่อไม่ให้ผู้บริโภค public data
  ต้องพึ่ง `unit_price==0` เป็นสัญญาณเดียวอีกต่อไป
- `pipeline/build_offline_catalog.py`: `ladder_from_prices()` กรอง `price_missing` และ
  `non_standard_qty_tier` ออกจากบันไดราคาที่โชว์ลูกค้าโดยตรง

## Version diff

- `0.1.0b`: บันทึกรายการ tier/ราคาผิดปกติที่พบจาก cross-session review และการแก้ exporter/offline
  builder ให้แยกแยะกรณีเหล่านี้ได้โดยไม่แก้ราคาต้นทาง

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-31 | candidate | บันทึก 5 non_standard_qty_tier + 16 priced_without_qty_tier พร้อม fix ใน exporter/offline builder | c222ce6 | Claude |
