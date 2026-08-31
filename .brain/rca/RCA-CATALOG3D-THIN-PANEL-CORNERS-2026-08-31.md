---
version: "0.1.0b"
created_at: "2026-08-31T04:35:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T04:52:05+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "product-3d-assets"
  language: "th"
---

# RCA — แผ่นบางยื่นนอกมุมมนใน pilot 3D

## Symptom

ภาพ `output/catalog-3d/DW03/v001/preview.png` และภาพหลังของทั้งสองรุ่นแสดงมุมแผ่นเหลี่ยมยื่นจาก body มน แม้ glTF validator ไม่มี errors/warnings

## Evidence

`models.mjs` ใช้ RoundedBoxGeometry กับแผ่นลึก 0.0005–0.0008 เมตร และจำกัด radius ด้วยครึ่งหนึ่งของด้านที่สั้นที่สุด มุมในระนาบ XY จึงเกือบเหลี่ยม แต่ body มี radius 5.2–6.5 มม. แผ่นขนาดใกล้ body จึงยื่นออกจาก silhouette ภาพ source ไม่มีมุมแผ่นลักษณะนี้

## Root Cause

ใช้ rounded solid สำหรับชั้น case-seam/back-cover/front-inset ที่ไม่จำเป็นและไม่มีหลักฐานชัดในภาพ; radius ผูกกับความหนาแกน Z แทน outline ใน XY

## Why the issue escaped detection

Unit tests และ glTF validator ตรวจ finite geometry/bounds/รูปแบบไฟล์ ไม่ตรวจ silhouette เทียบ reference จึงพบใน visual gate หลัง re-import ตาม SPEC 3D-08 ไม่ใช่ production regression

## Proposed prevention

ตัดชั้น generic ที่ไม่ได้รองรับด้วยภาพออก คง body และส่วนจำเพาะรุ่น; เพิ่ม test ห้ามแผ่น synthetic เหล่านี้กลับมา สร้าง version ใหม่โดยไม่เขียนทับ v001 และตรวจ render front/back/side อีกครั้ง ห้ามใช้ zero validator errors แทน likeness approval

เพิ่มเติมจาก `DW03/v003/preview-straight.png`: เห็นสี่เหลี่ยมจางตรงส่วนซ้อนของ charging-tail กับ charging-pad เพราะทั้งสองวาง front face ที่ Z เดียวกัน เกิด coplanar overlap โดย validator ไม่รายงาน เนื่องจากเป็นปัญหา render ไม่ใช่ invalid GLB แก้โดยวาง tail ต่ำกว่าหน้า disk และเพิ่ม regression test ตรวจ Z separation ก่อนสร้าง v004

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-31 | beta | บันทึกสาเหตุและการปรับใน approved pilot ก่อน owner review | uncommitted | ATHER |
