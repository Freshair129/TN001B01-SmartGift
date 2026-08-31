---
version: "1.0.0b"
created_at: "2026-08-31T17:19:31.697+07:00,ATHER,uncommitted"
last_update: "2026-08-31T17:19:31.697+07:00,ATHER"
status: "need review"
superseded_by: null
attributes:
  domain: "catalog3d-visual-audit"
  scope: "11 existing local review candidates; screenshots and findings only"
  language: "th"
---

# ผลตรวจ 3D catalog เทียบภาพต้นฉบับ — 31 สิงหาคม 2026

ตรวจจริงครบ **11 รุ่น / 37 screenshots** ใน Codex In-app Browser ที่ http://127.0.0.1:5191/ โดยเลือกแต่ละรุ่น เปิดภาพต้นฉบับ แล้วลากหมุนโมเดลถ่ายมุมเริ่มต้น ด้านข้าง และด้านหลัง ไม่สร้างภาพจำลองแทน screenshot.

**ผลตรวจรับความเหมือน: ยังไม่มีรุ่นที่ให้ผ่าน.** โมเดลใหม่ P8 ทั้ง 7 รุ่นไม่ผ่าน; รุ่นเก่า S1033/DW03/BW00-0 ต้องแก้รายละเอียดหรือยืนยันเพิ่ม และ W502 ต้องแก้โครงสร้างขาตั้ง. ผลนี้ไม่ใช่คำตัดสินความถูกต้องของตัวสินค้าจริงหรือ canonical mapping.

ตรวจอย่างเดียว (C-1 / LOW): เพิ่มรายงานและ screenshots; ไม่แก้โมเดล generator viewer index/schema ราคา inventory หรือ public catalog. ไม่มี commit/push. ป้าย review-ready ใน metadata เดิมยังไม่ถูกเปลี่ยน และ **ไม่ควรอ่านเป็นผ่าน visual QA**.

## วิธีตรวจและขอบเขตหลักฐาน

- 33 screenshots = 11 รุ่น × 3 มุม. อีก 4 ภาพคือ BW00-0 Silver/top, TDK01-1 Blue/top, TZJ00-1 White และหมวด Classic Oriental ที่ไม่มีโมเดล.
- ชื่อ side/back เป็นมุมประมาณจากการลากหมุนรอบแกนตั้ง ไม่ใช่มุม orthographic ที่ตั้งองศาวัดจริง. ภาพต้นฉบับบางรุ่นมีมุมเดียว; การหมุนตรวจ geometry ไม่ยืนยันว่าใต้/หลังสินค้าจริงเป็นแบบนั้น.
- ทุกภาพ -view.jpg เป็น screenshot JPEG ตาม bytes ที่ Browser คืนมา ไม่ crop/แต่ง/เพิ่มชิ้นส่วน. ภาพบางใบมี scroll position ต่างกัน แต่เห็นตัวโมเดลและภาพเทียบ.
- initial capture attempts S1033-default.jpg/S1033-side.jpg/S1033-back.jpg ไม่ใช้ตัดสิน: full-page capture มี reflow และ keyboard rotation ไม่ได้ยืนยันผล. เก็บไว้แยกใน manifest; ภาพที่ใช้อยู่ในชื่อ *-view.jpg เท่านั้น.
- ตรวจ hash ของ GLB และภาพอ้างอิงครบ 11/11 ตรงกับ viewer index ปัจจุบัน; ตรวจ JPEG headers/ขนาดภาพและครบสามมุมต่อรุ่น.
- รันชุดทดสอบเทคนิคใหม่: **30 ผ่าน / 0 fail / 0 skip**. ตรวจ finite mesh, GLB parse, hashes และ routes ไม่ได้ตรวจหูแก้ว/ฝา/สายคล้อง/ความเหมือนภาพ.
- viewer เปิดและลากหมุนได้ทั้ง 11 รุ่น; logs ที่ browser คืนมารอบตรวจไม่มี error/warning. ทดลองสีเพิ่มเติม 3 รุ่นที่ระบุข้างต้น ไม่ได้ทดสอบทุก variant ทุกชื่อ.
- เกณฑ์ความเหมือนที่ใช้: silhouette, ชิ้นส่วนที่เห็น, ตำแหน่ง/การยึด, สีรายชิ้น, ผิวทะลุ/ชิ้นลอย; ไม่เรียกร้องรายละเอียดที่ต้นฉบับไม่แสดง.

## ผลรายรุ่น

| รุ่น | ผล visual QA | ข้อผิดพลาดที่เห็น | หลักฐาน |
|---|---|---|---|
| S1033 | ต้องเก็บรายละเอียด/ยืนยันเพิ่ม | บอดี้ วงกลมด้านหน้า สายสองข้างและขาตั้งพอจำแนกได้ แต่ปลาย connector และรายละเอียดวงกลมถูกย่อเป็นรูปทรงทั่วไป สี/โลหะไม่เหมือนในภาพทั้งหมด; ภาพอ้างอิงมุมเดียวความละเอียดต่ำยังยืนยันด้านหลังและบานพับไม่ได้ | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/S1033-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/S1033-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/S1033-back-view.jpg) |
| DW03 | ต้องแก้รายละเอียด | รูปทรงหลักและสายสี่เส้นพอใกล้เคียง แต่เมื่อมองด้านหลัง หัว USB ที่มีแถบทองอยู่ซ้ายในโมเดล ขณะที่ภาพต้นฉบับอยู่ขวา; หัวอื่น ๆ เป็นก้อนดำและผิวส้มเหลือง/เงาต่างจากภาพ | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/DW03-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/DW03-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/DW03-back-view.jpg) |
| W502 | ไม่ผ่าน — ขาตั้งผิดโครงสร้าง | ภาพต้นฉบับแสดงขาตั้งแบบกรอบเปิด แต่โมเดลเป็นแผ่นทึบ; ภาพด้านข้างแสดงท่าตั้งที่ฐานขาเลยใต้บอดี้ และแถบใต้แผ่นชาร์จเป็นสี่เหลี่ยมยาวแทนปุ่มโค้งสั้น | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/W502-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/W502-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/W502-back-view.jpg) |
| BW00-0 | ต้องแก้วัสดุ/ยืนยันฝา | ทรงกระบอกและรอยต่อฝาพอใกล้ภาพ แต่สีดำใน viewer สูญเสียรายละเอียดผิวและขอบ; มุม Silver/top แสดงจอเป็นวงดำเล็ก ซึ่งภาพต้นฉบับด้านหน้าที่ใช้เทียบยังยืนยันรูปแบบบนฝาไม่ได้; รูปต้นฉบับสูงล้น viewport | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-back-view.jpg) |
| TDK01-1 | ไม่ผ่าน — ฝา/รอยต่อมีส่วนแทรก | ทรงกระบอกพื้นฐานเท่านั้น; ภาพ top สี Blue พบวงโลหะจากรอยต่อฝาตัดผ่านบริเวณปุ่มทอง เพราะวงแหวนอยู่ผิดระนาบ; ปุ่มทอง/หน้าจอยังไม่มีหลักฐานจากภาพสินค้าที่อยู่ในกล่อง และผิวฝาไม่ต่อเนื่องกับภาพ | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-back-view.jpg) |
| TJS00-1 | ไม่ผ่าน — ชิ้นส่วนคนละแบบ | ต้นฉบับเป็นแก้วทรงสอบ มีร่องข้าง ฝาอ่อน/ตัวล็อกม่วง สายคล้องและสีไล่ระดับ; โมเดลเป็นกระบอกเรียบ ฝาดำและหูจับแข็งสีดำ ซึ่งไม่ปรากฏในภาพ | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TJS00-1-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TJS00-1-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TJS00-1-back-view.jpg) |
| TBY17-1 | ไม่ผ่าน — เปลือก/ขั้วสัมผัสผิด | โมเดลเป็นท่อ U หน้าตัดกลม ปลายเปิดเห็นโพรงและแผ่นสัมผัสจมตัดผิว ขณะที่ภาพมีเปลือกด้านนอกทรงโค้งแบน ปลายมนปิดและแผ่นสัมผัสด้านใน; ท่าหงายกลับจากภาพและไม่มีชิ้นดำด้านในตามต้นฉบับ | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TBY17-1-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TBY17-1-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TBY17-1-back-view.jpg) |
| TN00-2 | ไม่ผ่าน — แก้วและฐานผิด | ไม่มีฝาและทรงโค้งของแก้ว; หูเป็นท่อดำวางผิดแนวฝังอยู่ผิวด้านข้าง แทนหูสีขาวที่ยื่นจับได้; ฐานเป็นแผ่นสี่เหลี่ยมดำ แทนฐานสีขาวทรงมนพร้อมรายละเอียดอุ่นแก้ว | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TN00-2-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TN00-2-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TN00-2-back-view.jpg) |
| TNA0014 | ไม่ผ่าน — รูปทรงไม่ใช่ปกตามภาพ | ภาพคือปกสมุดสีดำมีลายผิว ตะเข็บ แถบปิดและรายละเอียดมุมล่าง; โมเดลมีแผ่นทองขนาดใหญ่ด้านนอกและวงแหวนทะลุหน้า–หลัง เห็นชัดจากด้านข้าง; แถบปิดและตะเข็บหาย | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-back-view.jpg) |
| TZJ00-1 | ไม่ผ่าน — ชุดพับ/ยึดหาย | ภาพแสดงชุดพับ/ชิ้นยึดหลายส่วนกลางบอดี้ แต่โมเดลเป็นกล่องเรียบพร้อมปุ่มและสายโค้งสองข้างซึ่งภาพนี้ไม่ยืนยัน; เปิดสี White ให้ตรงต้นฉบับแล้วยังเห็นว่าชิ้นส่วนหลักหาย | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-back-view.jpg) |
| TYS01-1 | ไม่ผ่าน — สภาพพับไม่ตรง | ภาพแสดงร่มพับเป็นแท่งสั้นเก็บในปลอกทรงกระบอก มีส่วนหัวดำและปุ่ม; โมเดลมีแกนโลหะและมือจับยื่นลงมา พร้อมวงเหลี่ยมสีทองกลางแท่งที่ไม่ปรากฏในภาพ | [มุมเริ่มต้น](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TYS01-1-default-view.jpg) · [ด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TYS01-1-side-view.jpg) · [ด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TYS01-1-back-view.jpg) |

## ข้อค้นพบร่วมและลำดับแก้

1. เริ่ม TN00-2 ให้มีแก้ว/ฝา/หู/ฐานตามภาพ แล้วตรวจ screenshot คู่รายมุมก่อนขยายรุ่นอื่น.
2. แก้ TJS00-1, TBY17-1, TNA0014, TZJ00-1 และ TYS01-1 ซึ่งโครงสร้างหรือชิ้นส่วนหลักผิด/ขาด; ไม่ใช้การเปลี่ยนสีแก้ปัญหารูปทรง.
3. แก้ TDK01-1 เรื่องระนาบวงแหวน/ฝา และ W502 เรื่องขาตั้งแบบกรอบเปิด.
4. เก็บรายละเอียด S1033/DW03 และวัสดุ/หลักฐานฝา BW00-0.
5. เพิ่มขั้นตรวจคู่ภาพจริงก่อนเผย index รอบถัดไป; geometry validation กับ visual QA ต้องมีผลแยกกัน.

P8 generator ใช้ primitive ที่ผูกกับ kind ของสินค้าและค่าเดา แต่ไม่ได้ทำชิ้นส่วนให้ตรงภาพรายรุ่น. ตัวอย่างที่ตรวจจาก code: TJS00-1 เพิ่ม torus handle, TN00-2 ใช้วัสดุ detail สีดำทั้งหูและฐาน, TNA0014 หมุนวงชาร์จเข้าระนาบที่ตัดผ่านปก, TDK01-1 วงรอยต่อฝาไม่ได้หมุนเข้าแนวนอน. builder ตั้ง review-ready หลังผ่าน technical checks อัตโนมัติ. รายละเอียด [RCA](O:/Org-EtohGroup/SmartGift/.brain/rca/RCA-CATALOG3D-VISUAL-QA-GAP-2026-08-31.md).

ภาพ BW00-0 ในแผงเทียบสูงล้น viewport ทำให้เทียบทั้งชิ้นยาก. เป็นข้อจำกัด UI แยกจากความถูกต้องของ GLB; รอบนี้ไม่ได้แก้ CSS.

## หมวดและ canonical coverage

| หมวด | Canonical ProductMaster | Candidate ที่ viewer แสดง | local-ready |
|---|---:|---|---:|
| Eco-Friendly | 4 | BW00-0, TDK01-1, TYS01-1 | 0 |
| Classic Oriental | 3 | ไม่มี | 0 |
| Novelty Self-Care | 5 | TJS00-1, TBY17-1, TN00-2 | 0 |
| Executive Smart Tech | 4 | W502, TNA0014, TZJ00-1 | 0 |

S1033 และ DW03 แสดงใน “ทั้งหมด” เพราะ candidate category ยัง null ตาม index. Candidate 11 รายการไม่เท่ากับ ProductMaster 11 ตัวที่เสร็จ; coverage canonical ยังคง 16 held / 0 local-ready. รุ่นที่ยังไม่มี GLB ไม่สามารถตรวจภาพโมเดลได้ในรอบนี้ และไม่ถูกนับว่าตรวจ geometry แล้ว.

[ภาพ Classic Oriental ที่ไม่มีโมเดล](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/category-classic-oriental-empty-view.jpg) · [manifest พร้อม SHA-256 ทุกรูป/GLB/reference](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/audit-manifest.json)

## แกลเลอรีครบ 11 รุ่น

### S1033 — ต้องเก็บรายละเอียด/ยืนยันเพิ่ม

บอดี้ วงกลมด้านหน้า สายสองข้างและขาตั้งพอจำแนกได้ แต่ปลาย connector และรายละเอียดวงกลมถูกย่อเป็นรูปทรงทั่วไป สี/โลหะไม่เหมือนในภาพทั้งหมด; ภาพอ้างอิงมุมเดียวความละเอียดต่ำยังยืนยันด้านหลังและบานพับไม่ได้

สิ่งที่ต้องแก้: ปรับปลายสายและผิวหน้าตามส่วนที่เห็นจริง แล้วตรวจขาตั้งกับภาพเพิ่ม; ยังไม่ผ่านตรวจรับ

![S1033 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/S1033-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/S1033-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/S1033-back-view.jpg)

### DW03 — ต้องแก้รายละเอียด

รูปทรงหลักและสายสี่เส้นพอใกล้เคียง แต่เมื่อมองด้านหลัง หัว USB ที่มีแถบทองอยู่ซ้ายในโมเดล ขณะที่ภาพต้นฉบับอยู่ขวา; หัวอื่น ๆ เป็นก้อนดำและผิวส้มเหลือง/เงาต่างจากภาพ

สิ่งที่ต้องแก้: แก้ลำดับหัวสายเมื่อมองด้านหลัง รายละเอียดหัวต่อและวัสดุ; ไม่ใช้การ flip ภาพอ้างอิงเพื่อให้ดูตรง

![DW03 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/DW03-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/DW03-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/DW03-back-view.jpg)

### W502 — ไม่ผ่าน — ขาตั้งผิดโครงสร้าง

ภาพต้นฉบับแสดงขาตั้งแบบกรอบเปิด แต่โมเดลเป็นแผ่นทึบ; ภาพด้านข้างแสดงท่าตั้งที่ฐานขาเลยใต้บอดี้ และแถบใต้แผ่นชาร์จเป็นสี่เหลี่ยมยาวแทนปุ่มโค้งสั้น

สิ่งที่ต้องแก้: ขึ้นขาตั้งและส่วนปุ่มหน้าใหม่ตามภาพ จัดระดับฐาน/มุมตั้งให้สัมพันธ์กัน

![W502 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/W502-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/W502-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/W502-back-view.jpg)

### BW00-0 — ต้องแก้วัสดุ/ยืนยันฝา

ทรงกระบอกและรอยต่อฝาพอใกล้ภาพ แต่สีดำใน viewer สูญเสียรายละเอียดผิวและขอบ; มุม Silver/top แสดงจอเป็นวงดำเล็ก ซึ่งภาพต้นฉบับด้านหน้าที่ใช้เทียบยังยืนยันรูปแบบบนฝาไม่ได้; รูปต้นฉบับสูงล้น viewport

สิ่งที่ต้องแก้: ปรับแสง/วัสดุให้เห็นส่วนประกอบ และตรวจฝาจากภาพด้านบนเมื่อมี; ไม่เดาตัวเลขบนจอ; ปรับการ fit ภาพเทียบภายหลัง

![BW00-0 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-back-view.jpg)

### TDK01-1 — ไม่ผ่าน — ฝา/รอยต่อมีส่วนแทรก

ทรงกระบอกพื้นฐานเท่านั้น; ภาพ top สี Blue พบวงโลหะจากรอยต่อฝาตัดผ่านบริเวณปุ่มทอง เพราะวงแหวนอยู่ผิดระนาบ; ปุ่มทอง/หน้าจอยังไม่มีหลักฐานจากภาพสินค้าที่อยู่ในกล่อง และผิวฝาไม่ต่อเนื่องกับภาพ

สิ่งที่ต้องแก้: แก้ระนาบรอยต่อฝาและสัดส่วนฝา; เอารายละเอียดที่ไม่มีหลักฐานออกหรือแยกให้ผู้ใช้เลือกอย่างชัดเจนก่อนสร้าง

![TDK01-1 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-back-view.jpg)

### TJS00-1 — ไม่ผ่าน — ชิ้นส่วนคนละแบบ

ต้นฉบับเป็นแก้วทรงสอบ มีร่องข้าง ฝาอ่อน/ตัวล็อกม่วง สายคล้องและสีไล่ระดับ; โมเดลเป็นกระบอกเรียบ ฝาดำและหูจับแข็งสีดำ ซึ่งไม่ปรากฏในภาพ

สิ่งที่ต้องแก้: สร้างทรงสอบ ร่อง ฝา/ตัวล็อกและสายคล้องใหม่; ลบหูจับที่แต่งขึ้นและแบ่งวัสดุตามภาพ

![TJS00-1 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TJS00-1-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TJS00-1-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TJS00-1-back-view.jpg)

### TBY17-1 — ไม่ผ่าน — เปลือก/ขั้วสัมผัสผิด

โมเดลเป็นท่อ U หน้าตัดกลม ปลายเปิดเห็นโพรงและแผ่นสัมผัสจมตัดผิว ขณะที่ภาพมีเปลือกด้านนอกทรงโค้งแบน ปลายมนปิดและแผ่นสัมผัสด้านใน; ท่าหงายกลับจากภาพและไม่มีชิ้นดำด้านในตามต้นฉบับ

สิ่งที่ต้องแก้: สร้างเปลือกและปลายปิดเป็นชิ้นจริง จัดแผ่นสัมผัส/แผ่นรองตามภาพ และตรวจแกนมิติก่อน export

![TBY17-1 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TBY17-1-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TBY17-1-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TBY17-1-back-view.jpg)

### TN00-2 — ไม่ผ่าน — แก้วและฐานผิด

ไม่มีฝาและทรงโค้งของแก้ว; หูเป็นท่อดำวางผิดแนวฝังอยู่ผิวด้านข้าง แทนหูสีขาวที่ยื่นจับได้; ฐานเป็นแผ่นสี่เหลี่ยมดำ แทนฐานสีขาวทรงมนพร้อมรายละเอียดอุ่นแก้ว

สิ่งที่ต้องแก้: สร้างแก้ว ฝา หูและฐานใหม่จากภาพที่เห็น; ตรวจการเชื่อมต่อหูและแยกสีของชิ้นส่วน

![TN00-2 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TN00-2-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TN00-2-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TN00-2-back-view.jpg)

### TNA0014 — ไม่ผ่าน — รูปทรงไม่ใช่ปกตามภาพ

ภาพคือปกสมุดสีดำมีลายผิว ตะเข็บ แถบปิดและรายละเอียดมุมล่าง; โมเดลมีแผ่นทองขนาดใหญ่ด้านนอกและวงแหวนทะลุหน้า–หลัง เห็นชัดจากด้านข้าง; แถบปิดและตะเข็บหาย

สิ่งที่ต้องแก้: สร้างปกภายนอกให้ตรงภาพก่อน แยกหน้าในจากภาพด้านใน; เอาวงแหวนลอยและแผ่นทองที่ไม่มีในภาพปกออก

![TNA0014 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-back-view.jpg)

### TZJ00-1 — ไม่ผ่าน — ชุดพับ/ยึดหาย

ภาพแสดงชุดพับ/ชิ้นยึดหลายส่วนกลางบอดี้ แต่โมเดลเป็นกล่องเรียบพร้อมปุ่มและสายโค้งสองข้างซึ่งภาพนี้ไม่ยืนยัน; เปิดสี White ให้ตรงต้นฉบับแล้วยังเห็นว่าชิ้นส่วนหลักหาย

สิ่งที่ต้องแก้: ตรวจว่าส่วนที่เห็นเป็นขาตั้ง/ชุดจับชนิดใดแล้วขึ้นรูปชิ้นส่วนนั้น; อย่าอนุมานจากชื่อ cable-powerbank

![TZJ00-1 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-back-view.jpg)

### TYS01-1 — ไม่ผ่าน — สภาพพับไม่ตรง

ภาพแสดงร่มพับเป็นแท่งสั้นเก็บในปลอกทรงกระบอก มีส่วนหัวดำและปุ่ม; โมเดลมีแกนโลหะและมือจับยื่นลงมา พร้อมวงเหลี่ยมสีทองกลางแท่งที่ไม่ปรากฏในภาพ

สิ่งที่ต้องแก้: ขึ้นรูปสภาพพับเก็บตามภาพปลอก/หัว/ปุ่ม ปรับสีรายชิ้น และตัดแกนยื่น/วงทองที่ไม่มีหลักฐาน

![TYS01-1 เทียบภาพต้นฉบับ](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TYS01-1-default-view.jpg)

[เปิดภาพด้านข้าง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TYS01-1-side-view.jpg) · [เปิดภาพด้านหลัง](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TYS01-1-back-view.jpg)

## ภาพตรวจเฉพาะจุด

### TNA0014 — วงแหวนทะลุหน้าและหลัง

![TNA0014 side](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TNA0014-side-view.jpg)

### TDK01-1 — วงแหวนตัดผ่านฝา

![TDK01-1 top](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TDK01-1-blue-top-view.jpg)

### BW00-0 — เปลี่ยนเป็น Silver เพื่อดูฝา ไม่ใช่ยืนยันสีในภาพต้นฉบับ

![BW00-0 top](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/BW00-0-silver-top-view.jpg)

### TZJ00-1 — White ตามภาพอ้างอิงก็ยังขาดชุดพับ

![TZJ00-1 White](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/TZJ00-1-white-view.jpg)

## Version diff / CHANGELOG

ไม่มีรายงาน → 1.0.0b: เพิ่ม visual audit จาก screenshot จริงครบ 11 รุ่น พร้อม 37 ภาพและข้อบกพร่อง; ไม่แก้ app/GLB/index และไม่ให้ผ่าน canonical/public gate.

| Version | Date | Status | Summary | Agent |
|---|---|---|---|---|
| 1.0.0b | 2026-08-31 | need review | Visual audit 11 models; 37 screenshots; technical pass is not likeness acceptance | ATHER |
