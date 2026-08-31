---
version: "0.1.1b"
created_at: "2026-08-13T01:37:23+07:00, ATHER, uncommitted"
last_update: "2026-08-13T05:03:06+07:00, ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "campaign-brief-and-recipient-matrix-template"
  domain: "smartgift-marketing"
  scope: "controlled-pilot-discovery-segmentation-and-campaign-approval"
  artifact_id: "SG-CBRM-001"
  language: "th"
  parent_artifacts:
    - "SG-BPPA-001@0.1.1b"
    - "SG-GTM-001@0.1.1b"
    - "SG-PTOR-001@0.1.1b"
---

# SmartGift Campaign Brief & Recipient Matrix Template

## 0. สถานะ ขอบเขต และมติที่ต้องการ

| รายการ | ค่า |
|---|---|
| สถานะ | `beta` — Boss อนุมัติโครงสร้าง Brief, Recipient Matrix และ Approval Gates สำหรับ Controlled Pilot Planning; Functional validation และระบบจัดเก็บยังรออนุมัติแยก |
| ความซับซ้อน | C-2 — Documentation-Driven Campaign Scoping |
| ความเสี่ยง | LOW ในรอบเอกสาร; MEDIUM เมื่อนำไปใช้กับราคา ข้อมูลผู้รับ Claim หรือ Fulfilment จริง |
| ใช้กับ | Discovery, Campaign scoping, Recipient segmentation, Offer-route brief และ Client approval |
| ไม่ใช่ | ใบเสนอราคา, รายชื่อผู้รับจริง, Purchase order, Production order, Consent record หรือ Public claim approval |

เอกสารนี้เป็นแบบฟอร์มกลางสำหรับตอบคำถามว่า “จะให้ใคร เพราะอะไร และควรได้รับการดูแลระดับไหน” ก่อนเริ่มเลือกสินค้า เป้าหมายคือให้ SmartGift แตกข้อเสนอสำหรับ “ลูกค้าของลูกค้า” ได้หลายกลุ่ม โดยไม่ล็อกทุกคนไว้ในสินค้า Theme หรือ Gift Tier เดียวกัน

**Approval record:** Boss ตอบ `approve` ใน Codex เมื่อ 2026-08-13 อนุมัติโครงสร้าง Campaign Brief, Recipient Matrix, การแยก 5 มิติ และ Approval Gates สำหรับ Controlled Pilot Planning การอนุมัตินี้ไม่อนุญาต Outreach บัญชีจริง, ไม่อนุมัติรายชื่อผู้รับ/PII, ราคา, Claim, Proposal, Purchase order, Production release หรือการสร้างระบบโดยอัตโนมัติ

มติระดับแบบจำลองที่อนุมัติแล้ว:

1. อนุมัติโครงสร้าง Campaign Brief
2. อนุมัติฟิลด์และกฎของ Recipient Matrix
3. อนุมัติการแยก `Recipient Relationship`, `Client Segment`, `Gift Tier`, `Theme` และ `Format`
4. อนุมัติ Approval Gate ก่อนส่งต่อไป Product selection, Pricing และ Proposal

มติที่ยังต้องดำเนินการแยก:

5. ให้ Functional Owner ตรวจและรับรอง RACI, Gate operation และ Privacy boundary
6. แต่งตั้งผู้รับผิดชอบจริงในแต่ละ Campaign instance
7. จัดทำ BRD/PRD และอนุมัติ Storage, Retention, Integration และ Migration หากจะนำ Template ไปสร้างระบบ

ไม่มีการแก้เว็บไซต์ ระบบฐานข้อมูล ราคา หรือข้อมูลลูกค้าในรอบเอกสารนี้

---

## 1. หลักการสำคัญ

SmartGift ใช้ลำดับการคิดนี้:

```text
Client
→ Campaign / Occasion
→ Recipient Relationship
→ Client-defined Segment
→ Treatment Objective
→ Gift Tier
→ Theme preference
→ Format
→ Offer Route
→ Product candidates ที่ผ่าน Readiness Gate
```

กติกาหลัก:

- เริ่มจากผู้รับและวัตถุประสงค์ ไม่เริ่มจากรายการสินค้า
- หนึ่ง Campaign มีผู้รับหลายกลุ่ม หลาย Gift Tier และหลาย Theme ได้
- `Signature` คือระดับการดูแล ไม่ใช่หมวดสินค้าและไม่ใช่ชื่อกลุ่มผู้รับ
- `Tech`, `Care & Wellness` และ `Taste` คือ Theme ไม่ใช่ระดับความสำคัญ
- Client Segment เป็นภาษาของลูกค้า เช่น `Member Platinum` หรือ `Key Media` โดยต้อง Mapping เข้าภาษากลางของ SmartGift
- สถานะ VIP หรือระดับสมาชิกต้องมาจากกติกาที่ลูกค้ายืนยัน ห้าม SmartGift เดาจากชื่อ ตำแหน่ง หรือข้อมูลส่วนบุคคล
- ยังไม่ต้องใส่ชื่อบุคคลในช่วง Brief; ใช้จำนวนและกติกาคัดเลือกก่อน
- Unknown ต้องระบุ `TBD` หรือ `Not provided` ห้ามเติมตัวเลขหรือคำรับรองให้ดูสมบูรณ์

---

## 2. โครงสร้างข้อมูล 5 มิติที่ห้ามรวมกัน

| มิติ | คำถามที่ตอบ | เจ้าของข้อมูลหลัก | ตัวอย่าง |
|---|---|---|---|
| Recipient Relationship | ผู้รับเกี่ยวข้องกับลูกค้าอย่างไร | Client + Account Manager | Customer & Member, Media & Creator |
| Client Segment | ลูกค้าเรียก/แบ่งกลุ่มนี้ว่าอะไร | Client | Platinum Member, Key Media |
| Gift Tier | ต้องดูแลเข้มข้นระดับใด | SmartGift + Client | Reach, Select, Signature, Bespoke |
| Theme | ความสนใจหรือความหมายของของขวัญคืออะไร | Client + Marketing | Tech, Care & Wellness, Taste |
| Format | ส่งมอบคุณค่าในรูปแบบใด | Product + Operations | Physical, Voucher/Experience, Hybrid |

ตัวอย่างที่ไม่ถูกต้อง:

- `Signature Tech VIP` เป็นค่าก้อนเดียวที่ตรวจสอบไม่ได้
- `Food customer` ปะปนประเภทผู้รับกับ Theme
- `Media Gift` ทำให้สื่อทุกคนถูกบังคับให้ได้ของเหมือนกัน

ตัวอย่างที่ถูกต้อง:

```text
Relationship: Media & Creator
Client Segment: Key Media
Gift Tier: Signature
Primary Theme: Care & Wellness
Format: Hybrid
```

---

## 3. Controlled Vocabulary สำหรับ Recipient Relationship

ใช้หนึ่งค่าเป็น Primary relationship ต่อ Matrix row:

| Code | Relationship | ใช้เมื่อ | ไม่ได้แปลว่า |
|---|---|---|---|
| `LEADERSHIP` | Leadership | ผู้บริหาร กรรมการ หรือบุคคลสำคัญภายในองค์กร | ต้องเป็น Signature เสมอ |
| `TEAM` | Team | พนักงาน ผู้สมัคร พนักงานใหม่ หรือทีมโครงการ | ต้องใช้ Theme เดียวกันทั้งหมด |
| `CUSTOMER_MEMBER` | Customer & Member | ลูกค้า ผู้ใช้บริการ หรือสมาชิกของ Client | ระดับสมาชิกถูกกำหนดโดย SmartGift |
| `PARTNER_DEALER` | Partner & Dealer | คู่ค้า ตัวแทนจำหน่าย Supplier หรือ Strategic partner | มีสิทธิ์ได้รับราคาหรือของเฉพาะโดยอัตโนมัติ |
| `MEDIA_CREATOR` | Media & Creator | สื่อ ผู้สร้างเนื้อหา KOL หรือผู้มีบทบาทด้านการสื่อสาร | SmartGift รับรองสถานะหรืออิทธิพลของบุคคลนั้น |
| `GUEST_PUBLIC` | Guest & Public | แขก ผู้ร่วมงาน Prospect หรือประชาชนในกิจกรรม | สามารถเก็บ PII ได้โดยไม่มีฐานกฎหมาย |
| `COMMUNITY` | Community | ชุมชน ผู้รับประโยชน์ หรือกลุ่มเพื่อสังคม | สามารถใช้ Impact claim โดยไม่มีหลักฐาน |

หากผู้รับมีหลายความสัมพันธ์ ให้เลือก Primary ตามเหตุผลที่ได้รับของขวัญใน Campaign นี้ และบันทึก Secondary relationship ใน Notes เฉพาะเมื่อจำเป็น

---

## 4. Campaign Brief — ส่วนที่ลูกค้าและ Account Manager ต้องกรอก

### A. Campaign Identity

| Field | Required | คำอธิบาย | ค่า |
|---|---|---|---|
| Campaign ID | yes | Temporary ID ที่ไม่ใช้ชื่อบุคคล | `[TBD]` |
| Client / Brand | yes | ชื่อองค์กรหรือแบรนด์ | `[TBD]` |
| Campaign name | yes | ชื่อทำงาน ไม่ใช่ Public claim โดยอัตโนมัติ | `[TBD]` |
| Campaign archetype | yes | Member Appreciation / Launch & Media / Employee Welcome / Other | `[TBD]` |
| Occasion / trigger | yes | เหตุการณ์ที่ทำให้เกิดการให้ | `[TBD]` |
| Campaign owner — Client | yes | Role ก่อน; ชื่อเมื่อได้รับอนุญาต | `[TBD]` |
| Account owner — SmartGift | yes | ผู้ประสานงาน | `[TBD]` |
| Brief date | yes | วันที่รับข้อมูล | `[TBD]` |
| Target delivery/event date | yes | วันที่ต้องใช้จริง | `[TBD]` |
| Brief status | yes | Discovery / Draft Matrix / Client Review / Approved / On Hold / Cancelled | `Discovery` |

### B. Business Context and Objective

| คำถาม | คำตอบ |
|---|---|
| ปัญหาหรือโอกาสทางธุรกิจคืออะไร | `[TBD]` |
| ผู้รับควรรู้สึกหรือทำอะไรหลังได้รับ | `[TBD]` |
| ความสำเร็จของ Campaign วัดอย่างไร | `[TBD — ห้ามเดา Target]` |
| มีบทเรียนจาก Campaign เดิมหรือไม่ | `[Not provided / แนบหลักฐาน]` |
| อะไรคือสิ่งที่ Campaign นี้ห้ามสื่อ | `[TBD]` |
| หากต้องลด Scope อะไรต้องคงไว้ | `[TBD]` |

### C. Brand and Message

| Field | Required | ค่า |
|---|---|---|
| Core campaign message | yes | `[TBD]` |
| Desired tone | yes | `[TBD]` |
| Logo/CI source and version | conditional | `[TBD / Not applicable]` |
| Required wording | conditional | `[TBD / Not applicable]` |
| Prohibited wording | conditional | `[TBD / Not applicable]` |
| Language(s) | yes | `[TBD]` |
| Claim requested | conditional | `[TBD / None]` |
| Claim evidence owner | conditional | `[TBD / Not applicable]` |
| Final brand approver | yes | `[TBD role]` |

ข้อความที่เกี่ยวกับ Sustainability, Recycled/Reuse, Health, Food safety, Medical benefit, Certification หรือ Social impact ต้องผ่าน Claim Gate แยก แม้ลูกค้าจะใส่มาใน Brief แล้วก็ตาม

### D. Recipient Summary

| Field | Required | ค่า |
|---|---|---|
| จำนวนผู้รับรวมโดยประมาณ | yes | `[TBD / range]` |
| จำนวน Segment ที่คาด | yes | `[TBD]` |
| แหล่งที่มาของเกณฑ์แบ่งกลุ่ม | yes | `[Client CRM rule / Event list rule / HR rule / Other]` |
| Client data owner | yes | `[TBD role]` |
| ใช้รายชื่อบุคคลในขั้นใด | yes | `[TBD / ไม่ใช้ใน Brief]` |
| Sensitive data involved | yes | `No / Unknown / Yes — privacy review required` |
| Distribution model | yes | Bulk to client / Individual fulfilment / Event handout / Digital delivery / Mixed |

### E. Commercial and Operational Constraints

| Field | Required | ค่า |
|---|---|---|
| Budget basis | yes | Per recipient / Campaign total / Range / Not disclosed |
| Approved budget value | no | `[TBD — ระบุ Currency และสถานะ approval]` |
| Tax/VAT treatment | conditional | `[TBD by Finance]` |
| Delivery location scope | yes | `[TBD at area level; ไม่ใส่ที่อยู่บุคคลใน Brief]` |
| Packaging constraints | yes | `[TBD]` |
| Personalization allowed | yes | None / Segment-level / Individual-level / TBD |
| Artwork deadline | conditional | `[TBD]` |
| Sample/proof required | yes | No / Digital proof / Physical sample / TBD |
| Storage/assembly constraints | conditional | `[TBD]` |
| Voucher/experience requested | yes | No / Possible / Required |
| Known exclusions | yes | `[Alcohol / Food allergen / Battery / Fragrance / Other / None known]` |

ตัวเลขราคา MOQ Lead time และ Validity ที่ยังไม่ผ่าน Commercial Gate ให้บันทึกว่า `TBD` ห้ามคัดลอกจาก Staging data ไปใช้เป็นคำมั่นต่อลูกค้า

---

## 5. Recipient Matrix — แบบฟอร์มหลัก

หนึ่งแถวหมายถึง “กลุ่มผู้รับที่ต้องได้รับ Treatment เดียวกัน” ไม่ใช่หนึ่งบุคคลและไม่ใช่หนึ่ง SKU

### 5.1 Core Matrix

| Field | Required | Rule |
|---|---|---|
| Row ID | yes | รหัสภายใน Campaign เช่น `R01`; ห้ามใช้ PII |
| Primary relationship | yes | ใช้ Controlled Vocabulary ในข้อ 3 |
| Client segment label | yes | ใช้คำที่ Client ยืนยัน เช่น `Platinum Member` |
| Segment definition / eligibility | yes | กติกาที่ตรวจซ้ำได้; ห้ามใช้ความเห็นส่วนตัวลอย ๆ |
| Estimated count | yes | จำนวนหรือ Range พร้อม Source/วันที่; `TBD` ได้ |
| Treatment objective | yes | ผู้รับควรรู้สึก/ทำอะไร |
| Gift tier | yes | Reach / Select / Signature / Bespoke |
| Tier rationale | yes | เหตุผลตามความสำคัญของ Campaign ไม่ใช่ตำแหน่งอย่างเดียว |
| Primary theme | yes | Theme ที่ตอบ Objective ดีที่สุด |
| Secondary themes | no | ไม่เกินที่จำเป็น; ใช้เพื่อเปิดทางเลือก ไม่ใช่บังคับ Bundle |
| Theme exclusions | yes | สิ่งที่ไม่เหมาะกับกลุ่มนี้ หรือ `None known` |
| Preferred format | yes | Physical / Voucher/Experience / Hybrid / Open |
| Personalization level | yes | None / Segment / Individual / TBD |
| Delivery channel | yes | Event / Bulk / Individual / Digital / Mixed / TBD |
| Message variation | yes | Shared / Segment-specific / Individual / TBD |
| Data classification | yes | Aggregate / Business contact / Personal / Sensitive / Unknown |
| Client approver | yes | Role หรือ Approved authority |
| Matrix status | yes | Draft / Client confirmed / Feasibility review / Approved / On hold |
| Notes / dependency | no | Constraint หรือคำถามเปิด |

### 5.2 Copy-ready Matrix

| Row ID | Relationship | Client Segment | Eligibility Rule | Count / Source date | Objective | Gift Tier / Rationale | Primary Theme | Secondary / Excluded Themes | Format | Personalization | Delivery | Message | Data Class | Client Approver | Status / Dependencies |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| R01 | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | Draft |
| R02 | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | Draft |
| R03 | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | Draft |

---

## 6. วิธีเลือก Gift Tier โดยไม่ผูกกับสินค้า

| Gift Tier | ใช้เมื่อ | คำถามตรวจสอบ | สิ่งที่ยังไม่ใช่คำสัญญา |
|---|---|---|---|
| Reach | ต้องเข้าถึงคนจำนวนมากด้วยแกนร่วมที่ชัด | ต้องรักษาความหมายขั้นต่ำอะไรให้เหมือนกัน | ราคาต่ำสุดหรือ MOQ ใด ๆ |
| Select | ต้องปรับให้เหมาะกับ Segment อย่างมีเหตุผล | มีความต่างของ Need/Context ที่ต้องตอบหรือไม่ | เลือกได้ทุก SKU |
| Signature | กลุ่มสำคัญต้องได้รับ Treatment ที่ตั้งใจและภาพลักษณ์สูง | Packaging, message, proofing หรือ service level ใดทำให้รู้สึกพิเศษ | ต้องเป็นของแพงหรือ Theme เดียว |
| Bespoke | ต้องออกแบบเฉพาะอย่างมีนัยสำคัญ | ความต้องการใดแก้ด้วย Route ปกติไม่ได้ | รับทำได้ทันทีโดยไม่ตรวจ feasibility |

การให้ผู้บริหารที่รักสุขภาพอาจเป็น:

```text
Relationship: Leadership
Client Segment: Executive Wellness Preference
Gift Tier: Signature
Theme: Care & Wellness
Format: Physical หรือ Hybrid ตาม Brief
```

ไม่ควรเขียนว่า `Signature = ผู้บริหาร` หรือ `Signature = Tech set` เพราะจะล็อกการเลือกโดยไม่จำเป็น

---

## 7. Theme Preference Card ต่อ Recipient Row

ใช้ส่วนนี้เมื่อ Theme สำคัญต่อการคัด Route:

| Field | ค่า |
|---|---|
| Matrix Row ID | `[Rxx]` |
| Primary Theme | `[Tech / Care & Wellness / Taste / Lifestyle & Travel / Impact / Work & Welcome / Culture & Local]` |
| Why this theme fits | `[TBD]` |
| Secondary Theme(s) | `[TBD / None]` |
| Explicit exclusions | `[TBD / None known]` |
| Food/allergy constraint | `[TBD / Not applicable]` |
| Health/medical claim risk | `[TBD / Not applicable]` |
| Sustainability/impact claim risk | `[TBD / Not applicable]` |
| Device/battery/IT constraint | `[TBD / Not applicable]` |
| Voucher geography/expiry constraint | `[TBD / Not applicable]` |
| Evidence or approver required | `[TBD]` |

---

## 8. Offer Route Handoff

หลัง Client ยืนยัน Recipient Matrix แล้ว Product/Sourcing จึงสร้าง Route โดยอ้าง Row ID ห้ามกลับไปเปลี่ยน Segment แบบเงียบ ๆ เพื่อให้เข้ากับสินค้าที่มี

ค่าเริ่มต้นคือ 2 Route ต่อกลุ่ม และเพิ่ม Route ที่ 3 ได้เฉพาะเมื่อมีความแตกต่างเชิงกลยุทธ์จริงตาม Product Taxonomy

| Field | Route A | Route B | Route C — optional |
|---|---|---|---|
| Matrix Row ID | `[TBD]` | `[TBD]` | `[TBD]` |
| Route idea | `[TBD]` | `[TBD]` | `[TBD]` |
| Treatment logic | `[TBD]` | `[TBD]` | `[TBD]` |
| Theme / Format | `[TBD]` | `[TBD]` | `[TBD]` |
| Candidate components | `[หลัง readiness review]` | `[หลัง readiness review]` | `[หลัง readiness review]` |
| Minimum required readiness | `[TBD]` | `[TBD]` | `[TBD]` |
| Price authority / validity | `[TBD]` | `[TBD]` | `[TBD]` |
| MOQ / lead-time authority | `[TBD]` | `[TBD]` | `[TBD]` |
| Claim/partner gates | `[TBD]` | `[TBD]` | `[TBD]` |
| Key trade-off | `[TBD]` | `[TBD]` | `[TBD]` |
| Feasibility status | Not reviewed | Not reviewed | Not reviewed |

Offer Route เป็นแนวทางประกอบข้อเสนอ ไม่ใช่ใบเสนอราคาหรือการจองสต็อก

---

## 9. ตัวอย่างสมมุติ — ห้าง/โปรแกรมสมาชิก

> ตัวอย่างนี้เป็นสถานการณ์สมมุติเพื่ออธิบายโครงสร้าง ไม่ใช่ Brief จริงของ The One หรือองค์กรใด และไม่มีข้อมูลบุคคลจริง

Campaign สมมุติ: งานเปิดตัวสิทธิประโยชน์สมาชิก โดยมีสื่อและสมาชิกหลายระดับ

| Row ID | Relationship | Client Segment | Eligibility Rule | Count | Objective | Tier | Theme | Format | Notes |
|---|---|---|---|---:|---|---|---|---|---|
| R01 | Media & Creator | Key Media | รายชื่อที่ Client Communications อนุมัติสำหรับงานนี้ | TBD | ช่วยให้เข้าใจและจดจำแกนข่าว | Signature | Care & Wellness หรือ Tech ตาม preference brief | Hybrid/Open | ห้าม SmartGift จัดอันดับสื่อเอง |
| R02 | Media & Creator | General Media | ผู้ลงทะเบียนสื่อที่ Client ยืนยัน | TBD | ให้ข้อมูลและประสบการณ์ที่สอดคล้องกัน | Select | Work & Welcome | Physical | ไม่ใช้คำว่า Key Media |
| R03 | Customer & Member | Top-tier Member | กฎ Tier จาก Client CRM ณ Cut-off date | TBD | แสดงการยอมรับและรักษาความสัมพันธ์ | Signature | เปิด Care / Taste / Lifestyle ให้เลือกตามข้อจำกัด | Physical/Experience | ไม่ส่งข้อมูลสุขภาพให้ SmartGift เว้นแต่จำเป็นและมีฐานกฎหมาย |
| R04 | Customer & Member | Core Member | กฎ Campaign eligibility ที่ Client ยืนยัน | TBD | กระตุ้นการมีส่วนร่วมกับสิทธิประโยชน์ | Select | Taste หรือ Lifestyle & Travel | Voucher/Experience | ต้องตรวจ Partner, expiry และ geography |
| R05 | Guest & Public | Event Guest | ผู้ร่วมงานตามกติกาลงทะเบียน | TBD | สร้างการรับรู้และความทรงจำร่วม | Reach | Culture & Local หรือ Work & Welcome | Physical/Digital | เก็บข้อมูลเท่าที่จำเป็น |

สิ่งที่ตัวอย่างนี้แสดง:

- สื่อไม่ได้มี Gift Tier เดียวกันทั้งหมด
- สมาชิกไม่ได้ถูกผูกกับสินค้าเดียวกันเพียงเพราะอยู่ใน Relationship เดียวกัน
- Client เป็นผู้กำหนด Tier/eligibility ของสมาชิกและรายชื่อสื่อ
- SmartGift ใช้ Theme และ Format เปิด Route ที่เหมาะกับแต่ละกลุ่ม
- `Signature` สามารถเป็น Care, Tech, Taste หรือ Hybrid ได้ตาม Treatment objective

---

## 10. Approval Gates

### Gate CB-0 — Brief Completeness

ผ่านเมื่อ:

- Campaign objective และวันใช้งานถูกระบุ
- Recipient summary มีจำนวนหรือ Range พร้อมสถานะ Source
- Constraint สำคัญและผู้อนุมัติถูกระบุ หรือทำเครื่องหมาย `TBD`
- ไม่มี PII ที่ไม่จำเป็นในเอกสาร Brief

ผลลัพธ์: `READY_FOR_MATRIX`

### Gate CB-1 — Recipient Matrix Confirmation

ผ่านเมื่อ:

- Client ยืนยัน Segment label และ Eligibility rule ทุกแถว
- Relationship, Gift Tier, Theme และ Format แยกฟิลด์กัน
- Count มี Source date หรือระบุว่า Estimate/TBD
- Client Approver และ Data owner ถูกระบุ

ผลลัพธ์: `READY_FOR_OFFER_DESIGN`

### Gate CB-2 — Offer Feasibility

ผ่านเมื่อ:

- Candidate Component ผ่าน Readiness state ที่งานนั้นต้องใช้
- ราคา MOQ Lead time และ Validity มี Authority ที่ตรวจได้
- Claim, Voucher/Partner, Food/Allergy, Battery และ Personalization gates ผ่านตามกรณี
- Operations ยืนยัน Fulfilment และ Proof/Sample path

ผลลัพธ์: `READY_FOR_PROPOSAL`

### Gate CB-3 — Proposal Scope Approval

ผ่านเมื่อ:

- Client เลือก Route หรืออนุมัติขอบเขตสำหรับ Quote/Sample
- Exclusion, dependency, approval timeline และ validity ถูกแสดง
- ขอบเขตข้อมูลผู้รับและ Fulfilment ถูกยืนยัน

ผลลัพธ์: `APPROVED_SCOPE` — ยังไม่เท่ากับ Purchase order หรือ Production release

---

## 11. Approval Matrix

| รายการ | Account Manager | Client Owner | Product/Sourcing | Operations | Finance/Commercial | Brand/Legal | Data/Privacy |
|---|---|---|---|---|---|---|---|
| Campaign objective | R | A | I | I | I | C | I |
| Recipient segment/eligibility | R | A | I | C | I | I | C |
| Gift Tier/Treatment | R | A | C | C | C | C | I |
| Theme/Format | R | C | A/R | C | C | C | C |
| Product readiness | I | I | A/R | C | C | C | I |
| Price/validity | I | I | C | I | A/R | I | I |
| Claim | C | C | C | I | I | A/R | C |
| Fulfilment | C | C | C | A/R | C | I | C |
| Recipient data transfer | I | C | I | R | I | I | A |
| Final scope approval | R | A | C | C | C | C | C |

Legend: `A` Accountable, `R` Responsible, `C` Consulted, `I` Informed. ชื่อบุคคลจริงให้กำหนดใน Campaign instance ไม่ใช่ใน Template กลาง

---

## 12. Privacy and Recipient-data Boundary

ช่วง Brief และ Matrix ใช้ข้อมูลระดับกลุ่มก่อน:

- ห้ามใส่ชื่อ เบอร์โทร อีเมล ที่อยู่ วันเกิด หรือข้อมูลสุขภาพรายบุคคลใน Matrix
- เก็บเฉพาะ Segment rule, Count, Data class, Owner และ Purpose
- Client ต้องเป็นผู้ยืนยันสิทธิ์และฐานที่ใช้ส่งข้อมูลผู้รับ
- ถ้าต้อง Fulfil รายบุคคล ให้แยก Recipient manifest ออกจากเอกสารนี้และกำหนด Access, transfer, retention และ deletion
- ห้ามใช้ข้อมูล Sensitive เพื่อปรับ Gift โดยไม่มีความจำเป็น ฐานกฎหมาย และการอนุมัติที่เหมาะสม
- ส่งออกเอกสารภายนอกต้องตรวจว่าไม่มี Internal note, Cost หรือ Source path ที่ไม่ควรเปิดเผย

---

## 13. Quality Checklist ก่อนขอ Client Approval

- [ ] Campaign objective เขียนเป็น Outcome ไม่ใช่ชื่อสินค้า
- [ ] ทุก Recipient row มี Relationship และ Client Segment แยกกัน
- [ ] Eligibility rule ตรวจสอบซ้ำได้และมาจาก Client
- [ ] Gift Tier มีเหตุผล ไม่ได้ผูกกับตำแหน่งหรือ Theme โดยอัตโนมัติ
- [ ] Theme preference และ exclusions ถูกระบุ
- [ ] Format ยังเปิดได้เมื่อ Client ไม่ต้องการถูกล็อก
- [ ] Count ระบุ Source date / Estimate / TBD อย่างตรงไปตรงมา
- [ ] Budget, price, MOQ และ lead time ไม่มีค่าที่เดาหรือไม่มี Authority
- [ ] Claim ที่มีความเสี่ยงถูก Flag
- [ ] Voucher/Experience มี Partner/expiry/geography gate
- [ ] Data class และ Privacy owner ถูกระบุ
- [ ] Approver และ Open decision ถูกระบุ
- [ ] ไม่มี PII รายบุคคลใน Brief/Matrix

---

## 14. Client Confirmation Block

| รายการ | ค่า |
|---|---|
| Campaign ID / Version | `[TBD]` |
| Matrix rows approved | `[TBD]` |
| Rows on hold / excluded | `[TBD / None]` |
| Approved assumptions | `[TBD / None]` |
| Open decisions and due date | `[TBD / None]` |
| Client approver role | `[TBD]` |
| Approval evidence reference | `[TBD]` |
| Approval date | `[TBD]` |
| SmartGift Account owner | `[TBD]` |
| Next authorized action | Offer design / Feasibility / Quote / Sample / Hold |

การอนุมัติ Matrix หมายถึงอนุมัติกลุ่มผู้รับและ Treatment direction เท่านั้น เว้นแต่ Approval evidence จะระบุ Price, Quantity, Artwork, Claim หรือ Production release แยกอย่างชัดเจน

---

## 15. Change Control ต่อ Campaign Instance

เปลี่ยน Version เมื่อเกิดเหตุใดเหตุหนึ่ง:

- เพิ่ม/ลบ Recipient row
- เปลี่ยน Eligibility rule หรือ Count อย่างมีนัยสำคัญ
- เปลี่ยน Gift Tier, Theme, Format หรือ Treatment objective
- เปลี่ยน Budget authority, delivery date หรือ geography
- เปลี่ยน Data class, personalization หรือ fulfilment model
- เปลี่ยนผู้มีอำนาจอนุมัติ

ทุก Version ต้องเก็บ:

- Version ID และวันที่
- ผู้แก้และเหตุผล
- แถว/ฟิลด์ที่เปลี่ยน
- Approval evidence ของ Version ใหม่
- ผลกระทบต่อ Offer, Quote, Artwork, Procurement และ Fulfilment

ห้ามแก้ Matrix ที่อนุมัติแล้วแบบทับเงียบ หากมีการเปลี่ยนให้สร้าง Revision และ Reconfirm ขอบเขตที่ได้รับผลกระทบ

---

## 16. Acceptance, Success and Exit Criteria

### Acceptance Criteria ของ Template

- รองรับ Campaign เดียวที่มีหลาย Relationship, Client Segment, Gift Tier, Theme และ Format
- แยกภาษาของ Client ออกจาก Controlled Vocabulary ของ SmartGift
- รองรับ Media, Member และระดับย่อยของลูกค้าของลูกค้าโดยไม่ใช้ PII
- ส่งต่อไป Product Taxonomy และ Offer Route ได้ด้วย Row ID
- แสดง Approval boundary และ Unknown อย่างชัดเจน

### Success Criteria ของ Pilot Use

- Account Manager และ Client สร้าง Matrix ที่ตีความตรงกันได้
- Product/Sourcing คัด Route โดยไม่ต้องเดาความสำคัญของผู้รับ
- ไม่มีสินค้า ราคา Claim หรือ Partner ถูกถือว่าพร้อมเพียงเพราะอยู่ใน Brief
- การแก้ Segment หรือ Treatment มี Revision และ Approval evidence
- ทีมสามารถอธิบายได้ว่าทำไมแต่ละกลุ่มจึงได้ Treatment ต่างกัน

### Exit Criteria ก่อนทำเป็นระบบ

- Template v0.1 ได้รับอนุมัติ
- ทดลองใช้กับ Brief จำลองครบ 3 GTM Plays
- Functional Owner ตรวจ Gate, RACI และศัพท์ควบคุม
- ระบุ Field authority, privacy, retention และ versioning ใน BRD/PRD
- วิเคราะห์ Mapping กับ SoT/CRM/Proposal workflow โดยไม่ทำลาย Source lineage
- อนุมัติ Implementation, Test และ Rollback plan แยก

---

## 17. Decision Record

| ID | Decision | Owner | Status |
|---|---|---|---|
| `CBRM-D01` | Campaign Brief sections | Marketing + Sales | Approved for Pilot Planning — Boss, 2026-08-13 |
| `CBRM-D02` | Recipient Relationship vocabulary | Marketing + Sales | Approved for Pilot Planning — Boss, 2026-08-13 |
| `CBRM-D03` | Recipient Matrix fields and row semantics | Marketing + Operations | Approved for Pilot Planning — Boss, 2026-08-13 |
| `CBRM-D04` | Gift Tier decision guide | Marketing + Sales + Product | Approved for Pilot Planning — Boss, 2026-08-13 |
| `CBRM-D05` | Offer Route handoff | Product + Sales + Operations | Strategic model approved; operational validation pending |
| `CBRM-D06` | Approval Gates and RACI | Founder/MD + Functional Owners | Strategic model approved; role assignment/validation pending |
| `CBRM-D07` | Privacy boundary | Client Data Owner + Privacy authority | Control model approved; privacy-authority validation pending |
| `CBRM-D08` | Campaign instance storage/implementation | Technical/Data authority | Deferred to BRD/PRD |

---

## 18. แหล่งอ้างอิง

- `docs/SMARTGIFT-BRAND-PRODUCT-PORTFOLIO-ARCHITECTURE-2026-08.md` v0.1.1b
- `docs/SMARTGIFT-GO-TO-MARKET-PLAN-2026-08.md` v0.1.1b
- `docs/SMARTGIFT-PRODUCT-TAXONOMY-OFFER-RULES-2026-08.md` v0.1.1b

ตัวอย่างชื่อ Client Segment ในเอกสารนี้เป็นข้อมูลสมมุติเพื่อแสดงโครงสร้าง ห้ามตีความเป็นข้อมูลลูกค้า รายชื่อผู้รับ หรือ Brief ที่ได้รับอนุมัติจริง

---

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.1b | 2026-08-13 | beta | Boss อนุมัติโครงสร้าง Brief, Recipient Matrix, 5 มิติ และ Approval Gates สำหรับ Pilot Planning; คง Functional validation, PII use และ Storage/Integration เป็น pending | uncommitted | ATHER |
| 0.1.0b | 2026-08-13 | draft | สร้าง Campaign Brief, Recipient Matrix, Gift Tier guide, Offer Route handoff, Approval Gates, RACI, Privacy boundary และตัวอย่างห้าง/โปรแกรมสมาชิกแบบสมมุติ | uncommitted | ATHER |
