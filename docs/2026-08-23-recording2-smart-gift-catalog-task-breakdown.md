---
version: "0.2.1b"
created_at: "2026-08-23T14:15:44+07:00,ATHER"
last_update: "2026-08-23T18:00:00+07:00,ATHER"
status: "candidate"
superseded_by: null
attributes:
  domain: "smart-gift-catalog"
  doc_type: "implementation-plan"
  scope: "Recording2.m4a — Smart Gift catalog, pricing, AI assistant, and deployment"
  language: "Thai"
---

# Recording 2 — Smart Gift Catalog Task Breakdown

เอกสารนี้แปลงคำสั่งงานและประเด็นที่ได้ยินจาก `Recording2.m4a` เป็นงานย่อยที่
ตรวจรับได้ โดยผูกกับช่วงเวลาในเสียงทุกงานที่มีหลักฐาน

สถานะเอกสาร: `candidate` — ใช้ review/assign งานก่อนเริ่ม implementation

## 1. Document control

| Field | Value |
|---|---|
| Source audio | `C:\Users\freshair\OneDrive\Documents\Sound recordings\Recording2.m4a` |
| Transcript | `full-transcript.md` — `.tmp-transcript/recording2-large-v3-20260822-r3/artifacts/full-transcript.md` (นอก repo) |
| Minute of Note | `FUNG-Minute-of-Note-Recording2.docx` — `.tmp-transcript/recording2-large-v3-20260822-r3/artifacts/FUNG-Minute-of-Note-Recording2.docx` (นอก repo) |
| Meeting context | The Street 5 — Meeting Session 4 — 2026-08-20, 13:00–17:00 |
| Product scope | Smart Gift; catalog, product presentation, pricing, sales workflow, AI/RAG assistant, brand direction |
| Document owner | ATHER — draft extraction; business owner ยังต้องยืนยัน |
| Final approver | **คุณเจี๊ยบ (CEO)** — ยืนยันโดยเจ้าของงาน 2026-08-24 (เดิมเอกสารระบุคุณบอสไว้ผิด) |
| Product/business reviewer | คุณเจี๊ยบ (CEO) — เป็นทั้งผู้ตรวจและผู้อนุมัติ |
| Status | Candidate — PIC และ approval gate บางรายการยังเป็น `TBD` |

## 2. Evidence boundary and naming rules

### 2.1 What the audio proves

- มีการพูดถึง Catalog ที่ต้องทำให้เห็นทั้งสินค้ารายชิ้นและ Gift Set ไม่ให้ผู้ซื้อเข้าใจว่า Smart Gift ขายเฉพาะของในกล่อง
- มีการพูดถึงหน้า Product Profile, การเลือกสี, ภาพ/Mockup และการนำเสนอสินค้าแบบ interactive
- มีการพูดถึงข้อมูล Catalog/Product list ใน Excel, Product Spec, ราคา และการทำ Personal Catalog
- มีการพูดถึงการขายรายชิ้นและเป็น Set ในหน้าเดียวกัน, กล่อง, Mix and Match, จำนวนขั้นต่ำ และราคาตามจำนวน
- มีการพูดถึง AI ในบทบาทผู้ช่วย Admin/Sales, Business Facts, FAQ, permission, template และการสร้างใบเสนอราคา
- มีการพูดถึงการทำ Logo/Color Mockup, ส่งตัวเลือกให้เลือกในกลุ่ม และค่อยย้ายต่อไปทำ Catalog

### 2.2 What the audio does not prove

- เสียงไม่ได้ใช้คำว่า `Master Product`, `Product Family`, `Variant` หรือ `SKU` เป็นศัพท์ schema อย่างเป็นทางการ
- ยังไม่มีหมวดหมู่สินค้าและจำนวนรายการที่จะเผยแพร่บนหน้าแรกที่อนุมัติแล้ว
- ไม่มีการ assign งานให้คุณปอนด์หรือคุณเซฟอย่างชัดเจนใน transcript
- ไม่มีการยืนยันว่า Speaker A/B คือคุณเจี๊ยบ/คุณบอส/คุณปอนด์/คุณเซฟ เพราะรอบนี้ไม่ได้ทำ speaker diarization
- การพูดถึง 20,000/25,000 บาท, Lead time และสีแบรนด์ยังเป็นประเด็นหารือหรือข้อเสนอ ไม่ใช่ business rule ที่อนุมัติแล้ว

### 2.3 Role labels used in this document

| Role label | Basis | Confidence | Boundary |
|---|---|---|---|
| `PIC-TECH` | Speaker ที่ใช้ “ผม”, สาธิตระบบ, อธิบาย AI, Catalog, deployment และปิดประชุม | Medium | เป็น role label ไม่ใช่ชื่อบุคคล |
| `PIC-BUSINESS` | Speaker เชิงสินค้า/ตลาด/กำไร/ลูกค้า/การขาย | Medium | เป็น role label ไม่ใช่ชื่อบุคคล |
| `PIC-CHEF` | มีการกล่าวถึง “น้องเชฟ” ให้ไปดูวิธี deployment | Medium | ระบุเป็นงานวิจัยวิธี ไม่ได้ยืนยันว่าเป็นผู้ implement |
| `REVIEW-JEAB` | คุณเจี๊ยบในบทบาทผู้ตรวจเนื้อหา — **เป็นคนเดียวกับ `APPROVE-CEO`** ใช้แยกกันเฉพาะเวลาต้องการชี้ว่าเป็นการตรวจ ไม่ใช่การอนุมัติ | High | — |
| `APPROVE-CEO` | **คุณเจี๊ยบ (CEO)** — ยืนยันโดยเจ้าของงาน 2026-08-24 และสอดคล้องกับ `knowledge_source` ที่ระบุ author เป็น "คุณเจี๊ยบ (CEO)" ทั้ง briefing แนวทางสินค้าและกฎราคา | High | ผู้อนุมัติ decision ทั้งหมด |
| `COORD-BOSS` | คุณบอส — เดิมเอกสารสมมติว่าเป็นผู้อนุมัติสูงสุด **แก้แล้ว**; หลักฐานที่มีคือ `captured_by` ของ ceo-briefing คือเป็นผู้บันทึก/ประสานงาน | Low | บทบาทที่แน่ชัดยังไม่ยืนยัน |
| `PIC-POND`, `PIC-SAFE` | รายชื่อผู้เข้าร่วมจาก metadata | None | ยังไม่พบ task assignment จากเสียง |

> หมายเหตุ: “น้องเชฟ” (C14) กับ “คุณเซฟ” (metadata) อาจเป็นคนเดียวกันหรือไม่ก็ได้ — transcript ไม่ยืนยัน จึงคง `PIC-CHEF` และ `PIC-SAFE` แยกกันจนกว่าจะได้คำตอบ (ดู §7 ข้อ Q7)

## 3. Target work model

งานนี้ควรแยกข้อมูลออกเป็นคนละแกน ไม่ทำรายการสินค้า 1,000+ รายการเป็นการ์ดแบน ๆ

```text
Category / Master Product
└── Product Family
    └── Product Model
        └── Variant
            └── SKU

Bundle / Gift Set
└── component SKUs + packaging + commercial rules

Collection / Campaign
└── curated products or bundles for New Year, Christmas, Premium, budget, etc.
```

ข้อเสนอสำหรับศัพท์ระบบ:

| Layer | Example | ใช้ทำอะไร |
|---|---|---|
| Category / Master Product | แก้วน้ำ, กระเป๋า | หมวดหรือรากข้อมูลระดับธุรกิจ |
| Product Family | แก้วรุ่น A, Backpack, Handbag | กลุ่มสินค้าที่มีคุณสมบัติร่วมกัน |
| Product Model | รุ่นย่อยที่มีหน้ารายละเอียดของตัวเอง | การนำเสนอและอ้างอิงสินค้าหลัก |
| Variant | สี, ขนาด, วัสดุ, finish | ตัวเลือกที่ลูกค้าเลือก |
| SKU | รุ่น A + สีดำ + 500 ml | หน่วยขาย/สต็อก/ราคาแบบระบุได้แน่นอน |
| Bundle | แก้ว + กระเป๋า + กล่อง | ข้อเสนอชุดที่ประกอบจาก SKU หลายตัว |
| Collection | New Year 2027, Premium | ชุดนำเสนอ/แคมเปญ ไม่ใช่ SKU ใหม่ |

## 4. Clip-to-task index

คำว่า “คำสั่งจากเสียง” หมายถึงมีถ้อยคำหรือเจตนาสั่งงาน/ส่งมอบงานปรากฏในช่วงนั้น
ส่วน “แตกงานจาก requirement” หมายถึงเป็นงานที่ต้องมีเพื่อทำให้สิ่งที่พูดในเสียงตรวจรับได้

`Command status` ของแต่ละ task ใน §5 ใช้ป้ายกำกับตายตัว 3 แบบ:

| Tag | ความหมาย |
|---|---|
| `[EXPLICIT]` | มีถ้อยคำสั่งงาน/ส่งมอบงาน/กำหนดทิศทางปรากฏในเสียงตาม timecode |
| `[INFERRED]` | แตกงานเชิงระบบจาก requirement ที่พูด; เสียงไม่ได้สั่งงานนี้โดยตรง |
| `[DECISION]` | เป็นประเด็นหารือ/ความเสี่ยงที่ต้องมีผู้อนุมัติ ยังไม่ใช่คำสั่งปิดงาน |

| Clip ID | Timecode | คำสั่ง/ประเด็นจากเสียง | Task |
|---|---:|---|---|
| C01 | 00:00:59–00:01:24 | อ้างข้อมูลเก่าใน Excel และ order เฉลี่ย/จำนวนสินค้า | T01, T06 |
| C02 | 00:03:00–00:05:32 | ใช้ budget/order เป็น baseline แต่ต้นทุนแต่ละชุดไม่เท่ากัน | T06, D01 |
| C03 | 00:07:49–00:08:02 | จุดสำคัญคือระบบที่ใส่สินค้าอื่นและช่วยขายความสะดวก ไม่ใช่แค่สินค้าใหม่ | T01, T03 |
| C04 | 00:09:57–00:10:13 | ขอให้สรุปวิธีคุยของทีมขายและมี Sales Script | T11 |
| C05 | 00:11:29–00:13:08 | เปรียบเทียบ stock/buy order และ lead time 7–15 วัน | T12, D02 |
| C06 | 00:16:00–00:16:48 | ถกแกน Catalog: Christmas หรือ New Year; น้ำหนักโน้มไปทาง New Year แต่ยังไม่ใช่มติ (ดู D08) | T03 |
| C07 | 00:17:11–00:18:48 | ให้ค้นพบจากคำกว้าง เช่น premium/ของแจก และไม่ทำให้ดูเหมือนขายแต่ Gift Set | T03 |
| C08 | 00:19:27–00:20:26 | ต้องมีสินค้ารายชิ้นอยู่ใน Catalog และส่งตัวอย่างให้ดู | T03, T04 |
| C09 | 00:27:21–00:29:14 | ส่ง reference; ทำ Product Profile, เลือกสี, ภาพ/วิดีโอ/interactive | T04 |
| C10 | 00:30:28–00:31:41 | ตรวจความเร็วส่งของและข้อจำกัดการผลิต | T12, D02 |
| C11 | 00:49:22–00:49:41 | คุยเรื่องคัด/จัดจำนวนสินค้าที่นำเสนอ แต่ถ้อยคำไม่ชัดว่าเป็นมติ | T03, D03 |
| C12 | 00:50:46–00:51:24 | สินค้ารายชิ้นและ Set อยู่หน้าเดียวกัน ไม่ผูกทุกอย่างไว้ในกล่อง | T05 |
| C13 | 00:52:13–00:56:34 | จำนวน, กล่อง, ขั้นต่ำ, ขายเดี่ยว, Mix and Match และการคิดราคา | T05, T06 |
| C14 | 00:57:06–00:57:47 | เครื่อง local ใช้ได้แล้ว แต่ต้องทำให้คนอื่นเข้าถึง; ให้เชฟดูวิธี deploy | T09 |
| C15 | 01:08:34–01:09:11 | ทดสอบว่าคำนวณราคาถูกไหม และเพิ่มข้อมูลเข้าไป | T01, T06 |
| C16 | 01:09:19–01:09:23 | จะมี Catalog/Product list แบบ Excel เข้ามา | T01 |
| C17 | 01:11:35–01:14:23 | AI เป็นตัวช่วย Admin/Sales; ทดลองสร้างใบเสนอราคาและให้คนตรวจ | T06, T07 |
| C18 | 01:17:09–01:19:38 | ตั้งคำสั่ง AI, Business Facts, FAQ, permission, template, Google Docs edit | T07, T08 |
| C19 | 01:25:07–01:26:31 | เลือกแนวแล้วเจน logo mockup; ส่ง Excel/spec; ทำ Personal Catalog และ template | T01, T04, T10 |
| C20 | 01:28:46–01:29:10 | ตัดสินใจเรื่องดึงข้อมูลภายนอกและความเสี่ยงทางกฎหมาย | T13, D04 |
| C21 | 01:29:18–01:32:24 | ส่งตัวอย่าง/prompt; ทำ Catalog mockup; เปลี่ยน logo; ส่งสี 2–3 แบบ | T03, T10 |
| C22 | 01:33:14–01:34:07 | Mockup ใน product/mobile และเลือกสีตามบุคลิกแบรนด์ | T10, D05 |
| C23 | 01:42:24–01:42:36 | สรุปงาน: ทำ logo/color mockup ลงกลุ่ม; ผ่านแล้ว move ต่อไป Catalog | T10, T03 |
| C24 | 01:46:47–01:46:58 | ต้องทำ Script ให้ Sales และ FAQ | T11 |

## 5. Task breakdown

### T01 — รับและจัดระเบียบ Product Catalog / Excel

| Field | Definition |
|---|---|
| Source clips | C01, C15, C16, C19 — 00:00:59–00:01:24; 01:08:34–01:09:23; 01:25:24–01:26:09 |
| Command status | [EXPLICIT] input/data handoff; owner of source file ยังไม่ชัด (Q1) |
| Goal | รวม Excel, Product List, Product Spec และข้อมูลลูกค้าเดิมเป็น source catalog ที่ตรวจย้อนกลับได้ |
| PIC | `PIC-BUSINESS` เป็น data owner — **TBD ชื่อคนส่งข้อมูล**; `PIC-TECH` เป็นผู้รับ/เตรียมข้อมูล |
| Approver | `APPROVE-CEO` เสนอให้อนุมัติ data scope; `REVIEW-JEAB` ตรวจความถูกต้องด้านสินค้า |
| AC | 1. มีไฟล์ต้นทางและ version ที่ระบุได้  2. ทุกแถวมี source reference  3. แยก product/family/model/variant/SKU ได้หรือทำเครื่องหมาย `unclassified`  4. ไม่ลบรายการเพราะเป็นสีหรือ SKU ซ้ำโดยยังไม่มีกฎ |
| SC | ค้นหาสินค้าตามประเภท/รุ่น/สี/งบได้ และตรวจได้ว่าข้อมูลที่ AI ใช้มาจากแถวใดใน Excel |
| Dependencies | ได้รับ Excel และ Product Spec จริง; ต้องตัดสินใจ taxonomy ใน T02 |
| Progress F-3 (2026-08-24) | ดึงใบราคาครบทุกไฟล์: **36 ไฟล์ · 2,368 แถว · 1,148 รหัส · 1,845 แถวมีราคาไล่ขั้น ≥5 ขั้น** (เดิม `price_staging` มีแค่ 12 รหัสที่ครบ 8 ขั้น) · ตรวจไขว้ C1/C5/A11/A20/A30/T20/T30 ตรงกับ price_staging ทุกตัว · 3 ไฟล์ layout เข้ากันไม่ได้ · ยังไม่ ingest เข้า canonical |
| Progress (2026-08-24) | ดึงชุดของขวัญ **479 รายการ** จากใบราคาธุรกิจ 2025 เข้า staging พร้อม component/สเปก/ราคา 8 ขั้น/รูป 459 ไฟล์ ทุกแถว trace กลับหน้า PDF ได้ — ดู [extraction report](2026-08-24-giftset-catalog-extract-report.md); 417 แถวสะอาด 62 แถวติดธง (ปัญหาอยู่ในใบราคาต้นฉบับ) · **ยังไม่ ingest เข้า canonical** รอ review |

### T02 — กำหนด Product Taxonomy และ SKU Boundary

| Field | Definition |
|---|---|
| Source clips | C11, C15, C16, C19 — 00:49:22–00:49:41; 01:08:34–01:09:23; 01:25:24–01:26:31 |
| Command status | [INFERRED] แตกงานเชิงระบบจากสิ่งที่พูด; **ไม่ได้มีคำสั่งใช้ศัพท์ schema โดยตรงในเสียง** |
| Goal | ทำให้สินค้าพันกว่าแถวเป็นโครงสร้าง `Category/Master → Family → Model → Variant → SKU` โดยไม่ทำข้อมูลหาย |
| PIC | `PIC-BUSINESS` + `PIC-TECH`; ชื่อ PIC รายคนต้องยืนยัน |
| Approver | `APPROVE-CEO` — proposed; `REVIEW-JEAB` เป็น product reviewer |
| AC | 1. “แก้วน้ำ/กระเป๋า” อยู่ระดับ Category/Master  2. “แก้วรุ่น A/B, Backpack/Handbag” อยู่ระดับ Family/Model ตาม taxonomy ที่อนุมัติ  3. สี/ขนาด/วัสดุเป็น Variant  4. SKU คือ combination ที่ขาย/คิดราคา/เช็กสต็อกได้  5. สีไม่สร้าง Product ใหม่  6. Bundle ไม่ duplicate Product แต่ reference SKU components |
| SC | สินค้าหนึ่งรุ่นแสดงเป็น Product card เดียวและเลือก Variant ได้; SKU ทุกตัวมีรหัสไม่ซ้ำและถูก trace กลับไปยัง source row |
| Dependencies | T01; ต้องมี decision D03 เรื่องจำนวนรายการที่นำเสนอ |
| Input (2026-08-23) | [SmartGift 2026 Campaign Architecture](2026-08-23-smartgift-2026-campaign-architecture.md) — เสนอ 4 กลุ่ม Category ระดับบนสุด (Smart Tech / Care & Wellness / Smart Work / Home & Travel) รหัส SKU ตัวอย่างตรวจกับ SoT แล้วมีจริง; รออนุมัติ D10 |

### T03 — ออกแบบ Collection/Catalog สำหรับเทศกาลและการค้นพบสินค้า

| Field | Definition |
|---|---|
| Source clips | C06–C08, C11, C21, C23 — 00:16:00–00:20:26; 00:49:22–00:49:41; 01:29:44–01:32:24; 01:42:24–01:42:36 |
| Command status | [EXPLICIT] product-presentation direction; ชื่อ Collection และแกนเทศกาลยังต้องอนุมัติ (D08) |
| Goal | ทำ Catalog ที่ดึงลูกค้าจากคำค้นกว้าง เช่น premium/ของแจก/ของขวัญปีใหม่ แล้วพาไปเลือกสินค้าได้ โดยไม่ทำให้เห็นแต่ Gift Set |
| PIC | `PIC-TECH` ทำ mockup/โครงหน้า; `PIC-BUSINESS` กำหนด collection และเนื้อหาสินค้า |
| Approver | `REVIEW-JEAB` review สินค้า/brand; `APPROVE-CEO` อนุมัติ collection และทิศทาง |
| AC | 1. มีหน้า Collection ที่ระบุ campaign 2. แสดง Product Family/Model ไม่ใช่การ์ด SKU ทุกสี 3. มี entry สำหรับสินค้ารายชิ้นและ Gift Set 4. ค้นจาก keyword กว้างได้ 5. จำนวนรายการที่นำเสนอเป็น curated list แยกจาก source catalog ทั้งหมด |
| SC | ผู้ใช้เข้า Catalog แล้วเข้าใจภายในหนึ่งหน้าว่า Smart Gift มีทั้งของรายชิ้นและชุด และเลือกต่อไปยัง Product Profile ได้โดยไม่ต้องถามทีมงานก่อน |
| Dependencies | T01, T02, T04, T05; D01 เรื่อง budget/collection และ D03 เรื่อง curated count |
| Input (2026-08-23) | 4 Strategic Gift Tiers (Reach / Select / Signature / Bespoke) จากเอกสาร Campaign Architecture — เป็นแกน Collection ทางเลือกนอกจากเทศกาล; ต้องตัดสิน D09 ก่อนทำ landing ใหม่ |

### T04 — สร้าง Product Profile และ Variant Selection

| Field | Definition |
|---|---|
| Source clips | C08–C09, C19, C22 — 00:19:27–00:20:26; 00:27:43–00:29:14; 01:25:07–01:26:31; 01:33:14–01:34:07 |
| Command status | [EXPLICIT] UX direction |
| Goal | ให้ลูกค้าเปิด Product Family/Model แล้วดูรายละเอียด เลือกสี/ตัวเลือก และดูภาพหรือ Mockup ได้ |
| PIC | `PIC-TECH` |
| Approver | `REVIEW-JEAB` ตรวจ product/brand copy; `APPROVE-CEO` อนุมัติ UX direction |
| AC | 1. Product card มี Product name/spec 2. เลือก Variant ได้ 3. สีเป็น swatch/option ไม่ใช่สินค้าซ้ำ 4. แสดง branding/mockup state 5. ระบุข้อมูลที่ยังไม่มีเป็น unknown ไม่เดา |
| SC | ลูกค้าสามารถเริ่มจาก Product Family เดียวและเปลี่ยนสี/ตัวเลือกได้โดยไม่ต้องเปิดการ์ดใหม่หลายใบ |
| Dependencies | T02; assets จาก T10; Product Spec จาก T01 |
| Progress (2026-08-24) | **หน้า 02/03 ใช้ข้อมูลจริงแล้ว** — https://claude.ai/code/artifact/96271ea5-91b6-4dc0-abaf-86cbd39fd214 · รูป/ชื่อ/สเปก/ราคา 8 ขั้น จาก staging 479 ชุด ทุกการ์ดมีเลขหน้า+sha ต้นทาง · สลับสี A/B/C ได้ในหน้าเดียว · แทน AI mockup ที่เป็น placeholder |

### T05 — รองรับขายรายชิ้น, Bundle และ Mix-and-Match

| Field | Definition |
|---|---|
| Source clips | C12–C13 — 00:50:46–00:56:34 |
| Command status | [EXPLICIT] business/UX direction |
| Goal | ให้สินค้าเดียวกันนำเสนอได้ทั้งแบบรายชิ้นและเป็น Set ในหน้าเดียวกัน โดยมองเห็นผลของกล่องและการเลือกของ |
| PIC | `PIC-BUSINESS` นิยาม commercial rule; `PIC-TECH` ทำ interaction |
| Approver | `REVIEW-JEAB` ตรวจความเข้าใจลูกค้า; `APPROVE-CEO` อนุมัติ rule |
| AC | 1. Product เดี่ยวและ Bundle แยกชนิดข้อมูล 2. Bundle อ้างอิง component SKU 3. เลือก/ไม่เลือกกล่องได้ตาม rule 4. Mix-and-Match ไม่สร้าง SKU ปลอม 5. กำหนดขั้นต่ำและกรณีสินค้าชิ้นเดียวใส่กล่องได้/ไม่ได้ |
| SC | เมื่อเปลี่ยนจากรายชิ้นเป็น Set ระบบยังแสดงรายการสินค้าและเงื่อนไขราคาไม่กำกวม และส่งต่อให้ T06 คำนวณได้ |
| Dependencies | T02; Product/Packaging rules จาก business (T05 เป็น input ของ T06 ไม่ใช่ dependent) |

### T06 — กำหนด Pricing Rule และใบเสนอราคา

| Field | Definition |
|---|---|
| Source clips | C01–C02, C13, C15, C17 — 00:00:59–00:05:32; 00:52:13–00:56:34; 01:08:34–01:09:11; 01:12:18–01:14:23 |
| Command status | [EXPLICIT] intent to test calculation; final prices remain unapproved (D01) |
| Goal | ทำสูตรราคาที่คำนึงถึง SKU, จำนวน, กล่อง, branding, ต้นทุน และเงื่อนไขการผลิต แล้วสร้างใบเสนอราคาให้คนตรวจได้ |
| PIC | `PIC-BUSINESS` เป็น owner ของราคา/ต้นทุน — **TBD ชื่อ**; `PIC-TECH` ทำ calculator/quote flow |
| Approver | `APPROVE-CEO` + product/business reviewer ที่ได้รับมอบหมาย |
| AC | 1. 20,000 บาทระบุเป็น scenario/reference ไม่ใช่ final price 2. แยก quantity tier 3. แยก box/packaging cost 4. แยก branding/custom cost 5. แสดง assumptions 6. ใบเสนอราคาต้องมี human review ก่อนส่งลูกค้า |
| SC | ทดสอบ scenario budget/quantity/box แล้วผลคำนวณสอดคล้องกับสูตรที่อนุมัติ และไม่ตอบราคาที่ไม่มี source rule |
| Dependencies | T01, T02, T05; D01 budget; D02 lead time/stock |
| Progress (2026-08-24) | **มีต้นทุนจริงแล้ว** — จับคู่ราคาขายกับใบต้นทุนซัพพลายเออร์ 797 รหัส (121 รหัสคำนวณกำไรครบ) กำไรขั้นต้น@100 median **38%**, r=62% · เครื่องมือของจริงคือ `smartgift-pricing/public/pricing.html` ที่ทีมมีอยู่แล้ว ไม่ใช่ worksheet · ดู [pricing worksheet v0.2.0b](2026-08-24-smartgift-package-pricing-worksheet.md) และ `data/review/price_vs_cost.csv` |

### T07 — AI Decision Support สำหรับ Admin/Sales

| Field | Definition |
|---|---|
| Source clips | C17 — 01:11:35–01:12:37 |
| Command status | [EXPLICIT] role boundary |
| Goal | ให้ AI เป็นผู้ช่วย Admin/Sales แนะนำข้อมูลและตัวเลือก ไม่ใช่ผู้ตอบลูกค้าอัตโนมัติโดยไม่มีคนตรวจ |
| PIC | `PIC-TECH` |
| Approver | `APPROVE-CEO`; `REVIEW-JEAB` ตรวจคำตอบเชิงธุรกิจ |
| AC | 1. รับคำถามด้านงบ/จำนวน/ความต้องการ 2. แนะนำ Product Family/Variant/Bundle ที่มี source 3. แสดงเหตุผลและข้อมูลอ้างอิง 4. ส่งผลให้ Admin/Sales review 5. ห้ามยืนยันราคา/stock/lead time ที่ไม่มี rule |
| SC | Admin/Sales ปิดการขายได้เร็วขึ้นโดยยังมี human control และตรวจย้อนกลับได้ว่า AI ใช้ข้อมูลใด |
| Dependencies | T01, T02, T06; T08 ให้ Business Facts/permission ที่ T07 ใช้ (ทำคู่ขนานได้ แต่ T07 ใช้งานจริงได้เมื่อ T08 มี approved version) |

### T08 — Business Facts, FAQ, Permission และ Template

| Field | Definition |
|---|---|
| Source clips | C18 — 01:17:09–01:19:38 |
| Command status | [EXPLICIT] system/configuration direction |
| Goal | ให้ทีมแก้ข้อมูลธุรกิจและกำหนดขอบเขต AI ได้เอง รวมถึงจัดการข้อมูลขัดแย้งจากหลายการประชุม |
| PIC | `PIC-TECH` ทำระบบ/configuration; `REVIEW-JEAB` เป็น content editor ที่เสียงกล่าวถึง |
| Approver | `APPROVE-CEO` สำหรับ permission และ business policy |
| AC | 1. มี Business Facts 2. มี FAQ ตัวอย่างคำถาม/คำตอบ 3. มี permission แยกความสามารถ เช่น สร้าง PDF/ใบเสนอราคา 4. มี Template ตามงาน 5. มีสถานะ draft/review/approved 6. ข้อมูลขัดแย้งต้องถูก flag ไม่เลือกเองเงียบ ๆ |
| SC | คุณเจี๊ยบหรือผู้ได้รับสิทธิ์สามารถแก้ข้อมูลผ่านเอกสาร/หน้าที่กำหนด และคำตอบ AI เปลี่ยนตาม version ที่อนุมัติได้ |
| Dependencies | T01, T06; ต้องมี IAM/permission boundary (T08 ไม่รอ T07) |

### T09 — Deployment/Hosting ให้บุคคลอื่นใช้งาน

| Field | Definition |
|---|---|
| Source clips | C14 — 00:57:06–00:57:47 |
| Command status | [EXPLICIT] handoff/research request |
| Goal | เปลี่ยนจากระบบที่ใช้งานได้เฉพาะเครื่อง local ให้ผู้ได้รับอนุญาตเข้าถึงได้ โดยไม่เปิดข้อมูลเกินขอบเขต |
| PIC | `PIC-CHEF` ค้น/ประเมินวิธี deployment; `PIC-TECH` ประสานและตัดสินใจทางเทคนิค |
| Approver | `APPROVE-CEO` ต้องอนุมัติ deployment/data exposure ก่อนเปิดใช้จริง |
| AC | 1. มีวิธี deploy ที่รองรับ workload 2. ระบุ host/compute/data boundary 3. มี authentication/permission 4. มี performance test 5. มี rollback 6. ไม่ expose local database หรือข้อมูลลูกค้าโดยไม่อนุมัติ |
| SC | ผู้ใช้อื่นเข้าถึง Catalog/AI ตามสิทธิ์ได้จริง และระบบยังตอบสนองได้โดยไม่ต้องเปิดเครื่องส่วนตัวแบบ unsafe |
| Dependencies | T07, T08; security/legal review; D04 |

### T10 — Logo, Color, Mockup และ Personal Catalog

| Field | Definition |
|---|---|
| Source clips | C09, C19, C21–C23 — 00:27:21–00:29:14; 01:25:07–01:26:31; 01:29:44–01:34:07; 01:42:24–01:42:36 |
| Command status | [EXPLICIT] short-term delivery: ทำ mockup และลงกลุ่มให้เลือก |
| Goal | สร้าง Logo/Color Mockup และตัวอย่าง Personal Catalog เพื่อให้ทีมเลือก direction ก่อนขยับ Catalog ต่อ |
| PIC | `PIC-TECH` เป็นผู้ทำ mockup/ส่งลิงก์ตามคำพูด “ผมจะ...” |
| Reviewers | `APPROVE-CEO` (คุณเจี๊ยบ) และผู้เข้าร่วมในกลุ่ม — รายละเอียด approval workflow ต้องยืนยัน |
| Approver | **คุณเจี๊ยบ (CEO)** — ยืนยัน 2026-08-24 |
| AC | 1. มีตัวเลือกสีอย่างน้อย 2–3 แบบ 2. มี mockup ใน product/mobile context 3. แสดงการวาง logo ลูกค้า 4. ส่งให้กลุ่ม review 5. มีผลเลือก/ไม่เลือกที่บันทึกได้ 6. Catalog development เริ่มหลัง direction ผ่าน |
| SC | ทีมเห็นภาพเดียวกันและเลือก brand direction ได้โดยไม่ต้องตีความจากข้อความอย่างเดียว |
| Dependencies | Brand decision D05; T03, T04 |
| Progress (2026-08-23) | **mockup พร้อม review** — AC1 ✅ 3 ทิศทางสี (A Corporate Navy / B Warm Festive / C Modern Teal) · AC2 ✅ 8 หน้า × 3 ทิศทาง = 24 ภาพ รวม desktop + mobile + หน้าผลงานลูกค้า + landing แกน Tier (01b) + Package A/B/C (07) · AC3 ✅ มีพื้นที่วางโลโก้ใน Product Profile · AC5 ✅ หน้า review มีช่องเลือก + สร้างข้อความสรุป D05 · AC4 ✅ ส่งกลุ่มแล้ว 2026-08-23 (artifact link) — รอผลเลือก · AC6 ⏳ รอ D05 |
| Artifacts | Review page: https://claude.ai/code/artifact/faf75054-bc1f-4c33-80cd-638a9210d77a (shared to group) · Vercel (public, noindex): https://smartgift-catalog-mockup.vercel.app — project `pornpon/smartgift-catalog-mockup`, redeploy 2026-08-23 (รอบ 2) จาก `output/catalog-mockup-20260823/vercel-deploy/` — 21 PNG ต้นฉบับเต็ม รวม 01b · ไฟล์ต้นฉบับ: `Bussiness-01-SmartGift/output/catalog-mockup-20260823/` (15 PNG, `review.html`, `prompts.json`, `run-batch.py`, `DESIGN-BRIEF.md`) · เจนด้วย Codex CLI 0.147 built-in `image_gen` |
| Past-clients page (06) | ชื่อ 12 ลูกค้าจากหน้าเว็บ + ช่วงปีจาก SoT (`output/catalog-mockup-20260823/past-clients-evidence.md`) — **SoT ไม่มี line items จึงไม่รู้ว่าขายสินค้าอะไรให้ใคร** ช่องรูปเว้นเป็น "รอรูปงานจริง" ไม่ใส่สินค้าสมมติ; เปิด data request DRF-2026-08-23#3.1 ขอรายการสินค้า/รูปงานจริงจากทีมขาย |
| Caveats | ตัวเลขทุกตัวในภาพ (สเปก, ช่วงจำนวน, ช่วงงบในตัวกรอง) เป็น placeholder ที่ AI เจน ไม่ใช่ข้อมูลจาก Excel/Product Spec; ชื่อคอลเลกชัน "ปีใหม่ 2027" ใช้ชั่วคราวรอ D08; โลโก้ "SMART GIFT" เป็น wordmark ชั่วคราว |

### T11 — Sales Script และ FAQ สำหรับทีมขาย

| Field | Definition |
|---|---|
| Source clips | C04, C24 — 00:09:57–00:10:13; 01:46:47–01:46:58 |
| Command status | [EXPLICIT] requirement; PIC ไม่ได้ระบุชื่อ (Q5) |
| Goal | ทำ Script/FAQ ให้ Sales อธิบายสินค้า ราคา lead time และการเลือก Set/รายชิ้นได้สอดคล้องกัน |
| PIC | `PIC-BUSINESS` หรือ Sales lead — **TBD**; `PIC-TECH` ช่วยทำ template/AI integration |
| Approver | `APPROVE-CEO` + Sales/Product reviewer ที่ได้รับมอบหมาย |
| AC | 1. มีคำถาม-คำตอบหลัก 2. มี flow งบ/จำนวน/branding 3. ระบุสิ่งที่ห้ามรับปาก 4. link ไป Product/Bundle/SKU ที่ถูกต้อง 5. มี human review ก่อนใช้จริง |
| SC | Sales สองคนตอบ scenario เดียวกันได้สอดคล้อง และลดการให้ข้อมูลราคา/lead time ที่ไม่มีหลักฐาน |
| Dependencies | T05, T06, T07, T08, D02 |

### T12 — Service Promise, Stock และ Lead Time

| Field | Definition |
|---|---|
| Source clips | C05, C10 — 00:11:29–00:13:08; 00:30:28–00:31:41 |
| Command status | [DECISION] หารือเรื่อง lead time/stock; ยังไม่ใช่คำสั่งปิดงาน (D02) |
| Goal | ตัดสินใจ service promise และกฎ stock/buy order ก่อนนำไปใส่ Catalog, AI และ Sales Script |
| PIC | `PIC-BUSINESS` + Operations/Supply owner — **TBD** |
| Approver | `APPROVE-CEO` หรือผู้อนุมัติ commercial policy — ต้องยืนยัน |
| AC | 1. เลือก lead time ที่อนุมัติแล้ว 2. แยก stock-ready กับ made-to-order 3. ระบุขั้นต่ำ/ข้อยกเว้น 4. มี source/vendor evidence 5. ห้ามใช้คำว่า 7 วัน/15 วันก่อน approved |
| SC | Catalog, AI และ Sales Script ให้คำตอบ lead time เดียวกันและมีสถานะข้อมูลล่าสุด |
| Dependencies | T01, T06, T11; vendor/product data |

### T13 — External Data Access และ Legal Boundary

| Field | Definition |
|---|---|
| Source clips | C20 — 01:28:46–01:29:10 |
| Command status | [DECISION] risk gate ที่พูดถึงชัดเจน; ไม่ใช่ authorization ให้ scrape (D04 / legal) |
| Goal | กำหนดว่าจะใช้ข้อมูลภายนอกจาก public source/API ที่ได้รับอนุญาตเท่านั้น |
| PIC | `PIC-TECH` เตรียมทางเลือก; `APPROVE-CEO` ตัดสินใจความเสี่ยง/ขอบเขต |
| Approver | `APPROVE-CEO` (คุณเจี๊ยบ) ร่วมกับที่ปรึกษา legal — legal ยังไม่ระบุตัว |
| AC | 1. มี source allowlist 2. ระบุสิทธิ์การใช้ข้อมูล 3. มี API/public route เมื่อเป็นไปได้ 4. block source ที่ต้องใช้วิธีเสี่ยง 5. เก็บ provenance ของข้อมูล |
| SC | ระบบไม่ดึงข้อมูลจากแหล่งที่ยังไม่มี approval และสามารถอธิบายที่มาของข้อมูลใน Catalog/AI ได้ |
| Dependencies | T01, T07, T09; legal review |

## 6. Decision and approval register

| Decision ID | ต้องตัดสินใจ | Owner to prepare | Approver | Blocking tasks |
|---|---|---|---|---|
| D01 | Budget baseline: 20,000 / 25,000 / อื่น ๆ และสูตรราคา | `PIC-BUSINESS` | `APPROVE-CEO` | T03, T06, T11 |
| D02 | Lead time/stock promise: 7 / 7–15 / 15 วัน และ buy order vs stock | Operations + `PIC-BUSINESS` | `APPROVE-CEO` | T06, T11, T12 |
| D03 | จำนวน curated products ต่อ Collection; ห้ามตีความเสียงช่วง 00:49 เป็นมติจนกว่าจะยืนยัน | `PIC-BUSINESS` + `PIC-TECH` | `APPROVE-CEO` | T02, T03 |
| D04 | Deployment/hosting/data access สำหรับผู้ใช้อื่น | `PIC-TECH` + `PIC-CHEF` | `APPROVE-CEO` | T07, T08, T09 |
| D05 | Logo/color/brand direction — **ตัวเลือกพร้อมแล้ว** (T10 review page) รอส่งกลุ่มและรอผลเลือก | `PIC-TECH` ทำตัวเลือก ✅ | `APPROVE-CEO` (คุณเจี๊ยบ) | T03, T04, T10 |
| D06 | ใครเป็นเจ้าของ Excel/Product Spec และใคร approve product facts | `PIC-BUSINESS` | `APPROVE-CEO` | T01, T02, T06 |
| D07 | Sales owner และผู้อนุมัติ Script/FAQ | Sales lead — TBD | `APPROVE-CEO` | T07, T11 |
| D09 | ใช้ 4 Gift Tiers (Reach/Select/Signature/Bespoke) เป็นแกน Collection หลัก แทนหรือควบคู่เทศกาล (D08) — **asked 2026-08-23** ส่งกลุ่มพร้อม mockup เทียบ 01 (เทศกาล) vs 01b (Tier) × 3 สี; รอเคาะ | `PIC-BUSINESS` | `APPROVE-CEO` | T03, mockup หน้า 01 |
| D10 | อนุมัติ 4 กลุ่มสินค้าเป็น Category ระดับบนสุดของ taxonomy | `PIC-BUSINESS` + `PIC-TECH` | `APPROVE-CEO` | T02 |
| D11 | MOQ ต่อ Tier (100+/50+/10+/1–10) เป็น rule หรือแนวทาง | `PIC-BUSINESS` | `APPROVE-CEO` | T05, T06, T11 |
| D08 | แกน Collection แรก: New Year / Christmas / อื่น ๆ — เสียงช่วง 00:16 โน้มไปทาง New Year แต่ยังไม่มีผู้อนุมัติ | `PIC-BUSINESS` | `APPROVE-CEO` + `REVIEW-JEAB` | T03 |

## 7. PIC/approval gaps

สิ่งที่ยังต้องถามและไม่ควรเดา — ทุกข้อต้องมีสถานะก่อนเริ่ม implementation:

| # | คำถาม | ถามใคร | ปลดบล็อก | สถานะ | คำตอบ/วันที่ |
|---|---|---|---|---|---|
| Q1 | ใครเป็น data owner ของ Excel/Product Catalog ต้นฉบับ | คุณเจี๊ยบ (CEO) / `PIC-BUSINESS` | D06, T01 | asked | ส่งในกลุ่ม 2026-08-23 — รอคำตอบ |
| Q2 | ใครมีอำนาจ approve taxonomy และ SKU mapping | คุณเจี๊ยบ (CEO) | D03, T02 | asked | ส่งในกลุ่ม 2026-08-23 — รอคำตอบ |
| Q3 | คุณเจี๊ยบเป็น reviewer, editor หรือ final approver ของ Product Facts/Brand | คุณเจี๊ยบ (CEO) | T03, T04, T08, T10 | **answered** | 2026-08-24: คุณเจี๊ยบเป็น CEO และเป็นผู้อนุมัติ — สอดคล้องกับ knowledge_source |
| Q4 | คุณบอสเป็น final approver ของทุก task หรือเฉพาะ direction/การเปิดระบบ | เจ้าของงาน | ทุก D | **answered** | 2026-08-24: ผู้อนุมัติคือคุณเจี๊ยบ (CEO) ไม่ใช่คุณบอส — แก้ D01–D11 แล้ว |
| Q5 | ใครเป็น PIC ฝั่ง Sales/Operations สำหรับ pricing, lead time และ Sales Script | `APPROVE-CEO` | D01, D02, D07, T06, T11, T12 | partial | 2026-08-24: Sales = แอน ธิกุล (active) / เจนจิรา มีดี (เดิม) จาก stg_doc; Operations ยังไม่ทราบ |
| Q6 | คุณปอนด์และคุณเซฟจะรับ task ใดหรือเป็นผู้ review ในรอบถัดไป | คุณเจี๊ยบ (CEO) | — | asked | ส่งในกลุ่ม 2026-08-23 — รอคำตอบ |
| Q7 | “น้องเชฟ” ใน C14 คือคุณเซฟหรือไม่ | ผู้เข้าร่วมประชุม | T09, D04 | asked | ส่งในกลุ่ม 2026-08-23 — รอคำตอบ |
| Q8 | แกน Collection แรกเป็น New Year ใช่หรือไม่ (ยืนยัน C06) | คุณเจี๊ยบ (CEO) | D08, T03 | asked | ส่งในกลุ่ม 2026-08-23 — รอคำตอบ |
| Q9 | 12 ลูกค้าบนหน้าเว็บ (GMMTV, กฟน., ONE BANGKOK ฯลฯ) เคยสั่งสินค้าอะไร มีรูปงานจริงไหม — SoT มีแค่ยอดเอกสาร | ทีมขาย / แอน | หน้าผลงานใน T03, DRF-2026-08-23#3.1 | open | — |
| Q10 | D09: ใช้ 4 Tier เป็นแกน Collection หลัก หรือคงเทศกาล หรือทั้งคู่ | คุณเจี๊ยบ (CEO) | D09, T03 | asked | ส่งกลุ่มพร้อม mockup 01 vs 01b 2026-08-23 — รอคำตอบ |
| Q11 | กล่องปัจจุบัน (มีแบบเดียว — fact 2026-08-24) คือรุ่นไหน ทุนเท่าไร; แผน sourcing กล่อง Drawer/Magnetic สำหรับ Tier | `PIC-BUSINESS` / จัดซื้อ | T05, D11, pricing worksheet | open | — |

สถานะที่ใช้: `open` → `asked` (ระบุวันที่ถาม) → `answered` (ระบุคำตอบและผู้ตอบ) → นำคำตอบไปอัปเดต PIC/Approver ใน §5–§6 และบันทึกใน CHANGELOG

**อัปเดต 2026-08-24:** เจ้าของงานยืนยันว่าผู้อนุมัติคือ **คุณเจี๊ยบ (CEO)** ไม่ใช่คุณบอส — D01–D11 และทุก task เปลี่ยนเป็น `APPROVE-CEO` แล้ว ดูหลักฐานประกอบใน [Q1–Q11 evidence answers](2026-08-24-q1-q11-evidence-answers.md)

## 8. Acceptance gate for this task document

เอกสารฉบับนี้ถือว่า ready for review เมื่อทุกข้อเป็น `met` — สถานะ ณ v0.1.1b:

| # | เกณฑ์ | สถานะ | หลักฐาน / สิ่งที่ยังขาด |
|---|---|---|---|
| G1 | ทุก task มี Goal, AC, SC, PIC และ Approver | partial | **Approver ปิดแล้วทุก task** = `APPROVE-CEO` (คุณเจี๊ยบ) ยืนยัน 2026-08-24 · เหลือ PIC ฝั่ง Operations (lead time/stock) ที่ยังไม่มีชื่อ — ปิดได้เมื่อ Q5 ครบ |
| G2 | ทุก task ที่อ้างว่าเป็นคำสั่งจากเสียงมี timecode | met | ทุก task มี Source clips ผูกกับ C01–C24 และช่วงเวลาใน §4 |
| G3 | งานที่เป็น inference ถูกทำเครื่องหมายว่าแตกงานเชิงระบบ | met | ใช้ป้าย `[EXPLICIT]` / `[INFERRED]` / `[DECISION]` ใน Command status ทุก task; T02 = INFERRED, T12/T13 = DECISION |
| G4 | ไม่ระบุชื่อ speaker จาก transcript เป็นข้อเท็จจริงโดยไม่มี diarization | met | §2.3 ใช้ role label; ชื่อบุคคลปรากฏเฉพาะเมื่อถูกเอ่ยถึงในเสียง ไม่ใช่ในฐานะผู้พูด |
| G5 | ไม่ยกระดับ budget, lead time, logo/color, แกน Collection หรือ scraping เป็นมติโดยไม่มี approval | met | D01, D02, D05, D08, T13; C06 แก้ถ้อยคำจาก “สรุป” เป็น “โน้มไป…ยังไม่ใช่มติ” |
| G6 | Owner/Approver gaps ถูกถามและปิดก่อนเริ่ม implementation | partial | **Q3/Q4 ปิดแล้ว** (ผู้อนุมัติ = CEO), Q5 partial (ได้ชื่อฝั่ง Sales จาก SoT) · ยังค้าง Q1, Q2, Q6, Q7, Q8, Q10, Q11 |

- [ ] G1 partial
- [x] G2 met
- [x] G3 met
- [x] G4 met
- [x] G5 met
- [ ] G6 partial (asked, รอคำตอบ)

## 9. Success criteria for the work package

หลังจาก owner และ approver ยืนยันแล้ว:

1. มี Product Catalog source ที่ trace ได้ถึง Excel/source row
2. มี taxonomy ที่ไม่ทำให้สี/ขนาดทุกตัวกลายเป็น Product ใหม่
3. มี Product Profile ที่เลือก Variant ได้
4. มี Bundle ที่อ้างอิง SKU และรองรับรายชิ้น/Set ในหน้าเดียวกัน
5. มี pricing/lead-time rules ที่อนุมัติแล้วและ AI ใช้ได้โดยไม่เดา
6. มี Business Facts/FAQ/Permission/Template ที่มี version และผู้อนุมัติ
7. มี Catalog mockup, Logo/Color direction และผลเลือกที่ตรวจสอบได้
8. มี deployment/data-access decision ก่อนเปิดให้คนอื่นใช้งาน

## 10. Non-goals

- ไม่ลบหรือยุบ SKU จากฐานข้อมูลเพียงเพื่อให้หน้า Catalog สั้นลง
- ไม่สร้างราคา final จากตัวเลข 20,000/25,000 โดยไม่มี pricing approval
- ไม่ให้ AI ตอบลูกค้าหรือยืนยันราคา/stock/lead time แบบไร้ human review
- ไม่ระบุชื่อผู้พูดจาก transcript เพียงอย่างเดียว
- ไม่เปิดระบบ local ให้บุคคลภายนอกก่อนผ่าน deployment, IAM และ data-access approval
- ไม่ scrape ข้อมูลภายนอกโดยถือว่าเสียงประชุมเป็น authorization
- ไม่ถือว่าแกน Collection (New Year/Christmas) เป็นมติจากเสียงช่วง 00:16 จนกว่า D08 จะอนุมัติ

## 11. Provenance

- STT: faster-whisper `large-v3`, CUDA `float16`, 1,063 segments
- Transcript average confidence: ประมาณ `0.5771`
- Speaker diarization: ไม่ได้ทำในรอบนี้
- Timecodes: อ้างอิง transcript ที่สร้างจากไฟล์เสียง 107.40 นาที; คำถอดบางช่วงมีความคลาดเคลื่อน จึงต้องเปิดเสียงยืนยันก่อนใช้เป็น legal/commercial commitment
- Related artifact: `minutes-content.json` — `.tmp-transcript/recording2-large-v3-20260822-r3/artifacts/minutes-content.json` (นอก repo)
- Related attribution note: `speaker-attribution-inferred.md` — `.tmp-transcript/recording2-large-v3-20260822-r3/artifacts/speaker-attribution-inferred.md` (นอก repo)

## 12. CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-23 | candidate | แตก task จาก Recording2 พร้อม timecode, Goal, AC, SC, PIC, Approver และ approval gaps | pending | ATHER |
| 0.2.1b | 2026-08-24 | candidate | T06: พบต้นทุนจริงใน `businesses/smartgift/source/drive/` (เดิมสรุปผิดว่าไม่มี) จับคู่ราคาขาย-ต้นทุน 797 รหัส กำไรจริง median 38% · เขียน pricing worksheet ใหม่เป็น v0.2.0b · ชี้ไปที่ pricing engine ที่มีอยู่แล้ว | pending | ATHER |
| 0.2.0b | 2026-08-24 | candidate | **เปลี่ยนผู้อนุมัติ D01–D11 และทุก task จาก `APPROVE-BOSS` เป็น `APPROVE-CEO` (คุณเจี๊ยบ)** ตามที่เจ้าของงานยืนยัน; เพิ่ม `COORD-BOSS`; ปิด Q3/Q4, Q5 เป็น partial | pending | ATHER |
| 0.1.9b | 2026-08-24 | candidate | ทำ F-3 ครบ 36 ไฟล์; เจอ+แก้บั๊ก 5 ข้อ (รหัสตัวอักษรเดียว, layout ราย page, ตารางราคาเดียว, encoding ไทย 2 ตระกูล, คอลัมน์สี); RCA เพิ่มภาคผนวกสำหรับส่งทีม pipeline | pending | ATHER |
| 0.1.8b | 2026-08-24 | candidate | T04: สร้างหน้า 02/03 จากข้อมูลจริง (แทน placeholder); RCA ข้อมูลราคาตกหล่น — พบ 39/39 ไฟล์ catalog lane ไม่มีราคา 2,292 SKU | pending | ATHER |
| 0.1.7b | 2026-08-24 | candidate | T01: ดึง gift set catalog 479 รายการ + รูป 459 เข้า staging (../scripts/extract_giftset_catalog.py); พบราคาผิดในใบราคาต้นฉบับ 38 รายการ | pending | ATHER |
| 0.1.6b | 2026-08-23 | candidate | เพิ่มหน้า 07 Package A/B/C × 3 สี (T05 AC2 ตัวอย่าง Bundle อ้างอิง SKU); Vercel redeploy 21 ภาพ; ส่งกลุ่มเคาะ D09 → Q10 `asked` | pending | ATHER |
| 0.1.5b | 2026-08-23 | candidate | เจน 01b landing แกน Tier × 3 สี เพื่อเทียบ D09; รับ input Campaign Architecture (4 กลุ่ม × 4 Tiers): map เข้า T02/T03, เพิ่ม D09–D11, ตรวจรหัส SKU กับ SoT | pending | ATHER |
| 0.1.4b | 2026-08-23 | candidate | Vercel deploy สำเร็จ (smartgift-catalog-mockup.vercel.app); เพิ่มหน้า 06 ผลงานและลูกค้า (3 ภาพ) ใช้เฉพาะข้อเท็จจริงจาก SoT; บันทึกว่าไม่มี line items ต่อลูกค้า → Q9 + DRF-2026-08-23#3.1 | pending | ATHER |
| 0.1.3b | 2026-08-23 | candidate | ส่งกลุ่มแล้ว: T10 AC4 ✅, §7 Q1–Q8 → `asked`, G6 → partial; เตรียม Vercel deploy folder (ยังไม่ deploy) | pending | ATHER |
| 0.1.2b | 2026-08-23 | candidate | T10: mockup 15 ภาพ (3 สี × 5 หน้า) + review page พร้อม; D05 ตัวเลือกพร้อม รอส่งกลุ่ม; เพิ่มแถว Progress/Artifacts/Caveats ใน T10 | pending | ATHER |
| 0.1.1b | 2026-08-23 | candidate | Review ตาม §8: เพิ่ม tag EXPLICIT/INFERRED/DECISION, แก้ C06 ไม่ให้เป็นมติ + เพิ่ม D08, ตัด dependency วน T05↔T06 และ T07↔T08, แยก PIC-CHEF/PIC-SAFE เป็นคำถาม Q7, §7 เป็นตาราง tracking Q1–Q8, §8 แสดงสถานะรายเกณฑ์ | pending | ATHER |
