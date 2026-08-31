---
version: "0.1.0b"
created_at: "2026-08-23T19:00:00+07:00,ATHER"
status: "candidate"
superseded_by: null
attributes:
  domain: "smart-gift-catalog"
  doc_type: "taxonomy-input"
  source: "ข้อความจากผู้ใช้ 2026-08-23 (รายงานสถาปัตยกรรมแคมเปญ SmartGift 2026) — ไม่ใช่จาก Recording2"
  language: "Thai"
---

# SmartGift 2026 — 4 Product Groups × 4 Gift Tiers (input สำหรับ T02/T03/T05)

เอกสารนี้เก็บโครงสร้างที่ผู้ใช้ส่งมาแบบคงต้นฉบับ แล้ว map เข้ากับ work model ใน
[task breakdown](2026-08-23-recording2-smart-gift-catalog-task-breakdown.md) §3 พร้อมระบุว่าข้อใดมีหลักฐานใน SoT ข้อใดยังเป็น claim

## 1. Map เข้ากับ work model

| Layer ใน §3 task doc | สิ่งที่เอกสารนี้ให้ | สถานะ |
|---|---|---|
| **Category / Master** | 4 กลุ่ม: ① Smart Tech & Gadgets ② Care & Wellness ③ Smart Work & Office Stationery ④ Home & Travel Lifestyle | candidate — ตอบ T02 AC1 (ระดับบนสุด) รอ Q2 approve |
| **Family / Model** | Power Bank (C/T/A-series), Smart Notebook, Neck/Eye Massager, Hand Warmer, Vacuum Flask 304/316, Humidifier, Tea set, Executive Stationery | candidate — ต้อง map กับ `product_master` code จริง |
| **Variant / SKU** | ยังไม่ระบุ (สี/ความจุ) | ใช้กฎเดิม T02 AC3–5 |
| **Collection / Campaign** | 4 Tiers: Reach / Select / Signature / Bespoke — นิยามด้วย *ผู้รับ + MOQ + บรรจุภัณฑ์* ไม่ใช่ราคา | candidate — นี่คือ "แกน Collection" ทางเลือกใหม่ นอกเหนือจาก New Year/Christmas ใน D08 |
| **Bundle** | Package A (Essential Success) / B (Professional Synergy) / C (Prestige Excellence) | candidate — ตัวอย่าง Bundle ที่ reference SKU ข้ามกลุ่ม (T05 AC2) |

ข้อสังเกตเชิงโครงสร้าง: **กลุ่มสินค้า (Category) กับ Tier เป็นคนละแกน** — สินค้าหนึ่งรุ่นอยู่ใน 1 กลุ่มแต่ขึ้นได้หลาย Tier (เช่น A20 อยู่ทั้ง Select และใน Package B) ดังนั้นใน schema ควรเป็น `product.category` (1:1) + `tier_eligibility` (1:N) ไม่ใช่ folder ซ้อนกัน

## 2. ตรวจกับ SoT (2026-08-23)

| Claim ในเอกสาร | SoT | ผล |
|---|---|---|
| รหัส C1, C5, A11, A20, A30, T30 | มีใน `product_master` (source `price`) พร้อมชื่อความจุ | ✅ ตรง |
| T20 | มีรหัส แต่ `name` = NULL | ⚠️ ต้องเติมสเปก |
| "2,055 SKUs" | `catalog_sku` 2,295 แถว / 1,995 รหัสไม่ซ้ำ; `product_master` 5,704 แถว (3 source ซ้อนกัน) | ≈ ใกล้เคียง แต่ไม่ตรงตัวเลขใด — ระบุที่มาก่อนใช้ |
| "703 เซ็ต" | ชื่อที่มีคำว่า set/ชุด = 155 | ❌ หาที่มาไม่เจอ |
| ACV +42% | ไม่มีข้อมูลใน SoT | ❌ claim ไม่มีหลักฐาน — ห้ามใส่ใน Catalog/Sales Script จนกว่ามี source |
| MOQ 100+ / 50+ / 10+ / 1–10 | ไม่มี rule ที่อนุมัติ | ⚠️ เข้า D01/D02 — เป็นข้อเสนอ ไม่ใช่ rule |
| Lead Time Control | — | ⚠️ เข้า D02 |

## 3. ต้นฉบับ 4 กลุ่ม (คงไว้ตามที่ส่งมา)

**กลุ่มที่ 1: Smart Tech & Gadgets** — Power Bank C1/C5 (5,000mAh) → T20/T30 (20,000–30,000mAh, Solar) → A30 (30,000mAh, ไฟฉาย + LED); Smart Power Bank Notebook 8,000–12,000mAh (Wireless Charging, Light-up logo, Flash Drive 32GB)

**กลุ่มที่ 2: Care & Wellness** — Neck Massager (Low Pulse, 4 โหมด 15 ระดับ, 2.5W), Eye Massager (ความร้อน 3 ระดับ), Hand Warmer Power Bank 10,000mAh (ร้อนใน 10 วิ, จอแสดงอุณหภูมิ), เตารีดพกพา 170°C

**กลุ่มที่ 3: Smart Work & Office Stationery** — สมุดปกหนัง A5/A6, ปากกา Brass Wood / หมึกซึม

**กลุ่มที่ 4: Home & Travel Lifestyle** — Vacuum Flask SUS304 500ml (LED อุณหภูมิ), SUS316 370ml (One-button, สายหิ้ว), Humidifier, ชุดกาน้ำชาเซรามิก

## 4. ต้นฉบับ 4 Tiers

| Tier | ผู้รับ | SKU ตัวอย่าง | บรรจุภัณฑ์ | MOQ (เสนอ) |
|---|---|---|---|---|
| Reach (Mass Awareness) | มวลชน / พนักงานทั่วไป | C1 / C5 / A11 | Basic Standard | 100+ |
| Select (Functional Excellence) | คู่ค้า / หัวหน้างาน | Hand Warmer / A20 | Drawer Box | 50+ |
| Signature (VIP Engagement) | ลูกค้า VIP / พันธมิตรหลัก | Smart Notebook / T30 | Magnetic Clasp + EVA + อโรมา | 10+ |
| Bespoke (Executive Hybrid) | ผู้บริหารระดับสูง | Signature Set + Voucher 5 ดาว | Premium Hybrid Box | 1–10 |

หลักคิดที่ควรเก็บเป็น Business Fact (T08): "Psychological Fairness" — แยกระดับด้วย*บรรจุภัณฑ์ + ฟีเจอร์* ไม่ใช่ราคาอย่างเดียว เพื่อเลี่ยง Workplace Value Comparison

## 5. Bundle ตัวอย่าง

| Package | ส่วนประกอบ (กลุ่ม) | กลุ่มเป้าหมาย |
|---|---|---|
| A — Essential Success | C-Series (①) + Hand Warmer (②) | พนักงาน |
| B — Professional Synergy | Notebook (③) + A-Series (①) | ระดับกลาง |
| C — Prestige Excellence | Smart Notebook 12,000 (①) + T30 Solar (①) + Neck Massager (②) | VIP |

## 6. สิ่งที่ต้องตัดสินใจเพิ่ม

| ID | ประเด็น | กระทบ |
|---|---|---|
| D09 | ใช้ 4 Tiers เป็นแกน Collection หลัก แทน/ควบคู่ เทศกาล (D08)? | T03, หน้า 01 ของ mockup |
| D10 | อนุมัติ 4 กลุ่มเป็น Category ระดับบนสุดของ taxonomy | T02 |
| D11 | MOQ ต่อ Tier (100/50/10/1–10) เป็น rule หรือแค่แนวทาง | T05, T06, T11 |

## 7. ผลต่อ mockup ที่ทำไปแล้ว

- หน้า 01 (landing) ปัจจุบันใช้แกน "ปีใหม่ 2027" — ถ้า D09 เลือก Tier เป็นแกนหลัก ต้องทำ landing ใหม่เป็น 4 Tier cards
- หน้า 02 (family grid) ใช้หมวด "กระบอกน้ำและแก้ว" — map ได้เป็นกลุ่ม ④ ไม่ต้องแก้
- หน้า 04 (gift set builder) รองรับ Package A/B/C ได้เลย — ต้องเพิ่ม preset
- ยังไม่ได้เจนภาพใหม่ รอ D09
