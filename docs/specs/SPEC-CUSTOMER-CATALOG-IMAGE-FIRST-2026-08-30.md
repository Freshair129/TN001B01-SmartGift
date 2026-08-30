---
version: "0.1.2b"
created_at: "2026-08-30T11:35:20+07:00,ATHER"
last_update: "2026-08-30T21:20:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "customer-catalog-ui"
  scope: "local catalog presentation; image-first customer browsing"
  language: "th"
---

# ข้อเสนอ: Catalog สำหรับลูกค้า เห็นสินค้าจริงและเข้าใจชุดของขวัญ

## สถานะและเป้าหมาย

**ผู้ใช้ยืนยัน:** หน้า `http://localhost:5180/#/catalog` มี **ลูกค้า** เป็นผู้ใช้งานหลัก และต้องอิงสินค้าจริงใน catalog

ผู้ใช้ตอบ **“ok”** อนุมัติข้อเสนอ v0.1.0b หลังยืนยันกลุ่มผู้ใช้เป็นลูกค้าแล้ว; Complexity **C-2**, Risk **MEDIUM** สำหรับการเปลี่ยน UI ไม่มี schema migration หรือ public deployment ในขอบเขต ปัจจุบัน implementation เป็น **local partial** ยังไม่ผ่านเกณฑ์จับคู่ภาพหนึ่ง SKU และหนึ่ง offer

ความสำเร็จ: ลูกค้ามองภาพแล้วรู้ว่าเป็นสินค้าอะไร แยกสินค้ารายชิ้นกับชุดของขวัญได้ และเปิดดูรายละเอียดของรายการที่เลือกได้ตรงตัว โดยไม่ต้องเข้าใจคำว่า ProductMaster, BOM, CBM หรือ Data Governance

หลักฐานปัญหาเดิมอยู่ใน [RCA v0.1.1b](../../.brain/rca/RCA-CATALOG-IMAGE-FIRST-2026-08-30.md): กล่องแสดง 8 รายการตายตัว ข้อมูลไม่เปลี่ยนตามหมวด ราคาไม่ตรงกับแผงข้อมูล และฝ้ากระจกบังตัวอักษร

## บริบทการออกแบบที่เสนอให้ยืนยัน

ตาม `impeccable` ได้รับคำตอบเรื่องกลุ่มเป้าหมายและการอนุมัติบริบทต่อไปนี้แล้ว จึงบันทึกใน PRODUCT.md โดยไม่รีแบรนด์หรือเพิ่มขั้นตอนซื้อขาย:

- **Register:** brand สำหรับ customer catalog/showroom ของ SmartGift; ไม่ใช่ dashboard จัดการคลัง
- **Users / purpose:** ลูกค้าองค์กรเลือกดูสินค้าและชุดของขวัญก่อนคุยรายละเอียดกับทีมขาย
- **Brand personality:** ชัดเจน, พิถีพิถัน, ตรงไปตรงมา; ความน่าเชื่อถือมาจากภาพ/รายละเอียดจริง
- **Anti-reference:** หน้า anatomy ที่ผู้ใช้ส่งมา ซึ่งให้กล่องกระจกและป้ายเทคนิคเด่นกว่าสินค้า ไม่เสนอแนว dashboard หรือเปลี่ยนเป็นเว็บโฆษณาขนาดใหญ่
- **Accessibility:** เสนอ WCAG 2.2 AA เป็นเป้าหมายตรวจรับ, ใช้คีย์บอร์ดได้, focus ชัด, รองรับ reduced motion และภาษาไทยอ่านง่าย; ยังไม่อ้างว่าผ่านมาตรฐานแล้ว
- **Design principles:** ภาพจริงนำทาง; แยกสินค้า/ชุดชัด; ชื่อและรายละเอียดตรงรายการ; เปิดเผยเฉพาะข้อมูลที่ลูกค้าควรเห็น; ไม่เติมข้อกล่าวอ้างหรือราคาที่ไม่มีหลักฐาน

[ASSUMPTIONS]

1. รอบแรกเป็นการเลือกดูและเปิดรายละเอียด ยังไม่เพิ่มตะกร้า ชำระเงิน ฟอร์มเก็บข้อมูลลูกค้า หรือระบบส่งใบเสนอราคา
2. คงสี/ตัวอักษรของ SmartGift ที่มีอยู่ในเว็บเป็นฐาน ไม่รีแบรนด์ทั้งระบบ
3. เสนอให้เลิกใช้กล่อง 2.5D ในหน้าลูกค้าหลัก; ไม่ลบไฟล์ engine ที่อาจมีผู้ใช้งานอื่นโดยอัตโนมัติ

## ข้อเสนอหน้าจอ

### 1. หน้ารวมสินค้า

- หัวข้อ **“สินค้าและชุดของขวัญองค์กร”** แทน Anatomy Explorer
- ตัวเลือกสี่หมวดด้านบนก่อนพื้นที่สินค้า รักษา slug/ความหมายตาม ADR-001; ชื่อไทยที่เสนอคือ **รักษ์โลก**, **เทคโนโลยีและการทำงาน**, **ศิลปะและวัฒนธรรม**, **ไลฟ์สไตล์และการดูแลตัวเอง** เป็น display labels ไม่เปลี่ยน taxonomy
- แยกมุมมอง **“สินค้ารายชิ้น”** กับ **“ชุดของขวัญ”** พร้อมจำนวนที่ตรงกับข้อมูล ไม่ปะปนเป็นรายการเดียว
- พื้นที่หลักเป็นรูปสินค้าหรือรูปชุดที่ยืนยันตรงรหัส ภาพเต็มวัตถุ ไม่ตัดส่วนสำคัญ ด้านล่างเป็นชื่อไทยและคำอธิบายสั้นที่มีหลักฐาน
- การ์ดภาพสินค้าใช้ได้เพราะเป็นตัวเลือกเปรียบเทียบสินค้าจริง ไม่ใช่การ์ด emoji + ข้อความตกแต่งซ้ำๆ
- กดรูปหรือ **“ดูรายละเอียด”** แล้วเปิดรายการเดิม ไม่เปลี่ยนเพียงหมวด
- ไม่แสดงภาพกล่อง 2.5D, controls Compact/Float/Explode/Auto-Rotate, สถิติคลัง, vault status และชื่อ engine บนหน้านี้
- ไม่มีรูปที่ยืนยันแล้วให้แสดง **“ยังไม่มีภาพสินค้า”** อย่างชัดเจน; ห้ามใช้รูปคล้ายกันหรือภาพ AI มาปะปนว่าเป็นของจริง และไม่ถือว่ารอบ image-first ผ่านหากไม่มีภาพจริงแม้แต่รายการเดียว

### 2. รายละเอียดสินค้า/ชุด

ลำดับการอ่าน: **ภาพใหญ่ → ชื่อ → รหัสอ้างอิงสำหรับคุยกับทีมขาย → รายละเอียด → ของในชุด → เงื่อนไขราคาเมื่อยืนยันแล้ว**

- สินค้ารายชิ้น: ชื่อ วัสดุ ขนาด สี/ตัวเลือก เฉพาะที่มีข้อมูลยืนยัน; ไม่เติม lead time หรือ MOQ ที่เดาเอง
- ชุดของขวัญ: แสดงหัวข้อ **“ในชุดประกอบด้วย”** พร้อมชื่อ ภาพย่อยที่จับคู่แล้ว และจำนวนจาก `components`; ไม่ใช้คำว่า BOM กับลูกค้า
- หากชุดยังไม่มีส่วนประกอบที่ตรวจยืนยัน ให้แจ้ง **“รายละเอียดชุดอยู่ระหว่างยืนยัน”** ไม่สร้างรายการจากชื่อชุดหรือ model associations
- แสดงรหัสอ้างอิงสินค้า/ชุดที่ทีมขายใช้จริงได้ แต่ไม่โชว์ UUID, product-family IDs หรือรหัส supplier ภายในโดยไม่จำเป็น
- ไม่สร้างปุ่มขอใบเสนอราคาที่กดแล้วไม่มีปลายทางจริง; การเพิ่มช่องทางติดต่อเป็นงานถัดไปเมื่อยืนยันปลายทางและขอบเขตแล้ว

### 3. ราคาและข้อมูลภายใน

- ใช้ price authority ตาม AGENTS: FlowAccount export + pricing calculator ไม่อ้าง raw PDF, HTML hardcode หรือสถานะใน staging ว่าเป็นราคาพร้อมเสนอขาย
- แสดงราคาต่อชิ้น/ต่อชุดและจำนวนขั้นต่ำกำกับตามหลักฐาน; ไม่เอาราคาที่ 10 ชุดไปติดป้ายราคาสำหรับ 1 ชิ้น
- ถ้ายังยืนยันราคาไม่ได้ให้ใช้ข้อความ **“สอบถามราคา”** โดยไม่ทำเป็นปุ่มที่ไม่มีการทำงาน; ห้ามแสดง 0 บาทหรือ “เริ่มต้น” ที่ไม่มี quantity basis
- ไม่แสดงต้นทุน กำไร markup supplier code ราคาโรงงาน ค่าขนส่งจีน-ไทย CBM หรือ audit logs ในมุมมองลูกค้า
- เสนอให้ customer shell ไม่มีลิงก์ไป Price Calculator, Bundles & BOM เชิงระบบ หรือ Data Governance; ไม่ลบความสามารถทีมภายในหรือเพิ่มระบบ login ในงานนี้

## แหล่งภาพและการจับคู่

- ใช้ภาพต้นฉบับใน catalog ของโปรเจกต์เท่านั้นสำหรับสินค้าที่ระบุว่าเป็นของจริง; ไม่แก้ raw PDF/Excel และไม่ดึงรูปจากเว็บภายนอกในรอบนี้
- ต้นฉบับที่พบในการตรวจ RCA เป็นจุดเริ่มต้นค้นภาพ ไม่ใช่รายการภาพที่จับคู่เสร็จแล้ว
- ก่อนใช้แต่ละภาพต้องตรวจ **source file + page + source code + target SKU/offer + crop ของภาพ** ให้สัมพันธ์กัน และเก็บ hash ของต้นฉบับ/ภาพเพื่อย้อนตรวจได้
- ไม่ใช้รูปจาก blueprint เชิงแนวคิดหรือภาพหน้ารวมเป็นหลักฐานภาพ SKU โดยอัตโนมัติ
- ถ้าต้องเพิ่ม media mapping artifact/contract ให้หยุดเสนอ schema และรับอนุมัติเฉพาะส่วนนั้นก่อน ไม่แทรก field ใน master/pipeline โดยปริยาย
- ภาพอ้างอิงราคาใน PDF ต้องครอบเฉพาะรูปสินค้า ไม่เผยต้นทุน ข้อมูลติดต่อส่วนบุคคล หรือข้อมูล supplier ที่ติดมากับหน้าเอกสาร

## โครงหน้าที่เสนอ

```text
SmartGift                         สินค้าและชุดของขวัญองค์กร

[รักษ์โลก] [เทคโนโลยีฯ] [ศิลปะฯ] [ไลฟ์สไตล์ฯ]
[สินค้ารายชิ้น] [ชุดของขวัญ]                      จำนวนรายการ

รูปสินค้าจริง              รูปสินค้าจริง              รูปสินค้าจริง
ชื่อไทย                    ชื่อไทย                    ชื่อไทย
ราคา/สถานะราคา            ราคา/สถานะราคา            ราคา/สถานะราคา
ดูรายละเอียด              ดูรายละเอียด              ดูรายละเอียด

เมื่อเลือกรายการ: ภาพใหญ่ + รายละเอียดของรายการนั้น
ถ้าเป็นชุด: “ในชุดประกอบด้วย” + ภาพ/ชื่อ/จำนวนที่ยืนยัน
```

มือถือเรียงข้อมูลโดยภาพกับชื่ออยู่ติดกัน ไม่มีแผงรายละเอียดที่หลุดไปไกลหลังเนื้อหาทั้งหมด ไม่มีข้อความเอียง/ฝาทับรูป และไม่เกิด horizontal overflow

## Parent / peer review และขอบเขตความปลอดภัย

- Parent: [สถาปัตยกรรมระบบ](../SMARTGIFT_SYSTEM_ARCHITECTURE.md), AGENTS และ [ADR-001](../decisions/ADR-001-ECO-FRIENDLY-CATEGORY-REFACTOR.md); คงหมวด/ราคา/คลังและ Zero-PII invariants
- Peer: `public/index.html`, `public/gift-anatomy-25d.js`, `public/serve.py` และ master JSON เดิม; ต้องอ่าน working-tree diff ล่าสุดก่อน implementation เพราะมีงานอื่นแก้ไฟล์อยู่
- [ADR-002 v1.1.1b beta](../decisions/ADR-002-PRICELIST-MASTER-SQL-SNAPSHOT.md) อนุมัติ local SQL projection ตามขอบเขตของตน ไม่ใช่ runtime promotion; ไม่สลับ catalog ไปใช้ `pricelist_master.json` อัตโนมัติ
- ไม่สร้าง tier/แพ็กเกจใหม่ และไม่เปลี่ยน ontology; หากต้องแสดง tier ให้รักษา Reach / Select / Signature / Bespoke และไม่เหมารวมเป็นระดับของลูกค้าแต่ละคน
- **การเอาเมนูออกไม่ใช่ access control:** server ปัจจุบันมี `/api/catalog`, `/api/audit-logs`, `/api/formula` และ routes ภายใน การทำ UI นี้ไม่ป้องกันการเข้าถึง endpoint เหล่านั้น
- **Public-release gate แยกต่างหาก:** ต้องมี customer-safe response allowlist และขอบเขตเข้าถึงข้อมูลภายในที่ตรวจสอบแล้วก่อนเปิดให้ลูกค้าผ่านเครือข่าย/เผยแพร่จริง การเปลี่ยน security/API เป็นขอบเขตเสี่ยง HIGH ที่ต้องเสนออนุมัติแยก ไม่อยู่ในข้อเสนอ UI รอบนี้

## แผนหลังอนุมัติและเกณฑ์ตรวจรับ

1. ยืนยันบริบทข้างต้นและบันทึก PRODUCT.md; ตรวจข้อมูล/ภาพที่จะใช้จริงและเสนอ media contract เพิ่มหากจำเป็น → ตรวจ source/SKU/สิทธิ์ใช้ภาพครบ
2. ปรับเฉพาะ customer catalog presentation ตามเอกสารที่อนุมัติ → ตรวจเลือกหมวด/ชนิดสินค้า/รายละเอียดได้ตรงข้อมูล ไม่มีรายการตายตัว
3. ตรวจ desktop 1440px, tablet 768px, mobile 390px และ 320px, keyboard/focus/reduced motion → รูปไม่บิดเบี้ยว ชื่อไม่ถูกบัง ไม่มี overflow และข้อความอ่านได้
4. ตรวจภาพจริงอย่างน้อยหนึ่ง SKU และหนึ่ง offer ที่ยืนยันครบก่อนเรียกงาน image-first ว่าเสร็จ; รายการที่ไม่มีภาพ/ข้อมูลแสดงสถานะตามจริง และไม่อ้าง coverage ทั้ง catalog ถ้าตรวจเพียงบางรายการ
5. ตรวจทุกหมวด รวม empty/loading/error state และราคา/quantity basis; เพิ่ม regression checks ป้องกันภาพผิดรายการ ข้อมูลค้างหลังสลับหมวด และ fallback ที่ทำให้ดู approved
6. รัน relevant tests หลัง implementation และตรวจ diff ว่าไม่แตะ raw files, pricing/inventory engine, vaults หรือไฟล์งานอื่น; ไม่รัน master pipeline เพื่อทำ UI

**Exit ของรอบเอกสาร:** ผู้ใช้อนุมัติแล้ว แต่การอนุมัติไม่แทนผลตรวจรับ image mapping และ public-release gates

## Approval

อนุมัติผ่านคำตอบ “ok” ใน task นี้ เมื่อ 2026-08-30 ครอบคลุมรูปแบบหน้าลูกค้าและบริบทการออกแบบ โดยเฉพาะการถอด 2.5D ออกจากหน้าหลัก ใช้ภาพจริง และแยกข้อมูลทีมภายในออกจากการนำเสนอ

การอนุมัตินี้ไม่รวม schema migration, public deployment, การอนุมัติราคา/BOM, ระบบส่งใบเสนอราคา หรือระบบสิทธิ์ใหม่

## ผล implementation และการตรวจรับในเครื่อง (2026-08-30)

- เพิ่ม `public/customer-catalog.js` / `.css` และจุดเชื่อมใน `public/index.html`; ซ่อน UI ภายในเฉพาะ route catalog ไม่ลบ engine/เส้นทางเดิม และไม่เปลี่ยน master หรือ pricing/inventory logic
- แยกข้อมูล canonical products 16 รายการกับ catalog offers 357 รายการจาก source เดิม; ไม่รวม seasonal records 2 รายการที่ normalizer ของหน้า internal เติมเข้าไป
- ตัวกรองสินค้ารายชิ้นทั้งสี่หมวดได้ 4 / 4 / 3 / 5 รายการ; เพิ่มรายการจาก 24 เป็น 48 และเปิดรายละเอียดตรงรหัส พร้อมคืน focus เมื่อกดปิด
- Renderer รับเฉพาะชื่อ รหัส หมวด ภาพที่ผ่านเงื่อนไข และส่วนประกอบที่ยืนยัน ไม่ส่งต้นทุน/metadata ภายในไปสร้าง DOM; ชื่อที่ลงท้าย `(P-xx)` ตัดออกเฉพาะ display ไม่แก้ source
- รูปที่รับได้ต้องมีรหัสตรงชนิดรายการ, `generated_from_catalog === false`, `visual_status === source-photo` และ path ภายในที่อนุญาต; รูปซ้ำกำกวม/รูป generated ไม่ถูกใช้แทนภาพสินค้าจริง
- รูปต้นฉบับ 4 รูปจาก media manifest เดิมยังไม่มีรหัสตรง master จึงแสดงเป็น **ภาพอ้างอิงที่ยังไม่จับคู่รายการขาย** แยกจาก list; ไม่แสดงราคา/ส่วนประกอบร่วมกัน ไม่ใช่ image coverage ของ 373 records
- ราคายังแสดง “สอบถามราคา”; BOM ที่ยังไม่ verified แสดง “รูปแบบสินค้าและส่วนประกอบอยู่ระหว่างยืนยัน” รวมถึง TGC09-3 ที่มี conflict; ไม่แก้ส่วนประกอบโดยอนุมาน

### Verification evidence

| ตรวจ | ผล |
|---|---|
| `node --test tests/customer_catalog.test.cjs` | 10 ผ่าน; source identity, generated-image rejection, filters/empty input, price allowlist, BOM gate, invalid paths/duplicates, supplier display tags, neutral offer label, inline script syntax |
| `node --check public/customer-catalog.js` และ scoped `git diff --check` ทั้ง staged/unstaged | ผ่าน |
| Python 3.13: `test_pricing_calculator.py`, `test_auto_quote_service.py`, `test_cascade_inventory.py` | 21 + 6 + 4 ผ่าน; ไม่รัน full discovery เพราะมี archival/integration tests ที่เขียนข้อมูลจริง |
| Browser 1440 / 768 / 390 / 320px | document width 1425 / 753 / 375 / 305px ไม่ล้นแนวนอน; ตรวจภาพ tablet/mobile และ modal บน 390px |
| โหลดภาพต้นฉบับ | 4/4 โหลดสำเร็จ; object-fit contain; modal บนมือถือ scrollWidth เท่ากับ clientWidth |
| Reduced motion | emulation reduce ได้ transition 0s; คืนค่า emulation หลังตรวจ |
| Error + retry | block เฉพาะ catalog/pricelist/fallback requests ชั่วคราวได้ข้อความผิดพลาดและ 0 cards; คืน network แล้วกดลองใหม่ได้ 16 cards |
| Existing route smoke | `#/offers` ยังแสดงเมนูภายในและ section เดิม; กลับ catalog ซ่อนเมนูได้ |
| Keyboard | focus ชัด, ปุ่มปิดคืน focus; native Escape ยังไม่ยืนยันผ่าน automation จึงต้อง manual UAT เพิ่ม ไม่อ้าง WCAG conformance |
| Loading / empty state | มี renderer และ unit coverage ของข้อมูลว่าง; ยังไม่ได้ browser fixture ของสองสถานะนี้ |

### ข้อจำกัดและ gate ที่ยังไม่ผ่าน

1. **ยังไม่ครบ image-first acceptance:** ต้องจับคู่ภาพจริงกับอย่างน้อยหนึ่ง canonical SKU และหนึ่ง offer พร้อม provenance ก่อนเรียกงานเสร็จ ไม่ใช้ภาพ AI หรือใกล้เคียงชดเชย
2. **TGC09-3 conflict:** source reference หน้า 22 เป็นกระบอกน้ำ/สมุด/ปากกา แต่ master components เป็น PM-MSG/PM-PB10K; ห้ามแก้ BOM ในงาน presentation
3. **ชนิดรายการในต้นทาง:** `catalog_offers` มีชื่อรายการที่ดูเป็นสินค้ารายชิ้น เช่น flash drive; จึงใช้ label กลาง “รายการจากแคตตาล็อก” แทนการอ้างว่าทั้งหมดเป็นชุด ไม่เดาชนิดจากชื่อ/BOM ที่ยังไม่ verified ต้องยืนยันชนิดข้อมูลก่อนแยก physical gift sets ได้ครบตามแบบเป้าหมาย
4. **Media contract:** ไม่เพิ่ม/แก้ schema หรือสร้าง mapping ไปยัง PM SKU ที่ไม่มีหลักฐาน ต้องเสนออนุมัติส่วนนั้นแยก
5. **Public readiness:** API เดิมยังมีข้อมูลภายใน, image rights ใน production manifest ยัง not verified; preview bind เฉพาะ 127.0.0.1 ไม่ deploy และไม่ถือว่าพร้อมเปิดให้ลูกค้าภายนอก
6. Working tree มีงานอื่นแก้และ stage/commit ระหว่างทำงาน; ผลนี้อ้างไฟล์ในเครื่องขณะตรวจ ไม่ใช่ clean release snapshot งานนี้ไม่ได้สั่ง stage/commit/push

### Provenance ของภาพอ้างอิงที่นำกลับมาใช้

อ้าง metadata ใน `output/catalog-internal/production-manifest.json` และ `public/data/catalog_media.json` เดิม ไม่สร้าง contract ใหม่: source tech คือ `data-pipeline/01_raw/03_product_catalogs/2026 new catalogue of power banks&car charger&wireless charger.pdf`, SHA256 `066037E15F855D22D9D08B7E3ED440224EE6EC67D03A0D2CADB7F24325B25456` ตาม manifest; ไม่มี target master SKU ที่ยืนยัน จึงใช้เฉพาะ source-reference gallery

| Source code / page | Public asset SHA256 (ตรวจไฟล์ในรอบนี้) |
|---|---|
| S-1052 / 2 | `3F7977862CAAF8E569FFF3500A1A47DEDABBCAFB6D92062591DE063CEE46BDD5` |
| BST61401 / 3 | `B54D10AE7365D01C46A0C417127EC8973B877346C26DF95434E2D4D5B91E593E` |
| DW03 / 4 | `6335F5FCCC76BA185B57D0F00FC0367A9F8C8A92C7587636A191BDB978606BDC` |
| W502 / 7 | `3121549637246511E3AD5F06C85F64E60A4B10E0BAFA3E8148C996EF3D37EABF` |

## Follow-up: ภาพต้นฉบับ Business Gift (2026-08-30)

ผู้ใช้ขอ “เอาภาพสินค้าจากแคตมาใส่” เป็นการเติมภาพตาม spec ที่อนุมัติแล้ว ไม่ใช่การอนุมัติ schema/ontology หรือ canonical migration เพิ่มเติม

- ดึง original embedded images จำนวน **150 ภาพ** (JPEG 148 + PNG 2) รวม **1,464,824 bytes** จาก PDF โดยไม่สร้างภาพใหม่ ไม่แต่งภาพ/เพิ่ม resolution และไม่คัดลอกตารางต้นทุนลงภาพสาธารณะ
- ตรวจภาพแถวสินค้าและรหัสด้วยสายตาจาก review sheets 10 แผ่น ก่อนใช้ explicit code allowlist; เก็บไฟล์ต้นฉบับ PDF ไว้เหมือนเดิม
- เพิ่ม 149 records และแทนภาพ generated ของ TGC09-3 หนึ่ง record ใน `public/data/catalog_media.json`; ใช้ fields เดิมและคง media schema_version 1.0.0b ไม่มี contract ใหม่
- จับคู่เฉพาะ display alias `catalog_offers.offer_code` ที่ตรงกับ source code: **150/357 offers**, **0/16 ProductMaster**; `sets` เป็น media bucket เดิม ไม่ใช่คำรับรองว่าทุกรายการเป็น physical set หรือเป็น BundleOffer
- Canonical authority ยังคงเป็น `config/schema_genesisblock.yaml` v1.3.0; business code ที่ใช้ค้นภาพไม่ใช่ primary key `offer:`/`pm:` และงานนี้ไม่ promote legacy records เป็น canonical entities
- หน้า catalog เริ่มที่ “รายการจากแคตตาล็อก”, เรียงรายการมีภาพก่อน, ใช้รูปเต็มวัตถุเหนือชื่อในกริด 3/2/1 คอลัมน์ตามจอ; กดเปิดรูปใหญ่ได้ ภาพอ้างอิง 4 รูปที่ยังไม่จับคู่ย้ายลงท้ายหน้า
- เก็บ internal media showcase ไว้ 4 รายการเท่าเดิม ไม่ให้จำนวนภาพใหม่ขยาย layout ภายใน; ไม่ลบภาพ generated เดิมจากดิสก์ แต่ customer renderer ไม่ใช้ generated เป็นรูปสินค้าจริง
- ไม่เปลี่ยนชื่อ/source records, ราคา, BOM, stock, pipeline, vaults หรือ schema; ราคาเป็น “สอบถามราคา” และ TGC09-3 คง conflict gate
- ยังไม่ครบ image-first acceptance เดิมที่ต้องมี PM SKU อย่างน้อยหนึ่งรายการ; สิทธิ์ใช้ภาพเชิงพาณิชย์, ความครบถ้วนชื่อ/ชนิด/BOM, canonical mapping และ public readiness ยังต้องยืนยันแยก
- ไม่รัน manifest/pipeline generator ซึ่งเขียน category slices และ audit artifacts ของอีกงาน: `public/data/product_manifest.json` เป็น projection เก่าที่ต้อง regenerate/ตรวจใน lane นั้นก่อนใช้ offline integrity; localhost catalog อ่าน media manifest โดยตรง ไม่อ่าน projection นี้

### Verification รอบเติมภาพ

| ตรวจ | ผล |
|---|---|
| Node customer tests | 13 ผ่าน รวม stable photo-first order, 150 offer mappings, excluded codes, TGC09-3 conflict และ hashes ของ original assets |
| Python scoped tests | 36 ผ่าน: extraction 5 + pricing 21 + auto quote 6 + inventory 4; ไม่รัน full discovery/pipeline |
| Original assets | PIL decode/verify ผ่าน 150/150; SHA256 ตรง ledger ทุกไฟล์และ PDF source hash ก่อน/หลังไม่เปลี่ยน |
| Media endpoint handler | GET 200 (sets 153 = source-photo 150 + creative เดิม 3); POST 405 |
| Category coverage | Eco 0/1, Tech 113/250, Classic 5/17, Lifestyle 32/89; browser เปลี่ยนหมวดแล้วจำนวนตรง |
| Browser desktop 1440px | ค่าเริ่มต้น 24 การ์ดพร้อมรูป; รูปใน viewport โหลดสำเร็จ, object-fit contain, document width/scrollWidth 1425px เท่ากัน |
| Browser mobile 390px | document width/scrollWidth 375px เท่ากัน; รูปการ์ด 343px เต็มความกว้างหลังแก้ mobile thumbnail override; modal 352px ไม่ล้น, รูป THB03-2 โหลดตรงรหัสพร้อมสถานะรายละเอียดรอยืนยัน |
| Pagination / PM tab | เพิ่ม 24 → 48 การ์ดพร้อมรูป; PM tab ยังมี 16 records และ 0 matched photos ไม่ใส่รูปเดา |

ไม่อ้างภาพทุกไฟล์ผ่าน browser network load: browser ใช้ lazy loading ตรวจเฉพาะที่เข้า viewport; ความครบ 150 ไฟล์ตรวจด้วย decode + hashes บนดิสก์

### รายการที่เว้นจาก candidate 156 รายการ

| Code | เหตุผล |
|---|---|
| TGC06-4 | รูปหน้า 23 เป็นชุดสมุด/ปากกา/USB และอุปกรณ์ แต่ชื่อ conceptual offer เดิมอ้าง Smart Notebook + Power Bank + Metal Pen; ไม่ผูกภาพกับคำบรรยายที่ขัดกัน |
| TYD05-2, TBS03-4, TPH00-3, TPC01-7, TPS00-2 | Text extraction พบรหัสที่บริเวณหัวกระดาษ แต่ภาพ render รหัสถูก header ทับ; ไม่ถือว่าตรวจ code/photo บนหน้าเดียวกันได้ |

### Provenance ledger ของภาพที่ใช้งาน

Source: `data-pipeline/01_raw/02_factory_pricelists_pdf/02-ใบราคา2025-ชุดของขวัญธุรกิจ-ฺBusinessGift.pdf`

Source SHA256: `1369832f7df36d9f00230ae2cfc872965246804a9ef1f4be5f4518b798f95002`

ตารางนี้เป็นหลักฐาน internal ใน spec ไม่ส่ง raw source path/hash ไป media endpoint; target คือ offer_code ตรงตัวใน master เดิม และ asset อยู่ใต้ `public/assets/catalog-media/`

| Code | PDF page | Image object | Asset | SHA256 |
|---|---|---|---|---|
| FXD66-2 | 1 | Image40 | source-offer-FXD66-2.jpg | `9b7c4fc779a9aa46e28662291f6a5c1503e2205ca3c1e73398eb817bae376b9a` |
| FXD8816 | 3 | Image59 | source-offer-FXD8816.jpg | `3626116283d9a10daa2ea9136ee00778d8023bc7cd6940d06a8899effc74ea55` |
| TBC4117 | 5 | Image79 | source-offer-TBC4117.jpg | `2b191094c0a8f80b0bf8fa197d99e813e3741db3052ffd11ea7a2b7420498f87` |
| TTT17-2 | 6 | Image86 | source-offer-TTT17-2.jpg | `51d5cb693ca4af5d4178635076fe2ba71e1ab85719b72b9d3f29f36e9489c434` |
| TTT18-2 | 6 | Image87 | source-offer-TTT18-2.jpg | `fac8b3e826283b2631f778afbea8129feb1fb77960294fe2ab9ca11c5b402a71` |
| FXD37-3 | 6 | Image89 | source-offer-FXD37-3.jpg | `ad0a4516530ac4d050e2a3cd066e85ba47784fbe407a37b71ecd91313c40e113` |
| FXD35-2 | 7 | Image97 | source-offer-FXD35-2.jpg | `f6c45abdcd1b3fd8045479216b7b2cb0ad0a7f35597fbfb317338c2a07540282` |
| FXD32-3 | 8 | Image104 | source-offer-FXD32-3.jpg | `9c43a5569938677e5cd9baa755de69f4af0e02e9a3b79a2c2a0d5c0f0fa57920` |
| TTT15-3 | 9 | Image112 | source-offer-TTT15-3.jpg | `996a1860cd83199b21e2535285f51c5dcc30f04d99f43d6178071092c63ebe73` |
| FXD05-0 | 9 | Image110 | source-offer-FXD05-0.jpg | `19f4ed28df34eeb34952875ee9b9f9b07ac7eeedf45cc08771a9894bffdb1ec7` |
| FXD22-2 | 10 | Image122 | source-offer-FXD22-2.jpg | `fa63bc7e5a327e28494149704dad0447c238473ea52d481f7099e653e5e95922` |
| TTT06-2 | 12 | Image137 | source-offer-TTT06-2.jpg | `67db70d66d2936d05f9590a3010ebcfb0e8a660cda7e2c3db8f39a8b5e9f6661` |
| TTT05-3 | 12 | Image134 | source-offer-TTT05-3.jpg | `de3b3d992ccc50c7d75a845ed3e8bc841800f87d38a05e462c23dad1c8648a44` |
| TTT06-3 | 12 | Image138 | source-offer-TTT06-3.jpg | `d390398b4af7b14157b0129361885f7fc4cfcf9e0dbdc92b40f446da093a9072` |
| TTT07-4 | 13 | Image145 | source-offer-TTT07-4.jpg | `c0051b2df2be783817695b7b3b8869b592732e79b0c54ad6691268d32eecbca7` |
| TTT07-5 | 13 | Image142 | source-offer-TTT07-5.jpg | `3ff35ed170f2327dda9666212ac1070331a61dc67f47ff2d21e69f19889088ac` |
| TTT13-2 | 13 | Image143 | source-offer-TTT13-2.jpg | `95129389318d81ce25374ef806932f28a64b0646b9b2c9ef45656380353fe80a` |
| FXD19-5 | 16 | Image171 | source-offer-FXD19-5.jpg | `682a4564f89fc053e6c89d3ee3ec16b7ba00910e387588fb969cfb487b7800ed` |
| FXD00-3 | 17 | Image181 | source-offer-FXD00-3.jpg | `a45cd95e76237b019c5bd424040d98486d79a52000e0a106f8e000b9de1cb6a8` |
| MZA02-3 | 17 | Image178 | source-offer-MZA02-3.jpg | `4aa7ae4ecfb5e7fb88ae5eca64ec0e3156be754721d1ca5ed83821024f32cf0b` |
| TGC21-5 | 18 | Image190 | source-offer-TGC21-5.jpg | `ea8d9df9d1d1e211dac65dd3028501c479900c0d3355038102bc5595080081db` |
| TGC21-4 | 18 | Image189 | source-offer-TGC21-4.jpg | `c58565c53ce2f1313c6792073f875585bf99c1d8d572d50ac61e6bde0e9133ac` |
| TGC21-3 | 18 | Image187 | source-offer-TGC21-3.jpg | `a0b44decbb88cc9ee68c720316376742a58dd621224c75a78bd905732a949ee2` |
| TGC21-2 | 18 | Image186 | source-offer-TGC21-2.jpg | `45e93be8ed170604391a5ef109b997954515bef82206983ca33c7a3131c345cd` |
| MZA02-2 | 19 | Image198 | source-offer-MZA02-2.jpg | `e9360cbe4218b915708e2d92b6a075cbc5f9485bb50ac908635382873394264c` |
| TCS20-2 | 19 | Image200 | source-offer-TCS20-2.jpg | `845e8e4a9dbec3ae0a9c195a5156a37fbb947b74e67776deca50603d2083a166` |
| TCS30-3 | 20 | Image204 | source-offer-TCS30-3.jpg | `a3ff7165958229499e779cf194e0136ace848ba93c297aabbfcb48ea4379a48a` |
| TCS40-3 | 20 | Image209 | source-offer-TCS40-3.jpg | `92014887ed3b2e10978f7bcfb41e03297d579382ed72ec62e512a5ac5581b236` |
| TBC21-3 | 21 | Image218 | source-offer-TBC21-3.jpg | `9ea08f7ab21795a305c8e2803a69ac88548fa29f27f2a833fc3b67617d4f4965` |
| TJL3042 | 21 | Image212 | source-offer-TJL3042.jpg | `f249dba66d82f9d07d9175aa2f977e3a23e4ffd76097aec49c3b9416ea73cdd2` |
| TJL3143 | 21 | Image214 | source-offer-TJL3143.jpg | `725162ca1714d6bf1e1b082a5217ac08b568bd322fd705de3228d3c075a6cbf8` |
| TGC09-3 | 22 | Image222 | source-offer-TGC09-3.jpg | `cf2c7e18fc42649d401d4243bf714bbc0b2c1ae3633fe2bc453a29e8f0073d65` |
| TGC08-2 | 22 | Image223 | source-offer-TGC08-2.jpg | `f6fa7cc35fc0b74b751b2eac4d972a5a934899431c4951a8423490ab220c0dda` |
| TGC10-3 | 22 | Image225 | source-offer-TGC10-3.jpg | `dd5378476aace32729c78a89eafe4c8a5e1e6bffd1425d0065bf9796601286f4` |
| TGC10-7 | 22 | Image226 | source-offer-TGC10-7.jpg | `6f73ae990bce4377b333409fec163fbc3ec02f6d7a135be7416ff71e32944cb3` |
| QZA00-3 | 23 | Image232 | source-offer-QZA00-3.jpg | `161e12a958883006d16c6bec1c58bfdfca1d59a43c5333ce360f44e89bbf4dd3` |
| QZA01-3 | 23 | Image233 | source-offer-QZA01-3.jpg | `0c5500ca5df7faba1f9528891695c67944c514ac89042e290ce4454c6fb7d3b4` |
| QZA02-3 | 23 | Image234 | source-offer-QZA02-3.jpg | `63aa32193055fe70ac32ed6491ed107fe5182f84db2b8c33289a370731e4d50a` |
| QZA03-3 | 23 | Image235 | source-offer-QZA03-3.jpg | `8fc19c20d078c83abc7779f576c62215bcebee5f4d578af4b0713c7807a6e475` |
| MZB00-4 | 24 | Image244 | source-offer-MZB00-4.jpg | `9a6c4532dd142af9599be855aaa4f86f1844e360e74945bd5c70c81d458e96e4` |
| TBP1713 | 24 | Image242 | source-offer-TBP1713.jpg | `4241ce9dac3ebdcdde53bd91f41da89e50d7d8d703b54f17111bf0c6194a828a` |
| TBP1712 | 24 | Image243 | source-offer-TBP1712.jpg | `4f321d14f06414891c8362d7656bb05cb9dfe0c02a12515a2eff0eacc0a98725` |
| TBP1613 | 24 | Image240 | source-offer-TBP1613.jpg | `f117235a8a9fe7f8e8d83a676ef62725a4f14529885b1a23337f9af9f8d936a6` |
| TBP1612 | 25 | Image252 | source-offer-TBP1612.jpg | `e86f2cd0ab3b824b6f3d62f9347abc023d853b2021cb1a3ca21f4b761a70ebb4` |
| TBP1512 | 25 | Image251 | source-offer-TBP1512.jpg | `4ee5eca9b11cee9f4d5436f092bb392258a45bdbda1d2cac74f2d9a618183532` |
| TBH05-2 | 25 | Image254 | source-offer-TBH05-2.jpg | `cdf4ad01caa671cd769d9032afa840996fca4f0ebc27def41be1d377fe694999` |
| THB03-2 | 26 | Image262 | source-offer-THB03-2.jpg | `c2321ce406ab7ed251292597649f77eafedfe130f6af23bc9b860f5d92f02585` |
| TDS07-2 | 27 | Image273 | source-offer-TDS07-2.jpg | `0b6e9b2aab7fd4da338d65d84253b6d1dff7dbefff8f2fee884b709d75088be3` |
| TGC04-5 | 27 | Image275 | source-offer-TGC04-5.jpg | `7b3479290b396e0c21ba1a8259893cf1be56b0b7ccc8eb789a788ab98296cc07` |
| TTT02-2 | 29 | Image291 | source-offer-TTT02-2.jpg | `2b7932313a8ea5bd3dc68e8ae09e68332a8fc05bf76c58159469c481c40c23af` |
| TSPS3-2 | 29 | Image292 | source-offer-TSPS3-2.jpg | `6fbdacea35ff720843b2307516c952c4893e21ff8877225eacc74256c98f1412` |
| TSPS2-2 | 29 | Image294 | source-offer-TSPS2-2.jpg | `d1d45dd8bd9380e941fc375b9c5f7ed9b27c4c9aa244ba0ae970a1368a39e2ce` |
| TSPB2-2 | 29 | Image295 | source-offer-TSPB2-2.jpg | `738154fb0f3e1e0f7c5ef8b15cd54d4d061bcdec09d2c3f12818f164064e0681` |
| TYD0363 | 30 | Image304 | source-offer-TYD0363.jpg | `20b43067db3c1b3ef46636fe5cb78b826ac5463239fa1570b465c32d80c8cd50` |
| TYD0262 | 30 | Image305 | source-offer-TYD0262.jpg | `f64a7cb5da66fce57c673536a82b4ab6cd6efde3e6a2ad4e097df1b0dad2acdd` |
| TYD0162 | 30 | Image306 | source-offer-TYD0162.jpg | `605ad13506f91d50fd654afe6b55e83d57a3e4e3e2ef8362d51b69c7de415de8` |
| TSQ06-4 | 30 | Image301 | source-offer-TSQ06-4.jpg | `fdde5c9fdcd5891093252ce46c84079f377707282452474b7926435c0b4758b6` |
| TSQ04-3 | 31 | Image314 | source-offer-TSQ04-3.jpg | `e8b2a1b2bd21a161f63e1b0097f3df1d9e876bc22bd94be722f861ea4c653908` |
| TDS04-3 | 32 | Image323 | source-offer-TDS04-3.jpg | `a9f5fc65a01c5211b2bc68669fc01b45d079dc98dcc99a0a2dc819af04d7c5b5` |
| TDS03-3 | 32 | Image319 | source-offer-TDS03-3.jpg | `12cb1dd2aa5bc1a6fff4a17539916400ca03566e03855b35fc6c3fd2ce6878f9` |
| TDS02-3 | 33 | Image331 | source-offer-TDS02-3.jpg | `50d8082c0a711775860c5c17800976f957017cfb7b3cd5e71ce3fbf45ac378d8` |
| TDS03-2 | 33 | Image330 | source-offer-TDS03-2.jpg | `34338866d0badf8980ca7e6ad32a2afc9a517532f1976e4d38828de06e371ea9` |
| TDS02-2 | 33 | Image332 | source-offer-TDS02-2.jpg | `edeeb8d435ea2fae5e4a9b7ddaae06acd93d6e82381ec9f6a47bea0fe5498d17` |
| TDS01-2 | 33 | Image329 | source-offer-TDS01-2.jpg | `1325ae08f62b8683c84c5af99f2888b3a7f86177a485bf53a3320719d4890bd8` |
| TCH01-3 | 35 | Image349 | source-offer-TCH01-3.jpg | `eea9bf98510b0271952cb1b682ce79cb8d1460f919f308d962c4f8ba06dc2052` |
| TCH01-2 | 36 | Image353 | source-offer-TCH01-2.jpg | `a19d376f3b18e8b36150f83136a6e4886c3e71314232cd00160c1baed1bca047` |
| TCZ0033 | 38 | Image368 | source-offer-TCZ0033.jpg | `157695765ab2681a5c30f15b40dd8819f155173541011aaf536147a53ef1306f` |
| TJM03-3 | 40 | Image388 | source-offer-TJM03-3.jpg | `160d2402b7e9ca9c586a3cba818e9929ab487b6ea155efd27c69588a3dc4ff12` |
| TNB01-3 | 40 | Image384 | source-offer-TNB01-3.jpg | `12ccf4b6ac11de76538a87e97f25124096b3fa9055d8f9fee815f2f39eb96cc9` |
| TTT00-5 | 41 | Image393 | source-offer-TTT00-5.jpg | `58ca21d77cdc6783c7f6431d37f98b15771d94a75afbadc4bcbe1e5729b1abf4` |
| TTT01-4 | 41 | Image394 | source-offer-TTT01-4.jpg | `ac7c743f22d1aa4c947ff9b6df383615f03f13c15aeade93d23ae4b22b9ce853` |
| TTT00-4 | 41 | Image392 | source-offer-TTT00-4.jpg | `160025a04f7458fb1efab77d306f93935f768a28da661172a03ea77c0114a233` |
| TTT00-3 | 41 | Image391 | source-offer-TTT00-3.jpg | `2249273ec03d5e9ebff89e9ea66401d038ff17871eaebec8a6261e81c2c5b8bf` |
| MC00-1 | 42 | Image401 | source-offer-MC00-1.jpg | `3fb45af123a26d73aa206933ab156aa99aa1475a93f49ef63176f44f04a4a313` |
| MC00-2 | 42 | Image400 | source-offer-MC00-2.jpg | `6fb250f6b33125496bf2353aba67595a1874d3bc6d86a29efcd02acd7217d55d` |
| TBS01-2 | 43 | Image412 | source-offer-TBS01-2.jpg | `44b4d2a212d74bc1a00bf125602d3a992b8e83fce50112ae26bee82a3b8580b1` |
| TBS02-2 | 43 | Image409 | source-offer-TBS02-2.jpg | `168895fdc9641224fa2fce724b65173aa7a778263cded1f6200bd5ef2a59c4be` |
| TBS02-3 | 43 | Image410 | source-offer-TBS02-3.jpg | `f15681b3f45d17f688a6e64efad839a20f3a0924703dddaec8e915cfbec17913` |
| TBS02-4 | 43 | Image411 | source-offer-TBS02-4.jpg | `4fadae028f9c0ccc7afb8dd4da31e3493c394dc1ad92c837398992a8f05ce3f1` |
| TBS02-5 | 44 | Image418 | source-offer-TBS02-5.jpg | `3df1ec0b2dbcecaa40e8ad14e6b683595a238011795644bed2f29a60466a9d5a` |
| TBS02-6 | 44 | Image421 | source-offer-TBS02-6.jpg | `298f7257b37545d1a122768e898b17fda80c63c42805fbb4e1eaad57297ea309` |
| TBS01 | 44 | Image417 | source-offer-TBS01.jpg | `4452b8c79d2a970d7c7c74f639ad05018e6335061ef356a09460b92f467d4892` |
| TBS02 | 44 | Image416 | source-offer-TBS02.jpg | `3f019e29053cf2dc9a6501ea46f7cde6261a75872bdfee0174b3b5e0091b2f64` |
| TSX00-1 | 45 | Image427 | source-offer-TSX00-1.jpg | `b9e7d80a6cdb8dacbc5c19f955492c275bc9059e22b964111cd979b854d18fcb` |
| TBH03-3 | 45 | Image428 | source-offer-TBH03-3.jpg | `466ca0a5f1ce91712b02332cf9591b95def30d44ccc49bd59d1429a5be133910` |
| TBH01-3 | 45 | Image426 | source-offer-TBH01-3.jpg | `bd675bb943805d678744bcb2e6f8d8902661767e021d9bbd85b791f348ee9169` |
| TBH00-6 | 45 | Image425 | source-offer-TBH00-6.jpg | `722698d77ab6cdaf3a023eea4a94dc34945bf803ade38360e85b47f7f1a50b72` |
| TBH01-4 | 46 | Image435 | source-offer-TBH01-4.jpg | `db6dadb51ae5f1e202149e092f54d59ca46d3d3dffbf5506e4a55069e6243c6c` |
| TBH00-4 | 46 | Image436 | source-offer-TBH00-4.jpg | `ab41179abe9ee4a91a5c9ba4e393ae639827062c654c7a325aa87cc4b1a58c2c` |
| TBJ03-3 | 46 | Image433 | source-offer-TBJ03-3.jpg | `f71c33ea95bf558f846d9157912eb54782dcc4efd9179fe89277ddeefa7574d3` |
| TBH01-2 | 46 | Image434 | source-offer-TBH01-2.jpg | `d59fe06b890a385fa2a1ee70dd3c95bc6820c4d3abf165b0749e5affd7713a8d` |
| TSB03-2 | 47 | Image446 | source-offer-TSB03-2.jpg | `8ec5834d27cc89d05d2ae5c0253d8113e511de37fa6b74ada4d32001987b8e61` |
| TSB02-2 | 47 | Image449 | source-offer-TSB02-2.jpg | `9d963025be82a9d63978e09493389ad6b8384418d6164209d54a2793a2ada449` |
| TSS01-2 | 47 | Image450 | source-offer-TSS01-2.jpg | `8717d44ad7211b5f27e9274c78d57afb789c7767eefb09b00cf9d3b26ecd227d` |
| TMQ1832 | 48 | Image457 | source-offer-TMQ1832.jpg | `81534b39cac8c27811f6c52c7b7d732503ec246a070273a48e96e7a909980777` |
| TCH00-2 | 48 | Image456 | source-offer-TCH00-2.jpg | `13d53550c15f9d2f0a3edcdad6b02e872fc81e292335bf49036364a81f17b7fb` |
| TPF7034 | 50 | Image474 | source-offer-TPF7034.jpg | `1d735419e82853388bb6c9fc8281ad9f7e8ea972ff3aca0f82c086327c8b45ae` |
| TBF6034 | 51 | Image479 | source-offer-TBF6034.jpg | `a8fbed60908ce2b46be7e23598a5e24bcb59434c55628b237c7f092b8562ecf7` |
| TBF7033 | 51 | Image477 | source-offer-TBF7033.png | `1fe99e59d31d10e4013b7f118f54a21459330ada1afe882f623fba9c3929fcc3` |
| TPH00-7 | 52 | Image490 | source-offer-TPH00-7.jpg | `6f9d105b3265686a727ab8664feca78db3813c30c5bd8081c21453a8a1369a32` |
| TPH00-5 | 52 | Image487 | source-offer-TPH00-5.jpg | `48a1f883e573a5c90d954ae40f9773a9226625543aae593c65e6784ecbbee273` |
| TPH00-4 | 52 | Image488 | source-offer-TPH00-4.jpg | `1fca7edb4ef2459e68db026a1c12807036556781df874da4b26cdcdcc4fbcc1d` |
| TPH01-3 | 52 | Image486 | source-offer-TPH01-3.jpg | `ecb19b7efc77ebff8a49c618a5d23ea3683aad9463953477f90216f9f2594757` |
| TPF09-2 | 53 | Image497 | source-offer-TPF09-2.jpg | `f65f318c1476d5b507f115d7ee8576aaa2d0bee545ce6b44aacc5ad21a4d8e4c` |
| TPF09-3 | 53 | Image498 | source-offer-TPF09-3.jpg | `7a872491d9c5597bcb879652e8468e0698fb52e8abf4b9f060c99d0a5f98ba1d` |
| TPF19-3 | 53 | Image494 | source-offer-TPF19-3.jpg | `16d2d53ae0a1985ff596b9997df5cee319d5ee2e1084d28f3186c9335fb2f387` |
| TPF29-3 | 53 | Image496 | source-offer-TPF29-3.jpg | `0df707d9e126a2c6e53fc12fd0ec911384e89c222a50c579d7f5c19d2e4ba961` |
| TPM00-3 | 54 | Image501 | source-offer-TPM00-3.jpg | `938dbb8584843e0fd8afc0220b2ea7bc684188e489464fbc5aa08a0ff6636e2c` |
| TPM01-3 | 54 | Image502 | source-offer-TPM01-3.jpg | `87c83cf728c4a80625f1d4ce8afeee28e7bc232e81fe73072548064237212d50` |
| TCW0013 | 56 | Image518 | source-offer-TCW0013.jpg | `f1088b547df06f672492a564b34e0533e7aab6703f0144ade9ab8555810c24e0` |
| TDP10-2 | 57 | Image525 | source-offer-TDP10-2.png | `6fba7f6916cd3414b4a681becc1ebb9cf365d6ee9a5fc98c7abd8b73ec0861ce` |
| TDP10-7 | 57 | Image530 | source-offer-TDP10-7.jpg | `31f4ea971bf7ae847b806e1cc7aa7212cd1dda97b86983dd94c75391ba29397a` |
| TDP10-8 | 57 | Image531 | source-offer-TDP10-8.jpg | `5bdbbb210a3d0ac8b1430aa2f99e427b4bf21e951b5a4ef6a2b48b261368fb94` |
| TPT00-2 | 61 | Image561 | source-offer-TPT00-2.jpg | `4b8e25e610864d453b8b62aaec35bcd30d12bda4794b80df2def5c63004fce30` |
| TPT10-7 | 61 | Image563 | source-offer-TPT10-7.jpg | `d755df10aaddd9e211cfb5085b3247dd8e8938eae5af0dc5b4fad212bf340c13` |
| TPT03-3 | 62 | Image567 | source-offer-TPT03-3.jpg | `c3e5c2746b68602e74438c0406b8b6fc17c2f1d9ad0e709f6f29995626f8c176` |
| TPT03-4 | 62 | Image572 | source-offer-TPT03-4.jpg | `b8b4874c4f51dc76d4e6c1c345cd55406eb913cecde205b4c9c21dc77dddc5e2` |
| TPT12-4 | 63 | Image576 | source-offer-TPT12-4.jpg | `0011832b6e51044542da35394c8ca1ea3f5a658d195331d7cb6db135155d2fb6` |
| TPC14-4 | 64 | Image585 | source-offer-TPC14-4.jpg | `4727ddc88d1d8a101e517f0532cf1a30c4b90480d35368c70254b9e7834d4b4a` |
| TPC13-5 | 64 | Image586 | source-offer-TPC13-5.jpg | `25568a4ce8cd643d5cf2e8af275e5a6e36f9367e8e298eaf7c3b0ef8e65a3ac6` |
| TPC16-6 | 64 | Image588 | source-offer-TPC16-6.jpg | `a54bd31d2854bb9482a54b78d1e7b032b82a1a6a5ff3052e1605501ff633664c` |
| TPC13-7 | 64 | Image589 | source-offer-TPC13-7.jpg | `44c916a931765635657b26281a484dddd57a11cf2923b77b3ad505203f950fd4` |
| TPC03-4 | 65 | Image593 | source-offer-TPC03-4.jpg | `f7ccbe78df488f0130d8377c9127c9c81de0ea9fa8b53fcd37bfacfcebc03b76` |
| TPC03-3 | 65 | Image592 | source-offer-TPC03-3.jpg | `d8e9f537ab8d9e472f9b1f95366a64f00365f0d69b4c132023a96a18c6d41025` |
| TPC00-2 | 66 | Image604 | source-offer-TPC00-2.jpg | `bed2033ab4982be5e236d4237ecd30f85aa8910fbf5c593656a4aecd04449be8` |
| TPC00-3 | 66 | Image600 | source-offer-TPC00-3.jpg | `eca68b5d1e0a16ac19e4a973f4b355c318bcd6902ec9d16d946a84ad19f61110` |
| TPC11-3 | 66 | Image601 | source-offer-TPC11-3.jpg | `45670d37a79c1d8ca896ac9965a8aaaf097d9d12d32a01417512598c468301b5` |
| TRJ00-3 | 67 | Image612 | source-offer-TRJ00-3.jpg | `38cf1a9ff80bab67e9e67bd997f36390c0dd313c2ecf7dab420258b27ca10573` |
| TPY10-7 | 67 | Image613 | source-offer-TPY10-7.jpg | `2e57f7f99eb7193961a6613a89c73b4447d46aa39f7c916d8089f2297b39d8a2` |
| TPY00-7 | 68 | Image618 | source-offer-TPY00-7.jpg | `e8f8819913d3069823f2388bfff26866b58b0e778f30e6e7b11ada599ff2d147` |
| TPY00-6 | 68 | Image616 | source-offer-TPY00-6.jpg | `4091da6ea2b71fd195791be169b91e5effa71434f1ba735bf8550c3d605ad1aa` |
| TPY02-6 | 68 | Image619 | source-offer-TPY02-6.jpg | `663d8be382526186f5f881d6ab98e4696c8e5b362629d45be0b0f73b66d6a228` |
| TPY01-6 | 68 | Image620 | source-offer-TPY01-6.jpg | `7e67dcf2a3112f3a5012f6f9f89b6ca9fd2f76bb67bfc8657c26172931900703` |
| TPY00-3 | 69 | Image626 | source-offer-TPY00-3.jpg | `25a9dd76e1a3b033a1fcf5a69f24818b5cef1813f85c3578f608ec6fbd2a0456` |
| TPY01-3 | 69 | Image625 | source-offer-TPY01-3.jpg | `0389a450e0c55e7a6b1e5caccd577a8069f712a84db79236484c7361ecffb5cf` |
| THY00-3 | 69 | Image629 | source-offer-THY00-3.jpg | `69bc796bcca5370c5b77a4984b40eec0dbe8817685c3f8919f08ba98382ef371` |
| THY01-3 | 69 | Image628 | source-offer-THY01-3.jpg | `f63f1715501614c8a09d6c700320a8e2d9a6da7a8516a03818a7dcb447f3e4db` |
| TNN03-3 | 70 | Image633 | source-offer-TNN03-3.jpg | `ffdd860c7fa0b7bda2ba31752d19e45c50e21e39eb393f383c99d75ff619950e` |
| TNR01-3 | 73 | Image663 | source-offer-TNR01-3.jpg | `bd1c08fb01c829687e5aca83cc2590880258c9955259507a487d0599334d5c1c` |
| TPP00-2 | 73 | Image664 | source-offer-TPP00-2.jpg | `03d54f8a86a64b7956b6bc78a4d88cd1856fc241439455f9283ff7595c3d3df3` |
| TPD01-2 | 74 | Image671 | source-offer-TPD01-2.jpg | `82736c72e1ff5b28607f22e9e9a939c4dd3f4004bc46d6880b243442531d9f5d` |
| TPD00-2 | 74 | Image672 | source-offer-TPD00-2.jpg | `86704fb5a5bcf9722a27d708a8ee205384b9a58b632d723686c8e2d2c83eebae` |
| TPS03-3 | 75 | Image676 | source-offer-TPS03-3.jpg | `2e7ff0d717a6a7ca3a504ba108e5d4394881b35472a4633a9c43e39b15aa8e4a` |
| TPJ00-2 | 76 | Image689 | source-offer-TPJ00-2.jpg | `2a649d1ad1404f0acf539059fbaa320a6e9aafea718f8596a4202b4b087b74e6` |
| TPJ00-3 | 76 | Image688 | source-offer-TPJ00-3.jpg | `f5c436e222c59d43310659d8ecace7798eb4f478760e873183596684bef0966a` |
| TPJ01-3 | 76 | Image684 | source-offer-TPJ01-3.jpg | `34125b7962d85a5ef3345eda0c935b6403aefe80be204674254930dd5dc8ebfd` |
| TPB00-2 | 77 | Image695 | source-offer-TPB00-2.jpg | `675f1428242dfa975b26652a86b77ba0da2f987a26bd7e367f7602d08176ebf4` |
| TPB01-3 | 77 | Image694 | source-offer-TPB01-3.jpg | `4757004a6010ce3070e0c95dc6578a0109a45c6a5e3a459046a9535e84a24328` |
| BW00-0 | 77 | Image696 | source-offer-BW00-0.jpg | `af3116e7f1d6d3ab8160d65f31c4afac03a54c7f15a6f7af20b59291310c3240` |
| TBT10-3 | 78 | Image702 | source-offer-TBT10-3.jpg | `b865f80089b0dbd04a0804e44061ad77d70390349546193f7dce4bd85a50a761` |

## Version diff

- ไม่มีเอกสารเดิม → `0.1.0b candidate`: เสนอ customer catalog แบบ image-first พร้อมขอบเขตข้อมูล ภาพ และเกณฑ์ตรวจรับ
- RCA `0.1.0b → 0.1.1b`: บันทึกคำยืนยันว่าผู้ใช้หลักเป็นลูกค้า
- `0.1.0b candidate → 0.1.1b beta`: บันทึกอนุมัติ, local presentation, test evidence และ gates ที่ยังไม่ผ่าน
- `0.1.1b → 0.1.2b beta`: เพิ่มภาพต้นฉบับ 150 offers, provenance ledger, image-first ordering และกริดภาพ; ไม่แก้ canonical data
- Code/runtime: customer presentation + tests และ loopback preview; data/price/BOM/vault/pipeline ไม่เปลี่ยนจากงานนี้

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.2b | 2026-08-30 | beta | เติมภาพ source-photo 150 offers และ provenance; PM/canonical/BOM/public gates ยังเหลือ | uncommitted | ATHER |
| 0.1.1b | 2026-08-30 | beta | บันทึกอนุมัติและ local partial implementation; image mapping/public gates ยังไม่ผ่าน | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | เสนอหน้าลูกค้า ใช้ภาพสินค้าจริงและรายละเอียดชุด แยกข้อมูลภายในและ public-release gate | uncommitted | ATHER |
