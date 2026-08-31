---
version: "0.2.0b"
created_at: "2026-08-14T09:48:52+07:00, ATHER, 603ccb2"
last_update: "2026-08-14T10:44:34+07:00, ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "product-context"
  domain: "smartgift-marketing"
  scope: "public-landing-and-portfolio-demo"
  artifact_id: "SG-PRODUCT-CONTEXT-001"
  language: "th"
---

# Product

## Register

brand

## Users

ผู้ใช้หลักคือ Founder, Sales, Marketing และ Product/Sourcing ที่เปิดเดโมบนโน้ตบุ๊กหรือจอประชุมเพื่อทำความเข้าใจโครงสร้าง SmartGift Portfolio ร่วมกัน ผู้ใช้ต้องเห็นความแตกต่างระหว่าง Gift Tier, Theme, Format และ Package concept ได้ภายในเวลาอันสั้น โดยไม่ตีความหน้าเดโมเป็นแคตตาล็อกพร้อมขายหรือใบเสนอราคา

## Product Purpose

เดโมนี้แสดงวิธีเปลี่ยนการนำเสนอจากรายการสินค้าจำนวนมากไปสู่พอร์ตที่เริ่มจากผู้รับและระดับการดูแล มีหน้า Catalog Index หนึ่งหน้าและ Package Detail หนึ่งหน้าเพื่อให้ทีมเห็นทั้งภาพรวมและความลึกของแพ็กเกจ

Public Landing ที่ `/` เป็น front door ของ SmartGift สำหรับผู้เข้าชมทั่วไป โดยเชื่อมไป Catalog และ Package Detail ก่อน ส่วน Login และ Sales Dashboard เป็นหลังบ้านที่ผู้ใช้เลือกเข้าเองผ่าน CTA แยกต่างหาก

ความสำเร็จของเดโมคือทีมสามารถอธิบายได้ว่า:

- `Reach`, `Select`, `Signature` และ `Bespoke` เป็น Gift Tier
- `Tech` และ `Care & Wellness` เป็น Theme ไม่ใช่แบรนด์ย่อย
- Package concept เป็นตัวอย่าง `CONCEPT_READY` และไม่ใช่ราคา สต็อก หรือคำสั่งผลิต

## Brand Personality

Precise, tactile, quietly confident. ภาษาไทยต้องตรง กระชับ และให้ภาพของการคัดสรรของขวัญที่มีโครงสร้าง มากกว่าการโฆษณาความหรูหราแบบกว้าง ๆ

## Anti-references

- เว็บอีคอมเมิร์ซลดราคาและกริดสินค้าที่นำด้วยราคา
- Luxury template สีดำทองที่ใช้คำหรูโดยไม่มีรายละเอียด
- SaaS card wall ที่ทุกส่วนมีไอคอน การ์ดมน และเงาฟุ้งเหมือนกัน
- Slide deck ที่ต้องกดทีละหน้าเพื่อค้นหาข้อมูล
- Public catalogue ที่ทำให้ concept, price staging หรือภาพตัวอย่างดูเหมือนพร้อมขาย

## Design Principles

1. เริ่มจากระดับการดูแลและบริบทผู้รับ ไม่เริ่มจากจำนวน SKU
2. แยก Tier, Theme, Format และ Readiness ให้เห็นในตำแหน่งคงที่
3. ให้ภาพสินค้าเป็นหลักฐานเชิงภาพ แต่ใช้ข้อความกำกับเพื่อป้องกันการตีความเกินจริง
4. ใช้ Catalog Index ที่สแกนเร็ว และ Detail ที่อธิบาย Package Anatomy ได้จริง
5. รักษา SmartGift เป็น master brand เดียวตลอดเดโม
6. ให้ public brand experience มาก่อน และแยก back-office access ออกจากเส้นทางสำรวจ Portfolio

## Public and Back-office Boundary

- Public: `/`, `/portfolio`, `/portfolio/catalog` และ Package Detail
- Public back-office entry: `/login`
- Protected: `/dash`, `/admin`, `/profile`, `/graph` และข้อมูลดาวน์โหลด
- การเปิด Landing หรือ Catalog ต้องไม่เรียกการเขียนข้อมูล Blob หรือเปลี่ยนสิทธิ์ผู้ใช้

## Accessibility & Inclusion

- เป้าหมาย WCAG 2.2 AA สำหรับ contrast, focus และ semantic structure
- ใช้งานลิงก์และตัวกรองได้ด้วย keyboard
- รองรับ `prefers-reduced-motion`
- ภาษาไทยต้องอ่านได้บน Windows โดยไม่พึ่งฟอนต์ดาวน์โหลดภายนอก
- ภาพทุกภาพมี alt text ที่บอกวัตถุและบริบท ไม่ใช้ชื่อไฟล์เป็น alt text

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.2.0b | 2026-08-14 | beta | ขยาย product context ให้มี public Landing เป็น front door และแยก Sales Dashboard เป็น back office | 603ccb2 | ATHER |
| 0.1.0b | 2026-08-14 | beta | Boss อนุมัติ product context สำหรับเดโม Catalog Index และ Package Detail | 603ccb2 | ATHER |
