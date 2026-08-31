---
version: "1.0.0b"
created_at: "2026-08-31T17:22:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T17:22:00+07:00,ATHER"
status: "need review"
superseded_by: null
attributes:
  domain: "catalog3d-quality"
  scope: "Read-only visual audit; no model or application changes"
---

# RCA: โมเดล 3D ผ่าน technical tests แต่ไม่ตรงภาพสินค้า

## Symptom

Boss พบ TN00-2 มีหูแก้วสีดำผิดแนว ฝาหายและฐานไม่ตรงต้นฉบับ หลังส่งงาน P8 ว่าสร้าง GLB และตรวจแล้ว. ตรวจจริงต่อครบ 11 รุ่นพบ 8 รุ่นต้องแก้โครงสร้าง/ชิ้นส่วนหลัก และ 3 รุ่นต้องเก็บรายละเอียดหรือยืนยันหลักฐานเพิ่ม. ไม่มีรุ่นที่ให้ผ่าน visual acceptance ใน audit นี้.

## Evidence

- [รายงานและ screenshots](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/REPORT.md): 37 screenshots จาก in-app viewer เดิม; ตรวจ model ทุกตัวมุมเริ่มต้น/ด้านข้าง/ด้านหลัง เทียบ original reference ที่ viewer แสดง
- [manifest](O:/Org-EtohGroup/SmartGift/output/catalog-3d/visual-audit-2026-08-31/audit-manifest.json): GLB/reference hashes 11/11 ตรง index และ screenshot bytes/ขนาดครบ; ไม่มี model/index edit ระหว่าง audit
- [generator](O:/Org-EtohGroup/SmartGift/scripts/catalog3d/models-evidence-estimated.mjs:30): travel-mug สร้างหูจับทั้งที่ต้นฉบับ TJS00-1 เป็นสายคล้อง
- [TN00-2](O:/Org-EtohGroup/SmartGift/scripts/catalog3d/models-evidence-estimated.mjs:37): ฐานและหูใช้ material detail สีดำ, ไม่มี lid mesh, ตัวแก้วเป็น cylinder; screenshot ยืนยันความต่าง
- [TNA0014](O:/Org-EtohGroup/SmartGift/scripts/catalog3d/models-evidence-estimated.mjs:40): page-block สีทองอยู่ภายนอก และ torus หมุน Math.PI/2 รอบ X ทำให้วงทะลุหน้า/หลัง ต่างจากปกดำที่เห็นใน original
- [TDK01-1](O:/Org-EtohGroup/SmartGift/scripts/catalog3d/models-evidence-estimated.mjs:29): lid-seam torus ใช้ rotation default อยู่ระนาบ XY แทนระนาบรอยต่อแนวนอน; ภาพ top สี Blue เห็นส่วนโลหะแทรกผ่านฝา
- [test ใหม่ของ P8](O:/Org-EtohGroup/SmartGift/tests/catalog3d-evidence-estimated.test.mjs:6) ตรวจรายชื่อ recipe, จำนวน mesh/triangles และ geometry fingerprint หลังเปลี่ยนสี ไม่มี assertion ชิ้นส่วนสำคัญหรือการเทียบภาพ
- [builder](O:/Org-EtohGroup/SmartGift/scripts/catalog3d/build-evidence-estimated.mjs:34) ตรวจ visible_pixels และ triangle count แล้วกำหนด review-ready โดยไม่ต้องมี visual-review record รายรุ่น
- รันชุด tests เดิมใน audit นี้ยังผ่าน 30/30 แม้ screenshots แสดงชิ้นส่วนผิด/หาย จึงเป็นหลักฐานว่า test scope ไม่ครอบคลุม likeness

## Root Cause

Generator P8 นิยาม geometry ตามชนิดสินค้าแบบทั่วไปและค่าประมาณ แต่ไม่จัดส่วนประกอบตามภาพต้นฉบับจริงรายรุ่น. มีความผิดพลาดเฉพาะเรื่อง material assignment และระนาบ rotation ซึ่ง GLB validator ยอมรับเพราะโครงสร้างไฟล์ยัง valid.

ขั้นส่งงานใช้ความสำเร็จของ export/re-import/hash/nonblank render และการโหลด viewer เป็นหลักฐานเพียงพอ โดยไม่ได้เปิดดู screenshot เทียบ source ทีละรุ่น. ป้าย estimated และ pending owner review จึงไม่ได้ป้องกันการส่งชิ้นส่วนที่เห็นชัดในภาพผิดรูป. คำกล่าวก่อนส่งงานทำให้เข้าใจเกินขอบเขตที่ทดสอบจริง.

## Why the issue escaped detection

1. ไม่มี visual checklist ต่อรุ่นสำหรับ silhouette, ชิ้นส่วนที่มองเห็น, การเชื่อมต่อ, สีรายชิ้น และผิวทะลุ/ชิ้นลอย
2. การ render สี่มุมเป็นการสร้างไฟล์ภาพ; ไม่มีขั้นบังคับอ่านภาพเหล่านั้นเทียบกับ source ก่อนส่ง
3. Technical tests ตรวจเพียงรูปทรงไม่แบน/ไม่ NaN และจำนวนชิ้น ไม่ตรวจ open ends, self-intersections, plane orientation หรือชิ้นส่วนที่แต่งเพิ่ม
4. Builder ตั้ง review-ready จากผลเทคนิคโดยไม่แยก visual_checked/needs_rework ที่มีหลักฐาน screenshot
5. ไม่มีการแบ่งงานหนึ่งรุ่นแล้วตรวจ likeness ก่อนขยาย generator เจ็ดรุ่น

## Proposed prevention

- แก้และตรวจ TN00-2 รายรุ่นก่อน: แสดงภาพคู่มุมเดียวกันพร้อมส่วนประกอบที่ต้องมี และตรวจด้านข้างเรื่องหู/ฝา/ฐาน
- เพิ่ม visual review record แยกจาก glTF validation: reviewer, screenshot hashes, source hash, visible-feature checklist และผล needs_rework/visually_checked; owner approval ยังแยกต่างหาก
- ทดสอบเฉพาะ invariants ที่มีความหมายต่อ geometry: ระนาบวงแหวน, ฝา/หูที่เชื่อมกับตัวแก้ว, ปลายเปลือกปิด, ขาตั้งมีช่องเปิดตามภาพ; ไม่ใช้จำนวน meshes เป็นตัวแทนความเหมือน
- เก็บรุ่นเก่า immutable และทำ v002 ตาม scope ที่ได้รับอนุมัติเมื่อเริ่มแก้; ห้ามแทน screenshot ด้วยภาพ AI หรือแก้ภาพ source ให้เหมือนโมเดล
- ให้ผลเทคนิคและผล visual แยกในรายงานส่งงาน; อย่าให้ผ่าน customer-ready หรือ canonical identity จากการ export สำเร็จ

ข้อเสนอในหัวข้อนี้ยังไม่ได้ implement. รอบนี้เพิ่มเฉพาะ audit artifacts และ RCA ตามคำขอให้ตรวจพร้อม screenshots.

## Version diff / CHANGELOG

ไม่มี RCA → 1.0.0b: บันทึก visual evidence gap และข้อเสนอป้องกันจาก audit 11 รุ่น. ไม่มี code, GLB, schema หรือ publication changes.

| Version | Date | Status | Summary | Agent |
|---|---|---|---|---|
| 1.0.0b | 2026-08-31 | need review | Root cause and prevention from 37 screenshot audit | ATHER |
