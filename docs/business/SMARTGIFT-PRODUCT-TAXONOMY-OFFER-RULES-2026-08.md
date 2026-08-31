---
version: "0.1.1b"
created_at: "2026-08-13T01:28:11+07:00, ATHER, uncommitted"
last_update: "2026-08-13T01:37:23+07:00, ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "product-taxonomy-and-offer-rules"
  domain: "smartgift-marketing"
  scope: "controlled-pilot-product-classification-and-offer-assembly"
  artifact_id: "SG-PTOR-001"
  language: "th"
  parent_artifacts:
    - "SG-BPPA-001@0.1.1b"
    - "SG-GTM-001@0.1.1b"
---

# SmartGift Product Taxonomy & Offer Rules

## 0. สถานะ ขอบเขต และมติที่ต้องการ

| รายการ | ค่า |
|---|---|
| สถานะ | `beta` — Boss อนุมัติ Taxonomy model สำหรับ Controlled Pilot Planning; Readiness ของสินค้า ราคา Claim และ Partner ยังต้องผ่าน Owner gate รายมิติ |
| Parent architecture | `SMARTGIFT-BRAND-PRODUCT-PORTFOLIO-ARCHITECTURE-2026-08.md` v0.1.1b |
| Parent GTM | `SMARTGIFT-GO-TO-MARKET-PLAN-2026-08.md` v0.1.1b |
| ความซับซ้อน | C-2 — Documentation-Driven Classification |
| ความเสี่ยง | MEDIUM — การจัดประเภทผิดอาจทำให้เสนอราคา Claim, MOQ, Lead time หรือ Format ที่ยังไม่พร้อม |
| ใช้กับ | Controlled Pilot planning, Product readiness, Proposal assembly และ Content review |
| ไม่ใช่ | Database schema, Migration approval, Pricing policy, ERP/CRM implementation หรือ Public catalogue approval |

เอกสารนี้กำหนดภาษากลางและกฎสำหรับเปลี่ยนข้อมูลสินค้า/บริการที่กระจัดกระจายให้เป็นองค์ประกอบข้อเสนอที่ตรวจสอบได้ โดยไม่ทำให้ “พบสินค้าในแคตตาล็อก” กลายเป็น “พร้อมขาย” โดยอัตโนมัติ

**Approval record:** Boss ตอบ `approve` ใน Codex เมื่อ 2026-08-13 อนุมัติ Object model, Controlled vocabulary, Readiness model, Theme/Format/Tier rules และ Offer assembly rules สำหรับ Controlled Pilot Planning การอนุมัตินี้ไม่แต่งตั้ง Functional Owner, ไม่อนุมัติราคา/ต้นทุน/Claim/Partner/SKU รายการใด, ไม่อนุมัติ Migration หรือ Public catalogue และไม่ทำให้ Candidate ใดเป็น `QUOTE_READY` หรือ `SELL_READY` โดยอัตโนมัติ

มติระดับแบบจำลองที่อนุมัติแล้ว:

1. อนุมัติ Object model และ Controlled vocabulary
2. อนุมัติ Readiness states และ Gate requirements
3. อนุมัติกฎ Theme, Format และ Gift Tier eligibility
4. อนุมัติกฎประกอบ Offer Route และข้อเสนอหลาย Recipient Segment

มติที่ยังต้องดำเนินการแยก:

5. แต่งตั้ง Taxonomy Owner, Product Readiness Owner, Commercial Approver และ Claim Approver
6. ให้ Functional Owner ตรวจและรับรองกฎเชิงปฏิบัติของราคา Claim และ Voucher/Experience ก่อนใช้งานจริง
7. จัดทำ BRD/PRD และอนุมัติ Storage/Migration แยก หากจะนำ Taxonomy ไปสร้างระบบ

ไม่มีการแก้ฐานข้อมูล เว็บไซต์ แคตตาล็อก หรือราคาในรอบเอกสารนี้

---

## 1. ปัญหาที่เอกสารนี้แก้

Portfolio Architecture แยก Campaign, Recipient, Client Segment, Gift Tier, Theme และ Format แล้ว แต่หากไม่มี Product Taxonomy ทีมยังอาจตีความไม่ตรงกัน เช่น:

- สินค้า Power bank ถูกเรียกเป็น `Signature Tech` ทั้งที่ Signature เป็นระดับ Treatment ไม่ใช่หมวดสินค้า
- สินค้าที่มีชื่อใน PDF ถูกเสนอราคา ทั้งที่ราคา MOQ หรือ Lead time ยังไม่ผ่านการอนุมัติ
- Dining voucher ถูกจัดเป็น Food SKU ทั้งที่จริงเป็น `Taste` Theme และ `Voucher/Experience` Format
- สินค้าที่มีคำว่า ECO ถูกใช้ Claim รักษ์โลกโดยไม่มี Material/Certification evidence
- Gift Set หนึ่งชุดมี Tech, Care และ Taste ปนกัน แต่ฐานข้อมูลเดิมเก็บ Category เดียว
- ทีมขายใช้ราคา Estimate, ราคา Catalogue และราคา Quote ปะปนกัน
- สินค้าถูกย้ายหรือเปลี่ยนชื่อจน Source lineage ที่ Persist ไว้ไม่ตรง

เอกสารนี้จึงแยก 4 เรื่องออกจากกัน:

```text
Product identity
≠ Product classification
≠ Commercial readiness
≠ Campaign treatment
```

---

## 2. Live Data Baseline — ตรวจเมื่อ 2026-08-13

ผลจากการ Query `data/sot.duckdb` แบบ read-only:

### 2.1 Catalogue และ Price Records

| Dataset | สถานะที่พบ |
|---|---:|
| `catalog_sku` | 2,295 แถว |
| `catalog_sku.code` ไม่ซ้ำ | 1,995 ค่า |
| `catalog_sku` ที่มี `source_sha256` | 2,295 แถว |
| `price_staging` | 2,837 แถว จาก 40 Source files |
| MOQ ต่ำสุด/มัธยฐาน/สูงสุดใน `price_staging` | 1 / 20 / 1,000 |
| `price_staging.approved_at IS NOT NULL` | **0 แถว** |
| `price_staging.approved_at IS NULL` | **2,837 แถว** |

### 2.2 Category เดิมใน `stg_product`

| Category เดิม | จำนวนแถว |
|---|---:|
| Gift Set | 703 |
| ไม่มี Category | 519 |
| Other | 40 |
| Flash Drive | 32 |
| แอลกอฮอล์ | 14 |
| บรรจุภัณฑ์ | 4 |
| ECO | 2 |
| แฟลชไดร์ฟ/แฟลชไดร์ฟการ์ด | 4 |
| ค่าขนส่ง | 1 |

### 2.3 ข้อสรุปจาก Baseline

1. Category เดิมไม่ละเอียดพอสำหรับ Portfolio Model เพราะ Gift Set เป็นรูปแบบการจัดชุด ไม่ใช่ความสนใจของผู้รับ
2. Record ที่ไม่มี Category หรืออยู่ใน `Other` ต้องผ่าน Human classification ก่อนใช้ใน Pilot
3. ราคาใน `price_staging` ปัจจุบันเป็น Staging ทั้งหมดและไม่มี Approval record จึง **ห้ามถือเป็น Quote-ready price**
4. MOQ ระดับ 1 หรือค่าปลายสุด 1,000 ต้องตรวจ Context ต่อรายการ ห้ามนำ Min/Max ไปทำ Claim รวม
5. ตัวเลข Dataset เปลี่ยนได้ตามการ Ingest; Snapshot นี้ไม่แทน Migration ledger หรือ Audit report

> **Gate หลัก:** `catalogued ≠ concept ready ≠ quote ready ≠ sell ready`

---

## 3. Core Principles

### T1 — One product, multiple classifications

สินค้าหนึ่งรายการมี Primary Theme หนึ่งค่าและ Secondary Theme ได้ แต่ไม่จำเป็นต้องสร้าง SKU ใหม่ทุกครั้งที่นำไปใช้คนละ Campaign

### T2 — Gift Tier belongs to Treatment

Reach, Select, Signature และ Bespoke เป็นระดับการดูแลของ Treatment/Offer Route สินค้ามีได้เพียง `tier_eligibility` ไม่ได้มีตัวตนเป็น Signature โดยลำพัง

### T3 — Client Segment stays client-owned

Product Taxonomy ห้ามกำหนดว่าผู้รับเป็น VIP, Key Media หรือ Tier A การ Mapping นี้เกิดใน Campaign Recipient Matrix ที่ลูกค้าอนุมัติ

### T4 — Evidence before readiness

ทุก Readiness state ต้องอ้าง Source, Reviewer และเวลา ไม่มี Source หรือ Approval เท่ากับไม่ผ่าน Gate

### T5 — Price is time-bound

ราคาต้องมี Currency, Quantity/MOQ, Includes/Excludes, Validity, Source และ Approver ราคาเก่าหรือไม่มี Validity ไม่ใช่ราคา Current

### T6 — Claims are scoped

Claim ด้าน ESG, Health, Food, Safety, Origin, Community impact หรือ Certification ผูกกับ Item/Partner/Batch ที่มีหลักฐาน ไม่ใช้คำจากชื่อสินค้าแทนหลักฐาน

### T7 — Source paths are identity

Source file/path/SHA-256 เป็น Lineage identity ห้ามย้าย เปลี่ยนชื่อ หรือลบเพื่อจัด Taxonomy โดยไม่มี Dependency map, Migration plan และ Approval แยก

### T8 — Public simplicity, internal precision

ลูกค้าเห็นชื่อและตัวเลือกที่เข้าใจง่าย แต่ Record ภายในต้องเก็บสถานะและข้อจำกัดครบ

---

## 4. Canonical Object Model

### 4.1 Catalogue Product

หน่วยข้อมูลสินค้าจาก Supplier, Catalogue, Price file หรือ Transaction source

```text
CatalogueProduct
├─ identity
├─ provenance
├─ physical/functional attributes
├─ proposed classifications
└─ readiness dimensions
```

Catalogue Product อาจยังไม่พร้อมใช้ในข้อเสนอ

### 4.2 Offer Component

องค์ประกอบที่ผ่านเกณฑ์เพียงพอสำหรับใช้ใน Offer Route เช่น:

- Physical product
- Packaging
- Printed card/artwork
- Service เช่น personalization, assembly หรือ delivery
- Voucher/Experience entitlement

Offer Component ต้องมี Readiness state และ Scope ชัดเจน

### 4.3 Offer Route

แนวทางข้อเสนอหนึ่งแบบสำหรับ Recipient Segment หนึ่งกลุ่มหรือหลายกลุ่มที่มี Treatment เดียวกัน

```text
OfferRoute
├─ concept/message
├─ gift_tier
├─ primary_theme
├─ secondary_themes[]
├─ offer_format
├─ components[]
├─ commercial terms
├─ constraints
└─ approval/evidence
```

### 4.4 Campaign Treatment

การผูก Offer Route เข้ากับ Recipient Relationship และ Client-defined Segment ใน Campaign หนึ่ง

```text
CampaignTreatment
= Campaign
× Recipient Relationship
× Client-defined Segment
× Gift Tier
× Offer Route
```

### 4.5 Product Family

กลุ่มสินค้าที่มี Identity หรือรูปแบบร่วมกัน ใช้ช่วยค้นหาและจัดการ ไม่ใช่ Marketing Positioning เช่น:

- Power bank family
- Drinkware family
- Massage device family
- Gift box family
- Dining voucher family

---

## 5. Canonical Field Contract

Field contract นี้เป็น Logical contract สำหรับ Pilot ไม่ใช่คำสั่งสร้าง Table

### 5.1 Identity & Provenance

| Field | Type | Required | กฎ |
|---|---|---:|---|
| `product_ref` | string | yes | Stable internal reference; ห้ามใช้ Display name เป็น Identity |
| `business_id` | enum | yes | Pilot นี้ใช้ `smartgift`; ห้ามปนธุรกิจอื่น |
| `supplier_or_brand` | string | when known | แยก Supplier/Brand จาก Theme |
| `supplier_model_code` | string | when known | เก็บตาม Source ไม่ normalize จนสูญเสียความหมาย |
| `canonical_name` | string | yes | ชื่อภายในที่คนตรวจได้ |
| `display_name_th` | string | before public use | ผ่าน Copy review |
| `source_file` | path/string | yes | Workspace-relative identity ตาม Provenance contract |
| `source_sha256` | SHA-256 | yes | ต้องตรง Source bytes |
| `source_page_or_row` | string | when applicable | ตำแหน่งย้อนกลับ |
| `extraction_method` | enum | yes | `text`, `vision`, `manual`, `import` หรือค่าที่อนุมัติ |
| `source_observed_at` | datetime | yes | วันที่เห็นข้อมูล ไม่ใช่วันอนุมัติ |

### 5.2 Classification

| Field | Type | Required | กฎ |
|---|---|---:|---|
| `product_family` | controlled string | yes | กลุ่มเชิงสินค้า/ฟังก์ชัน |
| `primary_theme` | enum | yes before concept use | เลือกได้หนึ่งค่า |
| `secondary_themes` | enum[] | optional | รวมทั้งหมดไม่เกิน 3 Theme |
| `component_type` | enum | yes | `product`, `packaging`, `service`, `voucher`, `experience` |
| `tier_eligibility` | enum[] | yes before offer use | `reach`, `select`, `signature`, `bespoke` ตามเกณฑ์ |
| `occasion_fit` | enum[] | optional | ใช้แนะนำ ไม่ใช่ข้อห้ามถาวร |
| `recipient_notes` | string | optional | บอกข้อควรพิจารณา ห้ามกำหนด Client Tier |
| `prohibited_contexts` | string[] | when applicable | ข้อห้ามเชิงกฎหมาย ศาสนา อายุ สุขภาพ หรือ Policy |

### 5.3 Commercial

| Field | Type | Required for `QUOTE_READY` | กฎ |
|---|---|---:|---|
| `price_amount` | decimal | yes | ห้ามใช้ Float display โดยไม่มี Currency/rounding rule |
| `currency` | ISO currency | yes | เช่น THB |
| `price_basis` | enum | yes | `per_piece`, `per_set`, `per_entitlement`, `project_fee` |
| `quantity_from` | integer | yes | Quantity tier ที่ราคานี้ใช้ |
| `quantity_to` | integer/null | yes | null = ไม่มีเพดานที่ Source ระบุ |
| `moq` | integer | yes | มี Source/Context |
| `price_includes` | string[] | yes | เช่น printing/box/card |
| `price_excludes` | string[] | yes | VAT, shipping, artwork, sample ฯลฯ |
| `lead_time_value` | integer | yes | ห้ามเขียน “เร็ว” โดยไม่มีหน่วย |
| `lead_time_unit` | enum | yes | business/calendar days/weeks |
| `lead_time_basis` | string | yes | หลัง Artwork/Deposit/Approval ใด |
| `valid_from` | date | yes | วันที่เริ่มใช้ |
| `valid_until` | date | yes | หมดอายุแล้วต้อง Block Quote |
| `commercial_source_ref` | string | yes | Source + page/row/hash |
| `commercial_approved_by` | string | yes | ผู้มี Authority จริง |
| `commercial_approved_at` | datetime | yes | แยกจาก Extracted time |

### 5.4 Specification & Operations

| Field | Required for `SELL_READY` | ตัวอย่าง |
|---|---:|---|
| `approved_spec` | yes | Material, capacity, size, colour, model |
| `artwork_methods` | when branded | Screen, laser, UV, print area |
| `sample_requirement` | yes | none/digital/physical/production sample |
| `packaging_options` | yes | Standard, gift box, custom packaging |
| `qc_criteria` | yes | Visual/function/count/packaging checks |
| `warranty_or_support` | when applicable | Tech device/experience support |
| `fulfilment_modes` | yes | bulk, multi-location, named-recipient |
| `delivery_constraints` | when applicable | Battery, temperature, fragile, restricted item |
| `operations_owner` | yes | ผู้ยืนยันส่งมอบได้ |
| `operations_approved_at` | yes | เวลาที่อนุมัติ Scope นี้ |

### 5.5 Claims & Compliance

| Field | Required when claimed | กฎ |
|---|---:|---|
| `claim_id` | yes | Stable reference |
| `claim_text` | yes | ข้อความที่อนุญาตจริง ไม่ใช่คำกว้าง |
| `claim_scope` | yes | SKU, batch, supplier, partner, geography |
| `evidence_ref` | yes | Certificate/test/source/contract |
| `issuer` | yes | ใครออกหลักฐาน |
| `issued_at` | when present | วันที่ออก |
| `expires_at` | when applicable | หมดอายุแล้ว Block claim |
| `claim_approved_by` | yes | Brand/Legal/Product ตาม Authority |
| `claim_approved_at` | yes | Approval record |
| `required_disclaimer` | when applicable | ต้องมากับ Claim ทุกครั้ง |

### 5.6 Voucher/Experience

| Field | Required for `QUOTE_READY` | กฎ |
|---|---:|---|
| `partner_legal_name` | yes | ชื่อนิติบุคคล ไม่ใช่เพียงชื่อร้าน |
| `entitlement_description` | yes | ผู้รับได้สิทธิ์อะไร |
| `face_value` | when applicable | แยกจาก Cost/Sell price |
| `redemption_channel` | yes | code, app, branch, booking ฯลฯ |
| `valid_locations` | yes | สาขา/พื้นที่ที่ใช้ได้ |
| `expiry_rule` | yes | วันที่หรืออายุสิทธิ์ |
| `capacity_or_blackout` | when applicable | วันห้ามใช้/จำนวนจำกัด |
| `refund_transfer_rule` | yes | คืน/โอน/ทดแทนได้หรือไม่ |
| `support_owner` | yes | ใครช่วยผู้รับเมื่อใช้ไม่ได้ |
| `reconciliation_method` | yes | วิธีตรวจ issued/redeemed/expired |
| `tax_and_invoice_rule` | yes | Finance review |
| `data_shared` | yes | ข้อมูลใดส่งให้ Partner |
| `partner_contract_ref` | yes | Contract/DPA/terms ที่ Active |

---

## 6. Controlled Vocabulary

### 6.1 Themes

| Code | Display | Definition |
|---|---|---|
| `TECH` | Tech | เทคโนโลยี อิเล็กทรอนิกส์ การเชื่อมต่อ หรืออุปกรณ์ดิจิทัล |
| `CARE_WELLNESS` | Care & Wellness | การพักผ่อน สุขภาวะ และการดูแลตนเองโดยไม่อ้างผลรักษา |
| `TASTE` | Taste | อาหาร เครื่องดื่ม และประสบการณ์การกินดื่ม |
| `LIFESTYLE_TRAVEL` | Lifestyle & Travel | การใช้ชีวิต เดินทาง บ้าน และของใช้ประจำวัน |
| `IMPACT` | Impact | สิ่งแวดล้อม สังคม ชุมชน หรือ Ethical sourcing ที่มีหลักฐาน |
| `WORK_WELCOME` | Work & Welcome | การทำงาน โต๊ะทำงาน Onboarding และอุปกรณ์สำนักงาน |
| `CULTURE_LOCAL` | Culture & Local | อัตลักษณ์ งานคราฟต์ ศิลปะ วัฒนธรรม และท้องถิ่น |

ไม่เพิ่ม Theme ใหม่ผ่าน Sales copy โดยตรง ต้องผ่าน Taxonomy Owner และ Version bump

### 6.2 Component Types

| Code | ความหมาย |
|---|---|
| `PRODUCT` | สินค้าที่จับต้องได้ |
| `PACKAGING` | กล่อง ถุง Ribbon Card หรือ Packaging component |
| `SERVICE` | ออกแบบ สกรีน Personalization, Assembly, Fulfilment |
| `VOUCHER` | สิทธิ์ที่แทนมูลค่าหรือบริการและ Redeem ภายหลัง |
| `EXPERIENCE` | กิจกรรม/บริการที่ต้อง Booking หรือเข้าร่วม |

### 6.3 Offer Formats

| Code | Derivation rule |
|---|---|
| `PHYSICAL` | Components มี Product/Packaging/Service แต่ไม่มี Voucher/Experience |
| `VOUCHER_EXPERIENCE` | Route ส่งมอบสิทธิ์/ประสบการณ์โดยไม่มี Physical product หลัก |
| `HYBRID` | มี Physical และ Voucher/Experience ใน Route เดียว |

Offer Format เป็นค่าที่ Derive จาก Components ไม่ควรพิมพ์เองโดยไม่ตรวจส่วนประกอบ

### 6.4 Gift Tier Eligibility

| Code | ความหมาย |
|---|---|
| `REACH` | ทำซ้ำได้ คุมต้นทุน/คุณภาพได้ เหมาะกับจำนวนมากตาม Capacity จริง |
| `SELECT` | คัดและปรับตัวเลือกให้กลุ่มเฉพาะได้ในขอบเขตมาตรฐาน |
| `SIGNATURE` | ผ่าน Quality bar สูง รองรับ Curated presentation/Personalization ตาม Scope |
| `BESPOKE` | ต้องพัฒนาเฉพาะโครงการและผ่าน Design/Commercial/Operations review |

---

## 7. Theme Classification Rules

### 7.1 General Rule

1. Primary Theme สะท้อนเหตุผลหลักที่ผู้รับจะใช้หรือชื่นชอบ Component
2. Secondary Theme ต้องมีคุณค่าจริง ไม่ Tag เพื่อเพิ่ม Search reach
3. รวม Primary + Secondary ไม่เกิน 3 Theme
4. Gift Set ต้อง Classify จากองค์ประกอบและ Concept ไม่ใช้ `Gift Set` เป็น Theme
5. Packaging ไม่มี Theme โดยปริยาย เว้นแต่ Material/Design มีผลต่อ Concept และมีหลักฐาน

### 7.2 Tech

ใช้เมื่อฟังก์ชันหลักพึ่งพา Electronics, Digital connectivity หรือ Technology utility

ต้องตรวจเพิ่ม:

- Battery/capacity/spec
- Safety/certification ที่เกี่ยวข้อง
- Warranty/support
- Compatibility
- Transport restriction

### 7.3 Care & Wellness

ใช้กับการพักผ่อน Comfort, self-care หรือ well-being

ห้าม:

- อ้างรักษา ป้องกัน บำบัด หรือวินิจฉัยโรคโดยไม่มี Authority
- ใช้คำว่า Medical grade, ลดอาการ หรือดีต่อสุขภาพจากชื่อสินค้าเพียงอย่างเดียว

### 7.4 Taste

ใช้กับอาหาร เครื่องดื่ม Dining และ Culinary experience

ต้องตรวจ:

- อย./ใบอนุญาตที่เกี่ยวข้อง
- Ingredient/allergen
- Shelf life
- Storage/temperature
- Religious/dietary constraint
- Delivery geography

### 7.5 Lifestyle & Travel

ใช้เมื่อคุณค่าหลักอยู่ที่การใช้ชีวิต บ้าน การเดินทาง หรือ Personal accessory

คำว่า Lifestyle กว้าง จึงต้องระบุ Product family และ Use case เพิ่มเสมอ

### 7.6 Impact

ใช้ได้เมื่อมี Evidence อย่างน้อยหนึ่งประเภท:

- Material composition/certificate
- Recycled/recyclable scope ที่ระบุชัด
- Ethical/supply-chain certification
- Community producer/source agreement
- Impact statement ที่มี Method และ Owner

คำว่า `ECO`, สีเขียว หรือภาพธรรมชาติไม่ถือเป็น Evidence

### 7.7 Work & Welcome

ใช้กับอุปกรณ์ทำงาน Office utility หรือ Onboarding experience และผสม Tech/Lifestyle ได้

### 7.8 Culture & Local

ต้องมี Source, creator/community attribution และสิทธิ์ใช้ Design/Story ห้ามใช้ Cultural identity เป็นเพียง Decorative claim

---

## 8. Readiness State Model

### 8.1 States

```text
DISCOVERED
  ↓
CLASSIFIED
  ↓
CONCEPT_READY
  ↓
QUOTE_READY
  ↓
SELL_READY
  ↓
SUSPENDED / RETIRED
```

| State | ใช้ทำอะไรได้ | สิ่งที่ห้าม |
|---|---|---|
| `DISCOVERED` | Inventory และตรวจ Source | ห้ามใช้ใน Client concept/quote |
| `CLASSIFIED` | Search/analysis ภายใน | ห้ามแสดง Availability/price |
| `CONCEPT_READY` | ใช้เป็น Concept example พร้อม Caveat | ห้าม Quote หรือรับคำสั่งซื้อ |
| `QUOTE_READY` | ใช้สร้างข้อเสนอภายใน Validity/Scope | ห้ามรับ Order หาก Operations/Compliance ยังไม่ผ่าน |
| `SELL_READY` | ใช้ในข้อเสนอและรับ Order ตาม Approved scope | ห้ามใช้เกิน Quantity/validity/geography/claim scope |
| `SUSPENDED` | เก็บประวัติและเหตุผลหยุด | ห้ามเสนอใหม่ |
| `RETIRED` | Audit/ประวัติเท่านั้น | ห้าม Reactivate โดยไม่สร้าง Review ใหม่ |

### 8.2 State Transition Rule

- Transition ต้องมี `from`, `to`, `reason`, `evidence_refs`, `approved_by`, `approved_at`
- State ย้อนกลับได้เมื่อราคา หมดอายุ Supplier เปลี่ยน Evidence ถูกถอน หรือ Incident เกิด
- `QUOTE_READY` และ `SELL_READY` ไม่เป็นสถานะถาวร ต้อง Revalidate ตาม Validity
- การ Copy Record ห้าม Copy Approval โดยอัตโนมัติ

---

## 9. Readiness Dimensions

State รวมต้องไม่ปิดบัง Dimension ที่ยัง Fail

| Dimension | ค่าแนะนำ | Owner |
|---|---|---|
| Identity | unknown / verified / conflict | Taxonomy/Product |
| Provenance | missing / partial / complete | Data/Provenance |
| Classification | proposed / reviewed / approved | Taxonomy Owner |
| Specification | missing / draft / approved | Product/Sourcing |
| Commercial | missing / stale / current / approved | Finance/Commercial |
| Supplier | unverified / verified / active / suspended | Sourcing |
| Operations | unknown / feasible / approved / blocked | Operations |
| Claim | none / evidence-pending / approved / expired / rejected | Brand/Legal |
| Partner | not-applicable / pending / active / suspended | Commercial/Legal |
| Media asset | missing / internal-only / client-ready / public-approved | Marketing/Brand |

### 9.1 Aggregate State Rule

Aggregate state เท่ากับ Gate ต่ำสุดที่ Required dimensions ผ่าน ไม่ใช้ค่าเฉลี่ยหรือ Majority vote

ตัวอย่าง:

- Spec approved + Price missing = สูงสุด `CONCEPT_READY`
- Price current แต่ `approved_at` ไม่มี = ไม่เป็น `QUOTE_READY`
- Quote ready แต่ Operations blocked = ไม่เป็น `SELL_READY`
- Claim evidence expired = Claim route ถูก Block แม้ Product ขายแบบไม่ใช้ Claim อาจยังทำได้

---

## 10. Gate Requirements

### 10.1 `CLASSIFIED`

- Product identity และ Source reference มี
- Primary Theme, Product family และ Component type ถูกเสนอ
- Human reviewer ตรวจไม่ให้ Category เดิมถูก Copy แบบ Blind

### 10.2 `CONCEPT_READY`

- `CLASSIFIED` ผ่าน
- Identity/Provenance complete
- Spec ขั้นต่ำพออธิบายสินค้าโดยไม่ทำให้เข้าใจผิด
- Image/description มีสิทธิ์ใช้ในขอบเขต Internal/Client concept
- Availability/price แสดงเป็น `subject to confirmation`
- Prohibited context และ Claim risk ถูกระบุ

### 10.3 `QUOTE_READY` — Physical Product

- `CONCEPT_READY` ผ่าน
- Supplier active
- Approved spec
- Price, currency, quantity tier, MOQ และ includes/excludes ครบ
- `commercial_approved_by/at` มีค่า
- Validity ยังไม่หมด
- Lead-time basis มี
- Required certificate/transport condition มี
- Route-level packaging/service cost ถูกนับหรือ Exclude ชัด

**Current consequence:** `price_staging` 2,837 แถวที่ `approved_at` ว่างทั้งหมดไม่ผ่าน Gate นี้จากข้อมูลดังกล่าวเพียงอย่างเดียว

### 10.4 `SELL_READY` — Physical Product

- `QUOTE_READY` ผ่าน
- Operations feasibility approved
- Sample/proof rule agreed
- QC/packaging/fulfilment/delivery scope approved
- Warranty/support และ Exception owner มีเมื่อเกี่ยวข้อง
- Campaign-specific Artwork/Claim ผ่าน Gate

### 10.5 `QUOTE_READY` — Voucher/Experience

- Partner identity และ Active contract
- Entitlement, face value/cost/sell price ครบ
- Expiry, location, blackout, capacity และ refund/transfer rule ครบ
- Redemption/reconciliation/support flow approved
- Tax/invoice และ Data-sharing ผ่าน Review

### 10.6 `SELL_READY` — Voucher/Experience

- `QUOTE_READY` ผ่าน
- Issuance test และ Redemption test ผ่าน
- Failure/replacement/escalation path พร้อม
- Quantity/capacity ถูก Reserve หรือยืนยันตาม Contract
- Customer-facing terms และ support contact ถูกอนุมัติ

---

## 11. Gift Tier Eligibility Rules

Eligibility ระบุว่า Component เหมาะจะเป็นส่วนหนึ่งของ Treatment ใด ไม่ได้กำหนด Tier ของผู้รับ

### 11.1 Reach Eligibility

ต้องมี:

- Repeatable production/fulfilment
- Predictable price/MOQ/lead time
- QC ที่ทำซ้ำได้
- Branding/packaging มาตรฐาน
- Capacity เหมาะกับ Quantity จริง

### 11.2 Select Eligibility

ต้องมี:

- Choice/variation ที่คุมได้
- Theme fit ชัด
- Standard customization boundary
- Quote/operations process ที่ไม่ต้องพัฒนาใหม่ทั้งโครงการ

### 11.3 Signature Eligibility

ต้องมี:

- Quality/finish/spec ที่ตรวจได้
- Presentation/packaging ที่สอดคล้องกับ Campaign
- Personalization หรือ Curated composition ตาม Scope
- Sample/proof และ QC bar ที่สูงขึ้น
- Story/claim ที่มี Evidence หากใช้

ราคาแพงเพียงอย่างเดียวไม่ทำให้ผ่าน Signature eligibility

### 11.4 Bespoke Eligibility

หมายถึง Component/Service สามารถเข้าสู่ Bespoke development ได้ โดยต้องมี:

- Design/engineering feasibility
- IP/rights boundary
- Development fee/economics
- Revision/change control
- Prototype/sample plan
- Minimum timeline และ owner

Bespoke ไม่ควรถูก Tag เป็น Ready แบบถาวร; ทุกโครงการต้อง Review ใหม่

---

## 12. Offer Assembly Rules

### O1 — Start from approved Recipient Matrix

ห้ามสร้าง Route จากสินค้าแล้วค่อยเลือกผู้รับ ต้องมี Campaign, Relationship, Client Segment, Objective และ Gift Tier ก่อน

### O2 — Two routes by default

ข้อเสนอใช้ 2 Route เป็น Default และเพิ่ม Route ที่ 3 เฉพาะเมื่อมี Strategic difference จริง ห้ามเปลี่ยนเพียงสีหรือ SKU แล้วเรียกคนละ Route

### O3 — Theme coherence

- Route มี Primary Theme หนึ่งค่า
- Secondary Themes รวมแล้วไม่เกิน 3
- ทุก Component ต้องสนับสนุน Concept หรือ Functional need
- ห้าม Tag stuffing เพื่อให้ดูหลากหลาย

### O4 — Readiness by stage

| Sales stage | Minimum component state |
|---|---|
| Internal ideation | `CLASSIFIED` พร้อมเห็น Risk |
| Client concept | `CONCEPT_READY` |
| Proposal with price | `QUOTE_READY` |
| Order acceptance/production | `SELL_READY` |

### O5 — Shared campaign layer

หลาย Gift Tier ใน Campaign เดียวต้องมีองค์ประกอบร่วมตามที่เหมาะสม:

- Campaign message
- Visual/colour family
- Packaging cues
- Approval timeline
- Delivery milestone

ความต่างของ Tier ควรเกิดจาก Treatment depth ไม่ใช่ทำให้ดูเป็นคนละแบรนด์

### O6 — No automatic VIP inference

ราคา ประวัติซื้อ หรือ Profile ห้ามถูกใช้กำหนด Client Segment โดย SmartGift หากลูกค้าไม่ได้ให้ Definition/Mapping

### O7 — Hybrid is fail-closed

Route ที่มี Voucher/Experience ต้องผ่าน Partner Gate ทั้งหมด หากไม่ผ่านต้องเสนอ Physical alternative หรือถอด Route ไม่ใช้ Placeholder entitlement

### O8 — Constraints before aesthetics

Budget, quantity, required-by date, delivery, regulation และ Recipient restrictions ต้องผ่านก่อนเลือก Packaging/Story ที่สวยงาม

### O9 — No hidden costs

Proposal ต้องระบุว่า Price รวม/ไม่รวม VAT, Shipping, Printing, Box, Card, Artwork, Sample, Personalization และ Project fee อย่างไร

### O10 — Proposal traceability

ทุก Component ใน Route ต้อง Trace ไปยัง Product ref, Source, Readiness evidence และ Price validity ได้

---

## 13. Naming Rules

### 13.1 Customer-facing Offer Name

```text
SmartGift [Gift Tier] — [Theme or Campaign Edition]
```

ตัวอย่าง:

- SmartGift Select — Member Welcome
- SmartGift Signature — Care × Taste
- SmartGift Signature — Key Media Edition
- SmartGift Bespoke — Executive Experience

ห้ามใช้ชื่อนี้เพื่อหลบ Readiness เช่นตั้ง `Signature` ให้สินค้าที่ไม่มี Quality/operations evidence

### 13.2 Internal IDs

| Object | Pattern ตัวอย่าง |
|---|---|
| Campaign | `SGC-YYYYMM-####` |
| Treatment | `{campaign_id}-T##` |
| Offer Route | `{treatment_id}-R#` |
| Component | `{route_id}-C##` |
| Claim | `SGCL-####` |
| Readiness decision | `SGRD-YYYYMMDD-####` |

ID pattern เป็น Proposal และต้องผ่านระบบ/ข้อมูล Review ก่อน Implementation

### 13.3 Product Display Name

ชื่อภายนอกควรประกอบจาก:

```text
[Functional name] + [Meaningful differentiator] + [Model when needed]
```

หลีกเลี่ยง:

- Keyword stuffing
- Claim ที่ไม่มี Evidence
- ชื่อ Supplier ภายในที่ไม่มีสิทธิ์ใช้
- “Premium”, “Eco”, “Medical”, “Luxury” เป็นคำอัตโนมัติ

---

## 14. Pricing & Commercial Rules

### 14.1 Price Types

| Type | ใช้ที่ไหน | กฎ |
|---|---|---|
| `SOURCE_PRICE` | Evidence/Staging | ห้ามแสดงลูกค้าโดยอัตโนมัติ |
| `ESTIMATE` | Early concept | ต้องมี Range, assumption และ disclaimer |
| `APPROVED_QUOTE_PRICE` | Proposal | มี Approver, validity, quantity และ inclusions |
| `ORDER_PRICE` | Accepted commercial record | ต้องตรงเอกสารสั่งซื้อ/อนุมัติจริง |

### 14.2 MOQ Rules

- MOQ ผูกกับ Supplier/model/customization/quantity tier
- ห้ามใช้ MOQ ต่ำสุดของ Dataset เป็น Claim ของทั้ง Portfolio
- คำว่า “เริ่ม 10 ชุด” ใช้เฉพาะรายการ/Route ที่ผ่าน Quote gate ตามจำนวนดังกล่าว
- Candidate copy “5–10 ชิ้น” ต้อง Block หากไม่มี Approved source ต่อ Route

### 14.3 Margin Boundary

- ไม่มี Approved cost = ห้ามคำนวณ Margin
- `buy_price = 0` ไม่ได้แปลว่า Cost เป็นศูนย์
- Cost workbook ที่อยู่ใน Migration ledger สถานะ pending ต้องมี Schema/CR แยกก่อนใช้เป็น Cost authority
- Pilot ต้องเก็บ Design, Sample, Rework, Packaging, Shipping และ Labor cost แยกจาก Product cost

### 14.4 Validity

หมด `valid_until` แล้ว State ต้องลดจาก `QUOTE_READY` จนกว่า Commercial approval ใหม่จะเสร็จ

---

## 15. Claim & Content Rules

### 15.1 Claim Classes

| Class | ตัวอย่าง | Approver |
|---|---|---|
| Product fact | ความจุ วัสดุ ขนาด | Product/Sourcing |
| Commercial | MOQ ราคา Lead time | Commercial/Finance |
| Quality/safety | Certification, warranty | Product/Legal ตามความเสี่ยง |
| ESG/Impact | Recycled content, community impact | Legal/Brand/Product |
| Health/Wellness | Comfort/self-care wording | Legal/Brand |
| Food | Ingredient, allergen, shelf life | Product/Legal |
| Partner/Voucher | locations, expiry, entitlement | Commercial/Legal |
| Social proof | Client logo, case study, volume | Client permission + Brand/Legal |

### 15.2 Claim Lifecycle

```text
PROPOSED → EVIDENCE_ATTACHED → REVIEWED → APPROVED
                              ↘ REJECTED
APPROVED → EXPIRED / REVOKED / SUPERSEDED
```

Public content ใช้เฉพาะ `APPROVED` และ Scope ต้องตรงกับ Media/Channel/Period

### 15.3 Image Rules

ภาพสินค้าใน Catalogue ไม่เท่ากับมีสิทธิ์นำไปโฆษณา ต้องระบุ:

- Image source
- Owner/license/permission
- Allowed channel
- Editing restriction
- Expiry เมื่อมี
- Product/model match

---

## 16. Example Mappings

ตัวอย่างเหล่านี้เป็น Logic example ไม่ใช่สินค้าพร้อมขาย

### 16.1 Power bank สำหรับ Welcome Kit

```text
product_family: POWER_BANK
primary_theme: TECH
secondary_themes: [WORK_WELCOME]
component_type: PRODUCT
tier_eligibility: [SELECT]  # Signature ต้องผ่าน quality/presentation review เพิ่ม
readiness: CLASSIFIED หรือสูงกว่าตาม Evidence จริง
```

### 16.2 Wellness Gift Set

```text
components:
  - massage/comfort device → CARE_WELLNESS
  - drinkware → LIFESTYLE_TRAVEL หรือ CARE_WELLNESS ตาม Concept
  - packaging → PACKAGING
offer_format: PHYSICAL
```

คำว่า Wellness ไม่อนุญาต Medical claim

### 16.3 Dining Voucher

```text
component_type: VOUCHER
primary_theme: TASTE
offer_format: VOUCHER_EXPERIENCE
```

จะเป็น `QUOTE_READY` ได้เมื่อ Partner contract, expiry, locations, redemption, reconciliation, tax และ support ครบ

### 16.4 Signature Care × Taste Hybrid

```text
gift_tier: SIGNATURE        # อยู่ที่ Offer Route
primary_theme: CARE_WELLNESS
secondary_themes: [TASTE]
components:
  - curated physical set
  - dining/spa entitlement
offer_format: HYBRID
```

Physical และ Partner components ต้องผ่าน Gate ของตนเองทั้งคู่

### 16.5 ECO-labelled Catalogue Item

```text
source_name_contains: ECO
primary_theme: pending human review
impact_claim_status: EVIDENCE_PENDING
```

ชื่อ `ECO` ไม่ทำให้ Primary Theme เป็น `IMPACT` และไม่อนุญาต Public claim

---

## 17. Taxonomy Review Workflow

### Step 1 — Intake

รับ Candidate จาก Catalogue/Price/Supplier/Transaction พร้อม Source path/hash/page/row

### Step 2 — Identity Resolution

ตรวจ Code/model/name/brand/source ว่าเป็นสินค้าเดียวกัน Variant หรือ Conflict ห้าม Merge จากชื่อคล้ายเพียงอย่างเดียว

### Step 3 — Classification Proposal

เสนอ Product family, Theme, Component type, eligibility และ restrictions

### Step 4 — Human Review

Taxonomy Owner อนุมัติ Classification; Product/Sourcing ตรวจ Spec/identity

### Step 5 — Readiness Review

แต่ละ Owner อนุมัติ Dimension ของตน ไม่ให้คนเดียว Self-approve ทุกเรื่อง

### Step 6 — Offer Use

Campaign Lead เลือกเฉพาะ Components ที่ State พอกับ Sales stage

### Step 7 — Expiry/Revalidation

Price, supplier, claim, partner, image rights และ operations evidence ถูกตรวจตาม Validity/Trigger

---

## 18. Quality Checks

### 18.1 Record-level Checklist

- [ ] Product ref stable
- [ ] Business ID ถูกต้อง
- [ ] Source path/hash/page/row ครบ
- [ ] Code/model conflict ถูกแก้หรือระบุ
- [ ] Primary Theme หนึ่งค่า
- [ ] Theme รวมไม่เกิน 3
- [ ] Component type ถูกต้อง
- [ ] Gift Tier เป็น eligibility ไม่ใช่ Recipient identity
- [ ] Commercial data มี Authority/validity หากใช้
- [ ] Claims มี Evidence/approval
- [ ] Restrictions มีเมื่อเกี่ยวข้อง
- [ ] State ตรงกับ Dimension ที่ต่ำสุด

### 18.2 Offer-level Checklist

- [ ] มี Approved Recipient Matrix
- [ ] Route แตกต่างเชิง Strategy จริง
- [ ] Components ทุกชิ้นผ่าน State ตาม Sales stage
- [ ] Theme/format สอดคล้องกับ Components
- [ ] Price/MOQ/includes/excludes/validity ครบ
- [ ] Claim/Artwork/Image rights ผ่าน
- [ ] Operations/Delivery feasibility ผ่าน
- [ ] Voucher/Experience ผ่าน Partner Gate หากมี
- [ ] Proposal trace กลับ Source ได้

### 18.3 Automated Checks ที่เสนอสำหรับอนาคต

ยังไม่ Implement ในรอบนี้:

- Reject `QUOTE_READY` เมื่อ Commercial approval/validity ขาด
- Reject `IMPACT` เมื่อไม่มี Active claim evidence
- Reject `HYBRID` เมื่อไม่มี Active Partner component
- Reject Offer ที่ Theme เกิน 3
- Reject Public asset ที่ Claim/Image approval ขาด
- Reject Price ที่ Quantity ต่ำกว่า MOQ
- Warn Source identity conflict จาก Code/name/hash

---

## 19. Governance และ Change Control

### 19.1 Roles

| Role | Authority |
|---|---|
| Taxonomy Owner | Vocabulary, classification และ version |
| Product Readiness Owner | Identity, spec, supplier และ product feasibility |
| Commercial Approver | Price, MOQ, validity และ commercial terms |
| Operations Approver | QC, fulfilment, delivery และ capacity |
| Claim Approver | Claim/evidence/disclaimer/expiry |
| Partner Approver | Voucher/experience contract และ operations |
| Campaign Owner | ใช้ Approved components ประกอบ Route |

### 19.2 Separation of Duties

- ผู้ Extract ข้อมูลไม่อนุมัติ Commercial readiness ด้วยตนเองโดยปริยาย
- Sales ไม่ยกระดับ State เพื่อให้ส่ง Quote ทัน
- Marketing ไม่อนุมัติ Supplier spec หรือ Cost
- Product/Sourcing ไม่อนุมัติ Public legal claim โดยลำพังเมื่อมีความเสี่ยง

### 19.3 Versioning

| Change | Version impact |
|---|---|
| แก้คำอธิบาย/ตัวอย่าง | Patch |
| เพิ่ม Theme/State/Required field/rule | Minor |
| เปลี่ยน Object model หรือลบ/rename semantic | Major |

ทุก Record ที่ใช้ใน Campaign ควรอ้าง Taxonomy version เพื่อ Reproduce การตัดสินใจได้

---

## 20. Pilot Adoption Plan

### Phase A — Dry Classification

คัด Candidate ให้พอสร้างอย่างน้อย 2 Route สำหรับแต่ละ GTM Play โดยไม่ย้าย Source และไม่แก้ Production DB

ตรวจ:

- Classification agreement
- Evidence gaps
- Readiness bottleneck
- เวลาที่ใช้ต่อ Record

### Phase B — Offer Simulation

ใช้ Scenario สมมติ 3 แบบจาก GTM ทำ Recipient Matrix และ Offer Routes

ตรวจ:

- State gate ทำงานเชิงกระบวนการหรือไม่
- Route อธิบายง่ายหรือซับซ้อนเกินไป
- Missing price/spec/claim ถูกเปิดเผยหรือถูกซ่อน

### Phase C — Controlled Pilot Use

หลัง GTM Owner/Budget/Account list พร้อม ใช้ Taxonomy กับบัญชีที่อนุมัติ และเก็บ:

- Components selected/rejected
- Gate failure reason
- Quote revision
- Feasibility time
- Claim/operations exception

### Phase D — Implementation Decision

ตัดสินว่าจะเก็บ Taxonomy ใน File, Database, CRM หรือ Product service จาก Evidence Pilot ผ่าน BRD/PRD ใหม่ ห้ามถือ Logical contract นี้เป็น Schema implementation โดยอัตโนมัติ

---

## 21. In Scope / Out of Scope

### In Scope

- Vocabulary และ Object model
- Logical fields
- Theme/Format/Tier eligibility
- Readiness states/dimensions/gates
- Offer assembly/naming/pricing/claim rules
- Review workflow และ QA checklist
- Pilot adoption plan

### Out of Scope

- Classify/approve SKU ทั้งหมด
- Import cost workbooks
- Approve `price_staging` rows
- เปลี่ยน DuckDB schema หรือ source files
- สร้าง API/UI/Configurator
- แก้ Copy เว็บไซต์หรือ Deploy
- เปิด Voucher/Experience partner
- อนุมัติ ESG/Health/Food claim จริง
- กำหนด Margin/Price policy

---

## 22. Acceptance, Success และ Exit Criteria

### 22.1 Acceptance Criteria

- ทุกทีมแยก Product, Component, Route และ Treatment ได้ตรงกัน
- Signature ถูกใช้เป็น Gift Tier/Treatment เท่านั้น
- Theme และ Format ไม่ถูกปะปน
- Readiness State มี Required evidence และ Owner ชัด
- `price_staging` ที่ไม่ Approved ไม่ผ่าน `QUOTE_READY`
- Impact/Voucher/Health/Food มี Gate เฉพาะ
- Source path/hash lineage ถูกเก็บและไม่ถูกย้ายเพื่อจัดหมวด

### 22.2 Success Criteria ของ Dry Run

- สร้าง 2 Route ต่อ GTM Play ได้จาก Candidate ที่ตรวจแล้ว หรือรายงาน Gap อย่างตรงไปตรงมา
- Reviewer สองคนจัด Classification ตรงกันหรือ Resolve disagreement ด้วย Rule ได้
- ไม่มี Component ต่ำกว่า Required state หลุดเข้า Proposal simulation
- ทุก Price/Claim/Restriction Trace กลับ Evidence ได้
- Unknown ถูกแสดงเป็น Unknown ไม่ถูกเติมเพื่อให้ข้อเสนอดูสมบูรณ์

### 22.3 Exit Criteria ก่อน Implementation

- Taxonomy v0.1 ได้รับอนุมัติ — ผ่านระดับ Strategic model เมื่อ 2026-08-13
- Owner ทุกบทบาทได้รับการแต่งตั้ง
- Dry classification และ Offer simulation ผ่าน
- Storage/authority/privacy/versioning requirements ถูกเขียนใน BRD/PRD
- Migration impact ต่อ `catalog_sku`, `price_staging`, `product_master` และ Consumers ถูกวิเคราะห์
- Rollback และ Rebuild path ได้รับอนุมัติ

---

## 23. Decision Record

| ID | Decision | Owner | Status |
|---|---|---|---|
| `TAX-D01` | Canonical object model | Marketing + Product | Approved for Pilot Planning — Boss, 2026-08-13 |
| `TAX-D02` | Theme vocabulary | Marketing/Brand | Approved for Pilot Planning — Boss, 2026-08-13 |
| `TAX-D03` | Format/component vocabulary | Product + Operations | Strategic model approved; operational validation pending |
| `TAX-D04` | Readiness states and gates | Product + Sales + Operations + Finance | Strategic model approved; gate-owner validation pending |
| `TAX-D05` | Gift Tier eligibility | Marketing + Sales + Product | Approved for Pilot Planning — Boss, 2026-08-13 |
| `TAX-D06` | Pricing/validity rules | Finance/Commercial | Control model approved; Finance/Commercial validation pending |
| `TAX-D07` | Claim rules | Brand + Legal/Compliance | Control model approved; Claim/Legal validation pending |
| `TAX-D08` | Voucher/Experience fields | Commercial + Legal + Operations | Control model approved; Partner/Operations validation pending |
| `TAX-D09` | Taxonomy Owner | Founder/MD | Pending |
| `TAX-D10` | Future storage/implementation | Technical/Data authority | Deferred to BRD/PRD |

---

## 24. แหล่งอ้างอิง

### Parent documents

- `docs/SMARTGIFT-BRAND-PRODUCT-PORTFOLIO-ARCHITECTURE-2026-08.md` v0.1.1b
- `docs/SMARTGIFT-GO-TO-MARKET-PLAN-2026-08.md` v0.1.1b

### Data/evidence

- `data/sot.duckdb`: `catalog_sku`, `stg_product`, `price_staging`, `product_master`
- `data/provenance/source_registry.jsonl`
- `docs/competitive-brief-thailand-2026-08.md`
- `docs/raw-business-file-dependency-map-2026-08-09.md`

Snapshot counts in this document were queried on 2026-08-13 and may drift after ingest. Re-query and reconcile with Migration ledger before implementation or public claim.

---

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.1b | 2026-08-13 | beta | Boss อนุมัติ Taxonomy model สำหรับ Pilot Planning; คง Functional Owner, readiness รายสินค้า, ราคา, Claim, Partner และ Storage/Migration เป็น pending | uncommitted | ATHER |
| 0.1.0b | 2026-08-13 | draft | กำหนด Product/Offer taxonomy, readiness states, evidence gates, tier eligibility, offer assembly, pricing/claim rules และ Pilot adoption plan | uncommitted | ATHER |
