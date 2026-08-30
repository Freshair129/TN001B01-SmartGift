---
version: "0.1.0b"
created_at: "2026-08-30T18:20:00+07:00,ATHER,uncommitted"
last_update: "2026-08-30T18:20:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  doc_type: "technical-design"
  domain: "smartgift-catalog-media"
  scope: "Source-based product imagery for Catalog and Seasonal Expo"
  language: "th"
---

# SPEC: ภาพสินค้าอ้างอิงจริงสำหรับ Catalog และ Seasonal Expo

## 1. ปัญหาและขอบเขต

หน้าจอเดิมใช้พื้นหลัง ad แบบนามธรรมและป้ายชิ้นส่วน ทำให้ผู้ใช้ไม่เห็นว่าสินค้าจริงในชุดมีหน้าตาอย่างไร คำขอนี้จึงเพิ่มชั้นภาพสินค้าให้เห็นก่อนดูราคาและ BOM โดยใช้ภาพที่ตรวจรหัสกับ Catalog แล้ว หรือภาพที่สร้างใหม่จากภาพอ้างอิงนั้น

ภาพในสเปกนี้เป็น **creative preview** เพื่อช่วยสื่อสารรูปทรงและบรรยากาศเท่านั้น ไม่ใช่หลักฐานสเปก ราคา ต้นทุน stock หรือ BOM และไม่ผูกภาพชุดเหล่านี้เข้ากับ package ฤดูกาลที่ไม่มี source mapping ตรงกัน

## 2. หลักฐานภาพที่ใช้

- ใช้ source-matched set creative 4 ชุด: `FXD66-3`, `TMK00-4`, `FXD6064`, `TGC09-3`
- ใช้ภาพสินค้าเดี่ยว 6 รหัส: `S-1052`, `BST61401`, `DW03`, `UT3056`, `S1033`, `W502`
- เพิ่ม hero `FXD66-3` ที่สร้างด้วย image generation จาก reference `set-FXD66-3-source.png` โดยคงสินค้าสามชิ้นและจัดแสงใหม่
- manifest กลางอยู่ที่ [`public/data/catalog_media.json`](../../public/data/catalog_media.json) และไฟล์สื่ออยู่ใต้ `public/assets/catalog-media/`
- `source-photo` หมายถึงภาพต้นฉบับจาก Catalog; `generated-clean` และ `generated_from_source_reference` หมายถึงภาพจัดฉาก/สร้างใหม่จาก reference ไม่ใช่ภาพถ่ายยืนยันสินค้า

## 3. พฤติกรรมที่ตรวจรับ

1. Catalog view แสดง hero, ภาพชุด และภาพสินค้าเดี่ยวพร้อมรหัสสินค้า ก่อนส่วน BOM Anatomy
2. Seasonal Expo แสดง hero และภาพชุดจาก Catalog ก่อนการ์ด package เพื่อให้เข้าใจภาพรวมก่อนเปิดรายละเอียด
3. ป้ายทุกภาพระบุสถานะ source หรือ generated และมี disclaimer ภาษาไทย
4. หาก manifest หรือ path ไม่ผ่าน allowlist ให้ซ่อนส่วนภาพ/แสดงข้อความรอข้อมูล และไม่เดาภาพจากชื่อสินค้า
5. `/api/media` รับเฉพาะ `GET`, ส่ง JSON customer-safe และไม่เปิดเผย factory cost, profit, CBM, provenance path หรือ PII
6. ข้อมูล package, schema PK/FK, BOM, ราคาโรงงาน และ Profit Gate ฿25,000 ยังมาจาก master เดิม ไม่ถูกแก้ด้วยภาพ

## 4. Acceptance และความเสี่ยง

- ตรวจ syntax ของ inline JavaScript และ API route
- ตรวจว่าไฟล์ภาพทั้ง 11 ไฟล์ resolve จาก path ที่ manifest อนุญาต
- ตรวจ `/api/media` ได้ `200` สำหรับ `GET` และ `405` สำหรับ method อื่น
- ตรวจ browser ว่า Catalog และ Expo มีภาพจริง, alt text, lazy loading และไม่เกิด console/page error
- ความเสี่ยงคงเหลือ: สิทธิ์ใช้งานภาพและการยืนยันสเปกสินค้าไม่ได้ถูกอนุมานจากภาพ ต้องตรวจโดยเจ้าของ Catalog ก่อนใช้เชิงพาณิชย์

## 5. Version diff / changelog

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | beta | เพิ่มภาพ source-based และ generated creative preview ให้ Catalog/Expo พร้อม customer-safe media endpoint | uncommitted | ATHER |

