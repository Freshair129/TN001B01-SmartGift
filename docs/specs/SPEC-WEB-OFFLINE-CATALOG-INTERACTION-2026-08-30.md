---
version: "0.2.0b"
created_at: "2026-08-30T19:30:00+07:00,ATHER"
last_update: "2026-08-30T22:05:00+07:00,Claude"
status: "beta"
superseded_by: null
attributes:
  domain: "smartgift-customer-catalog"
  doc_type: "product-specification"
  scope: "separate web catalog and offline customer catalog"
  language: "th"
---

# SPEC — SmartGift Web Catalog และ Offline Customer Catalog

## 1. เป้าหมายและสถานะ

แยกประสบการณ์สำหรับลูกค้าออกเป็นสองช่องทางที่ใช้ข้อมูลชุดเดียวกัน แต่ส่งมอบคนละแบบ:

1. **Catalog หน้าเว็บ** — เปิดจาก URL สำหรับค้นหา เลือกหมวด เปรียบเทียบสินค้า และเปิดรายละเอียดชุดแบบโต้ตอบ
2. **Catalog ไฟล์ออฟไลน์** — ไฟล์ที่ส่งให้ลูกค้า เปิดด้วยการดับเบิลคลิกได้โดยไม่ต้องใช้อินเทอร์เน็ต มีประสบการณ์แบบ flipbook ที่ค้นหา/ซูม/เปลี่ยนหน้า/ดู thumbnails/auto-flip ได้

เอกสารนี้เป็น **C-3 / Risk HIGH candidate** เพราะเพิ่ม public surface และแพ็กเกจไฟล์ที่ต้องแยกจาก internal catalog, API และข้อมูลราคา/ต้นทุนอย่างชัดเจน รอบนี้ยังไม่แก้ application code หรือ deploy จนกว่าจะได้รับอนุมัติเอกสาร

## 2. หลักฐานและสิ่งที่เรียนรู้จาก reference

ตรวจตัวอย่างคู่แข่งที่ผู้ใช้ส่งมา: [FlipHTML5 reference](https://online.fliphtml5.com/xgczt/qizk/#p=1)

ความสามารถที่พบและจะนำมาเป็น baseline ด้าน interaction:

- เปลี่ยนหน้าและไปหน้าสุดท้าย
- page counter และช่องกระโดดไปหน้าที่ต้องการ
- zoom in และแถบ zoom
- thumbnails rail
- search ในเล่ม
- Auto Flip
- fullscreen
- sound toggle, social share และ email share ในเมนู More
- ลูกศรนำทางที่เห็นตลอดเวลา

SmartGift จะทำให้ชัดและทันสมัยขึ้นด้วยข้อมูลจริงของเรา: ภาพสินค้าเด่นกว่าเอฟเฟกต์, filter ตามหมวด/โอกาส, product detail drawer, ขยาย “ในชุดประกอบด้วย”, compare tray จำกัดไม่เกิน 3 รายการ และ CTA “ขอใบเสนอราคา” ที่ไม่แสดงต้นทุนภายใน

## 3. สมมติฐานที่ใช้รอการยืนยัน

1. หน้าเว็บลูกค้าจะมี entrypoint แยกจาก internal dashboard เช่น `/catalog/` หรือ `/catalog.html`; `#/catalog` เดิมยังเก็บไว้สำหรับการตรวจภายในจนกว่า cutover จะผ่าน
2. ไฟล์ออฟไลน์หลักจะเป็น **single-file HTML** ที่ฝัง customer-safe JSON และรูปที่อนุญาตทั้งหมด เพื่อให้เปิดจาก `file://` ได้โดยไม่พึ่ง fetch หรือ server; จะสร้าง PDF digital เป็น fallback สำหรับลูกค้าที่ต้องการพิมพ์
3. ทั้งสองช่องทางใช้ snapshot เดียวกันจาก `public/data/pricelist_public.json` และ `public/data/catalog_media.json` พร้อม manifest จาก `public/data/product_manifest.json` **ฉบับ customer-safe เท่านั้น** ที่อ่าน catalog version/hash ได้ในหน้าปกหรือเมนูข้อมูล; hash ที่แสดงต่อลูกค้าต้องเป็น hash ของ customer-safe snapshot เอง ไม่ใช่ hash ของ source ภายใน
4. รายการที่ภาพหรือ BOM ยังไม่ยืนยันจะติดสถานะตามจริงและไม่ถูกทำให้ดูเป็นสินค้าพร้อมขายด้วยภาพประดิษฐ์, ราคา 0 หรือข้อความเดา; ภาพ generated ใช้ได้เฉพาะแบบ `generated_from_source_reference` ที่มี label ตาม SPEC-EXPO-CATALOG-MEDIA ห้ามใช้ภาพสินค้าที่แต่งขึ้นโดยไม่มี source reference

## 4. ขอบเขตข้อมูลและความปลอดภัย

### ข้อมูลที่อนุญาตสำหรับลูกค้า

- ชื่อสินค้า/ชุด, รหัสอ้างอิงที่อนุญาต, หมวด, ภาพที่ผ่าน media allowlist
- คำอธิบายและส่วนประกอบที่มี `bom_status=verified`
- สถานะ “สอบถามราคา” หรือ SRP/quantity ladder ที่ผ่าน customer-safe projection
- ชื่อ occasion/tier/segment ที่เป็นข้อมูล portfolio และ approved customer copy

### ข้อมูลที่ห้ามอยู่ใน web หรือ offline package

- factory cost, margin, profit gate, CBM, freight และ supplier identity
- FlowAccount/source path/hash, audit log, internal formula, raw Excel/PDF
- CRM, รายชื่อลูกค้า, ผู้ติดต่อ, quotation history และ PII ทุกชนิด
- รูปที่ยังไม่จับคู่กับรายการขาย หากไม่มี label ว่าเป็น source reference

การซ่อนเมนูไม่ใช่ access control: web endpoint ต้องตอบเฉพาะ projection ที่ผ่าน allowlist; offline package ต้องสร้างจาก projection เดียวกันและตรวจด้วย forbidden-field scan ก่อนส่ง

**Blocker ที่พบตอน review (2026-08-30) — แก้แล้ว 0.1.2b:** `public/data/product_manifest.json` เคยมี `data_integrity_hashes` ที่ระบุ path/size/hash ของ source ภายใน (`pricelist_master.json`, `factory_costs.json`, `smartgift_catalog_master.json`) ในโฟลเดอร์ `public/` ที่ถูก deploy ซึ่งขัดกับข้อห้ามข้างต้นและ ADR-004 ข้อ 3. ตอน fix ยังพบว่า category slices (`public/data/categories/*.json`) ฝัง `logistics_freight_est` (อัตรา freight ต่อ CBM/kg, ต้นทุน inland China ต่อชิ้น) และ `packaging_carton` (CBM) ซึ่งต้องห้ามเช่นกัน. `generate_product_manifest.py` ถูกแก้ให้: (1) public manifest มี hash เฉพาะ `pricelist_public`/`catalog_media` ด้วย endpoint path ไม่ใช่ repo path, (2) lineage ภายในเต็มย้ายไป audit manifest ใต้ `data-pipeline/04_review_reports/` ที่ไม่ถูก deploy, (3) slice products ผ่าน field allowlist ตัด freight/carton/`product_master` ออก, (4) `catalog_version` คิดจาก hash ของ `pricelist_public` ไม่ใช่ master, (5) เพิ่ม fail-closed boundary scan ใน generator และ unit tests

**ความเสี่ยงที่ยังเหลือ — แก้แล้ว 0.1.3b:** internal dashboard ถูกแยกออกจาก `public/index.html` แล้ว: หน้า deploy (`index.html`) เหลือเฉพาะ customer catalog + Seasonal Expo แบบ customer-safe ถาวร (ไม่มีสูตร landed cost, คอลัมน์ factory/CBM/freight, supplier code, สถานะ profit gate หรือ path `data-pipeline/`; ราคา package แสดง "สอบถามราคา") ส่วน dashboard เต็มทั้ง 6 views ย้ายไป `public/internal.html` ซึ่ง `.vercelignore` กันออกจาก deployment สำหรับใช้ตรวจภายในผ่าน local server เท่านั้น; มี regression test `tests/test_public_surface_boundary.py` สแกน forbidden markers ในไฟล์ deploy ทุกไฟล์

## 5. ประสบการณ์ Catalog หน้าเว็บ

### Information architecture

1. **Landing** — โลโก้ Smart Gift Thailand, hero จากภาพสินค้าจริง, CTA “เลือกดูสินค้า” และ “เปิด Catalog ออฟไลน์”
2. **Browse** — search, หมวด 4 หมวด, filter occasion/tier, สลับ “สินค้ารายชิ้น/ชุดของขวัญ”, card ที่เห็นภาพก่อนข้อความ
3. **Product/Set detail** — gallery, ชื่อ/รหัส, สถานะราคา, คำอธิบาย, accordion “ในชุดประกอบด้วย”, ปุ่ม “เปรียบเทียบ” และ “ขอใบเสนอราคา”
4. **Compare tray** — รายการที่เลือกได้สูงสุด 3 รายการ, ลบ/สลับ, เปิดรายละเอียดแบบ side-by-side; ไม่แสดง cost/CBM
5. **Quote brief** — เก็บเฉพาะรหัสรายการและข้อความ brief ในหน้าจอ; ส่งออกเป็นข้อความที่ผู้ใช้คัดลอกได้ ไม่บันทึก PII หรือประวัติใบเสนอราคาใน catalog vault

### Interaction และ responsive behavior

- card คลิก/กด Enter เปิด detail drawer หรือ modal และคืน focus เมื่อปิด
- sticky filter bar บน desktop; บนมือถือใช้ bottom sheet และไม่เกิด horizontal overflow
- search ใช้ชื่อไทย/อังกฤษ/รหัส; empty/loading/error state ต้องอ่านได้และ retry ได้
- motion ใช้เฉพาะ transition สั้น ๆ และปิดได้เมื่อ `prefers-reduced-motion: reduce`
- keyboard: Tab, Enter, Escape, arrow navigation ใน gallery/flipbook และ focus ring ที่เห็นชัด
- image-first: `object-fit: contain`, มี caption/source status ตาม manifest และไม่ใช้ภาพใกล้เคียงแทนภาพที่ยังไม่มี

## 6. ประสบการณ์ Catalog ไฟล์ออฟไลน์

### รูปแบบการส่งมอบ

- `SmartGift-Catalog-Offline-<catalog_version>.html` — เปิดได้ด้วย double-click จาก `file://`; ไม่มี network request
- `SmartGift-Catalog-Offline-<catalog_version>.pdf` — digital PDF สำรอง; selectable Thai text, bookmarks และ internal links ถ้าข้อมูลพร้อม
- ไฟล์ ZIP เป็น convenience wrapper ที่มี HTML, PDF และ `README-เปิดใช้งาน.txt`; ไม่จำเป็นต้องติดตั้งโปรแกรมเพิ่ม
- ขนาดไฟล์ HTML เดี่ยวตั้งเป้าไม่เกิน 25 MB เพื่อแนบอีเมลได้: ภาพฝังต้องผ่าน downscale/บีบอัดสำหรับจอ (ไม่ใช้ไฟล์ต้นฉบับเต็ม) และตัดภาพนอก allowlist ออกตั้งแต่ build; ถ้าเกินเป้าให้รายงานใน build manifest ไม่ปล่อยผ่านเงียบ ๆ
- ฟอนต์ไทยใช้ subset ฝังในไฟล์จากฟอนต์ open license (เช่น Sarabun/OFL) พร้อม system font stack เป็น fallback; ห้ามโหลดฟอนต์จาก network ตาม offline acceptance

### Flipbook controls

แถบควบคุมใช้โทนส้มและไอคอนเรียบง่าย โดยมี:

- สารบัญ, ย้อนกลับ, ถัดไป, page counter และช่องไปหน้าที่ต้องการ
- thumbnails rail ที่เปิด/ปิดได้
- ค้นหาในเล่ม
- zoom in/out และ fit-to-screen
- Auto Flip พร้อมปรับความเร็ว; ค่าเริ่มต้นปิด และเมื่อ `prefers-reduced-motion: reduce` ให้ปิด auto-flip กับใช้การเปลี่ยนหน้าแบบตัดแทนแอนิเมชันพลิก
- เต็มจอ
- คัดลอกลิงก์ไม่ได้เมื่อเปิด `file://`; ใช้ปุ่ม “แชร์ไฟล์” เพื่อแสดงชื่อไฟล์/วิธีแนบแทน
- ปุ่ม “ดูสินค้าในหน้านี้” เปิด product detail overlay จาก snapshot เดียวกัน

### Offline acceptance

- เปิดจาก `file://` ใน Chrome/Edge หลังปิด network แล้วยังโหลดภาพ ข้อมูล และ interaction ครบ
- ไม่มี external font, CDN, analytics, API หรือ fetch ที่ทำให้หน้า blank เมื่อออฟไลน์
- เปิด search, thumbnails, zoom, auto-flip, fullscreen, keyboard navigation และ detail overlay ได้
- แสดง version/hash และ disclaimer ว่าเป็น customer catalog snapshot
- ถ้าสื่อหายหรือข้อมูลไม่ครบ ให้แสดง “ยังไม่มีภาพ/รายละเอียดที่ยืนยัน” แทนการใช้ placeholder ที่ดูเหมือนสินค้าจริง

## 7. Visual direction — SmartGift Orange

- Primary orange: `#FC5900`
- Deep brown: `#675443`
- Gold accent: `#D6A641`
- Warm paper: `#FFF8F0`
- Ink: `#2C241F`
- ใช้โลโก้ Smart Gift Thailand จาก asset ที่ผู้ใช้ส่ง, รักษาสัดส่วนและ clear space
- รูปสินค้าเป็นพระเอก; หลีกเลี่ยง glassmorphism, dark dashboard, เงาหนัก และ 2.5D ที่บังสินค้า
- Desktop ใช้ editorial grid; mobile ใช้ภาพเต็ม card และ controls แบบ bottom sheet
- Web ใช้ white/warm paper เป็นพื้น; offline viewer ใช้ deep brown ที่มีแถบส้ม แต่หน้าเอกสารยังคงพื้นกระดาษเพื่ออ่านง่าย

## 8. Source of truth และ lineage

| ช่องทาง | Source | ขอบเขต |
|---|---|---|
| Web | `public/data/pricelist_public.json` + `public/data/catalog_media.json` | customer-safe projection และรูปที่ผ่าน allowlist |
| Web (หมวด) | `public/data/categories/*.json` ตาม index ใน manifest | slice ต่อหมวดสำหรับ browse; อยู่ใต้ allowlist เดียวกัน |
| Manifest | `public/data/product_manifest.json` (customer-safe) | catalog version/hash ของ customer-safe artifacts เท่านั้น; ห้ามมี source path ภายใน (ดู Blocker ใน §4) |
| Offline HTML | snapshot ที่ build จาก source เดียวกัน | ฝังข้อมูล/รูปทั้งหมดในไฟล์เดียว, no network |
| Offline PDF | layout proof จาก `output/pdf/` | ไม่มี cost/CBM/profit/PII; สถานะ proof จนกว่าจะผ่าน content/media/rights review |
| Internal review | `data-pipeline/02_prepared/pricelist_master.json` และ local API | ไม่ส่งออกไปยังลูกค้าและไม่ฝังใน package |

ต้องเก็บ build manifest ที่มี catalog version, source hashes, asset list และ generated-at; manifest สำหรับลูกค้าห้ามมี source path, supplier หรือ PII

## 9. Verification plan หลังอนุมัติ

1. สร้าง web entrypoint แยกและตรวจ route/API ว่ามีเฉพาะ customer-safe allowlist → ห้ามมี internal menu/field ใน DOM หรือ response
2. สร้าง offline single-file HTML และ PDF จาก snapshot เดียวกัน → ตรวจเปิดจาก `file://` หลังปิด network
3. ทดสอบ interaction: search, filters, detail, BOM disclosure, compare ≤3, quote brief, thumbnails, zoom, auto-flip, fullscreen, keyboard และ reduced motion — หมายเหตุ: ณ 2026-08-30 BOM ทั้ง 17 แถวยัง `verified=false` จึงยังไม่มีรายการที่เปิดเผย BOM ได้; ข้อนี้ผ่านได้ต่อเมื่อมี BOM ยืนยันแล้วอย่างน้อยหนึ่งรายการผ่าน lane ตาม ADR-005
4. ตรวจ viewport 1440, 1024, 768, 390 และ 320 px → ไม่มี overflow, ภาพไม่บิด, ภาษาไทยไม่ตก/ถูกบัง
5. ตรวจ asset provenance และ content audit: อย่างน้อยหนึ่ง canonical SKU และหนึ่ง offer ต้องมีภาพ/รหัสตรงกันก่อนเรียก image-first acceptance ผ่าน
6. สแกน forbidden fields, PII, external URLs, network calls และ metadata ทั้ง web bundle/offline HTML/PDF/ZIP — ปัจจุบัน `validate_public_projection` ใน exporter ครอบคลุมเฉพาะ `pricelist_public.json`; ต้องสร้าง scanner ระดับ bundle เพิ่มก่อนถือว่าเกณฑ์นี้ตรวจได้จริง
7. สร้าง preview report และ hash ของไฟล์ส่งมอบ; deploy web แยกจาก internal app และไม่ถือ local/offline proof เป็น production evidence

## 10. ผลกระทบและสิ่งนอกขอบเขต

- **MEDIUM/HIGH:** มี public surface ใหม่, static snapshot lifecycle และความเสี่ยงข้อมูลภายในรั่วผ่าน bundle
- ไม่เปลี่ยน schema GenesisBlock, ProductMaster, BOM, pricing calculator, inventory cascade หรือ vault
- ไม่สร้าง customer login, CRM, payment, order history หรือ quote persistence
- ไม่อัปโหลดไฟล์ไป FlipHTML5; ใช้ interaction เป็นแนวคิดเท่านั้นและคง asset/ข้อความของ SmartGift
- ไม่ใช้ภาพ/โลโก้/ข้อความของคู่แข่งในไฟล์ส่งลูกค้า

## 11. Parent / peer review

- Parent: [`AGENTS.md`](../../AGENTS.md), [`SMARTGIFT_SYSTEM_ARCHITECTURE.md`](../SMARTGIFT_SYSTEM_ARCHITECTURE.md), [`DATA_PIPELINE_AND_VAULT_STRUCTURE.md`](../DATA_PIPELINE_AND_VAULT_STRUCTURE.md)
- Peer: [`SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30.md`](SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30.md) — image-first และ customer-safe boundary
- Peer: [`SPEC-SMARTGIFT-LANDSCAPE-CATALOG-2026-08-30.md`](SPEC-SMARTGIFT-LANDSCAPE-CATALOG-2026-08-30.md) — PDF digital/print proof และการไม่ใช้ภาพเดา
- Peer: [`SPEC-EXPO-CATALOG-MEDIA-2026-08-30.md`](SPEC-EXPO-CATALOG-MEDIA-2026-08-30.md) — media allowlist, สถานะภาพ `source-photo`/`generated_from_source_reference` และ label ที่ต้องแสดง
- Peer: [`ADR-004-CUSTOMER-SAFE-PRICELIST-ENDPOINT.md`](../decisions/ADR-004-CUSTOMER-SAFE-PRICELIST-ENDPOINT.md) — public projection และ deployment boundary
- Peer: [`ADR-003-SEASONAL-PKG-SCHEMA-PROFIT-GATE.md`](../decisions/ADR-003-SEASONAL-PKG-SCHEMA-PROFIT-GATE.md) — package identity/seasonal gate; ไม่ส่ง cost/profit ให้ลูกค้า

## 12. Approval gate

Boss อนุมัติและสั่ง build offline bundle เมื่อ 2026-08-30 — สร้างแล้วด้วย `pipeline/build_offline_catalog.py` (deliverables ใน `output/offline/`, audit manifest ใน `data-pipeline/04_review_reports/offline_bundle_manifest.json`)

**ผล offline acceptance (2026-08-30):** ไฟล์ HTML เดี่ยว 1.88 MB / 51 หน้า มี network request เดียวคือตัวเอกสารเอง (ไม่มี subresource/fetch/`<link>`/`@import`) จึงเปิดจาก `file://` ได้โดยไม่พึ่ง network; ทดสอบจริงผ่านเบราว์เซอร์: สารบัญ, เปลี่ยนหน้า/กระโดดหน้า, thumbnails 51 รายการ, ค้นหาในเล่ม, ซูม/fit, Auto Flip (เริ่มต้นปิด, ปิดถาวรเมื่อ reduced motion), เต็มจอ, overlay "สินค้าในหน้านี้", dialog "แชร์ไฟล์", keyboard navigation ทำงานครบ; ปก/หน้าท้ายแสดง version + snapshot hash + disclaimer; boundary scan (forbidden markers + external refs) และ size gate ผ่าน; PDF proof 10.5 MB สร้างผ่าน headless Chrome (selectable Thai text; ไม่มี bookmarks — ข้อจำกัดของ print-to-pdf); ZIP 11.4 MB มี HTML + PDF + README

**Deviation ที่บันทึกไว้:** ฟอนต์ไทยใช้ system font stack (Leelawadee UI/Tahoma/Noto Sans Thai) ยังไม่ฝัง Sarabun subset — ต้องดาวน์โหลดไฟล์ฟอนต์ OFL ซึ่งรอ approve แยก; ผลกระทบ: การ render ต่างเครื่องอาจต่างกันเล็กน้อย แต่ไม่มีการโหลดฟอนต์จาก network

## Version diff

- `0.1.0b candidate`: เพิ่มข้อเสนอแยก web catalog กับ offline single-file/PDF, interaction baseline จาก FlipHTML5, SmartGift Orange visual system, customer-safe data boundary และ verification gates
- `0.1.3b` → `0.2.0b` (beta): Boss อนุมัติ; build offline bundle ครั้งแรก — flipbook HTML เดี่ยว 51 หน้า + PDF proof + ZIP ผ่าน `pipeline/build_offline_catalog.py`, offline acceptance และ boundary scan ผ่าน, บันทึก deviation เรื่องฟอนต์ (system stack, Sarabun subset รอ approve)
- `0.1.2b` → `0.1.3b`: แยก internal dashboard ออกจาก `public/index.html` — หน้า deploy เหลือ catalog + expo แบบ customer-safe ถาวร, dashboard เต็มย้ายไป `public/internal.html` (vercelignore), เพิ่ม boundary regression test สำหรับไฟล์ deploy
- `0.1.1b` → `0.1.2b`: ปิด Blocker ของ `product_manifest.json` — แยก public/internal manifest, allowlist ให้ category slices (ตัด freight/CBM/carton/`product_master`), `catalog_version` จาก hash ของ `pricelist_public`, เพิ่ม boundary scan + tests; บันทึกความเสี่ยงที่เหลือของ `public/index.html`
- `0.1.0b` → `0.1.1b` (review pass): บันทึก Blocker ของ `product_manifest.json` ที่มี source path/hash ภายในใน `public/`; เพิ่ม lineage ของ category slices และ customer-safe manifest; กำหนด size budget ≤25 MB กับฟอนต์ไทย subset ฝังไฟล์; auto-flip เริ่มต้นปิดและเคารพ reduced motion; ระบุ dependency ว่า BOM ยัง `verified=false` ทั้ง 17 แถว และ scanner ระดับ bundle ยังต้องสร้าง; เพิ่ม peer SPEC-EXPO-CATALOG-MEDIA และเงื่อนไขภาพ generated ที่มี source reference

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.2.0b | 2026-08-30 | beta | Boss อนุมัติ; build offline bundle แรก (HTML 51 หน้า/PDF/ZIP) ผ่าน acceptance + boundary scan; deviation ฟอนต์บันทึกแล้ว | 9b4f749 | Claude |
| 0.1.3b | 2026-08-30 | candidate | แยก internal dashboard ไป internal.html (ไม่ deploy); index.html เหลือ catalog+expo customer-safe ถาวร; เพิ่ม public surface boundary test | ac52752 | Claude |
| 0.1.2b | 2026-08-30 | candidate | ปิด blocker product_manifest: แยก public/internal manifest, slice allowlist ตัด freight/CBM, boundary scan + tests; note ความเสี่ยง index.html | 374278e | Claude |
| 0.1.1b | 2026-08-30 | candidate | review pass: blocker product_manifest, lineage หมวด/manifest, size/font budget, reduced motion, BOM/scanner dependency, peer media spec | cd5d7d2 | Claude |
| 0.1.0b | 2026-08-30 | candidate | เสนอ web/offline catalog แยก runtime พร้อม flipbook interactions และ offline acceptance | cd5d7d2 | ATHER |
