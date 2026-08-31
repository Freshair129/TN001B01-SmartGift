---
version: "0.1.1b"
created_at: "2026-08-13T01:21:14+07:00, ATHER, uncommitted"
last_update: "2026-08-13T01:28:11+07:00, ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "go-to-market-plan"
  domain: "smartgift-marketing"
  scope: "controlled-pilot-market-entry"
  artifact_id: "SG-GTM-001"
  language: "th"
  parent_artifact: "SG-BPPA-001@0.1.1b"
---

# SmartGift Go-to-Market Plan — Recipient-first Portfolio

## 0. สถานะ ขอบเขต และมติที่ต้องการ

| รายการ | ค่า |
|---|---|
| สถานะ | `beta` — Boss อนุมัติ GTM model สำหรับ Controlled Pilot Planning; Pilot Execution ยังรอ Owner, Budget และ Account list |
| Parent authority | `SMARTGIFT-BRAND-PRODUCT-PORTFOLIO-ARCHITECTURE-2026-08.md` v0.1.1b |
| ความซับซ้อน | C-2 — Documentation-Driven Execution |
| ความเสี่ยง | MEDIUM — กระทบข้อความตลาด วิธีขาย การคัดบัญชี ข้อเสนอ และการวัดผล แต่ยังไม่อนุญาต Public Rollout |
| ระยะเวลา | Controlled Pilot 90 วันหลังแต่งตั้ง Owner และอนุมัติงบ |
| Primary market | B2B Corporate Gifting ในประเทศไทย |
| Working offer name | `SmartGift Multi-Audience Campaign` |

เอกสารนี้แปลง Portfolio Architecture ที่ Boss อนุมัติแล้วให้เป็นแผนเข้าตลาดแบบควบคุม โดยเน้นลูกค้าเดิมและลูกค้าอุ่นก่อนการสร้าง Awareness ในวงกว้าง

**Approval record:** Boss ตอบรับ GTM Plan ใน Codex เมื่อ 2026-08-13 การอนุมัตินี้ครอบคลุม Beachhead, Account priority, Pilot Plays, Messaging, Funnel และ Measurement model แต่ไม่แต่งตั้ง Owner, ไม่อนุมัติงบ, ไม่อนุมัติรายชื่อบัญชีติดต่อ และไม่อนุญาต Public Rollout

มติระดับกลยุทธ์ที่ Boss อนุมัติเมื่อ 2026-08-13:

1. อนุมัติ Beachhead Market และลำดับ Account Priority
2. อนุมัติ 3 Pilot Plays และ Messaging Hierarchy
3. อนุมัติ Funnel, Stage Gate และ Measurement Contract

Activation Gate ที่ยังรอ:

4. แต่งตั้ง Pilot Owner, Account Owner, Product Readiness Owner และ Analytics Owner
5. อนุมัติงบและทรัพยากรสำหรับ Pilot โดยแยกจากงบ Full Rollout

เอกสารนี้ไม่อนุมัติการแก้เว็บไซต์ การยิงโฆษณา การติดต่อบัญชีจริง การซื้อสต็อก การทำ Voucher Partnership หรือการเผยแพร่ Claim โดยอัตโนมัติ

---

## 1. Executive Summary

### 1.1 เป้าหมายเชิงกลยุทธ์

ใน 90 วันแรก SmartGift ไม่ควรพยายาม “เป็นที่รู้จักในตลาดทั้งหมด” แต่ควรพิสูจน์ 3 เรื่องให้ได้ก่อน:

1. ลูกค้าองค์กรเข้าใจและเห็นคุณค่าของการเริ่มจาก Recipient Matrix หรือไม่
2. ฝ่ายขายสามารถเปลี่ยน Brief เดียวเป็นข้อเสนอหลายกลุ่มผู้รับได้เร็วและแม่นขึ้นหรือไม่
3. Product/Sourcing/Operations สามารถส่งมอบหลาย Gift Tier โดยไม่ทำให้ต้นทุน ความเสี่ยง และ Revision หลุดการควบคุมหรือไม่

### 1.2 GTM Thesis

> SmartGift จะชนะช่วง Pilot ด้วยความสัมพันธ์เดิมและความสามารถจัดข้อเสนอให้ตรงหลายกลุ่มผู้รับ ไม่ใช่ด้วยการเพิ่มจำนวน SKU หรือซื้อ Paid Reach ขนาดใหญ่

เหตุผลจากหลักฐานภายใน:

- ลูกค้าที่เคยซื้อมีอัตราชนะในข้อมูลย้อนหลัง 52.1% เทียบกับ 3.2% สำหรับกลุ่มที่ยังไม่เคยซื้อ
- มีลูกค้าเงียบเกิน 12 เดือน 468 ราย โดยมีช่องทางติดต่อ 349 ราย
- กลุ่ม Active และ Quiet 6–12 เดือนรวม 79 บัญชี เป็นฐานที่ควรรักษาก่อนหาลูกค้าใหม่กว้าง ๆ
- ใบเสนอราคาจำนวนมากจบแบบไม่มีการตอบกลับ จึงต้องแก้ Follow-up และ Stage discipline พร้อมกับเปลี่ยนข้อเสนอ
- ฐานะการเงินทำให้แผนที่ใช้เงินต่ำและเห็นสัญญาณภายในหนึ่งไตรมาสเหมาะกว่าการซื้อ Awareness ขนาดใหญ่

ข้อมูลข้างต้นมาจาก `competitive-brief-thailand-2026-08.md` และ SoT ที่มีข้อมูลถึง 2026-06-22 ใช้ภายในเพื่อจัดลำดับงาน ห้ามใช้เป็น Public Claim โดยไม่มีการตรวจซ้ำ

### 1.3 Beachhead Strategy

เริ่มจาก 3 Use Case ที่ Portfolio Model แสดงคุณค่าได้ชัด:

1. **Customer & Member Appreciation** — หลาย Segment ภายใต้โปรแกรมเดียว
2. **Launch/Event with Media** — Media, Creator, Guest และ Member ใน Campaign เดียว
3. **Employee Welcome & Recognition** — Staff, Manager และ Leadership ต่างระดับ

### 1.4 ช่องทางหลัก

1. Account-based Outreach ไปยังลูกค้าเดิมและลูกค้าอุ่น
2. Discovery ผ่านโทรศัพท์และ LINE โดยใช้ข้อมูลตามสิทธิ์
3. Owned Website/Content สำหรับช่วยอธิบายและรับ Brief
4. Case Study และ Referral หลังมี Pilot Evidence
5. ยังไม่ใช้ Paid Media ขนาดใหญ่จนรู้ Conversion, Cost-to-serve และ CAC baseline

---

## 2. Decision Inheritance จาก Portfolio Architecture

แผนนี้ต้องรักษาการตัดสินใจที่อนุมัติแล้ว:

| Decision | ผลต่อ GTM |
|---|---|
| One Master Brand | ทุก Campaign ใช้ SmartGift เป็น Master Brand ไม่มี Tech/Care/Taste แยกเป็นแบรนด์อิสระ |
| Recipient-first | Discovery เริ่มจาก Campaign และ Recipient ไม่เริ่มจากรายการสินค้า |
| Client-defined Segment | ใช้ชื่อ Tier/Segment ของลูกค้าตามจริง ไม่ตั้งชื่อแทน |
| Gift Tier | Reach, Select, Signature และ Bespoke เป็นระดับการดูแล ไม่ใช่ประเภทผู้รับ |
| Flexible Themes | Tech, Care, Taste, Lifestyle, Impact, Work และ Culture ผสมได้ตาม Guardrail |
| Format boundary | Physical, Voucher/Experience และ Hybrid เป็นคนละรูปแบบการส่งมอบ |
| Evidence before claim | ไม่มีหลักฐาน = ไม่มี Claim และไม่มีข้อเสนอที่ทำให้ลูกค้าเข้าใจว่า Ready |

หาก GTM Experiment ใดต้องเปลี่ยนความหมายข้างต้น ต้องเปิด Revision ของ Parent Architecture ก่อน ไม่แก้ความหมายผ่าน Sales Script หรือ Campaign Copy โดยลำพัง

---

## 3. Market Reality และข้อจำกัด

### 3.1 สิ่งที่ SmartGift มีอยู่แล้ว

- เว็บไซต์มีสินค้าใส่โลโก้และบริการ Custom Corporate เป็นสองทางเข้า
- เว็บไซต์รับ Brief จากงบ จำนวน กลุ่มผู้รับ และเป้าหมาย
- มีหมวดสินค้า Tech, Health/Wellness, Office, Bag และ Gift Set ให้ลูกค้าเข้าใจเบื้องต้น
- มี SoT, ประวัติลูกค้า ใบเสนอราคา และข้อมูลแคตตาล็อกสำหรับทำ Account-based work ภายใน
- มี Gift Set และ MOQ ต่ำในสินค้าบางรายการเป็นหลักฐานสนับสนุนแนวคิด

### 3.2 สิ่งที่ยังไม่พร้อม

- ราคาปัจจุบันและต้นทุนรายสินค้ายังไม่ครบพอสำหรับสร้าง Price/Margin Tier มาตรฐาน
- Impact/ESG assortment และหลักฐานยังไม่พอสำหรับใช้เป็น Positioning หลัก
- Voucher/Experience partner, Contract, Redemption และ Reconciliation ยังไม่ได้รับการยืนยัน
- ยังไม่มี Baseline ว่า Recipient Matrix ลดเวลาขายหรือเพิ่ม Conversion เท่าใด
- Industry classification ของลูกค้าจำนวนมากยังไม่สมบูรณ์ จึงไม่ควรเทงบตาม Industry สมมติ
- Pilot Owner, Budget และ Cross-functional operating cadence ยังไม่ได้แต่งตั้ง

### 3.3 ภูมิทัศน์ข้อความคู่แข่ง

จากการตรวจเว็บไซต์สาธารณะเมื่อ 2026-08-13:

- ผู้เล่นด้าน Eco ใช้ Sustainable Product, MOQ ต่ำ และความเร็วเป็นแกนข้อความ
- ผู้เล่นงานคราฟต์เสนอชุดของขวัญออกแบบได้และเริ่มขั้นต่ำระดับ 10 ชุด
- ผู้เล่น Corporate Gift Set อธิบายการคัดตามผู้รับ โอกาส และระดับผู้รับ พร้อม Packaging/Personalization

ดังนั้น SmartGift ไม่ควรพึ่งคำว่า “MOQ ต่ำ”, “Custom” หรือ “Premium Gift Set” เพียงอย่างเดียว จุดทดลองที่ต่างกว่าคือ **Multi-Audience Campaign Architecture** ซึ่งทำให้หลาย Recipient Segment อยู่ใต้ Brief และ Brand Experience เดียวกัน

แหล่งสาธารณะใช้เพื่อวิเคราะห์ข้อความเท่านั้น ไม่ใช้ยืนยันยอดขาย คุณภาพ หรือความสามารถส่งมอบของคู่แข่ง

---

## 4. Ideal Customer Profile สำหรับ Pilot

Pilot ICP ต้องเป็นองค์กรที่มีความซับซ้อนของผู้รับมากพอให้ Portfolio Model สร้างคุณค่า แต่ไม่ซับซ้อนจน Pilot ควบคุมไม่ได้

### 4.1 Firmographic/Operational Fit

| เกณฑ์ | Fit ที่ต้องการ | เหตุผล |
|---|---|---|
| ประเภทธุรกิจ | องค์กรที่มีสมาชิก ลูกค้า พนักงาน สื่อ หรือคู่ค้าหลายกลุ่ม | เห็นประโยชน์ของ Recipient Matrix |
| ความสัมพันธ์ | ลูกค้าเดิมหรือ Warm Account ก่อน | ลดต้นทุน Discovery และมี Trust เดิม |
| Campaign timing | มีงานภายใน 30–120 วัน แต่ยังมีเวลาทำ Feasibility/Sample | ไม่สั้นจนข้าม Gate และไม่ไกลจนวัดไม่ได้ |
| ผู้ตัดสินใจ | เข้าถึง Marketing/CRM/HR/Corporate Comms/Procurement Owner ได้ | ต้องยืนยัน Segment, Budget และ Approval |
| จำนวนผู้รับ | มีอย่างน้อย 2 Segment หรือ 2 Gift Tier | ใช้ทดสอบข้อเสนอ Multi-Audience จริง |
| Data readiness | ลูกค้าสามารถให้จำนวน/เกณฑ์ Segment โดยไม่ส่ง PII เกินจำเป็น | ทำ Matrix ได้โดยไม่สร้างความเสี่ยง |
| Operational fit | มีสินค้าหรือรูปแบบที่ผ่าน Readiness Gate อย่างน้อย 2 Route | ป้องกันข้อเสนอที่ทำไม่ได้ |

### 4.2 Buyer Roles

| Buyer/Influencer | Pain หลัก | Message ที่ควรใช้ |
|---|---|---|
| Marketing / Brand | ของขวัญหลายกลุ่มแต่ภาพแคมเปญต้องเป็นหนึ่งเดียว | Brief เดียว แยก Treatment ได้โดย Brand ไม่แตก |
| CRM / Loyalty | สมาชิกหลาย Tier และต้องบริหารสิทธิ์ต่างกัน | ใช้ชื่อ Segment ขององค์กรและ Mapping ของขวัญต่อ Campaign |
| Corporate Comms / PR / Event | มี Media, KOL, Guest และ Executive ในงานเดียว | แยก Press/Guest/VIP treatment บน Timeline เดียว |
| HR / People | Staff, Manager, Leadership ต้องการของต่างกัน | ทำ Welcome/Recognition หลาย Tier โดยยังเป็น Program เดียว |
| Procurement | ต้องควบคุมราคา จำนวน Spec และ Approval | Recipient Matrix ทำให้ Scope และเหตุผลของแต่ละ Tier ตรวจได้ |
| Executive Sponsor | ต้องการผลทางความสัมพันธ์ ไม่ต้องการกองสต็อก | จัดงบให้คนสำคัญตามความจำเป็นและพอดีกับจำนวน |

### 4.3 Disqualification

ยังไม่ควรรับเป็น Pilot หาก:

- ลูกค้าต้องการเพียงสินค้าราคาต่ำสุดรายการเดียวและไม่ต้องแบ่งผู้รับ
- ต้องส่งเร็วจนไม่มีเวลาตรวจ Spec, Sample หรือ Claim
- ต้องใช้ Voucher/Impact/Health Claim ที่ยังไม่ผ่าน Readiness
- ลูกค้าไม่สามารถยืนยัน Budget owner, Segment owner หรือ Approver
- ต้องใช้ PII รายบุคคลก่อนมี Data-sharing/Retention boundary
- ต้องการ Bespoke เต็มรูปแบบแต่ยังไม่มี Feasibility และ Commercial owner

---

## 5. Account Prioritization

### Priority A — Existing Relationship

1. ลูกค้าที่ซื้อใน 6 เดือนล่าสุด
2. ลูกค้าที่เงียบ 6–12 เดือน
3. ลูกค้าเงียบเกิน 12 เดือนที่มีประวัติซื้อและช่องทางติดต่อ

วิธีคัด:

- มีสัญญาณ Use Case ตรงกับ 3 Pilot Plays
- มี Account owner หรือประวัติผู้ติดต่อที่ตรวจสอบได้
- มีฤดูกาล/วันครบรอบ/รอบงานที่พอประมาณได้จากหลักฐานเดิม
- ไม่มีปัญหาค้างชำระ ข้อพิพาท หรือข้อจำกัดที่ Account owner ยังไม่เคลียร์

### Priority B — Warm Prospect

ลูกค้าที่เคยขอราคาแต่ไม่เคยซื้อ ใช้หลัง Priority A และต้องแยก Message/Expectation เพราะอัตราชนะย้อนหลังต่ำกว่าลูกค้าเดิมมาก

### Priority C — New Market

เริ่มหลัง Pilot ได้ Proof, Case Study, Cost-to-serve และ Sales cycle baseline แล้ว ใช้ Owned Search, Referral และ Partnership ก่อน Paid Scale

### Privacy Boundary

รายชื่อบัญชี บุคคล เบอร์โทร อีเมล ประวัติซื้อ และ Segment จริงต้องอยู่ในระบบหรือไฟล์ Local ที่มีสิทธิ์ ไม่ใส่ในเอกสาร GTM ที่ Track ใน Git

---

## 6. Three Beachhead Plays

### Play A — Member Appreciation Architecture

| มิติ | แนวทาง |
|---|---|
| Buyer | CRM/Loyalty, Marketing, Procurement |
| Trigger | Member event, Anniversary, Tier renewal, Appreciation campaign |
| Recipient | General, Loyal, VIP, Invitation-only ตามชื่อจริงของลูกค้า |
| Offer | Reach/Select/Signature Matrix ภายใต้ Campaign เดียว |
| Theme | Care, Taste, Lifestyle, Tech ตามข้อมูลที่ลูกค้าอนุญาต |
| Format | Physical เป็น Baseline; Hybrid เฉพาะ Partner Ready |
| CTA | นัด Recipient Mapping Session |
| Pilot proof | Matrix approved, Proposal route accepted, Delivery feasibility |

### Play B — Launch & Media Architecture

| มิติ | แนวทาง |
|---|---|
| Buyer | Corporate Comms, PR, Event, Brand Marketing |
| Trigger | Product launch, Store opening, Press event, Brand activation |
| Recipient | General Media, Key Media, Creator, Guest, Member, Partner |
| Offer | Select Press/Guest Pack + Signature Key Media/VIP route |
| Theme | Tech, Work, Taste, Lifestyle |
| Format | Physical; Hybrid เมื่อ Experience พร้อม |
| CTA | ส่ง Event date, audience count และ approval timeline |
| Pilot proof | Brief completeness, revision count, on-time readiness |

### Play C — Employee Welcome & Recognition

| มิติ | แนวทาง |
|---|---|
| Buyer | HR/People, Employer Brand, Administration, Procurement |
| Trigger | Onboarding cohort, Promotion, Service anniversary, Recognition |
| Recipient | Staff, Manager, Leadership หรือ Client-defined grade |
| Offer | Select Welcome/Recognition + Signature Leadership treatment |
| Theme | Work, Tech, Care, Lifestyle |
| Format | Physical เป็น Baseline |
| CTA | ส่ง cohort/segment, required date และ brand guideline |
| Pilot proof | Repeatability, fulfilment effort, recipient/client feedback |

---

## 7. Messaging Architecture

### 7.1 Master Message

> **SmartGift — เริ่มจากคนรับ ไม่ใช่เริ่มจากของ**

### 7.2 Commercial Explanation

> เราช่วยแยกผู้รับในหนึ่งแคมเปญตามความสัมพันธ์และความสำคัญ แล้วคัดระดับของขวัญ Theme และรูปแบบให้เหมาะกับแต่ละกลุ่ม โดยยังรักษาภาพแบรนด์และการบริหารโครงการเดียวกัน

### 7.3 Working Offer Message

> **หนึ่งแคมเปญ หลายกลุ่มผู้รับ หลายระดับของขวัญ แต่สื่อสารแบรนด์เดียวกัน**

### 7.4 Proof Hierarchy

ใช้ Proof ตามลำดับและเฉพาะที่ผ่าน Claim Approval:

1. Campaign/Recipient process ที่อธิบายและสาธิตได้
2. ตัวอย่าง Matrix และ Proposal route ที่ไม่เปิดเผยข้อมูลลูกค้า
3. Product/Set ที่มีราคา MOQ, Lead time และ Spec พร้อม
4. Case Study ที่มีสิทธิ์ใช้ชื่อ ภาพ และผลลัพธ์
5. ตัวเลขประสบการณ์ ลูกค้า และการส่งมอบที่ตรวจ SoT/Scope แล้ว

### 7.5 CTA Hierarchy

| Stage | CTA |
|---|---|
| Awareness | ดูตัวอย่างหนึ่งแคมเปญหลายกลุ่มผู้รับ |
| Consideration | ส่ง Campaign Brief เบื้องต้น |
| Qualification | นัด Recipient Mapping Session |
| Proposal | ยืนยัน Campaign Recipient Matrix |
| Decision | เลือก Route และอนุมัติ Feasibility/Sample scope |

### 7.6 Claims ที่ห้ามใช้ใน Pilot

- “MOQ ต่ำที่สุดในตลาด”
- “ทำได้ตั้งแต่ 5 ชิ้น” หาก SKU/Quote ที่อนุมัติไม่รองรับ
- “รักษ์โลก” หรือ “ลด Carbon” โดยไม่มีหลักฐานระดับสินค้า/Partner
- “เพื่อสุขภาพ” ในความหมายเชิง Medical outcome
- “ใช้ได้ทุกร้าน/ทุกสาขา” สำหรับ Voucher ที่ยังไม่มี Contract
- “เหมาะกับ VIP” จากการอนุมานข้อมูลส่วนบุคคลโดยลูกค้าไม่ได้กำหนด Segment
- ตัวเลขลูกค้า ยอดขาย หรือชิ้นงานที่ Scope/Period/Source ยังไม่ผ่าน Claim Review

---

## 8. Offer Packaging สำหรับ Pilot

### 8.1 Entry Offer — Recipient Mapping Session

**Input ขั้นต่ำ**

- Campaign objective และ occasion
- Recipient relationship/segment/count
- Budget range
- Required-by date
- Brand/approval constraint

**Output**

- Campaign Recipient Matrix v0.1
- Risk/unknown list
- Feasibility request สำหรับ 2–3 Route

Commercial term, ระยะเวลา Session และผู้มีสิทธิ์ดำเนินการต้องกำหนดโดย Pilot Owner ห้ามสมมติว่าเป็นบริการฟรี

### 8.2 Core Offer — Multi-Audience Proposal

ข้อเสนอหนึ่งฉบับควรมี:

1. Campaign objective และ assumption
2. Recipient Matrix
3. Route A/B และ Route C เฉพาะเมื่อมีความต่างจริง
4. Gift Tier/Theme/Format ต่อ Segment
5. ราคา จำนวน MOQ, Lead time และ Validity ที่มาจาก Source ที่อนุมัติ
6. Sample/Proof/QC plan
7. Delivery scope
8. Exclusion, dependency และ approval schedule

### 8.3 Custom Offer — Bespoke

เปิดเฉพาะเมื่อมี:

- Commercial owner
- Design/Development scope
- Minimum project economics ที่ Finance อนุมัติ
- IP/Artwork/Brand rights
- Sample and revision policy
- Timeline buffer และ Change control

### 8.4 Voucher/Experience Add-on

มีสถานะ `not generally available` จนกว่าจะผ่าน Partner Readiness Gate ห้ามใช้เป็นส่วนบังคับของ Pilot ทั้งสาม

---

## 9. Sales Funnel และ Stage Gates

| Stage | วัตถุประสงค์ | Required evidence | Exit criteria |
|---|---|---|---|
| `ACCOUNT_SELECTED` | เลือกบัญชีตาม Priority | Source/relationship/use-case fit | Account owner ยืนยันให้ติดต่อได้ |
| `DISCOVERY_SCHEDULED` | นัดผู้มีบริบทแคมเปญ | Contact basis + agenda | มีวันนัดและผู้เข้าร่วม |
| `DISCOVERY_COMPLETE` | เข้าใจ Campaign/Recipient | Discovery note ตามสิทธิ์ | Objective, segment, count, budget/date known หรือระบุ unknown |
| `MATRIX_DRAFTED` | แปลงโจทย์เป็นโครงสร้าง | Recipient Matrix v0.1 | ลูกค้าตรวจชื่อ Segment และ Tier mapping |
| `FEASIBILITY_REVIEW` | ตรวจว่าส่งมอบได้ | Product/price/MOQ/lead-time/claim evidence | อย่างน้อย 2 Route ผ่านหรือปิดเป็น no-fit |
| `PROPOSAL_SENT` | ส่งข้อเสนอที่ Trace ได้ | Approved proposal + validity | ผู้ตัดสินใจได้รับและมี next action/date |
| `DECISION` | Won/Lost/Hold | Decision reason | สถานะและเหตุผลถูกบันทึก |
| `DELIVERY` | ผลิต/QC/ส่งมอบ | Approved proof + checklist | Delivery acceptance ตาม Scope |
| `REVIEWED` | เรียนรู้จาก Pilot | Outcome/effort/feedback | Retrospective และ recommendation เสร็จ |

### Follow-up Discipline

- ทุก Proposal ต้องมี Account owner และ next-action date
- ไม่มีการตอบกลับต้องไม่ค้างไม่จำกัดเวลา ต้องปิดหรือพักตาม SLA ที่ Pilot Owner อนุมัติ
- Lost reason ต้องแยก `price`, `timing`, `no fit`, `no decision`, `competitor`, `operational constraint` และ `unknown`
- ห้ามเรียก Proposal ว่า “ชนะ” จากการตอบรับเชิงบวก ต้องมีคำสั่งซื้อ/ข้อตกลงตาม Authority จริง

---

## 10. Channel Plan

### Channel 1 — Existing-account Outreach

ช่องทางหลักของ Pilot:

- Account owner โทรหรือ LINE ตามช่องทางที่มีสิทธิ์
- เปิดด้วย Campaign timing หรือประวัติความสัมพันธ์ที่ตรวจสอบได้
- ไม่ส่งแคตตาล็อกกว้างเป็นข้อความแรก
- CTA คือ Discovery/Recipient Mapping ไม่ใช่บังคับเลือก SKU

### Channel 2 — Owned Website

เว็บไซต์ปัจจุบันมี Custom Corporate และ Campaign Brief อยู่แล้ว จึงใช้เป็นช่องทางสนับสนุนได้หลังตรวจ Copy/Claim/Tracking โดยไม่จำเป็นต้องสร้างระบบใหม่ทันที

ข้อกำหนดก่อนเปลี่ยน Production:

- Architecture และ GTM Copy review
- Claim/source review
- Analytics event definition
- Form privacy/retention review
- Build และ Browser verification
- Separate deployment approval

### Channel 3 — Content & Sales Assets

ลำดับ Asset ที่ต้องสร้างหลัง GTM อนุมัติ:

1. One-page “หนึ่งแคมเปญ หลายกลุ่มผู้รับ”
2. Recipient Matrix ตัวอย่าง 3 Archetype
3. Route comparison template
4. FAQ: Signature ไม่ใช่ของผู้บริหารเท่านั้น
5. Case Study template ที่เก็บ Source/permission
6. Sales discovery card

### Channel 4 — Referral/Partner

เริ่มเมื่อมี Pilot proof โดยทดลองกับ Event agency, CRM/Loyalty consultant หรือ HR partner ที่มี Audience fit และไม่ขัด Channel ownership

### Channel 5 — Paid Media

สถานะ `deferred` จนกว่าจะมี:

- Landing conversion baseline
- Qualified lead definition
- Sales cycle และ Close rate
- Gross margin/Cost-to-serve ที่เชื่อถือได้
- Budget owner และ stop condition

---

## 11. Content Plan สำหรับ 90 วัน

| ช่วง | Content/Asset | วัตถุประสงค์ | Gate |
|---|---|---|---|
| วัน 1–15 | Internal terminology sheet | ให้ทีมใช้คำตรงกัน | Portfolio review |
| วัน 1–15 | 3 anonymized Recipient Matrices | ฝึก Discovery และ Proposal | No PII/brand misuse |
| วัน 16–30 | One-page offer | ใช้ใน Controlled Outreach | Claim review |
| วัน 16–30 | Discovery card + qualification checklist | ลด Brief ที่ไม่ครบ | Sales/Operations review |
| วัน 31–60 | Controlled landing/copy candidate | อธิบายโมเดลและรับ Brief | Separate web approval |
| วัน 31–60 | FAQ/objection sheet | ตอบคำถามเรื่อง Tier/ราคา/MOQ | Finance/Product review |
| วัน 61–90 | Pilot case-study draft | สร้าง Proof สำหรับรอบถัดไป | Client permission + Source review |
| วัน 61–90 | Executive pilot report | ตัดสิน Go/Revise/Stop | Analytics contract |

ห้ามเผยแพร่ Asset ที่มี Client logo, quote, recipient data หรือผลลัพธ์ก่อนมีสิทธิ์เป็นลายลักษณ์อักษร

---

## 12. 90-Day Execution Plan

### Phase 0 — Activation Gate

เริ่มนับวัน Pilot หลังมีครบ:

- Pilot Owner
- Budget/expense boundary
- Account selection authority
- Product Readiness Owner
- Analytics Owner
- Legal/PDPA escalation path

### Days 1–15 — Prepare

1. Freeze Pilot terminology จาก Parent Architecture
2. สร้าง Product Readiness shortlist สำหรับ 3 Plays
3. กำหนด Source of truth ของ Price/MOQ/Lead time
4. ทำ Discovery card และ Recipient Matrix template
5. เลือก Candidate accounts แบบ Local/PDPA-safe
6. เก็บ Baseline เวลา/Revision ของกระบวนการเดิมถ้ามี

**Exit:** ทีมทำ Dry run 3 Scenario ได้โดยไม่มี Claim หรือ Operational unknown ที่ถูกซ่อนไว้

### Days 16–30 — Internal Rehearsal

1. Sales role-play ทั้ง 3 Plays
2. Operations/Finance ตรวจ Proposal routes
3. ทดสอบ Lost/no-fit path
4. สร้าง One-page controlled asset
5. กำหนด CRM/Sheet logging โดยไม่แก้ระบบใหญ่

**Exit:** Proposal template ผ่าน Review และทุก Stage มี Owner/exit criteria

### Days 31–60 — Controlled Discovery

1. ติดต่อบัญชีที่อนุมัติ 3–5 ราย
2. ทำ Discovery และ Draft Matrix
3. บันทึกความเข้าใจ/ข้อโต้แย้ง/เวลา/Revision
4. ส่ง Proposal เฉพาะ Route ที่ผ่าน Feasibility
5. หยุดบัญชีที่ไม่มี Fit แทนการฝืนขาย

**Exit:** มี Discovery evidence เพียงพอให้เห็นว่า Message และ Matrix ใช้งานได้หรือไม่

### Days 61–90 — Pilot Delivery & Decision

1. ดำเนินงานเฉพาะ Pilot ที่ลูกค้าอนุมัติจริง
2. เก็บ Effort, rework, feasibility, commercial และ delivery evidence
3. ขอ Feedback ตามสิทธิ์
4. สรุปผลแยกตาม Play/Gift Tier/Format
5. เสนอ `GO`, `REVISE` หรือ `STOP`

**Exit:** ผู้บริหารตัดสินจากข้อมูลที่ Trace ได้ ไม่ใช่ความรู้สึกของทีม

---

## 13. Measurement Contract

### 13.1 North-star สำหรับ Pilot

> จำนวน Campaign ที่ยืนยัน Recipient Matrix แล้วผ่าน Feasibility ไปสู่ข้อเสนอหรือคำสั่งซื้อจริง โดยไม่มี Critical Claim/Delivery/PDPA exception

North-star นี้ไม่กำหนด Target เชิงตัวเลขจนกว่า Analytics Owner จะเก็บ Baseline และผู้บริหารอนุมัติ

### 13.2 Funnel Metrics

| Metric | Definition ขั้นต้น | Source | Owner |
|---|---|---|---|
| Selected accounts | บัญชีที่ผ่าน Priority/Fit และอนุญาตให้ติดต่อ | Local CRM/approved list | Account Owner |
| Discovery completion | Session ที่เก็บ Required field หรือ unknown ครบ | Discovery record | Sales Owner |
| Matrix acceptance | ลูกค้ายืนยัน Segment label และ mapping | Approved matrix | Account Owner |
| Feasibility pass | Route ที่ Product/Finance/Ops ยืนยันทำได้ | Feasibility record | Product Owner |
| Proposal cycle time | Discovery complete ถึง Proposal sent | Stage timestamps | Analytics Owner |
| Revision count | Revision ที่เปลี่ยน Scope/Route ก่อน Decision | Proposal log | Sales Owner |
| Conversion | Won ตาม Authority / Proposal sent | Order/decision record | Sales + Finance |
| Cost-to-serve | Labor/sample/design/logistics per Pilot | Approved cost record | Finance |
| On-time delivery | ส่งตาม accepted milestone | Delivery evidence | Operations |
| Critical exception | Claim, pricing, voucher, delivery หรือ PDPA breach | Incident/exception log | Governance Owner |

### 13.3 Learning Metrics

- Buyer เข้าใจคำว่า Recipient Matrix หรือไม่
- Signature ถูกเข้าใจเป็นระดับการดูแลหรือยังถูกตีความเป็นผู้บริหาร
- ลูกค้าต้องการเลือก Theme เองหรือให้ SmartGift แนะนำ
- จำนวน Route ที่เหมาะสมคือ 2 หรือ 3
- กลุ่มใดเห็นคุณค่าของ Hybrid จริง
- จุดใดทำให้ทีมใช้เวลาหรือ Revision มากที่สุด

### 13.4 Data Quality

ทุก Metric ต้องมี:

- Definition
- Numerator/denominator หากเป็นอัตรา
- Source
- Time window
- Owner
- Missing-data rule
- Caveat

ห้ามรวมคำชม ตัวอย่าง UI หรือการมีเอกสารเป็นหลักฐาน Conversion

---

## 14. Experiment Backlog

| ID | Hypothesis | Test | Success signal | Stop condition |
|---|---|---|---|---|
| `EXP-01` | Recipient-first opener สร้าง Discovery ที่มีคุณภาพกว่า SKU-first | เปรียบเทียบ Script แบบควบคุม | Required fields ครบและ next step ชัด | ลูกค้าสับสนหรือ Cycle timeเพิ่มโดยไม่มีคุณค่า |
| `EXP-02` | ข้อเสนอ 2 Route ตัดสินใจง่ายกว่า 3+ Route | ใช้ 2 Route เป็น Default | Revision/decision time ลดลง | ลูกค้าขาดทางเลือกสำคัญซ้ำ ๆ |
| `EXP-03` | Member Appreciation เป็น Beachhead ที่แข็งที่สุด | Controlled discovery | Matrix acceptance + feasible proposal | ไม่มี Account fit หรือ Complexity สูงเกิน Pilot |
| `EXP-04` | Signature message ใช้ได้กับ Key Media/VIP ไม่จำกัด Executive | Concept test | Buyer ใช้คำและ mapping ได้ถูกต้อง | เกิดความเข้าใจว่า Signature = ราคาแพง/ผู้บริหารเท่านั้น |
| `EXP-05` | Owned one-page ช่วย Qualified Brief | Controlled asset | Brief completeness สูงขึ้น | Lead ไม่ตรง Fit หรือ Privacy/claim issue |

Experiment ต้องมี Owner, sample, start/end, data source และ approval ก่อนเริ่ม ห้ามเลือกเฉพาะผลที่ดูดีมาสรุป

---

## 15. Budget Framework

งบยังเป็น `TBD` และต้องแยกหมวดเพื่อเห็นต้นทุนจริง:

| หมวด | ตัวอย่าง | Owner |
|---|---|---|
| People time | Workshop, Discovery, Design, Sourcing, Operations | Pilot Owner |
| Sample/prototype | ตัวอย่างสินค้า กล่อง Artwork | Product/Finance |
| Content | One-page, photo, case study | Marketing |
| Tools/analytics | Tracking/CRM configuration ที่อนุมัติ | Analytics/Technical Owner |
| Partner | Voucher/experience setup ถ้าผ่าน Gate | Commercial/Legal |
| Logistics | Sample และ Pilot delivery | Operations |
| Contingency | เฉพาะความเสี่ยงที่ระบุและมีเพดาน | Finance |

ห้ามซ่อน Sample, Rework, Design time หรือ Shipping ไว้ในราคาสินค้าโดยไม่มี Cost owner เพราะจะทำให้ Pilot ดูคุ้มเกินจริง

---

## 16. Operating Cadence และ RACI

### 16.1 Cadence

| ความถี่ | การประชุม/Review | Output |
|---|---|---|
| รายสัปดาห์ | Pilot pipeline review | Stage, blocker, next action, exception |
| ก่อนส่ง Proposal | Feasibility gate | Price/MOQ/lead-time/claim/format approval |
| ก่อนผลิต | Proof/QC gate | Accepted sample/artwork/scope |
| หลัง Delivery | Retrospective | Outcome, rework, feedback, cost |
| วัน 30/60/90 | Executive checkpoint | Continue/adjust/stop decision |

### 16.2 RACI

| Workstream | A | R | C |
|---|---|---|---|
| Pilot strategy | Founder/MD | Pilot Owner | Marketing, Sales, Finance |
| Account selection/contact | Sales Owner | Account Owner | PDPA/Client Owner |
| Messaging/content | Marketing Owner | Campaign Lead | Brand, Legal |
| Product readiness | Product Owner | Sourcing | Finance, QC, Operations |
| Price/commercial | Finance/Commercial Owner | Estimator | Sales, Product |
| Delivery | Operations Owner | Operations | Product, Account Owner |
| Measurement | Analytics Owner | Analyst | Sales, Finance, Operations |
| Exception/stop | Pilot Owner | Workstream owner | Founder/Legal/Finance ตามความเสี่ยง |

ชื่อบุคคลต้องถูกแต่งตั้งก่อน Phase 0 ผ่าน

---

## 17. Risks และ Stop Conditions

| Risk | Prevention | Stop/escation |
|---|---|---|
| ข้อเสนอใช้ราคา/MOQ เก่า | Source validity และ approver ก่อนส่ง | หยุด Proposal จน Refresh |
| Signature กลายเป็น Price ladder | ใช้ treatment/service criteria | ทบทวน Message และ Proposal template |
| Public copy เกินหลักฐาน | Claim checklist | Unpublish/block release |
| Impact/Health claim หลุด | Evidence gate | Reject asset/route |
| Voucher redemption ไม่พร้อม | Partner readiness | ห้ามเสนอ Hybrid route |
| Recipient data เกินจำเป็น | Matrix ใช้จำนวน/segment ก่อน PII | Quarantine/delete ตาม policy และแจ้ง owner |
| Sales ส่ง Catalogue กว้างแทน Discovery | Script/QA review | Retrain และไม่นับเป็น GTM test |
| Pilot เพิ่มงานแต่ไม่เพิ่มคุณค่า | เก็บ time/revision/cost | Stop หรือ Simplify model |
| งานคู่ขนานเปลี่ยน Web/UI ก่อน Gate | แยก Documented/Implemented/Published state | ห้ามถือ Code presence เป็น approval/live truth |

Critical exception ด้านราคา Claim, PDPA, Voucher หรือ Delivery ทำให้ Pilot route นั้นหยุดทันทีจน Owner ที่มีอำนาจตัดสินใจ

---

## 18. Deliverables

### ก่อน Controlled Discovery

- Approved GTM Plan
- Named owners และ budget boundary
- Product Readiness shortlist
- Campaign Brief template
- Recipient Matrix template
- Discovery/qualification card
- Feasibility checklist
- Proposal template
- Measurement dictionary

### ก่อน Pilot Delivery

- Client-approved Matrix
- Route feasibility evidence
- Price/MOQ/lead-time validity
- Artwork/sample approval
- Delivery/QC plan
- Data/claim/partner approvals ตาม Format

### หลัง 90 วัน

- Pilot evidence pack
- Funnel and cost report
- Learning by Play/Tier/Theme/Format
- Risk/exception log
- Recommendation `GO`, `REVISE` หรือ `STOP`
- Scope proposal สำหรับ Taxonomy, Sales Playbook และ BRD/PRD ถัดไป

---

## 19. Acceptance, Success และ Exit Criteria

### 19.1 Acceptance Criteria ของ GTM Plan

- ผู้บริหารอนุมัติ Beachhead, Account Priority และ 3 Plays
- Owner และ Budget ถูกแต่งตั้ง
- Message/Claim boundary ผ่าน Marketing/Product/Finance/Legal ตามความเกี่ยวข้อง
- Funnel stage และ Measurement definition มี Source/Owner
- ไม่มีการใช้ Public Rollout เป็นสมมติฐานของ Pilot

### 19.2 Success Criteria ของ Pilot

- ทั้ง 3 Plays ผ่าน Dry run และอย่างน้อยหนึ่ง Play มี Controlled client evidence
- Recipient Matrix ได้รับการยืนยันจากลูกค้าหรือมีเหตุผลปฏิเสธที่บันทึกได้
- Proposal ทุกฉบับผ่าน Feasibility ก่อนส่ง
- Outcome, cycle time, revision และ cost Trace ย้อนกลับได้
- ไม่มี Critical Claim, Pricing, Delivery, Voucher หรือ PDPA breach

### 19.3 Exit Criteria

- Day-90 review ออกมติ `GO`, `REVISE` หรือ `STOP`
- `GO` ต้องระบุว่า Scale เฉพาะ Play/Channel/Offer ใด ไม่ใช่อนุมัติทั้งหมดโดยอัตโนมัติ
- `REVISE` ต้องระบุ Hypothesis และรอบทดลองถัดไป
- `STOP` ต้องหยุด Public claim, campaign asset และ spend ที่เกี่ยวข้องตามแผน
- การสร้างระบบหรือแก้ Production ต้องมี BRD/PRD, Risk Assessment, Tests และ Deployment Approval แยก

---

## 20. Decision Record

| ID | Decision | Owner | Status |
|---|---|---|---|
| `GTM-D01` | Beachhead 3 Plays | Founder/MD | Approved for Pilot Planning — Boss, 2026-08-13 |
| `GTM-D02` | Account priority A/B/C | Founder/MD + Sales | Strategic priority approved; Sales validation pending |
| `GTM-D03` | Messaging hierarchy | Marketing + Founder/MD | Approved for Pilot Planning — Boss, 2026-08-13 |
| `GTM-D04` | Funnel and stage gates | Sales + Operations | Strategic model approved; operational validation pending |
| `GTM-D05` | Measurement contract | Analytics + Finance | Strategic model approved; definition/owner validation pending |
| `GTM-D06` | Pilot Owner | Founder/MD | Pending |
| `GTM-D07` | Pilot budget | Founder/MD + Finance | Pending |
| `GTM-D08` | Controlled outreach account list | Sales/Client authority | Pending — local/PDPA-safe |

---

## 21. แหล่งอ้างอิง

### ภายใน

- `docs/SMARTGIFT-BRAND-PRODUCT-PORTFOLIO-ARCHITECTURE-2026-08.md` v0.1.1b
- `docs/competitive-brief-thailand-2026-08.md`
- `docs/battlecard-bixitia-2026-08.md`
- `docs/sales-forecast-marketing-pipeline.md`
- `data/sot.duckdb`

### ภายนอก ตรวจเมื่อ 2026-08-13

- SmartGift Thailand: <https://smartgiftthailand.com/>
- EcoGifts / PremiumExpert: <https://www.ecogifts.biz/>
- THORR'S Gifts: <https://thorrsgifts.com/>
- Giftmanufactory: <https://www.giftmanufactory.com/premium-corporate-gift-set>

ข้อมูลตลาดอาจเปลี่ยนได้ ต้องตรวจซ้ำก่อนใช้ตัดสิน Full Rollout หรือ Claim เปรียบเทียบ

---

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.1b | 2026-08-13 | beta | Boss อนุมัติ GTM model สำหรับ Pilot Planning; คง Owner, Budget, Account list และ operational validation เป็น pending | uncommitted | ATHER |
| 0.1.0b | 2026-08-13 | draft | แปลง Portfolio Architecture ที่อนุมัติแล้วเป็น GTM Controlled Pilot: Beachhead, ICP, Plays, Messaging, Funnel, Channel, 90-day plan และ Measurement Contract | uncommitted | ATHER |
