---
version: "0.1.1b"
created_at: "2026-08-30T11:35:20+07:00,ATHER"
last_update: "2026-08-30T18:29:00+07:00,ATHER"
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

## Version diff

- ไม่มีเอกสารเดิม → `0.1.0b candidate`: เสนอ customer catalog แบบ image-first พร้อมขอบเขตข้อมูล ภาพ และเกณฑ์ตรวจรับ
- RCA `0.1.0b → 0.1.1b`: บันทึกคำยืนยันว่าผู้ใช้หลักเป็นลูกค้า
- `0.1.0b candidate → 0.1.1b beta`: บันทึกอนุมัติ, local presentation, test evidence และ gates ที่ยังไม่ผ่าน
- Code/runtime: customer presentation + tests และ loopback preview; data/price/BOM/vault/pipeline ไม่เปลี่ยนจากงานนี้

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.1b | 2026-08-30 | beta | บันทึกอนุมัติและ local partial implementation; image mapping/public gates ยังไม่ผ่าน | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | เสนอหน้าลูกค้า ใช้ภาพสินค้าจริงและรายละเอียดชุด แยกข้อมูลภายในและ public-release gate | uncommitted | ATHER |
