---
version: "0.1.0b"
created_at: "2026-08-30T17:28:00+07:00,ATHER,uncommitted"
last_update: "2026-08-30T17:28:53+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-production"
  scope: "internal-only; creative proof v0.2"
  language: "th"
---

# รายงานส่งมอบ SmartGift catalog creative proof v0.2

## ผลผลิต

- [PDF A4 แนวนอน 12 หน้า](../pdf/smartgift-catalog-adcreative-proof-v0.2.pdf): 297 × 210 มม. ทุกหน้า, PDF 1.7, 4,035,654 bytes
- PDF SHA-256: `91d8e8f355d6d1752715d87649992ab1bae021b3e90c072f46d0221b94efffbf`
- [ZIP ภาพ ad creative 4 เซ็ต](../artwork/smartgift-adcreative-4sets-v0.2.zip): PNG 1536 × 1024 px ต่อภาพ พร้อมคำอธิบายสถานะ proof, 9,064,013 bytes; ไม่รวม prompt/source path/hash/manifest ภายใน
- [Production manifest](production-manifest.json), [build report](pdf-build-report.json), [artwork package report](artwork-package-report.json) เป็นเอกสารภายใน ไม่ส่งหรือแนบไปกับ PDF ลูกค้า

## Coverage

| PDF | รายการ |
|---|---|
| หน้า 4–7 | FXD66-3, TMK00-4, FXD6064, TGC09-3: 1 ad creative ต่อเซ็ต |
| หน้า 8 | S-1052, BST61401, DW03: 3 รุ่น |
| หน้า 9 | UT3056, S1033, W502: 3 รุ่น |
| หน้าอื่น | ปก, Recipient-first / ระดับการดูแล, สารบัญภาพ, unboxing, gifting brief และปกหลัง |

เป็นเล่มคัดเลือก 4 เซ็ตกับสินค้าเดี่ยว 6 รุ่น ไม่ใช่สินค้าทั้งหมด ไม่อ้าง coverage ทุกหมวด และไม่ใช่เล่มขยาย 24 หน้าที่เคยเสนอ

## ผลตรวจ

- Source PDFs 9/9 ไฟล์มี SHA-256 ตรงกับก่อนผลิต รวม 5 concept PDFs และ 4 product catalogs ดู [source integrity](source-integrity-check.json)
- [Content audit](final-content-audit.json): PASS; หน้า 12/12 ขนาด A4 landscape, extract ภาษาไทยได้ทุกหน้า, ไม่มี replacement/null characters, Leelawadee UI regular/bold ฝังครบ 2 font resources และไม่มี Helvetica ที่ไม่ฝัง
- Bookmarks 12 จุดตรงหน้า 1–12; links 4 จุดในสารบัญหน้า 3 ชี้หน้า 4–7 โดย rectangle อยู่ในหน้า
- Text/metadata/object-string audit ไม่พบ source paths, hashes, cost/provenance fields, email/phone patterns; ไม่มี attachments, Filespec, embedded files, forms หรือ XMP ประกอบการตรวจภาพที่ใช้จริง ไม่ถือ text scan เพียงอย่างเดียวเป็นการรับรองข้อมูลใน raster
- Render PDF ฉบับ hash ข้างต้นครบ 12 หน้าเป็น PNG ที่ด้านยาว 1600 px; ตรวจภาพรายหน้า ไม่พบข้อความทับ/ตกขอบ วรรณยุกต์ถูกตัด รูปบิด หรือเลขหน้าผิด
- หน้า 1–6 ผ่าน [independent visual review](final-visual-audit-pages-1-6.md); เพิ่ม contrast หน้า 4/6 ตามข้อทักท้วงและตรวจซ้ำแล้ว หน้า 7–9 ตรวจโดยผู้ประกอบเล่ม; หน้า 10–12 มี independent visual review ยืนยันครบ 1 set / 4 brief topics / 4 set thumbnails ตามลำดับ
- หน้า 8–9 มี 3 รุ่นต่อหน้าและระบุภาพหลายมุมเป็นรุ่นเดียวกัน; หน้า 9 ระบุ UT3056 / S1033 “ปรับภาพด้วย AI” เพื่อไม่สื่อว่าพิกเซลสินค้าไม่เปลี่ยน
- บีบอัดเฉพาะสำเนาภาพที่ฝังใน PDF เป็น JPEG quality 95, subsampling 0 โดยไม่ resize; PNG ที่สร้างและ crop ต้นทางยังอยู่ครบ ไม่มีการ upsample หลังสร้าง
- ZIP ตรวจ CRC ผ่าน มี PNG 4 ไฟล์และ README เท่านั้น; PNG ไม่มี metadata fields และ hash ตรงกับภาพที่เลือก

## ข้อจำกัดและงานที่ไม่ได้ทำ

1. ภาพเซ็ตต้นทางกว้าง 236–352 px รูปทรงหลัก/สี/จำนวนสินค้าตรวจเทียบแล้ว แต่ AI สร้างรายละเอียดอักษร ลายพิมพ์ พอร์ต และวัสดุบางจุดใหม่ ไม่ใช่หลักฐานความเหมือนทุกจุดหรือสเปกการผลิต
2. FXD6064 มีการ์ดอวยพรในคำบรรยาย catalog แต่ไม่แยกเห็นในรูปชัด จึงไม่ได้สร้างการ์ดเพิ่มเอง
3. ภาพเซ็ตเมื่อวางเต็มความกว้าง A4 มีประมาณ 131 ppi ต่ำกว่าเป้าหมาย digital 150–200 ppi และ print 300 ppi; ขยายภาพไม่เพิ่มข้อมูลสินค้าจริง
4. ยังไม่ยืนยันสิทธิ์เผยแพร่ภาพ สเปก/stock/ราคา โลโก้ และช่องทางติดต่อ จึงใช้คำว่า “สอบถามราคา” และไม่สร้าง contact/claim เอง
5. ไม่มี printer ICC/output intent, bleed, PDF/X หรือ PDF/UA preflight และไม่ได้ตรวจปรู๊ฟกระดาษจริง; **ไม่ใช่ print-ready**
6. ใช้รหัส/ภาพ/คำบรรยายจากหน้า PDF ต้นทางตรงกันเป็น product lineage สำหรับ proof นี้ ไม่ใช้ canonical BOM ที่พบความขัดแย้ง ดู [RCA](../../.brain/rca/RCA-CATALOG-ASSET-SOURCE-VALIDATION-2026-08-30.md)
7. ไม่แก้ application code, schema, pipeline, master, raw, ราคา, inventory หรือ vault; ไม่รัน master pipeline/unit suite เพราะไม่มี domain logic change; ไม่ commit/push/deploy/เผยแพร่ภายนอก
8. คง deleted blueprint ที่ path เดิมและ untracked concept directory ซึ่งมีอยู่ก่อน ไม่ restore/move; ไม่ลบ `tmp/pdfs/business-pages` เพราะยังยืนยัน ownership ไม่ได้

## การแก้เล่มต่อ

ข้อมูลจัดหน้าอยู่ใน `production-manifest.json` และ `build_catalog.py` เป็นเครื่องมือผลิตเอกสารเฉพาะงานนี้ ไม่ได้เชื่อม pipeline หรือแก้เว็บ การ rebuild ใช้ bundled Python + ReportLab และ task-local `python-deps/uharfbuzz`; ต้อง render/audit ใหม่เมื่อแก้ไฟล์ ข้อความ สินค้า หรือภาพ เพราะรายงานนี้อ้าง PDF hash เดียวที่ระบุข้างต้น

## Version diff

`0.1.0b candidate` ของ design spec → `0.2.0b beta`: เปลี่ยนจาก wireframe เป็น PDF proof 12 หน้า เพิ่มภาพ ad creative จาก catalog จริง 4 เซ็ต และจำกัดสินค้าเดี่ยวหน้าละ 3 รุ่น คงขอบเขต proof และไม่อนุมัติ commercial claims หรือการเผยแพร่

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | beta | บันทึกผลผลิตและผลตรวจ PDF/ภาพ พร้อมข้อจำกัดของ creative proof v0.2 | uncommitted | ATHER |
