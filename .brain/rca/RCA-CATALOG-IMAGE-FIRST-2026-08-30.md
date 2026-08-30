---
version: "0.1.3b"
created_at: "2026-08-30T11:06:00+07:00,ATHER"
last_update: "2026-08-30T21:25:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "catalog-ui"
  scope: "localhost:5180/#/catalog; diagnosis and local presentation follow-up"
  language: "th"
---

# RCA: หน้า catalog อ่านยากและภาพไม่สัมพันธ์กับสินค้าที่เลือก

## สถานะและขอบเขต

- Complexity: C-2; ความเสี่ยงการแก้ UI ที่เสนอ: MEDIUM เพราะเกี่ยวข้องกับการผูกภาพกับตัวตนสินค้าและการแสดงราคา
- รอบนี้ตรวจหน้าเว็บ โค้ด master JSON และภาพหน้าแรกของ PDF แบบ read-only; เพิ่มเอกสาร RCA นี้เท่านั้น
- ยังไม่อนุมัติ implementation, ไม่แก้โค้ด/ราคา/BOM/หมวดหมู่, ไม่รัน pipeline, ไม่ publish/deploy
- Working tree มีการแก้ค้างจากงานอื่น และ HEAD เปลี่ยนจาก `d820ef2` เป็น `b8feb5b` ระหว่างตรวจ จึงเป็นหลักฐานจาก working tree ขณะตรวจ ไม่ใช่ frozen release snapshot

## Symptom

ผู้ใช้ระบุว่า `http://localhost:5180/#/catalog` ดูไม่รู้เรื่อง พร้อมภาพกล่องแยกชั้น 2.5D และต้องการให้อิงสินค้าจริงใน catalog

หน้าเว็บให้พื้นที่หลักแก่กล่องกระจกเอียง ชื่อสินค้าบางส่วนถูกบังและตัด ส่วนรายการข้อมูลจริงอยู่ในแผงแยกจากภาพหลัก ทำให้ไม่ชัดว่ากำลังดูหมวดสินค้า ชุดใด หรือส่วนประกอบของชุดใด

## Evidence

| หลักฐาน | ผลที่ตรวจพบ |
|---|---|
| `public/index.html:297` และ `public/gift-anatomy-25d.js` | หมุนทั้ง deck ด้วย `rotateX(52deg) rotateZ(-26deg)` รวมถึงข้อความสินค้า และขยับมุมตามเมาส์ |
| `public/index.html:402-420` | label/spec ขนาดเล็กและตัดด้วย ellipsis; ภาพผู้ใช้และ screenshot จากหน้าปัจจุบันยืนยันว่าอ่านรายละเอียดได้ยาก |
| `public/index.html:452-464`, `1137-1145` | ฝาครอบมี `backdrop-filter: blur(10px)` และอยู่เหนือชั้นสินค้า; screenshot ยืนยันว่าบัง/ทำข้อความด้านล่างพร่า |
| `public/index.html:1034-1124` | สินค้า 8 รายการ ชื่อ ราคา และ emoji เขียนตายตัวใน HTML ไม่ได้สร้างจาก master; stage มี `<img>` จำนวน 0 |
| เปลี่ยนหมวดด้วยปุ่ม `Novelty & Lifestyle` | สถานะเปลี่ยนหมวดและรายการด้านข้างนับได้ 94 รายการ แต่ stage ยังคง 8 SKU เดิมจาก Tech/Eco/Craft |
| `public/index.html:1348-1371` | `renderCategoryView` เปลี่ยนข้อความ/สถานะหมวด และรายการด้านข้าง ไม่ได้สร้างสินค้าใน stage ตามหมวด |
| `public/index.html:1790-1797` | คลิกชิ้นส่วนแล้ว map SKU กลับเป็นหมวด ไม่ใช่เปิดรายละเอียดสินค้าหรือ BOM ของ offer ที่เลือก |
| ทัมเบลอร์ `PM-TMB` | stage แสดง ฿150 แต่ master และรายการด้านข้างแสดง SRP ฿320; เป็นหลักฐานความขัดแย้งของการแสดงผล ไม่ใช่การรับรองว่าราคาใดพร้อมเสนอขาย |
| `data-pipeline/02_prepared/smartgift_catalog_master.json` | มี 16 canonical products และ 357 offers; ไม่พบ property ชื่อ image/photo/thumbnail ใน records สองกลุ่มนี้ |
| `data-pipeline/01_raw/SmartGift_2026_Portfolio_Blueprint.pdf` | 12 หน้า; ตรวจภาพหน้า 1 พบเป็นเอกสาร Recipient-First Blueprint ไม่ใช่หลักฐานภาพต่อ SKU โดยตัวมันเอง |
| `data-pipeline/01_raw/02_factory_pricelists_pdf/SmartGift-Premium_ใบราคาชุดของขวัญแปลไทย.pdf` | ตรวจภาพหน้า 1 พบภาพหน้าร้านและตารางสินค้าที่มีภาพประกอบ เป็นแหล่ง candidate สำหรับตามหาต้นฉบับภาพ ไม่ได้ตรวจรับ mapping ภาพกับทุก SKU แล้ว |

## Root Cause

1. **มุมมองหลักเป็นภาพจำลองที่แยกจากข้อมูลจริง:** HTML กำหนด 8 SKU เอง ขณะที่รายการด้านข้างใช้ master JSON จึงเกิดสองแหล่งข้อมูลที่ไม่สอดคล้องกัน ทั้งการเลือกหมวดและราคา
2. **องค์ประกอบตกแต่งทับเนื้อหาที่ต้องอ่าน:** ข้อความอยู่ใน plane ที่ถูกหมุน ฝ้ากระจกวางซ้อนด้านบน และชื่อใช้ ellipsis ทำให้ทั้งรูปลักษณ์และรายละเอียดสินค้าไม่ชัด
3. **ไม่มีการเชื่อมภาพต้นฉบับกับสินค้าใน renderer:** stage ใช้ emoji และ master ที่ตรวจไม่มี field ภาพต่อ record จึงยังไม่สามารถแสดงภาพสินค้าตรง SKU จาก catalog ได้โดยตรง
4. **พฤติกรรมคลิกไม่ตรงกับคำอธิบาย UI:** ข้อความบอกให้เลือกชิ้นส่วนเพื่อดู BOM แต่ event handler เปลี่ยนเพียงหมวด ไม่ได้เลือก offer หรือเปิด component detail

## Why the issue escaped detection

การค้นชุดทดสอบที่มีอยู่พบ tests ด้าน pricing, inventory, ingestion และโครงสร้าง master แต่ไม่พบ assertion เฉพาะหน้า anatomy สำหรับภาพจริง, ความตรงกันของราคา/หมวด, การเลือกชิ้นส่วน หรือภาพหน้าจอที่ตรวจการบังข้อความ จึงยังไม่มีหลักฐานว่าพฤติกรรม UI เหล่านี้ถูกป้องกันด้วย regression test

ไม่สรุปว่าไม่เคยมี manual QA เพราะรอบนี้ไม่มีหลักฐานประวัติการทดสอบทั้งหมด

## Proposed prevention (ยังไม่อนุมัติ)

[ASSUMPTIONS]

1. เป้าหมายของผู้ใช้คือเห็นว่าสินค้าคืออะไรจากภาพจริง และเข้าใจว่าชุดหนึ่งมีอะไรบ้าง ไม่ใช่เพียงปรับความสวยงามของกล่องจำลอง
2. ผู้ใช้ยืนยันแล้วว่าเป็นหน้าสำหรับ **ลูกค้า**; การจัดลำดับราคา/รหัส/รายละเอียด sourcing จะเสนอในแบบลูกค้าแยกจากมุมมองทีมภายใน ยังไม่ถือว่าอนุมัติ implementation

ทิศทางสำหรับทบทวนหลังยืนยันบริบท:

- ให้ภาพสินค้าจริง ชื่อภาษาไทย และรหัสสินค้าอยู่ในแนวตรง อ่านได้โดยไม่ต้องหมุนหรือเลื่อนชั้นกล่อง
- เลือกหมวดแล้วภาพและรายการต้องเปลี่ยนตรงกัน โดยอ้าง identity จากข้อมูลชุดเดียวกัน
- ถ้าเลือก offer ให้แสดงภาพของชุดนั้นและส่วนประกอบจาก `components`; ถ้าเลือกสินค้ารายชิ้นให้เปิดรายละเอียดของ SKU นั้น ไม่เปลี่ยนเพียงหมวด
- ภาพต้องระบุ source path + หน้า + รหัสที่ใช้จับคู่; ภาพหน้ารวมต้องแยกจากภาพ SKU และห้ามเอารูปสินค้าคล้ายกันหรือภาพที่สร้างขึ้นมาอ้างว่าเป็นสินค้าจริง
- ถ้ายังยืนยันภาพไม่ได้ ให้แสดงสถานะไม่มีภาพยืนยัน ไม่เติมรูปหรือ BOM ที่เดาเอง
- ไม่คัดลอกราคาจาก HTML ตายตัว; ตรวจ price authority จาก FlowAccount และ pricing calculator ตาม AGENTS ก่อนแสดงเป็นราคาพร้อมเสนอขาย
- แยกสินค้ารายชิ้นออกจากชุดของขวัญ และซ่อนข้อมูลเชิงเทคนิคที่ไม่จำเป็นไว้ในรายละเอียดตามกลุ่มผู้ใช้ที่ยืนยัน
- การเก็บ 2.5D เป็นมุมมองรองหรือถอดออกยังต้องยืนยัน ไม่ถือว่าอนุมัติลบทิ้งแล้ว

## Parent / peer impact

- รักษา 4 หมวดตาม ADR-001; ไม่เปลี่ยน taxonomy หรืออนุมานว่าสินค้าผ่านมาตรฐานสิ่งแวดล้อมจากการอยู่ในหมวด Eco
- ADR-002 เป็น candidate ตอนอ่านครั้งแรก แต่มีอีกงานแก้เอกสารนี้ระหว่างตรวจ จึงต้องอ่านสถานะ/ขอบเขตอนุมัติล่าสุดอีกครั้งก่อน implementation; ไม่อนุมานว่าการอนุมัติ SQL projection ครอบคลุม image mapping หรือราคา/BOM พร้อมขาย
- รักษา Zero-PII, price authority, stock constraints และขอบเขต cross-repo ใน AGENTS
- UI ใน `public/index.html` และ `public/gift-anatomy-25d.js` เป็นพื้นที่ implementation ที่อาจได้รับผลกระทบ; ต้องตรวจ diff ปัจจุบันอีกครั้งก่อนเริ่ม เพราะมีงานอื่นกำลังแก้ไฟล์
- หากต้องเพิ่ม image mapping contract ใน master/pipeline ให้เสนอเอกสาร/ADR แยกก่อน ไม่แทรก schema หรือรัน ingestion ในงาน UI โดยปริยาย

## Verification / acceptance / exit criteria ที่เสนอ

1. ผู้ใช้ยืนยันกลุ่มหลักเป็นลูกค้าแล้ว; `impeccable` setup ยังไม่มี PRODUCT.md จึงเสนอหลักการออกแบบที่เหลือให้ยืนยันก่อนบันทึก PRODUCT.md และเริ่ม implementation
2. ภาพทุกภาพที่แสดงว่าเป็นสินค้าจริงมีหลักฐานจับคู่ source/SKU; unresolved แสดงสถานะชัด
3. สลับครบ 4 หมวดแล้วภาพ ชื่อ จำนวน และรายการตรงกับข้อมูลอ้างอิง; ไม่มี stage ตายตัวข้ามหมวด
4. เลือก SKU/offer แล้วได้รายละเอียดตัวเดิมและ component quantity ตามข้อมูลที่ยืนยัน; ไม่มี BOM ที่สร้างจากการคาดเดา
5. ไม่มีราคาสองชุดขัดกัน และไม่มี fallback ราคา 0/สถานะ approved เมื่อข้อมูลไม่พอ
6. ตรวจ desktop/mobile, keyboard, focus, reduced motion และข้อความที่ไม่ถูกบังหรือตัดสาระสำคัญ
7. เพิ่ม regression checks ที่เกี่ยวข้อง แล้วรัน tests ตามความเสี่ยงหลังอนุมัติ implementation; รอบนี้ยังไม่ได้รัน suite และไม่อ้างว่า tests ผ่าน
8. ตรวจ scoped diff; ไม่แก้ raw Excel/PDF, ข้อมูลลูกค้า, vaults, pricing engine หรือไฟล์งานอื่น และไม่ deploy

## Audience clarification and next approval

ผู้ใช้ตอบ **“ลูกค้า”** เมื่อ 2026-08-30 จึงยืนยันผู้ใช้หลักแล้ว ไม่ถามเรื่องนี้ซ้ำ

ดูข้อเสนอที่ [CUSTOMER-CATALOG-IMAGE-FIRST](../../docs/specs/SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30.md) เพื่ออนุมัติรูปแบบลูกค้าและบริบทการออกแบบ คำตอบเรื่องกลุ่มผู้ใช้ไม่ถือเป็นการอนุมัติ code changes

## Version diff

### Follow-up หลังอนุมัติ implementation

ผู้ใช้อนุมัติ customer spec v0.1.0b ด้วย “ok” แล้ว ดูผล local partial และ verification ใน spec v0.1.1b; เนื้อหาด้านบนเป็นหลักฐานก่อนอนุมัติ ไม่ใช่สถานะปัจจุบัน

- ใช้ customer renderer แยกจากกล่อง hardcode โดยยังเก็บเส้นทางภายใน; ทำให้การเลือกหมวด/รายการใช้ข้อมูลจริงและเปิดรายละเอียดตรงรหัส
- ตรวจ media manifest ปัจจุบันได้ source-photo 4 รูป แต่รหัสไม่ตรง canonical/offer; ภาพ generated ถูกตัดออกจากหน้าลูกค้า เหลือ gallery ภาพอ้างอิงที่ระบุว่ายังไม่จับคู่ ไม่เดารหัส PM จากรูปลักษณ์
- พบหลักฐานเพิ่ม: `output/catalog-internal/production-manifest.json` และ `refs/set-TGC09-3-source.png` ระบุกระบอกน้ำ/สมุด/ปากกา แต่ master components เป็น PM-MSG/PM-PB10K; จึงปิดการอ้างส่วนประกอบที่ยังไม่ยืนยัน ไม่ซ่อม BOM ในงาน UI
- `catalog_offers` มีรายการ flash drive ด้วย จึงใช้ชื่อกลุ่มกลาง “รายการจากแคตตาล็อก” ไม่อ้างว่าทุก offer เป็นชุดจริง; ไม่เปลี่ยน taxonomy/source records
- Prevention: เพิ่ม regression tests 10 ข้อ, exact source-photo identity, data allowlist, unverified BOM/price gate; browser ตรวจ responsive, filters, pagination, modal close/focus, error/retry ตามผลใน spec
- **ยังไม่ปิด RCA ทั้งหมด:** image-to-master mapping, verified BOM/type, keyboard Escape UAT และ public-release gates ยังเหลือ ไม่อ้างว่า root causes ด้านข้อมูลได้รับการแก้ครบ

- ไม่มีเอกสารเดิม → `0.1.0b candidate`: เพิ่ม RCA, หลักฐานหน้าปัจจุบัน และแนวทางป้องกันเบื้องต้น
- `0.1.0b → 0.1.1b candidate`: บันทึกคำยืนยันว่าผู้ใช้หลักเป็นลูกค้า และเชื่อมข้อเสนอเพื่ออนุมัติ
- `0.1.1b candidate → 0.1.2b beta`: บันทึกผลหลังอนุมัติและ data gates ที่ยังไม่แก้
- Code/runtime: customer presentation + loopback preview; master data ไม่เปลี่ยนจากงานนี้

## CHANGELOG

### Follow-up ภาพจริงตามคำขอผู้ใช้

- สาเหตุที่ยังไม่มีภาพในรายการหลังเปลี่ยน UI: media source-photo เดิม 4 รหัสไม่ตรงรายการขาย; generated images ไม่ผ่าน source-photo gate จึงเหลือ placeholder อย่างถูกต้อง
- รอบนี้ตรวจ code column/ภาพแถวเดียวกันใน Business Gift PDF 80 หน้า ได้ 156 candidates; เว้น 5 รหัสที่ header ทับกับ TGC06-4 ซึ่งคำบรรยาย concept ขัดภาพ เหลือ 150 exact offer-code photos
- ดึง JPEG 148 + PNG 2 จาก embedded image bytes โดยไม่แต่งภาพและไม่แก้ raw PDF; ชื่อ source, หน้า, image object และ SHA256 ทุกภาพอยู่ใน customer spec v0.1.2b
- ใช้ media contract เดิม เชื่อม 150/357 offers และวางรายการมีภาพก่อนในกริด; ยังไม่มี PM mapping 16 รายการ ไม่ยืมรูปคล้ายกันและไม่อ้างว่าข้อมูลหก entities canonical ครบแล้ว
- Prevention เพิ่ม row-boundary/header exclusion tests และ regression ที่ตรวจ image identity, original byte hashes, stable photo-first order และ TGC09-3 conflict gate
- Visual QA พบ mobile rule เดิม width 64px ทับรูปการ์ดใหม่ จึงจำกัด rule นี้เฉพาะ placeholder; ตรวจซ้ำบน 390px รูปกว้าง 343px เท่าการ์ด ไม่ใช่ thumbnail 64px
- ตรวจ Node 13 tests + Python 36 tests ผ่าน (extraction 5, pricing/quote/inventory 31); รูป 150/150 decode ได้; PDF hash ก่อน/หลังตรงกัน
- ยังไม่ปิด RCA ด้านข้อมูล: ชื่อ/BOM/type ที่ไม่ยืนยัน, PM image mapping และ public/offline projection gates คงอยู่ ไม่รัน pipeline หรือ deploy ในงานนี้
- Version diff: RCA 0.1.2b → 0.1.3b; customer spec 0.1.1b → 0.1.2b; canonical schema 1.3.0 และ media contract 1.0.0b ไม่เปลี่ยน

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.3b | 2026-08-30 | beta | จับคู่ภาพต้นฉบับ 150 offers พร้อม provenance/tests; ไม่ promote BOM/PM/canonical readiness | uncommitted | ATHER |
| 0.1.2b | 2026-08-30 | beta | บันทึก local presentation และ regression evidence; ยังไม่ปิด image/BOM/public gates | uncommitted | ATHER |
| 0.1.1b | 2026-08-30 | candidate | บันทึกกลุ่มผู้ใช้หลักเป็นลูกค้า; ยังไม่แก้โค้ด | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | บันทึก root cause ของภาพ anatomy อ่านยาก ข้อมูลไม่สัมพันธ์กัน และช่องว่าง image mapping | uncommitted | ATHER |
