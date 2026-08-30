---
version: "0.1.0b"
created_at: "2026-08-30T17:00:04+07:00,ATHER,uncommitted"
last_update: "2026-08-30T17:00:04+07:00,ATHER"
status: "candidate"
superseded_by: null
attributes:
  domain: "catalog-media-provenance"
  scope: "Catalog source validation; out-of-scope pipeline findings; documentation only"
  language: "th"
---

# RCA: Catalog master และ path ภาพยังไม่ใช่หลักฐานพร้อมผลิตเล่ม

## สถานะและขอบเขต

- Complexity **C-2 / Risk LOW** สำหรับการบันทึก RCA นี้; การแก้ master/pipeline ไม่อยู่ในงานผลิต catalog และยังไม่ได้ดำเนินการ
- ผู้ใช้ยืนยันแนวทางผลิต: ใช้ภาพจริงจาก catalog เป็นต้นทาง สร้าง ad creative ต่อชุด และวางสินค้ารายชิ้น 2-3 รายการต่อหน้า การตรวจนี้รองรับการผลิตตามขอบเขตดังกล่าว ไม่ใช่การขออนุมัติแนวทางเดิมซ้ำ
- ตรวจเฉพาะ product/offer identity, components, image references และ product provenance; ไม่เปิด CRM และไม่ใช้ค่าราคา ต้นทุน กำไร หรือข้อมูลลูกค้าในข้อสรุป
- รอบนี้เพิ่มเอกสารไฟล์นี้เท่านั้น ไม่แก้ master, pipeline, application code, raw PDF/Excel หรือ vault และไม่รัน master pipeline
- หลักฐานเป็น local working-tree snapshot วันที่ 2026-08-30 เวลา 17:00 ICT ไม่ใช่ข้อสรุปว่าไม่มีภาพสินค้าใน PDF ต้นฉบับหรือในระบบอื่น

## Symptom

การนับจำนวน offer หรือการมี `components` / `image` เพียงอย่างเดียวทำให้ดูเหมือนมีรายการพร้อมจัดหน้า แต่บางองค์ประกอบไม่ตรงชื่อสินค้า และ path ภาพใน public projection ไม่ชี้ไปยังไฟล์ที่มีอยู่ในเครื่อง ณ เวลาตรวจ หากใช้ข้อมูลเหล่านี้สร้างภาพโดยไม่ย้อนตรวจ PDF จะเสี่ยงแสดงสินค้า จำนวนชิ้น และชุดของขวัญผิดรายการ

## Evidence

### จำนวนที่ตรวจแยกตามชนิดหลักฐาน

| แหล่ง/การตรวจ | จำนวน ณ ตรวจ | ความหมายและข้อจำกัด |
|---|---:|---|
| `smartgift_catalog_master.json`: canonical products | 16 | มี identity/name; ไม่ใช่จำนวนภาพจริงที่จับคู่เสร็จ |
| master เดียวกัน: catalog offers | 357 | มีรหัสและ `components` ทุกแถว |
| offer ที่ใช้ component signature เดียวกัน | 353 | `PM-MSG:1` และ `PM-PB10K:1`; ไม่ใช่หลักฐานว่าทั้ง 353 รายการเป็นชุดสองชิ้นนั้น |
| offer ที่มี page reference | 4 | `TGC06-4`, `TDD03-2`, `TMK0215`, `TWL01-8`; metadata ชี้ concept Blueprint ไม่ใช่ภาพ SKU ที่ตรวจรับแล้ว |
| `pricelist_public.json`: product masters / catalog offers | 427 / 1,110 | public identity projection คนละฐานกับ canonical 16/357; ห้ามนำจำนวนมาปะปน |
| public offers แยก `offer_kind` | set 1,080 / single 30 | เป็นค่าจำแนกในข้อมูล ไม่ใช่การตรวจภาพและจำนวนส่วนประกอบ |
| public offers ที่มี image reference | 994 | 994 path ไม่ซ้ำใน `/assets/products/catalog-2026/` |
| path ภาพดังกล่าวที่พบไฟล์จริงใต้ `public/` | 0 จาก 994 | ตรวจ resolve path + `Test-Path -PathType Leaf`; ไม่ได้ตรวจ media server ภายนอก |
| public offer statuses | auto 259 / flowaccount_only 94 / review_required 589 / unclassified 168 | status เหล่านี้ไม่ใช่ image/BOM clearance |
| source reference ของ SQL-derived offers | 1,110 | `source_ref.file = identity-review.json`; refs มี file/rowKey/hash แต่ไม่มี PDF page/crop mapping |
| รายการที่ตรวจรับครบ image + PDF page + code + contents จากการตรวจ master รอบนี้ | 0 | เป็นขอบเขตของการตรวจ master นี้เท่านั้น; งานผลิตยังค้นและตรวจภาพจาก raw PDF ได้ต่อ |

วิธีตรวจ: parse เฉพาะฟิลด์ที่เกี่ยวข้องจาก JSON, นับ array, จัดกลุ่ม component signature, จัดกลุ่ม offer kind/status/source reference และตรวจ file existence ของ image path โดยไม่ใช้ฟิลด์ราคา/ต้นทุน ไม่มีการรัน exporter หรือ ingestion

### หลักฐานระดับไฟล์และบรรทัด

| หลักฐาน | ผลที่ตรวจพบ |
|---|---|
| [intake](../../pipeline/01_intake.py), บรรทัด 50 และ 69-80 | เมื่อไม่พบ offer เดิม จะสร้าง record ใหม่และกำหนด `PM-MSG` กับ `PM-PB10K` อย่างละ 1 โดยตรง ไม่ได้ดึงรายการส่วนประกอบจาก source ของ offer นั้น |
| [canonical master](../../data-pipeline/02_prepared/smartgift_catalog_master.json), บรรทัด 1672-1687 | offer `444` ระบุว่าเป็นแฟลชไดร์ฟ แต่ components เป็นเครื่องนวดคอและ power bank |
| master เดียวกัน, บรรทัด 1786 และ 1793 | `MC00-1` มีชื่อชุด 6 ชิ้น แต่ component list ใช้ signature สองชิ้นเดียวกัน |
| master เดียวกัน, บรรทัด 3 และ 1384/1456/1528/1600 | metadata ชี้ `SmartGift_2026_Portfolio_Blueprint.pdf`; มี page reference เฉพาะสี่ offer ตั้งต้น จึงไม่ใช่ mapping ภาพจริงของ 357 offers |
| [public projection](../../public/data/pricelist_public.json), บรรทัด 6945-6952 | ตัวอย่าง `AS00-2` มี image path แต่ไฟล์ปลายทางไม่มีใน `public/` ณ ตรวจ |
| [exporter](../../pipeline/export_pricelist_master.py), บรรทัด 1256-1262 และ 1095-1098 | ส่งต่อ image field จาก imported offer ไปยัง master/public projection; path ที่เป็น string ไม่ใช่หลักฐาน asset existence หรือภาพตรงรหัส |
| [internal product provenance](../../data-pipeline/02_prepared/pricelist_master.json), บรรทัด 28709-28719 | `AS00-2` ย้อนถึง SQL table/key/statement line และ `identity-review.json / OFFER_AS00-2` ได้ แต่ ref นี้ไม่มี source PDF page/crop |

### ความขัดแย้งของ identity/contents ที่ต้องไม่รวมอัตโนมัติ

| รหัส | canonical concept/master | SQL-derived public identity | ผลต่อการผลิต |
|---|---|---|---|
| `TGC06-4` | ชื่อ Smart Notebook + Power Bank + Metal Pen; master บรรทัด 1384 เป็นต้นไป | Notebook + USB flash drive + bookmark + pen; public บรรทัด 13371-13379 | รหัสตรงกันแต่ contents ต่างกัน ต้องตรวจหน้า PDF จริงก่อนเลือกคำอธิบาย/ภาพ |
| `TMK0215` | ชื่อสมุด + ปากกาไม้ + ที่คั่น แต่ components เป็นปากกา + flash drive + tea infuser; master บรรทัด 1528-1547 | Coffee Cup + Power bank + Speaker + Wireless earbuds + Lighter; public บรรทัด 15303-15311 | ยังไม่มีฐานให้ใช้ชื่อหรือ BOM ฝั่งใดเป็นข้อเท็จจริงขายโดยอัตโนมัติ |
| `TWL01-8` | ชื่อเทียนหอม + แก้ว + สบู่ แต่ components มี aroma diffuser + coffee mug + neck massager; master บรรทัด 1600-1619 | ไม่ใช้ข้อมูลจากชื่อ concept เพื่อเติมของในชุด | ต้องยืนยันรายการจากภาพและข้อความต้นทาง ไม่ใช้ components เป็นคำรับรอง |

ชื่อและรหัสดังกล่าวเป็นหลักฐานความขัดแย้งและคำค้นสำหรับตามหาต้นฉบับ ไม่ใช่รายการชุดที่รับรองพร้อมใช้แล้ว

### Fingerprints ของข้อมูลที่ใช้ตรวจ

| ไฟล์ | SHA-256 |
|---|---|
| `data-pipeline/02_prepared/smartgift_catalog_master.json` | `63F3E5668DE6818CC3517543BDF0D1331BF7926D1769815290DBCD5F740C0AC7` |
| `data-pipeline/02_prepared/pricelist_master.json` | `D0CDE107F8351BF3E59487204987CFDE5584817CCBC2F1BC31A100691FBE447A` |
| `public/data/pricelist_public.json` | `68F80DB72D9DDE85C8014DCCD06219F6424686D4BA2A3E681B472FB4928A8783` |

## Root Cause

[ROOT CAUSE]

1. **Components ถูกสร้างจากค่าตายตัวแทนหลักฐานต่อ offer:** branch สำหรับ offer ใหม่ใน `pipeline/01_intake.py:50,69-80` กำหนด component สองตัวเดิมทุกครั้ง กลไกนี้อธิบาย signature ที่พบตรงกันใน 353 offers และตัวอย่างที่ไม่ตรงชื่อสินค้าได้โดยตรง
2. **การมี source identity/path ถูกตีความได้เกินหลักฐานที่เก็บ:** SQL provenance ย้อนถึง record ได้ แต่ไม่มีการเชื่อม PDF page/crop ใน refs ที่ตรวจ ขณะที่ exporter ส่งต่อ image string โดยขั้นตอนดังกล่าวไม่ได้พิสูจน์ว่ามีไฟล์จริงหรือเป็นภาพของรหัสนั้น ข้อมูลที่มีจึงยังไม่ใช่ media mapping ที่พร้อมใช้
3. **Concept กับ imported offer ใช้รหัสร่วมกันโดยมี contents ต่างกัน:** ตัวอย่าง `TGC06-4` และ `TMK0215` แสดงความขัดแย้งจริงระหว่างสอง projection การ match ด้วยรหัสอย่างเดียวจึงไม่พอสำหรับเลือกชื่อ ภาพ หรือส่วนประกอบ

ยังไม่มีหลักฐานว่าภาพ 994 ไฟล์เคยถูกสร้างแล้วถูกลบ หรือยังไม่เคยนำเข้า จึงไม่สรุปสาเหตุการไม่มีไฟล์บนดิสก์เป็นกรณีใดกรณีหนึ่ง และไม่สรุปประวัติการอนุมัติหรือเจตนาของผู้สร้างข้อมูล

## Why the issue escaped detection

- Component fallback ใช้รหัส ProductMaster ที่มีอยู่และ quantity เป็นบวกได้ แม้ความหมายของชุดผิด การผ่าน structure/reference checks จึงไม่พิสูจน์ semantic correctness; [exporter](../../pipeline/export_pricelist_master.py) บรรทัด 973-987 ตรวจ reference/identity/quantity ของ seasonal components แต่ไม่ได้เทียบภาพ source ของแต่ละชุด
- Public projection ที่มีชื่อและ image path ดูเหมือนพร้อมนำเสนอได้ แต่ field allowlist กับ record provenance แก้คนละปัญหากับการตรวจ asset existence และ source-image match
- Metadata ของ canonical master อ้าง Blueprint ในระดับไฟล์รวม ทำให้ผู้ใช้ downstream ไม่ควรอนุมานว่ามีหลักฐาน page/SKU สำหรับทุก imported row
- ไม่มีการตรวจประวัติ QA ทั้งหมดในงานนี้ จึงไม่กล่าวว่าไม่เคยมี manual review หรือ tests ใด ๆ มาก่อน

## Proposed prevention

### Workaround สำหรับงานผลิต catalog ที่ผู้ใช้ยืนยันแล้ว

1. ใช้ **source PDF + page + รหัสบนหน้า + ภาพ + ข้อความ** ที่ตรงกันเป็นหลักฐานต่อรายการ แยกชุดจริงกับสินค้ารายชิ้นก่อนจัดหน้า ไม่ดึง canonical fallback components มาบรรยายของในชุด
2. บันทึก product-only manifest สำหรับทีมภายใน: source file/hash/page, crop, source code, ชื่อที่ตรวจแล้ว และรายการ/จำนวนชิ้นที่มีข้อความรองรับ ใช้สถานะ `verified` เฉพาะขอบเขตที่ตรวจจริง; ถ้าข้อมูลไม่ครบให้เว้นรายละเอียดนั้นหรือข้ามรายการ ไม่เดา BOM จากภาพ
3. สร้าง ad creative โดย **reference ภาพจริงที่ผ่านการจับคู่**; เปลี่ยนฉาก องค์ประกอบแวดล้อม หรือการจัดแสงได้ตาม brief แต่ต้องไม่เปลี่ยนตัวสินค้า จำนวนชิ้น หรือเติมคุณสมบัติ ภาพ generated เป็นภาพนำเสนอ ไม่ใช่แหล่งความจริงของสินค้า และต้องตรวจเทียบต้นฉบับหลังสร้าง
4. ใช้ source crop/ภาพจริงเป็นจุดตรวจทานในขั้นผลิตและตรวจหน้าพิสูจน์ ไม่ใช้ภาพ generated ย้อนกลับไปยืนยัน SKU, สเปก วัสดุ จำนวนของในชุด หรือสิทธิ์การใช้ภาพ
5. สินค้ารายชิ้นวาง 2-3 รายการต่อหน้าตามที่ผู้ใช้ยืนยัน; creative ต่อชุดผูกกับชุดที่ยืนยันจริง จำนวนหน้าขึ้นกับ coverage ไม่เติมรายการให้ครบเป้าหมาย
6. เก็บ manifest/source evidence ใน `output/catalog-internal/` แยกจาก PDF ลูกค้า ไม่ฝัง source path/hash/provenance/supplier identity ใน PDF text, metadata หรือ attachments ตาม [ขอบเขต catalog](../../docs/specs/SPEC-SMARTGIFT-LANDSCAPE-CATALOG-2026-08-30.md) และ [ADR-004](../../docs/decisions/ADR-004-CUSTOMER-SAFE-PRICELIST-ENDPOINT.md)

### งานปรับข้อมูล/ระบบที่อยู่นอกขอบเขตนี้

- เสนอแผน repair แยกสำหรับการเอา fallback BOM ออกจากข้อมูลที่ยังไม่ยืนยัน พร้อมตรวจ downstream impact ก่อนเปลี่ยน master/pipeline
- เสนอ media/source contract แยกเมื่อจะนำ mapping เข้าระบบถาวร ให้มี source/page/crop/identity/rights และสถานะความครบถ้วน ไม่ถือว่าเอกสาร RCA นี้อนุมัติ schema หรือ engine change
- แยกการยืนยัน identity, source-image match, component semantics และ customer-safe release เป็นคนละ gate ไม่ promote ด้วย field presence หรือ `auto` status เพียงอย่างเดียว

## Verification และ Exit

- ยืนยันจำนวนและตัวอย่างจากฟิลด์ identity/components/media ที่ระบุข้างต้น และผูกกับ source fingerprints
- ตรวจลิงก์ไฟล์ใน RCA ให้ resolve ได้; ตรวจไม่มีข้อมูลลูกค้า ราคา ต้นทุน หรือกำไรในเอกสาร
- ไฟล์ master/pipeline/raw/vault ต้องไม่เปลี่ยนจากการเขียน RCA นี้ ไม่รัน unit suite/master pipeline เพราะไม่มีการแก้ domain logic
- Exit ของ RCA: บันทึกข้อค้นพบให้ทีมผลิตหลีกเลี่ยงแหล่งที่ยังไม่ยืนยัน งานผลิต PDF ดำเนินต่อได้จาก source PDF ที่ตรวจแล้ว; ไม่ประกาศว่า data repair หรือภาพครบทั้ง catalog เสร็จแล้ว

## Version diff

- ไม่มีเอกสารเดิม → `0.1.0b candidate`: เพิ่มหลักฐาน component fallback, image paths ที่ยังไม่พบไฟล์จริง, identity conflicts และ workaround สำหรับการผลิตจาก PDF ต้นทาง
- Master / pipeline / application code / raw / vault: ไม่มีการแก้จาก RCA นี้

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | candidate | บันทึก catalog asset/source validation และขอบเขตใช้ภาพ reference โดยไม่แก้ master/pipeline | uncommitted | ATHER |
