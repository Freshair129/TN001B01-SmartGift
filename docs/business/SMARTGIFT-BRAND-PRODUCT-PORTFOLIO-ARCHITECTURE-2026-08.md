---
version: "0.1.1b"
created_at: "2026-08-12T22:15:54+07:00, ATHER, uncommitted"
last_update: "2026-08-13T01:21:14+07:00, ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "brand-product-portfolio-architecture-proposal"
  domain: "smartgift-marketing"
  scope: "brand-positioning-product-portfolio-and-commercial-offer"
  artifact_id: "SG-BPPA-001"
  language: "th"
---

# SmartGift Brand & Product Portfolio Architecture Proposal

## 0. สถานะเอกสารและมติที่ต้องการ

| รายการ | ค่า |
|---|---|
| สถานะ | `beta` — Boss อนุมัติ Strategic Architecture สำหรับ Controlled Pilot 90 วัน; ยังไม่ใช่ Public Rollout หรือสิทธิ์เผยแพร่ Claim ที่ยังไม่ผ่าน Gate |
| ผู้ตัดสินใจหลัก | Founder / Managing Director |
| ผู้ร่วมพิจารณา | Marketing, Sales, Product/Sourcing, Operations, Finance, Legal/Compliance |
| ความซับซ้อน | C-2 — Documentation-Driven Implementation |
| ความเสี่ยง | MEDIUM — กระทบแบรนด์ แคตตาล็อก วิธีขาย เว็บไซต์ การเสนอราคา และการปฏิบัติการข้ามทีม |
| เอกสารสรุปผู้บริหาร | `SMARTGIFT-PORTFOLIO-EXECUTIVE-DECISION-DECK-2026-08.md` |

เอกสารนี้เสนอให้ SmartGift เปลี่ยนจากการนำเสนอแบบ “ร้านรวมสินค้าพรีเมียม” ไปสู่ **ระบบออกแบบของขวัญองค์กรตามกลุ่มผู้รับ** ซึ่งรองรับหลายกลุ่มผู้รับ หลายระดับการดูแล และหลายรูปแบบของขวัญภายในแคมเปญเดียว โดยยังรักษาภาพแบรนด์เดียวกัน

**Approval record:** Boss อนุมัติข้อเสนอใน Codex เมื่อ 2026-08-13 สำหรับการจัดทำเอกสารและ Controlled Pilot ตาม Guardrails ในเอกสารนี้ การอนุมัตินี้ไม่แต่งตั้ง Pilot Owner, ไม่อนุมัติงบประมาณ, ไม่อนุมัติ Public Claim และไม่อนุญาตให้ข้าม Product/Partner/Legal/PDPA Readiness Gate

มติระดับกลยุทธ์ที่ Boss อนุมัติเมื่อ 2026-08-13 มี 5 ข้อ:

1. อนุมัติ Positioning และ Brand Promise ที่เสนอในเอกสารนี้สำหรับการทดสอบ
2. อนุมัติโครงสร้างพอร์ตแบบหลายมิติ แทนการแตกแบรนด์ย่อยตามประเภทสินค้า
3. อนุมัติความหมายของ `Reach`, `Select`, `Signature` และ `Bespoke` ให้เป็น Gift Tier
4. อนุมัติ Pilot 90 วันในหลักการกับ 3 Campaign Archetype โดยยังไม่เปลี่ยนระบบหลัก และต้องแต่งตั้ง Owner/อนุมัติงบก่อนเริ่ม
5. อนุมัติให้จัดทำ GTM Plan, Product Taxonomy, Sales Playbook และ BRD/PRD เฉพาะส่วนที่ผ่าน Pilot แล้ว

---

## 1. Executive Summary

### 1.1 ปัญหา

SmartGift มีสินค้า แหล่งจัดหา ประสบการณ์ และลูกค้าองค์กรอยู่แล้ว แต่การสื่อสารยังเริ่มจาก “มีสินค้าอะไร” มากกว่า “ผู้รับเป็นใครและแคมเปญต้องการสร้างผลลัพธ์อะไร” ทำให้เกิดผลดังนี้:

- ลูกค้าต้องเลือกจากแคตตาล็อกจำนวนมากโดยไม่มีกรอบตัดสินใจ
- Product Line แบบ Tech, Care หรือ Food เพียงมิติเดียวไม่รองรับผู้รับที่มีรสนิยมผสม
- คำว่า Signature ถูกตีความเป็น “ของผู้บริหาร” ทั้งที่ลูกค้า VIP, Key Media หรือ Strategic Partner ก็อาจสมควรได้รับระดับ Signature
- ในแคมเปญเดียว ลูกค้าของ SmartGift อาจมีผู้รับหลายกลุ่มและหลายเกรด แต่ยังไม่มีโครงสร้างมาตรฐานสำหรับแบ่งงบ ข้อเสนอ และประสบการณ์
- จุดแข็งด้าน MOQ ต่ำและ Gift Set ถูกใช้เป็นรายละเอียดสินค้า มากกว่าจะถูกแปลงเป็นวิธีแก้โจทย์ลูกค้า

### 1.2 ข้อเสนอ

ให้ SmartGift ใช้โมเดลพอร์ตผลิตภัณฑ์แบบหลายมิติ:

```text
Client
× Campaign / Occasion
× Recipient Relationship
× Client-defined Segment
× Gift Tier
× Interest Theme
× Format
× Budget / Quantity / Lead Time / Constraints
```

โมเดลนี้ทำให้ลูกค้าสามารถจัดแคมเปญเดียวสำหรับ Media, Member, VIP Member, Partner และผู้บริหารได้ โดยแต่ละกลุ่มได้รับของขวัญต่างระดับและต่างความสนใจ แต่ยังใช้ Campaign Idea, Brand Identity และระบบบริหารโครงการเดียวกัน

### 1.3 Positioning ที่เสนอ

> **SmartGift — เริ่มจากคนรับ ไม่ใช่เริ่มจากของ**

คำอธิบายเชิงพาณิชย์:

> **ของขวัญองค์กรที่คัดให้ตรงคน ตรงโอกาส และพอดีกับจำนวน**

Working English line:

> **Right gift. Right people. Right quantity.**

### 1.4 ข้อเสนอคุณค่า

SmartGift ไม่ได้ขายเพียงสินค้าแต่ละชิ้น แต่ช่วยลูกค้า:

1. แยกผู้รับตามความสัมพันธ์และความสำคัญ
2. จัดระดับของขวัญตามวัตถุประสงค์และงบประมาณ
3. เลือกหรือผสม Tech, Care, Taste, Lifestyle, Impact และ Experience
4. ทำหลาย Gift Tier ภายใต้ Campaign Identity เดียวกัน
5. ดูแลตั้งแต่ Brief, การคัดเลือก, ตัวอย่าง, ผลิต, QC จนถึงการจัดส่งตามขอบเขตที่ยืนยันแล้ว

---

## 2. บริบทและหลักฐานที่ใช้

### 2.1 หลักฐานภายใน

เอกสารการแข่งขันภายในระบุข้อมูลที่เกี่ยวข้องกับข้อเสนอนี้:

- `stg_product` มีหมวด Gift Set 703 รายการ
- ระดับราคาของ Gift Set ที่บันทึกไว้มีมัธยฐานประมาณ 930 บาท และมีรายการสูงถึง 2,610 บาท
- `price_staging` ระบุ MOQ ที่พบบ่อยในช่วง 10–50 ชิ้น
- มีสินค้าในแคตตาล็อก 2,055 SKU แต่ข้อมูลราคาปัจจุบันที่พร้อมใช้งานยังไม่ครบ
- ข้อมูลต้นทุนรายสินค้ายังไม่พร้อมสำหรับสรุป Margin ราย Theme หรือ Gift Tier
- สินค้า ECO ที่ระบุชัดใน SoT ยังมีเพียง 2 รายการ จึงยังไม่พอสำหรับใช้เป็นคำสัญญาหลักของแบรนด์

แหล่งอ้างอิงภายใน:

- `competitive-brief-thailand-2026-08.md`
- `battlecard-bixitia-2026-08.md`
- `data/sot.duckdb`

ตัวเลขข้างต้นเป็นข้อมูลเพื่อออกแบบและตัดสินใจภายใน ห้ามนำไปใช้เป็นข้อความโฆษณาภายนอกจนผ่านการตรวจ Source, วันที่ข้อมูล และผู้อนุมัติ Claim

### 2.2 สถานะการสื่อสารปัจจุบัน

เว็บไซต์ SmartGift ปัจจุบันมีฐานที่สอดคล้องกับข้อเสนอนี้อยู่แล้ว:

- ใช้บทบาท `Corporate Gift, Premium Product & Brand Campaign Partner`
- มีบริการสินค้าใส่โลโก้และ `Custom Corporate`
- ระบุการเริ่มต้นสั่งได้ตั้งแต่ 10 ชุด
- รับ Brief จากงบ จำนวน กลุ่มผู้รับ และเป้าหมาย

ข้อเสนอนี้ไม่ได้รื้อฐานดังกล่าว แต่ทำให้โครงสร้าง “กลุ่มผู้รับ → ระดับการดูแล → ความสนใจ → รูปแบบ” ชัดพอสำหรับการตลาด การขาย และการปฏิบัติการ

### 2.3 ข้อสรุปเชิงกลยุทธ์

MOQ ต่ำยังเป็นเหตุผลสนับสนุนการซื้อ แต่ไม่ควรเป็น Positioning เพียงอย่างเดียว เพราะมีผู้เล่นอื่นประกาศ MOQ ระดับ 10 ชุดแล้ว พื้นที่ที่ SmartGift ควรพัฒนาคือ **การออกแบบหลายกลุ่มผู้รับภายในแคมเปญเดียว** และการเปลี่ยนความซับซ้อนดังกล่าวให้เป็นข้อเสนอที่ลูกค้าเข้าใจและซื้อได้ง่าย

---

## 3. หลักการออกแบบพอร์ต

### P1 — One Master Brand

ใช้ `SmartGift` เป็น Master Brand เดียว ไม่แตก Tech, Care, Taste หรือ Signature เป็นบริษัท แบรนด์ เว็บไซต์ หรือฐานลูกค้าอิสระในระยะ Pilot

### P2 — Recipient-first

เริ่มจากผู้รับ ความสัมพันธ์ และวัตถุประสงค์ของแคมเปญ ก่อนเลือกสินค้า

### P3 — Multi-dimensional, not fixed boxes

Tech, Care, Taste และ Theme อื่นเป็นองค์ประกอบที่ผสมได้ ไม่ใช่กล่องที่บังคับให้ลูกค้าเลือกได้เพียงหนึ่งประเภท

### P4 — Client taxonomy stays client-owned

ชื่อระดับสมาชิก ลูกค้า หรือคู่ค้าของแต่ละองค์กรเป็นของลูกค้า SmartGift ไม่เปลี่ยนชื่อหรือประกาศความหมายแทนลูกค้า แต่สร้าง Mapping เฉพาะแคมเปญไปยัง Gift Tier ของ SmartGift

### P5 — Gift Tier is treatment, not identity

`Signature` หมายถึงระดับการดูแล ไม่ได้แปลว่าผู้รับต้องเป็นผู้บริหาร ผู้รับอาจเป็น Key Media, VIP Member, Strategic Partner หรือบุคคลสำคัญประเภทอื่น

### P6 — Evidence before claim

Theme ที่มีข้อกำหนดเฉพาะ เช่น Impact, Sustainable, Health, Food Safety หรือ Voucher ต้องมีหลักฐาน Supplier, Certification, Terms และข้อจำกัดก่อนขายหรือสื่อสาร Claim

### P7 — Simple public surface, rich internal model

ลูกค้าไม่ควรต้องเรียนรู้ Taxonomy ทั้งหมด หน้าเว็บและฝ่ายขายต้องถามคำถามทีละขั้น ขณะที่ระบบภายในเก็บรายละเอียดครบเพื่อทำซ้ำและตรวจสอบได้

---

## 4. Canonical Portfolio Model

### 4.1 ลำดับการออกแบบข้อเสนอ

| ลำดับ | มิติ | คำถามที่ต้องตอบ |
|---|---|---|
| 1 | Client | องค์กรใดเป็นผู้ซื้อและเจ้าของแคมเปญ |
| 2 | Campaign / Occasion | ให้ในโอกาสอะไรและต้องการผลลัพธ์อะไร |
| 3 | Recipient Relationship | ผู้รับเป็นใครสำหรับองค์กรผู้ซื้อ |
| 4 | Client-defined Segment | ลูกค้าแบ่งผู้รับกลุ่มนี้อย่างไร |
| 5 | Gift Tier | SmartGift จะดูแลผู้รับระดับใด |
| 6 | Interest Theme | ผู้รับสนใจหรือเหมาะกับ Theme ใด |
| 7 | Format | ส่งมอบเป็น Physical, Voucher/Experience หรือ Hybrid |
| 8 | Constraints | งบ จำนวน วันใช้ การรับรอง การจัดส่ง และข้อจำกัดอื่นคืออะไร |

### 4.2 ความสัมพันธ์ของแต่ละมิติ

```text
Campaign
├─ Audience Group A
│  ├─ Client Segment A1 → Gift Tier → Theme(s) → Format
│  └─ Client Segment A2 → Gift Tier → Theme(s) → Format
├─ Audience Group B
│  └─ Client Segment B1 → Gift Tier → Theme(s) → Format
└─ Shared Campaign Layer
   ├─ Core message
   ├─ Visual identity
   ├─ Packaging family
   ├─ Approval rules
   └─ Delivery milestone
```

Campaign เดียวสามารถมีหลาย Audience Group และหลาย Gift Tier แต่ต้องมีส่วนกลางร่วมกัน เช่น Campaign Message, Brand Rules, Timeline และผู้อนุมัติ

---

## 5. Recipient Relationship Architecture

Recipient Relationship ตอบว่า “ผู้รับเป็นใครสำหรับลูกค้าของ SmartGift” ไม่ใช่บอกว่าสินค้าคืออะไร

| Code | Recipient Line | ขอบเขต | ตัวอย่าง |
|---|---|---|---|
| `LEADERSHIP` | Leadership | ผู้นำองค์กรและผู้มีอำนาจกำกับ | ผู้บริหาร กรรมการ ผู้ถือหุ้น |
| `TEAM` | Team | บุคลากรภายในองค์กร | พนักงาน ผู้จัดการ พนักงานอายุงานสูง |
| `CUSTOMER_MEMBER` | Customer & Member | ผู้ซื้อ ผู้ใช้บริการ หรือสมาชิกของลูกค้า SmartGift | Prospect, Customer, Member, Loyal Member, VIP Member |
| `PARTNER_DEALER` | Partner & Dealer | ผู้มีความสัมพันธ์เชิงธุรกิจกับองค์กร | คู่ค้า ตัวแทนจำหน่าย Sponsor Strategic Partner |
| `MEDIA_CREATOR` | Media & Creator | ผู้เผยแพร่หรือขยายการรับรู้ | สื่อมวลชน Industry Media, KOL, Influencer, Creator |
| `GUEST_PUBLIC` | Guest & Public | ผู้เข้าร่วมกิจกรรมหรือบุคคลทั่วไป | Event Guest, Booth Visitor, Prospect, Public Audience |
| `COMMUNITY` | Community | ชุมชนหรือกลุ่มผู้รับประโยชน์ | ผู้เข้าร่วม CSR หน่วยงานท้องถิ่น กลุ่มอาชีพ |

### 5.1 กฎการใช้

1. บุคคลหนึ่งอาจอยู่ได้หลาย Relationship ตามบริบท แต่หนึ่ง Treatment ในหนึ่ง Campaign ต้องระบุ Primary Relationship เดียว
2. Media และ Creator เป็นความสัมพันธ์ ไม่ใช่ Gift Tier; Key Media อาจได้รับ Select หรือ Signature ตามวัตถุประสงค์
3. Customer & Member ต้องเก็บชื่อ Tier ของลูกค้าตามที่ลูกค้านิยาม ห้าม SmartGift เดาสถานะจากมูลค่าของขวัญ
4. Relationship ที่เกี่ยวข้องกับผู้เยาว์ สุขภาพ การเงิน หรือข้อมูลอ่อนไหวต้องผ่านการทบทวน Legal/Compliance แยกต่างหาก

---

## 6. Client-defined Segment Mapping

### 6.1 วัตถุประสงค์

ลูกค้าแต่ละองค์กรมีภาษาและเกณฑ์แบ่งกลุ่มต่างกัน เช่น Tier A/B/C, Member/VIP, Dealer Gold/Silver หรือ Key/General Media จึงไม่ควรสร้างชื่อกลางที่บังคับทุกองค์กร

SmartGift ต้องเก็บสองค่าแยกกัน:

| ค่า | เจ้าของความหมาย | ตัวอย่าง |
|---|---|---|
| `client_segment_label` | ลูกค้า SmartGift | `VIP Member`, `Tier A`, `Key Media` |
| `smartgift_gift_tier` | SmartGift + ลูกค้าอนุมัติร่วมกัน | `Reach`, `Select`, `Signature`, `Bespoke` |

### 6.2 Mapping Table ต่อ Campaign

| Client Segment | จำนวน | Objective | Gift Tier | งบต่อราย | ผู้อนุมัติ | หมายเหตุ |
|---|---:|---|---|---:|---|---|
| ระบุโดยลูกค้า | TBD | ระบุโดยลูกค้า | Reach/Select/Signature/Bespoke | TBD | TBD | ห้ามเดา |

Mapping นี้เป็น Campaign Decision ไม่ใช่กฎถาวรของลูกค้า องค์กรเดียวกันอาจ Mapping VIP Member เป็น Signature ในแคมเปญขอบคุณลูกค้า แต่เป็น Select ในกิจกรรม Mass Event ได้

---

## 7. Gift Tier Architecture

Gift Tier ระบุระดับการออกแบบ การคัดเลือก การปรับแต่ง และการดูแล ไม่ใช่เพียงช่วงราคา

| Tier | บทบาท | เหมาะกับ | ระดับการปรับแต่ง | สิ่งที่ยังต้องกำหนดใน Pilot |
|---|---|---|---|---|
| **Reach** | เข้าถึงคนจำนวนมากและสร้างการจดจำ | Guest, Public, General Member, Mass Event | ต่ำถึงมาตรฐาน | MOQ, SLA, Packaging floor, Cost-to-serve |
| **Select** | คัดให้เหมาะกับกลุ่มเฉพาะ | Employee group, Member segment, General Media, Partner | เลือก Theme/Set/ข้อความได้ | จำนวนตัวเลือก, Sampling rule, SLA |
| **Signature** | ดูแลผู้รับสำคัญด้วยชุดที่ตั้งใจและภาพลักษณ์สูง | VIP Member, Key Media, Executive, Strategic Partner | สูง มี Packaging/Message/Personalization ตามขอบเขต | Quality bar, minimum value, approval, proofing |
| **Bespoke** | ออกแบบเฉพาะแคมเปญ กลุ่มเล็ก หรือรายบุคคล | Invitation-only, Board, Top-tier relationship | สูงสุดและต้องประเมินโครงการ | Feasibility, design fee, IP, timeline, minimum project value |

### 7.1 Guardrails

- Tier สูงกว่าไม่เท่ากับต้องใช้สินค้าราคาแพงกว่าเสมอ คุณค่ามาจากความเหมาะสม การออกแบบ การปรับแต่ง และประสบการณ์รวม
- ห้ามใช้ Gift Tier เป็นเครื่องมือสร้างหรืออนุมานระดับสมาชิกของลูกค้า
- ห้ามประกาศช่วงราคา Margin หรือ SLA ถ้ายังไม่มีต้นทุนและข้อมูลปฏิบัติการที่อนุมัติแล้ว
- Bespoke ต้องผ่าน Feasibility Review ก่อนออกใบเสนอราคา

---

## 8. Interest Theme Architecture

Theme ตอบว่า “ผู้รับสนใจหรือเหมาะกับอะไร” และสามารถเลือกหลาย Theme ใน Treatment เดียว

| Theme | ความหมาย | ตัวอย่างองค์ประกอบ | Guardrail |
|---|---|---|---|
| **Tech** | เทคโนโลยีและอุปกรณ์ใช้จริง | Flash drive, Power bank, Charger, Speaker, Smart accessory | ตรวจสเปก การรับรอง แบตเตอรี่ และ Warranty |
| **Care & Wellness** | การดูแล สุขภาวะ และการพักผ่อน | เครื่องนวด แก้วน้ำ อุปกรณ์พักผ่อน Wellness item | ห้ามใช้ Medical Claim โดยไม่มีหลักฐาน |
| **Taste** | อาหาร เครื่องดื่ม และรสนิยมการบริโภค | ชา กาแฟ ขนม Hamper Dining selection | ตรวจ อย. สารก่อภูมิแพ้ อายุสินค้า การเก็บและขนส่ง |
| **Lifestyle & Travel** | การใช้ชีวิต การเดินทาง และของใช้ประจำวัน | กระเป๋า ร่ม Drinkware Travel accessory | ตรวจความเหมาะสมตามผู้รับและบริบท |
| **Impact** | สิ่งแวดล้อม ชุมชน และผลกระทบเชิงบวก | วัสดุรีไซเคิล สินค้าชุมชน Social enterprise | ต้องมี Source/Certification/Impact evidence; ห้าม Green Claim ลอย ๆ |
| **Work & Welcome** | การทำงานและการต้อนรับ | Notebook, Desk set, Welcome kit, Office accessory | อาจใช้ร่วมกับ Tech/Lifestyle ได้ |
| **Culture & Local** | อัตลักษณ์ท้องถิ่น ศิลปะ และวัฒนธรรม | งานคราฟต์ งานชุมชน ของที่ระลึกท้องถิ่น | ตรวจสิทธิ์ ลิขสิทธิ์ ที่มา และการให้เครดิต |

### 8.1 Theme Combination

ตัวอย่าง Combination ที่อนุญาต:

- `Tech + Care`
- `Care + Taste`
- `Taste + Experience`
- `Impact + Culture & Local`
- `Tech + Work & Welcome`

จำนวน Theme ต่อ Treatment ควรจำกัดไว้ที่ 1–3 Theme เพื่อให้แนวคิดชัด การใช้มากกว่านั้นต้องมีเหตุผลใน Campaign Brief

---

## 9. Format Architecture

| Format | ความหมาย | ตัวอย่าง | ข้อกำหนดสำคัญ |
|---|---|---|---|
| **Physical Gift** | สินค้าที่ผลิตหรือจัดแพ็กและส่งมอบ | Gift Set, Gadget, Hamper | สต็อก MOQ, Sample, QC, Packaging, Delivery |
| **Voucher / Experience** | สิทธิ์ที่ผู้รับนำไปใช้ภายหลัง | Dining, Spa, Hotel, Workshop, Digital Reward | Partner contract, expiry, redemption, tax, refund, liability, reconciliation |
| **Hybrid** | Physical Gift รวมกับ Voucher/Experience | Wellness set + Spa voucher | ต้องบริหารทั้ง Physical fulfilment และ Digital entitlement |

### 9.1 Taste กับ Experience ต้องแยกกัน

- `Taste` เป็น Theme: ผู้รับสนใจอาหารและเครื่องดื่ม
- `Experience` เป็น Format: วิธีที่ผู้รับได้รับคุณค่าในภายหลัง
- Dining voucher จึงเป็น `Taste + Experience`
- Spa voucher เป็น `Care & Wellness + Experience`
- Health-food hamper เป็น `Care & Wellness + Taste + Physical Gift`

### 9.2 Voucher Boundary

Voucher/Experience ยังเป็นข้อเสนอเชิงแนวคิดจนกว่าจะมี:

1. รายชื่อ Partner และสิทธิ์จำหน่ายที่ยืนยันแล้ว
2. เงื่อนไขราคา ค่าธรรมเนียม ภาษี และการคืนเงิน
3. วันหมดอายุและกฎ Redemption
4. วิธี Reconciliation และหลักฐานการใช้สิทธิ์
5. เจ้าของการบริการเมื่อผู้รับมีปัญหา
6. PDPA และ Data-sharing boundary

---

## 10. Campaign / Occasion Architecture

Campaign/Occasion ตอบว่า “ให้ทำไม” และใช้กำหนดเป้าหมาย ข้อความ และช่วงเวลา

| Archetype | เป้าหมาย | Recipient ที่พบบ่อย |
|---|---|---|
| **Launch & Event** | สร้างการรับรู้ เข้าร่วมงาน หรือขยายข่าว | Media, Creator, Guest, Member, Partner |
| **Customer Appreciation** | รักษาความสัมพันธ์และขอบคุณ | Customer, Loyal Member, VIP, Partner |
| **Membership & Loyalty** | กระตุ้นการมีส่วนร่วม รักษาสมาชิก หรือมอบสิทธิ์ | Member หลายระดับ |
| **Employee Welcome & Recognition** | ต้อนรับ ยกย่อง หรือดูแลพนักงาน | Team, Manager, Leadership |
| **Seasonal & Milestone** | ปีใหม่ ครบรอบ เปิดสาขา หรือเหตุการณ์สำคัญ | ลูกค้า พนักงาน คู่ค้า ผู้บริหาร |
| **CSR & Community** | ส่งต่อประโยชน์หรือสร้างผลกระทบ | Community, Public, Partner |

หนึ่ง Campaign อาจมี Occasion หลักหนึ่งรายการและ Secondary Occasion ได้หนึ่งรายการ หากมากกว่านั้นควรแยก Brief เพื่อไม่ให้วัตถุประสงค์ปะปน

---

## 11. Naming Architecture

### 11.1 กฎการตั้งชื่อภายนอก

ใช้ชื่อที่ลูกค้าเข้าใจง่าย ไม่แสดง Taxonomy ทั้งหมดในชื่อสินค้า

รูปแบบแนะนำ:

```text
SmartGift [Gift Tier] — [Theme / Campaign Edition]
```

ตัวอย่าง:

- `SmartGift Signature — Care Edition`
- `SmartGift Signature — Tech × Care`
- `SmartGift Select — Member Welcome Kit`
- `SmartGift Reach — Launch Event Pack`
- `SmartGift Bespoke — Executive Dining Experience`

### 11.2 ชื่อภายใน

ข้อเสนอและข้อมูลภายในต้องเก็บมิติแยก ห้ามใช้ชื่อสินค้าเป็นแหล่งข้อมูลเดียว:

```text
campaign_id
recipient_relationship
client_segment_label
smartgift_gift_tier
themes[]
format
budget_per_recipient
quantity
required_by
constraints[]
approval_status
```

โครงสร้างนี้เป็น Draft Taxonomy เท่านั้น ยังไม่ใช่ BRD หรือ Database Schema ที่อนุมัติแล้ว

---

## 12. ตัวอย่างแคมเปญ — ห้างและ Loyalty Program

### 12.1 บริบทสมมติ

ตัวอย่างนี้ใช้ชื่อ “The One” ตามโจทย์สนทนาเพื่ออธิบายโมเดลเท่านั้น ไม่ได้อ้างว่าเป็น Brief จริง ไม่มีการยืนยัน Tier, งบ, สิทธิ์ใช้ชื่อแบรนด์ หรือความสัมพันธ์ทางธุรกิจ

สมมติว่าองค์กรจัดงานเปิดตัวและมีผู้รับหลายกลุ่ม:

- สื่อมวลชน
- Creator/KOL
- สมาชิกทั่วไป
- สมาชิกที่มี Engagement สูง
- สมาชิก VIP หรือ Invitation-only
- คู่ค้าและผู้บริหาร

### 12.2 Campaign Matrix ตัวอย่าง

| Recipient Relationship | Client Segment (สมมติ) | Objective | Gift Tier | Theme | Format | Treatment ตัวอย่าง |
|---|---|---|---|---|---|---|
| Media & Creator | General Media | ให้ข้อมูลครบและอำนวยความสะดวกทำข่าว | Select | Tech + Work | Physical | Press kit, USB, campaign material |
| Media & Creator | Key Media | สร้างประสบการณ์ที่เหมาะกับความสำคัญ | Signature | Tech + Taste | Hybrid | Premium press box + dining experience |
| Customer & Member | General Member | กระตุ้นการเข้าร่วมและจดจำแคมเปญ | Reach | Lifestyle | Physical หรือ Voucher | Branded item หรือ campaign benefit |
| Customer & Member | Loyal Member | ขอบคุณและรักษาความสัมพันธ์ | Select | Care + Taste | Physical หรือ Hybrid | Wellness/taste set ตามงบ |
| Customer & Member | VIP Member | มอบประสบการณ์เฉพาะกลุ่ม | Signature | Care + Taste | Hybrid | Curated gift + named message + experience |
| Customer & Member | Invitation-only | สร้างความประทับใจเฉพาะราย | Bespoke | เลือกตาม Profile ที่ได้รับอนุญาต | Hybrid | Personalized treatment หลัง Feasibility Review |
| Partner & Dealer | Strategic Partner | ยืนยันความสัมพันธ์ระยะยาว | Signature | Lifestyle + Taste | Physical | Partner appreciation set |
| Leadership | Executive Guest | ต้อนรับและให้เกียรติ | Signature/Bespoke | Lifestyle, Care หรือ Taste | Hybrid | Curated executive treatment |

### 12.3 สิ่งที่ต้องยืนยันก่อนเสนอจริง

1. ชื่อและเกณฑ์ Segment ที่ลูกค้าใช้จริง
2. จำนวนผู้รับและฐานกฎหมาย/ความยินยอมสำหรับข้อมูลที่ต้องใช้
3. Objective และ Gift Tier ต่อ Segment
4. งบต่อรายและงบรวม
5. วันที่ใช้ สถานที่ และจำนวนจุดส่ง
6. Brand Guideline, Claim และ Approval Owner
7. Partner/Voucher availability และเงื่อนไข
8. ข้อจำกัดของขวัญสำหรับสื่อ ผู้บริหาร ภาครัฐ หรือองค์กรที่มี Gift Policy

---

## 13. Customer Brief Flow

ฝ่ายขายหรือหน้าเว็บควรเก็บ Brief ตามลำดับนี้:

### Step 1 — Campaign

- งานหรือโอกาสคืออะไร
- เป้าหมายทางธุรกิจคืออะไร
- วันใช้และ Timeline คือเมื่อใด

### Step 2 — Recipient Map

- มีผู้รับกี่ Relationship
- แต่ละ Relationship มี Segment อะไรบ้าง
- ลูกค้าเรียกแต่ละ Segment ว่าอะไร
- จำนวนต่อ Segment เท่าไร

### Step 3 — Treatment

- ต้องการ Reach, Select, Signature หรือ Bespoke ต่อ Segment
- งบต่อรายและงบรวมเท่าไร
- ต้องการความแตกต่างระหว่าง Tier อย่างไร

### Step 4 — Interest

- ผู้รับสนใจ Tech, Care, Taste, Lifestyle, Impact, Work หรือ Culture ใด
- มี Theme ที่ห้ามใช้หรือข้อจำกัดด้านศาสนา สุขภาพ อายุ หรือวัฒนธรรมหรือไม่

### Step 5 — Format

- Physical, Voucher/Experience หรือ Hybrid
- ต้อง Personalize รายบุคคลหรือไม่
- จัดส่งรวม แยกสาขา หรือแยกรายบุคคล

### Step 6 — Governance

- ใครอนุมัติสินค้า ราคา แบบ โลโก้ Claim และรายชื่อผู้รับ
- มี Policy เรื่องของขวัญ PDPA ESG หรือ Procurement ใดบ้าง

ผลลัพธ์ของ Brief ไม่ใช่รายการสินค้า แต่เป็น `Campaign Recipient Matrix` ที่ลูกค้าและ SmartGift อนุมัติร่วมกันก่อนคัดสินค้า

---

## 14. Commercial Offer Architecture

ข้อเสนอเชิงบริการแบ่งเป็นสองโหมดตามฐานเว็บไซต์เดิม แต่เพิ่ม Recipient Architecture เข้าไป:

### 14.1 Ready-to-Brand

เหมาะกับ Campaign ที่มี Segment น้อย ใช้ Product/Set ที่ตรวจแล้ว และไม่ต้องออกแบบโครงสร้างซับซ้อน

- เลือกจากชุดที่ผ่าน Readiness Gate
- ปรับ Logo, Card และตัวเลือกที่กำหนด
- ใช้ Reach หรือ Select เป็นหลัก
- Signature ใช้ได้เฉพาะชุดที่ผ่าน Quality Bar

### 14.2 Custom Campaign

เหมาะกับ Campaign ที่มีหลาย Recipient Relationship หลาย Segment หรือหลาย Gift Tier

- Recipient Mapping Workshop
- Campaign Matrix
- Concept/Theme Route
- Multi-tier Proposal
- Sample/Proofing
- Production/QC/Delivery Plan
- Voucher/Experience เฉพาะ Partner ที่ผ่าน Gate

### 14.3 ข้อเสนอใหม่ที่ควรทดลอง

Working name:

> **SmartGift Multi-Audience Campaign**

คำอธิบาย:

> หนึ่งแคมเปญ หลายกลุ่มผู้รับ หลายระดับของขวัญ แต่สื่อสารแบรนด์เดียวกัน

ชื่อดังกล่าวเป็น Working Name รอทดสอบความเข้าใจกับลูกค้าและทีมขาย

---

## 15. Operating Model และผู้รับผิดชอบ

| งาน | Accountable | Responsible | Consulted |
|---|---|---|---|
| Positioning และ Portfolio Policy | Founder/MD | Marketing Owner | Sales, Product, Finance |
| Client Segment definition | Client Owner | Account Manager | Client Marketing/CRM |
| Gift Tier mapping | Marketing Owner + Client Approver | Account Manager | Finance, Product |
| Product readiness | Product/Sourcing Owner | Sourcing | QC, Finance, Legal |
| Theme/Claim approval | Marketing/Brand Owner | Campaign Lead | Legal/Compliance |
| Voucher/Experience readiness | Commercial Owner | Partnership Owner | Finance, Legal, Operations |
| Campaign Matrix approval | Client Approver | Account Manager | Marketing, Operations |
| Production/QC/Delivery | Operations Owner | Operations | Sourcing, Account Manager |
| Measurement | Marketing/Analytics Owner | Campaign Analyst | Sales, Client Owner |

Owner ที่ยังไม่ได้แต่งตั้งต้องระบุเป็น `TBD` ในเอกสารดำเนินงาน ห้ามสมมติชื่อหรืออำนาจอนุมัติ

---

## 16. Pilot 90 วัน

### 16.1 วัตถุประสงค์

พิสูจน์ว่า Recipient-first, Multi-tier Portfolio ทำให้ลูกค้าเข้าใจข้อเสนอเร็วขึ้น ฝ่ายขายสร้างข้อเสนอที่สม่ำเสมอขึ้น และ Operations ส่งมอบได้โดยไม่เพิ่มความซับซ้อนเกินควบคุม

### 16.2 Pilot Scope

เลือก 3 Campaign Archetype:

1. **Customer/Member Appreciation** — อย่างน้อย 2 Segment และ 2 Gift Tier
2. **Launch/Event with Media** — Media + Guest/Member อย่างน้อย 2 Relationship
3. **Employee Welcome/Recognition** — Team อย่างน้อย 2 Segment

แต่ละ Pilot ต้องมี:

- Campaign Brief
- Recipient Matrix
- Gift Tier Mapping
- Theme/Format selection
- ข้อเสนออย่างน้อย 2 Route แต่ไม่เกิน 3 Route
- Feasibility, Cost และ Lead-time Review
- Approval record
- Post-campaign review

### 16.3 Phase

| ช่วง | งาน | Exit Criteria |
|---|---|---|
| วัน 1–15 | Internal taxonomy workshop + คัดสินค้า/Partner ที่พร้อม | นิยามคำและ Readiness list ผ่านทีมที่เกี่ยวข้อง |
| วัน 16–30 | สร้าง Brief template, Campaign Matrix และ Proposal template | ฝ่ายขายทดลองใช้ภายใน 3 Scenario ได้ |
| วัน 31–60 | Controlled client discovery 3–5 ราย | มี Feedback ที่บันทึกได้และไม่มี Claim/Offer ที่ยังไม่พร้อมหลุดออกไป |
| วัน 61–90 | ทำ Pilot ที่ได้รับอนุมัติและสรุปผล | มีหลักฐาน Conversion/effort/quality และมติ Go/Revise/Stop |

### 16.4 Pilot Constraints

- ยังไม่สร้างเว็บไซต์ Configurator เต็มรูปแบบ
- ยังไม่เปิด Impact Line ภายนอกหากสินค้าและหลักฐานไม่ถึงเกณฑ์
- ยังไม่ขาย Voucher/Experience หาก Partner contract และ Redemption flow ไม่พร้อม
- ยังไม่กำหนด Price Tier หรือ Margin Target โดยไม่มีข้อมูลต้นทุน
- ห้ามใช้ข้อมูลสมาชิกหรือผู้รับที่เกินขอบเขตที่ลูกค้าอนุญาต

---

## 17. Success Metrics

Baseline ปัจจุบันยังไม่มีสำหรับโมเดลนี้ จึงต้องเก็บ Baseline ในช่วง Pilot และห้ามกำหนด Target เชิงตัวเลขโดยไม่มี Owner และแหล่งข้อมูล

| มิติ | Metric | ความหมาย |
|---|---|---|
| Customer understanding | เวลาจาก Discovery ถึงยืนยัน Recipient Matrix | ลูกค้าเข้าใจและตัดสินใจโครงสร้างเร็วขึ้นหรือไม่ |
| Sales efficiency | เวลาสร้างข้อเสนอและจำนวน Revision | Portfolio ช่วยลดงานซ้ำหรือไม่ |
| Commercial | Quote-to-order conversion ต่อ Archetype/Tier | ข้อเสนอใดสร้างคำสั่งซื้อได้จริง |
| Offer quality | อัตราผ่าน Feasibility ครั้งแรก | ฝ่ายขายเสนอของที่ทำได้จริงมากขึ้นหรือไม่ |
| Operations | On-time delivery, defect/rework, tier complexity | Multi-tier ส่งมอบได้โดยไม่เกิดความเสียหายหรือไม่ |
| Customer value | Client satisfaction และเหตุผลเลือก/ไม่เลือก | Positioning ตรงปัญหาจริงหรือไม่ |
| Recipient outcome | Redemption/usage/feedback เมื่อวัดได้และได้รับอนุญาต | ของขวัญถูกใช้และสร้างประสบการณ์หรือไม่ |
| Governance | Claim, certification, voucher หรือ PDPA exception | มีความเสี่ยงหลุดออกจาก Guardrail หรือไม่ |

ทุก Metric ต้องระบุ Source, Owner, Measurement window และ Data-quality status ก่อนใช้ตัดสินใจ

---

## 18. ความเสี่ยงและ Guardrails

| ความเสี่ยง | ผลกระทบ | Guardrail |
|---|---|---|
| Taxonomy ซับซ้อนเกินไป | ลูกค้าและฝ่ายขายสับสน | เปิดเผยเฉพาะคำถามทีละขั้น; เก็บโมเดลเต็มไว้ภายใน |
| SKU/ราคายังไม่พร้อม | เสนอแล้วทำไม่ได้หรือตอบช้า | Product Readiness Gate ก่อนเข้าชุดแนะนำ |
| ไม่มีต้นทุน | ตั้ง Tier แล้วไม่รู้กำไร | ห้ามประกาศ Margin/Price policy จน Cost data อนุมัติ |
| Voucher/Experience ไม่พร้อม | Redemption หรือข้อพิพาท | Partner/Terms/Reconciliation Gate |
| Greenwashing | เสียความน่าเชื่อถือและเสี่ยง Compliance | Impact Claim ต้องมีหลักฐานระดับ SKU/Partner |
| Medical/health claim | เสี่ยงกฎหมายและความเชื่อมั่น | Care ห้ามใช้ Medical Claim ที่ไม่ได้อนุมัติ |
| ใช้ Customer Tier ผิด | กระทบความสัมพันธ์ลูกค้า | Client เป็นเจ้าของ Segment; SmartGift ทำ Mapping ต่อ Campaign |
| ของขวัญไม่เหมาะกับ Policy | ผู้รับรับไม่ได้หรือเกิด Conflict | เก็บ Gift/Procurement/Anti-bribery constraint ใน Brief |
| Personalization ใช้ข้อมูลเกินจำเป็น | PDPA และความไว้ใจ | Data minimization, purpose, retention และ approval |
| แตกไลน์จนแบรนด์กระจัดกระจาย | งบการตลาดและความจำแบรนด์ลดลง | Master Brand เดียวใน Pilot |

---

## 19. In Scope / Out of Scope

### 19.1 In Scope

- Positioning และ Brand Promise สำหรับทดสอบ
- Recipient Relationship taxonomy
- Client-defined Segment mapping
- Gift Tier, Theme และ Format
- Naming rule
- Campaign Matrix และ Brief flow
- Pilot design และ measurement framework

### 19.2 Out of Scope

- Rebrand โลโก้ สี หรือ Visual Identity
- เปลี่ยนเว็บไซต์หรือระบบ CRM
- สร้าง Database schema/API/Configurator
- เซ็น Partner/Voucher contract
- ซื้อสินค้า เปิดสต็อก หรือรับประกัน MOQ/SLA ใหม่
- อนุมัติ Claim ด้าน ESG, Health หรือ Food Safety
- กำหนดราคาและ Margin policy
- ใช้ข้อมูลสมาชิกจริงหรือส่ง Campaign จริง

งาน Out of Scope ต้องมีเอกสารและการอนุมัติแยกหลัง Portfolio Proposal ผ่าน

---

## 20. เอกสารต่อเนื่องหลังอนุมัติ

| ลำดับ | เอกสาร | วัตถุประสงค์ |
|---|---|---|
| 1 | Go-to-Market Plan | เลือก Segment, Message, Channel, Pilot และ KPI |
| 2 | Product Taxonomy & Offer Rules | กำหนด Tag, Readiness, Naming และกฎผสมข้อเสนอ |
| 3 | Campaign Brief & Recipient Matrix Template | ใช้ Discovery และอนุมัติขอบเขตต่อแคมเปญ |
| 4 | Sales Playbook | คำถามขาย Proposal route และ Objection handling |
| 5 | Operations & Partner Readiness Standard | Product/Voucher/QC/Fulfilment gates |
| 6 | BRD/PRD | ใช้เมื่อจะสร้าง Configurator, CRM flow, Quote automation หรือ Voucher system |

BRD/PRD ต้องอ้างอิง Portfolio Architecture รุ่นที่อนุมัติ ห้ามให้ระบบเป็นผู้กำหนดกลยุทธ์ย้อนกลับ

---

## 21. Acceptance, Success และ Exit Criteria

### 21.1 Acceptance Criteria ของเอกสาร

- ผู้บริหารตัดสินใจ Positioning และ Portfolio Model ครบทุกข้อ
- Marketing, Sales และ Operations ใช้ความหมายของ Recipient, Segment, Gift Tier, Theme และ Format ตรงกัน
- Signature ถูกยืนยันว่าเป็น Gift Tier ไม่ใช่ Recipient Line
- Client Segment และ SmartGift Gift Tier ถูกเก็บเป็นคนละมิติ
- Voucher/Experience และ Impact มี Guardrail ชัดเจน
- Pilot Scope, Owner และข้อห้ามได้รับการอนุมัติ

### 21.2 Success Criteria ของ Pilot

- ทีมสร้าง Campaign Matrix สำหรับทั้ง 3 Archetype ได้โดยไม่เปลี่ยนความหมายของ Taxonomy
- ข้อเสนอที่ส่งให้ลูกค้าผ่าน Feasibility และ Claim Review ตามกติกา
- มี Baseline และผลวัดที่ตรวจย้อนกลับได้
- ไม่มี Known Critical Regression ด้านราคา Claim, Voucher, Delivery หรือ PDPA

### 21.3 Exit Criteria ก่อนขยายผล

- ผู้บริหารลงมติ `GO`, `REVISE` หรือ `STOP` จากหลักฐาน Pilot
- หาก `GO` ต้องมี GTM, Taxonomy, Sales Playbook และ Operating Standard ที่อนุมัติ
- หากต้องสร้างระบบ ต้องมี BRD/PRD และ Change Risk Assessment แยก
- เว็บไซต์ แคตตาล็อก และระบบขายต้องไม่เปลี่ยนก่อน Decision Gate ดังกล่าว

---

## 22. Decision Record

| Decision ID | เรื่อง | ทางเลือก | Owner | สถานะ |
|---|---|---|---|---|
| `D-01` | Positioning | Approve / Revise / Reject | Founder/MD | Approved for Pilot — Boss, 2026-08-13 |
| `D-02` | One Master Brand | Approve / Revise / Reject | Founder/MD | Approved for Pilot — Boss, 2026-08-13 |
| `D-03` | Multi-dimensional Portfolio Model | Approve / Revise / Reject | Founder/MD | Approved for Pilot — Boss, 2026-08-13 |
| `D-04` | Gift Tier definitions | Approve / Revise / Reject | Marketing + Sales + Finance | Strategic model approved; operational validation pending |
| `D-05` | Theme/Format boundary | Approve / Revise / Reject | Product + Operations + Legal | Strategic model approved; readiness validation pending |
| `D-06` | 90-day Pilot | Approve / Revise / Reject | Founder/MD | Approved in principle — execution waits for D-07 |
| `D-07` | Pilot owner and budget | Appoint / Defer | Founder/MD | Pending |

---

## 23. แหล่งอ้างอิง

### ภายใน

- `docs/competitive-brief-thailand-2026-08.md`
- `docs/battlecard-bixitia-2026-08.md`
- `docs/sales-forecast-marketing-pipeline.md`
- `data/sot.duckdb`

### ภายนอก

- SmartGift Thailand: <https://smartgiftthailand.com/>
- EcoGifts / PremiumExpert: <https://www.ecogifts.biz/>
- THORR'S Gifts: <https://thorrsgifts.com/>
- Giftmanufactory: <https://www.giftmanufactory.com/premium-corporate-gift-set>

แหล่งภายนอกใช้เพื่อเปรียบเทียบโครงสร้างข้อเสนอและข้อความสาธารณะเท่านั้น ไม่ถือเป็นหลักฐานยืนยันยอดขาย คุณภาพ หรือความสามารถในการส่งมอบของบุคคลภายนอก

---

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.1b | 2026-08-13 | beta | Boss อนุมัติ Positioning, Master Brand, Portfolio Model และ Controlled Pilot; คง Owner/Budget และ Readiness Gate เป็น pending | uncommitted | ATHER |
| 0.1.0b | 2026-08-12 | draft | เสนอ Positioning และพอร์ตหลายมิติ พร้อม Recipient/Segment/Gift Tier/Theme/Format, ตัวอย่าง Loyalty Program และ Pilot 90 วัน | uncommitted | ATHER |
