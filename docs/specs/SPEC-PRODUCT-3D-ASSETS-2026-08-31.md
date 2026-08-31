---
version: "0.2.7b"
created_at: "2026-08-31T04:02:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T12:39:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "product-3d-assets"
  scope: "local 3D review candidates and canonical ProductMaster evidence coverage; no customer publication or registry migration"
  language: "th"
---

# สเปก: สร้างโมเดลสินค้า 3D จากภาพ catalog และเก็บไฟล์แยก

## 1. สถานะ ผู้รับผิดชอบ และเป้าหมาย

- เจ้าของขอบเขต/ผู้อนุมัติ: Boss; ผู้จัดทำข้อเสนอทางเทคนิค: ATHER
- ทีมเพิ่มเติม/issue ภายนอก: ยังไม่กำหนด; อ้างอิงคำขอใน task นี้ ไม่สร้าง ticket หรือมอบหมายบุคคลอื่น
- สถานะ: **P0–P1 local artifacts พร้อมตรวจใน v004; Boss อนุมัติ implementation ด้วย “ลุย” แต่ยังไม่อนุมัติ likeness/public use; P2–P3 รอ review**
- Complexity: C-3; Risk: MEDIUM — เพิ่ม artifact contract แบบ local ไม่มี schema migration
- Parent: [ADR-008](../decisions/ADR-008-PRODUCT-3D-ASSET-PIPELINE.md), [AGENTS.md](../../AGENTS.md)
- Peer: [image-first spec](SPEC-CUSTOMER-CATALOG-IMAGE-FIRST-2026-08-30.md), [registry spec](SPEC-KNOWLEDGE-REGISTRY-2026-08-31.md), [canonical schema](../../config/schema_genesisblock.yaml)

เป้าหมายคือไฟล์โมเดลจริงที่นำไปประกอบ catalog 3D ต่อได้ ตรวจแหล่งภาพย้อนหลังได้ และไม่ต้องสร้าง geometry ใหม่เมื่อเปลี่ยนเพียงสี ไม่ใช่การปรับ UI หรือเปิดระบบใหม่ในรอบนี้

[ASSUMPTIONS]

1. “model 3D” หมายถึง mesh ที่หมุนได้และ export เป็น `.glb` ไม่ใช่เพียงภาพ PNG ที่ดูมีมิติ
2. ขอเริ่ม pilot 6 รุ่นที่มีภาพต้นฉบับแยกชัดเจนก่อน; ไม่ได้ถือว่าผู้ใช้จำกัดงานระยะยาวไว้เพียงหกรุ่น
3. ยอมให้สร้างแบบประมาณเพื่อ review ภายใน โดยระบุส่วนที่ไม่เห็น/ไม่มีขนาด; ไม่ถือเป็นแบบผลิตหรือ AR true-scale ที่ยืนยันแล้ว

สมมติฐานทั้งสามได้รับอนุมัติให้เริ่ม pilot แล้ว ไม่ใช่การยืนยันความแม่นยำของ geometry หรืออนุมัติ public use

## 2. บริบท ปัญหา และหลักฐานปัจจุบัน

SmartGift ต้องให้ลูกค้าเห็นสินค้าจริงและแยกรุ่นได้ หน้า anatomy เดิมมีรูปทรง procedural อยู่ใน `public/gift-anatomy-3d.js` แต่ยังไม่ใช่ไฟล์ asset แยกที่พิสูจน์เทียบกับสินค้าแต่ละรุ่น การใช้รูปทรงทั่วไปแทนทุกสินค้าจะทำให้ catalog เข้าใจผิดแม้จะหมุนได้

จำนวน prepared records ไม่เท่ากับจำนวนแม่พิมพ์/geometry: `ProductMaster.json` มี canonical records 16 และ source projections 427; `pricelist_master.json` มี product_masters 427 และ product_families 32 กลุ่ม ยังไม่มีผลตรวจ geometry ที่รองรับการประกาศจำนวนโมเดลทั้งหมด การสร้างซ้ำตามสีหรือรวมทั้งหมดตาม family จึงเสี่ยงทั้งจำนวนเกินและรวมผิดรุ่น

หลักฐานที่อ่านจากไฟล์จริง ณ 2026-08-31:

| แหล่ง | สิ่งที่ยืนยันได้ | สิ่งที่ยังยืนยันไม่ได้ |
|---|---|---|
| `public/data/catalog_media.json` | products 6, sets 153 และ hero 1 references | ไม่ใช่จำนวน physical products/unique meshes |
| `output/catalog-internal/production-manifest.json` | source PDF, page และ image mapping ของ 6 รหัส | ขณะเสนอเอกสารยังไม่ตรวจซ้ำ; P0 ตรวจ code ทุกหน้าและ visual หน้า 4/6 แล้ว ดู §9 |
| `output/catalog-internal/refs/single-*-source.png` | เปิดตรวจ original crops ของ 6 รุ่นแล้ว | ไม่รับรองว่าเป็นภาพถ่ายจริงแทน supplier render หรือมีมุมครบ |
| `public/gift-anatomy-3d.js` | Three.js 0.160.0 และ primitive geometry ใน scene | ไม่ใช่ผล reconstruction รายรุ่น |
| เครื่องมือ local | Node ใช้ได้; ไม่พบ Blender ใน PATH/ตำแหน่งมาตรฐานที่ตรวจ | ไม่ใช่การพิสูจน์ว่าไม่มี Blender ทุกตำแหน่ง; export/render pipeline ยังไม่ทดสอบ |

ไม่ใช้ภาพชุด TGC09-3 เป็น pilot ขวดน้ำ: peer spec บันทึกความขัดแย้งระหว่างภาพกับ BOM และยังไม่มี canonical pairing ที่ยืนยัน ห้ามอนุมานว่าเป็น `pm:PM-BOTTLE-LED` จากลักษณะคล้ายกัน

## 3. ขอบเขตและชุดเริ่มต้นที่เสนอ

### อยู่ในขอบเขตหลังอนุมัติ

- แยก geometry ของหกรหัสด้านล่าง เก็บ GLB/วัสดุ/metadata/preview เป็นไฟล์แยก
- เก็บข้อมูล rebuild ที่แก้รูปทรงต่อได้ และ local index สำหรับ review ไม่คัด raw PDF มาซ้ำทั้งไฟล์
- ตรวจ export/re-import, source hashes, รูปทรงเทียบภาพ และสถานะส่วนที่ประมาณ
- ตรวจสองรุ่นแรกก่อนขยายอีกสี่รุ่น; ถ้า likeness ไม่ผ่านให้รายงานและขอภาพเพิ่ม ไม่ลดเกณฑ์เพื่อให้ครบจำนวน

### นอกขอบเขต

- การสร้างครบ catalog หรือประกาศจำนวน geometry ทั้งหมดโดยใช้จำนวน prepared rows แทน
- การแก้ UI/API, ราคาหรือ BOM, canonical ProductMaster, schema, registry ledger และ vault
- การสร้างขวด/สินค้าอื่นจากภาพชุดที่ mapping ยังขัดแย้ง, แบบผลิต CAD, USDZ/AR, animation กลไก
- external image-to-3D, upload ภาพ, paid service, ติดตั้ง Blender ระดับระบบ, commit/push/deploy

### Pilot 6 รุ่น

ทุก path ในตารางอ้างใต้ `output/catalog-internal/refs/` และทุก page เป็นเลข 1-based **ตาม production manifest เดิม** ต้องตรวจ source page/code ก่อนเริ่มขึ้นรูป

| ลำดับ | Source code / หน้า PDF | Original crop | รูปทรงที่เห็น / ข้อจำกัด |
|---|---|---|---|
| 1 | S1033 / 6 | `single-S1033-source.png` | power bank สีขาว มีสายและขาตั้ง; ภาพระบุ 69.3 × 106.4 × 17.1 มม. ต้องยืนยันขอบเขตตัวถังเทียบอุปกรณ์ยื่น |
| 2 | DW03 / 4 | `single-DW03-source.png` | ตัวถังส้ม มีวงชาร์จและสายด้านหลัง; P0 พบ Size 108.3 × 67.3 × 23 มม. แต่ขอบเขตว่ารวมชิ้นยื่นหรือไม่ยังต้องยืนยัน |
| 3 | S-1052 / 2 | `single-S-1052-source.png` | ตัวถังดำทรงเหลี่ยมโค้ง วงชาร์จ สายคล้อง จอ; มุมที่ไม่เห็นต้องระบุ estimated |
| 4 | BST61401 / 3 | `single-BST61401-source.png` | ตัวถังขาวมีร่อง วงชาร์จและห่วงสีเทา; มุมมองไม่ให้ขนาดวัดจริง |
| 5 | W502 / 7 | `single-W502-source.png` | ตัวถังสีงาช้าง วงชาร์จและขาตั้ง; มีสองมุม แต่ตำแหน่งบานพับ/ความหนาต้อง review |
| 6 | UT3056 / 5 | `single-UT3056-source.png` | ตัวถังลายพราง ปุ่มส้มและสายคล้อง; น้ำกระเซ็นใน artwork บังบางส่วน ห้ามสร้างน้ำเป็นส่วนสินค้า |

S1033/UT3056 ใน public media ถูกระบุ generated-clean จึงใช้ original crops ข้างต้นเป็นหลัก ไม่ใช้ภาพ generated เพื่อยืนยันรายละเอียดที่ภาพต้นฉบับไม่มี

## 4. สัญญาไฟล์และวิธีขึ้นรูป

```text
PDF + original crops (hash/locator)
          ↓ ตรวจ source code / ขนาด / มุมที่มองเห็น
shape definition ── material variants
          ↓ export
GLB + metadata + preview จาก GLB ที่ re-import
          ↓ ตรวจคุณภาพ
internal model index → catalog integration ภายหลังอนุมัติแยก
```

เสนอที่เก็บแบบ versioned ใต้ `output/catalog-3d/`:

```text
model_catalog.json
<source-code>/v001/
  model.glb
  geometry-source.json
  variants.json
  metadata.json
  preview.png
```

- `model.glb`: geometry จริง มี default material ที่เปิดได้ทันที textures/buffers ฝังในไฟล์ ไม่พึ่ง URL ภายนอก ต้องมีความหนาและ silhouette ไม่ใช่ป้ายภาพแบนหมุนตามกล้อง
- `geometry-source.json`: ค่ารูปทรง/ส่วนประกอบที่ใช้ rebuild พร้อม generator version; code สำหรับ rebuild เก็บใน repo หลังอนุมัติ ไม่อ้างว่าเป็น `.blend` หรือ factory CAD
- `variants.json`: สี/วัสดุที่มีหลักฐาน ผูกกับ material slots เดิม ไม่คัด geometry ซ้ำ การเปลี่ยน variant ต้องใช้ consumer ที่อ่าน sidecar นี้; ไม่อ้างว่า viewer glTF ทั่วไปจะอ่าน JSON เพิ่มเอง
- `metadata.json`: internal provenance/ขนาด/สถานะตรวจรับ ตามตารางด้านล่าง
- `preview.png`: render จากไฟล์ GLB หลัง re-import ไม่ใช้ภาพ source หรือภาพ AI มาแทนผล render
- `model_catalog.json`: index ที่อ้างเฉพาะชุด version ที่ตรวจแล้ว; ไม่เป็น ProductMaster master ใหม่ รุ่นที่ hold ต้องยังเห็นได้ในรายงาน แต่ไม่อยู่ในรายการ ready

ไฟล์ GLB ใช้เมตร, right-handed, +Y up และด้านหน้า +Z ตาม [glTF 2.0 §3.4](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#coordinate-system-and-units) กำหนด origin กึ่งกลางฐานสำหรับวางในฉากเป็น convention ของโปรเจกต์ ส่วนขนาดที่ไม่ทราบให้บันทึก scale เป็น estimated แม้ตัวเลขในไฟล์จะมีหน่วยเมตร

แนวทางขึ้นรูปคือ local photo-referenced modeling: สร้าง body/ขอบโค้ง/ช่อง/สาย/ขาตั้งให้สัมพันธ์กับภาพ ไม่คาดหวังว่าภาพมุมเดียวจะแปลงเป็น geometry ที่ถูกต้องทุกด้านได้อัตโนมัติ ใช้ mesh แยกตามชิ้นที่มองเห็นเท่าที่จำเป็น ไม่เพิ่มกลไกภายในที่ไม่มีหลักฐาน ใช้ [GLTFExporter](https://threejs.org/docs/pages/GLTFExporter.html) เป็น candidate ของ export tool; ต้องพิสูจน์ความเข้ากันได้กับเวอร์ชันที่ pin ใน P0 ไม่ถือว่าเอกสาร current รองรับ API ทุกอย่างใน 0.160.0

### เกณฑ์ใช้ geometry ร่วมกัน

สี ผิวด้าน/เงา หรือลายเปลี่ยนอย่างเดียว → ใช้ mesh เดิมและเปลี่ยนวัสดุ ส่วนฝา หูจับ สาย/ช่องเสียบ หรือสัดส่วนต่างกัน → ไม่รวมอัตโนมัติ ขนาดต่างกันจะใช้ scale เดียวกันได้ต่อเมื่อมีหลักฐานสัดส่วน/รายละเอียดเหมือนกันจริง และบันทึกเหตุผลการรวม ไม่ใช้ product_family เป็น geometry ID

### Metadata ขั้นต่ำ

| Field | ความหมาย / เงื่อนไข |
|---|---|
| `asset_key`, `asset_version` | local artifact key และ version ภายในแพ็กเกจเท่านั้น ไม่ออก canonical/registry ID ใหม่ |
| `source_product_code` | รหัสจาก catalog เช่น S1033 ไม่ใช่ primary key ของ ProductMaster |
| `canonical_product_id`, `mapping_status` | null + unresolved จนพิสูจน์ pairing; ถ้ามีต้อง resolve กับ schema/record จริง |
| `sources[]` | relative file path, SHA-256, PDF page จากหลักฐาน, locator verification status; ไม่เก็บ contact headers |
| `registry_refs` | doc_id/pic_id/version IDs เฉพาะที่ resolve และ bytes ตรง; ไม่พบให้ null + unregistered ห้ามสร้างเอง |
| `dimensions`, `dimension_status` | หน่วยเมตร/แหล่งขนาด/ส่วนที่วัด; source-annotated หรือ estimated ไม่ใช้คำว่า measured โดยไม่มีการวัด |
| `estimated_regions[]` | เช่น back, underside, port-depth; ส่วนที่ภาพไม่ยืนยันต้องแยกจาก observed |
| `geometry_sha256`, `glb_sha256` | geometry payload สำหรับพิสูจน์ reuse และ hash ของไฟล์ส่งมอบ; rebuild ไม่จำเป็นต้องได้ GLB hash เดิมถ้า metadata เปลี่ยน |
| `generator`, `review_status`, `rights_status` | เครื่องมือ/เวอร์ชัน, draft/needs-reference/review-ready/approved; สิทธิ์เผยแพร่ยัง pending-owner-review ถ้าไม่มีหลักฐาน |

API/endpoints และ database migration: **ไม่เกี่ยวข้องใน pilot นี้** ไม่มีการสร้าง route หรือเพิ่ม registry Media subtype การอ่านแหล่งภาพจาก registry ไม่ได้อนุมัติให้เปลี่ยนทะเบียนเพื่อรองรับ GLB

## 5. ความปลอดภัย ความเสี่ยง และทางเลือก

ใช้เฉพาะไฟล์สินค้า allowlist ไม่มี CRM/PII/quotation history ไม่แก้ Excel และไม่ส่ง source images ไปบริการภายนอก metadata ภายในมี path/hash จึงต้องไม่คัดเข้า public payload หรือ GLB extras โดยอัตโนมัติ เก็บไว้ใต้ output ซึ่ง `.vercelignore` ปัจจุบัน exclude; ก่อนใช้งานจริงยังต้องตรวจ server route ไม่ให้ expose directory นี้ด้วย

| ความเสี่ยง | ผลกระทบ / โอกาส | การลดความเสี่ยง |
|---|---|---|
| ภาพไม่ครบด้าน ทำให้ทรง/พอร์ตผิด | สูง / สูง | estimated regions + visual gate; ขอรูปด้านที่ขาดสำหรับงานแม่นยำ |
| รวมคนละรุ่นเพราะชื่อ/family คล้าย | สูง / กลาง | evidence-based geometry grouping; canonical mapping unresolved จนตรวจผ่าน |
| ภาพ generated หรือ overlay ถูกเข้าใจเป็นของจริง | สูง / กลาง | original-only references; แยก water/background และไม่เติม certification/functional claims |
| GLB หนักหรือ shader/texture เปิดไม่ได้ | กลาง / กลาง | self-contained, re-import, ตรวจ triangle/bytes และ render artifact จริง |
| ภาพ/metadata ภายในถูกเผยแพร่เกินขอบเขต | สูง / ต่ำเมื่อคุม allowlist | local-only, no upload, no public extras; owner review ก่อนเผยแพร่ |
| เครื่องมือ export ที่มีไม่พอ | กลาง / กลาง | P0 capability gate; แจ้ง blocker ไม่ติดตั้งระบบ/ซื้อบริการเอง |

ทางเลือกภาพนิ่ง, primitive generic, external image-to-3D และ factory CAD เปรียบเทียบใน ADR-008; เลือก local photo-referenced modeling สำหรับ pilot ไม่รับรอง photorealism หรือ manufacturing accuracy

## 6. แผนหลังอนุมัติและเกณฑ์ตรวจรับ

ผู้ดำเนินการที่เสนอ: ATHER; ผู้ review ความเหมือน/ยอมรับส่วนประมาณ: Boss ยังไม่กำหนดวันส่งทั้ง catalog ประเมินขนาดงานเป็น phase ไม่รับปากเวลาที่ไม่ผ่าน capability test

| Phase | งาน / ขนาดงานตั้งต้น | Gate |
|---|---|---|
| P0 | freeze 6 sources, ตรวจหน้า/code, ทดสอบ export/re-import หนึ่ง asset, บันทึกเครื่องมือ — 1 capability batch | hashes ตรง; ไม่ต้อง external upload/ติดตั้งระบบ; ถ้าไม่ได้ให้หยุดแจ้ง |
| P1 | geometry + material slots + metadata + preview ของ S1033/DW03 — 2 โมเดล | automated tests ผ่าน และส่ง Boss review likeness ก่อนเพิ่มอีก 4 |
| P2 | อีก 4 รุ่น ใช้เกณฑ์เดียวกัน — 4 โมเดล | ห้ามนับ needs-reference เป็นโมเดลตรวจรับแล้ว |
| P3 | ตรวจทั้งชุดและสร้าง versioned index — 1 package | ไม่มี missing file/source mismatch; สรุป completed/estimated/held แยกกัน |

### Automated checks

- **3D-01:** GLB glTF 2.0 parse/re-import ได้; buffer/accessor/index ถูกต้อง ไม่มี NaN/Infinity หรือ external resource; bounds มีความหนาจริง
- **3D-02:** source hashes/page-code verification status ครบ; missing/changed input หยุด publish ไม่สลับใช้รูปใกล้เคียง
- **3D-03:** metadata ทุกโมเดลมี scale status/estimated regions และ unresolved canonical mapping ไม่ถูกเปลี่ยนเป็น pm อัตโนมัติ
- **3D-04:** เปลี่ยน material variant แล้ว geometry payload ไม่เปลี่ยน; มี test บน synthetic fixture เมื่อแหล่งจริงมีเพียงสีเดียว ไม่สร้างสีที่ไม่มีหลักฐานเพื่อให้ test ผ่าน
- **3D-05:** เป้าหมาย pilot ไม่เกิน 50,000 triangles และ 5 MiB ต่อ GLB; รายงานค่าจริงและเหตุผลถ้าเกินก่อนรับงาน ไม่กล่าวอ้าง FPS/มือถือโดยไม่ได้วัด
- **3D-06:** สร้าง preview จาก exported GLB; ย้ายแพ็กเกจแล้ว resource references ยัง resolve ได้ ไม่พึ่ง absolute path บนเครื่องผู้สร้าง
- **3D-07:** unit tests สำหรับ identity/metadata/variants และ integration test สำหรับ export→import→render; negative tests missing source, invalid mesh, interrupted publish และ unresolved mapping

### Visual / owner checks

- **3D-08:** เทียบ front/side/back กับ reference ที่มี: silhouette, สีพื้น, ชิ้นส่วนหลัก, ขอบ/รอยต่อ/สาย/ขาตั้ง; ด้านที่ไม่มีภาพดูได้แต่ไม่เรียกว่า verified
- **3D-09:** ไม่มี background/น้ำ/เงาถ่ายภาพติดเป็นวัตถุสินค้า; ไม่มีภาพแบนใช้แทนทรงทั้งชิ้น ไม่มีตัวอักษร/เครื่องหมายรับรองที่แต่งขึ้น
- **3D-10:** S1033 ใช้ขนาดในภาพหลังตรวจ locator/ขอบเขตตัวถัง; รุ่นอื่นระบุ estimated จนมีเอกสารขนาด ไม่อ้าง true-scale AR
- **3D-11:** ส่งมอบ 6 GLB พร้อม sidecars/preview และ rebuild instructions เมื่อทุกตัวผ่าน; ถ้าบางตัว hold รายงาน partial อย่างชัดเจน ไม่ประกาศ pilot ครบ

เกณฑ์สำเร็จของรอบเอกสารปัจจุบัน: parent/peer ไม่ขัดกัน มี source inventory, file contract, tests และ approval boundary; ไม่ใช้เกณฑ์นี้แทนความสำเร็จของการสร้างโมเดล

## 7. รายงานสถานะและ rollback

แต่ละ run รายงาน attempted/ready/held counts, source mismatch count, dimensions status, validation errors, triangle count และ GLB bytes ต่อรุ่น ไม่มี background monitoring/cloud telemetry ใน pilot

เขียนผลใน version directory ใหม่ ตรวจครบก่อนเปลี่ยน internal index แบบ atomic หาก input เปลี่ยน, export/render ล้มเหลว หรือ visual review ไม่ผ่าน ให้ index เดิมยังชี้ชุดเดิม เก็บ failed version แยกเพื่อ review ไม่เขียนทับ approved version; rollback คือคืน index ไป version ก่อนหน้าที่ผ่านตรวจ ไม่ลบต้นฉบับ ไม่มี public rollout หรือ registry CURRENT swap ในงานนี้

## 8. Source snapshot และคำขออนุมัติ

PDF ของทั้งหกรุ่น: `data-pipeline/01_raw/03_product_catalogs/2026 new catalogue of power banks&car charger&wireless charger.pdf`

| Input | SHA-256 ณ เวลาตรวจ |
|---|---|
| PDF ข้างต้น | `066037e15f855d22d9d08b7e3ed440224ee6ec67d03a0d2cadb7f24325b25456` |
| production-manifest.json | `55a0090ab4c25e1f23d41f2a3e73374b0f665c1c864af0f944fe0b1dc30cfb70` |
| single-S-1052-source.png | `0b925563c88b5f39ac5d093d8890cf87ca1f57da03b6aa7cff6c1de339245c37` |
| single-BST61401-source.png | `aeda95c943080e5011746dec1c1a691ae29bd2bda9cde613fcfbe8cdfbbcb180` |
| single-DW03-source.png | `5d35de381819f99158964f1c6ca86d6b5e8832335757aa31e095cbb309e72033` |
| single-UT3056-source.png | `37e81f1e234a0348f1dd069a697fe893941e0fb591fdf86595ffdd297ec62ad3` |
| single-S1033-source.png | `13611d39277ec28aa19c4a18c975ebfa304dd23b5750409a59b204d1c79464a2` |
| single-W502-source.png | `d8ab63eebea3eba3e7ef2aaaabb25e69326fd8c9861714dc3e092a3fb4936bed` |
| data-pipeline/02_prepared/ProductMaster.json | `347311b5ce50f1c65570bacde91c08ac0c28bdb576b5c9271ae34fb24a553368` |
| data-pipeline/02_prepared/pricelist_master.json | `d2a7f09a495cecf96d01006df232267737175d7d85b1b28b5e0a63ab476fa153` |

รายการนี้เป็น read-only snapshot ไม่ใช่หลักฐานอนุมัติ source rights, canonical pairing หรือ geometry accuracy หาก bytes เปลี่ยนต้องตรวจ snapshot ใหม่ก่อนสร้าง

**ขอ Boss อนุมัติสเปกนี้และ ADR-008 ให้เริ่ม pilot 6 รุ่นตาม P0–P3 โดยส่งสองรุ่นแรก review ก่อนขยายชุด** หากต้องการภาพ render อย่างเดียวแทน GLB หรือเลือกขวดน้ำเป็น pilot ต้องยืนยันขอบเขต/รุ่นและหลักฐานภาพก่อน implementation

## 9. Implementation evidence — P0–P1 / 2026-08-31

ชุดล่าสุดสำหรับ review: [model_catalog.json](../../output/catalog-3d/model_catalog.json) มี `review_candidates` 2, `models` 0 และ `held` 4 ไม่ตีความว่า pilot ครบ 6 หรืออนุมัติให้ลูกค้าใช้แล้ว

| โมเดล | GLB | Triangles / meshes | ขนาดไฟล์ | glTF errors / warnings |
|---|---|---|---|---|
| S1033 | [v004/model.glb](../../output/catalog-3d/S1033/v004/model.glb) | 7,712 / 12 | 546,404 bytes | 0 / 0 |
| DW03 | [v004/model.glb](../../output/catalog-3d/DW03/v004/model.glb) | 15,704 / 27 | 1,395,440 bytes | 0 / 0 |

แต่ละรุ่นมี geometry-source/variants/metadata/validation JSON และ PNG 1200 × 1200 จำนวน 4 มุมจาก GLB ที่บันทึกจริง รองรับชื่อสีใน source S1033 4 ชื่อและ DW03 5 ชื่อ โดยทดลอง material switching ใน render worker และตรวจ geometry fingerprint หลัง re-import แล้ว สี/วัสดุเป็นการประมาณจากภาพ ไม่ได้ color calibrate

หลักฐานการตรวจ:

- RED ก่อนมี contracts/models/GLB validator; GREEN unit tests 8 รายการ และ saved-artifact tests 3 รายการ รวม **11 ผ่าน / 0 fail / 0 skip**
- `node --test tests/catalog3d.test.mjs tests/catalog3d-artifacts.test.mjs` ตรวจ source hashes, missing/changed/path escape, canonical boundary, geometry reuse, invalid GLB, atomic index, coplanar regression และ package จริง
- Build `node scripts/catalog3d/build.mjs v004` export → official glTF validation → บันทึกไฟล์ → เปิดกลับผ่าน URI ใหม่ → render 4 มุม และทดลอง material variants ทั้งหมด ผ่าน; browser/worker ปิดแล้ว
- Source PDF hash และ original crops ทั้ง 6 ตรง snapshot; PDF text พบ source code ถูกหน้า 2–7 และเปิดภาพ render หน้า 4/6 ตรวจรหัส/ขนาด/สีแล้ว ไม่กู้ขนาดจากภาพ generated-clean
- ดู PNG ทั้ง 4 มุมของ v003; ใน v004 เปิดตรวจใหม่สามมุม DW03 ที่ hash เปลี่ยน ส่วนอีก 5 ภาพ hash ตรงกับภาพที่ตรวจแล้ว ไม่พบ generic corner plate หรือ coplanar overlap ที่เคยพบในรอบแรก
- เก็บ v001–v003 เป็นประวัติ iteration ไม่ลบ/เขียนทับ; v001 มี corner artifact, v003 มี coplanar artifact เล็กน้อย ดู [RCA](../../.brain/rca/RCA-CATALOG3D-THIN-PANEL-CORNERS-2026-08-31.md)
- ไม่รัน full repository unittest discovery เพราะมี tests ที่เขียน product manifest; ไม่อ้างว่าระบบอื่นผ่าน regression suite ในรอบนี้ และไม่ได้แก้ public/price/schema/registry files

เครื่องมือที่พิสูจน์จริง: Three.js 0.160.0, gltf-validator 2.0.0-dev.3.10 ติดตั้งเฉพาะ `scripts/catalog3d/node_modules`; Playwright 1.62.1 จาก bundled runtime และ Chromium 149.0.7827.55 ที่มีอยู่แล้ว ไม่ติดตั้ง Blender หรือ upload ภาพ

```powershell
$env:PLAYWRIGHT_MODULE='C:\Users\freshair\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright\index.mjs'
$env:CATALOG3D_CHROMIUM='C:\Users\freshair\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe'
```

รายละเอียด rebuild อยู่ใน [README](../../scripts/catalog3d/README.md) อาศัย Playwright library เป็น batch render worker ไม่ได้สร้าง/แก้หน้า catalog และไม่ใช้ profile ผู้ใช้

**ข้อจำกัดที่ยังต้อง review:** S1033 สายกาง/ขาตั้งและความลึกหัวต่อเป็นค่าประมาณ; DW03 ใช้ 23 มม. เป็นความหนาตัวถัง ทำให้ assembled depth รวมชิ้นยื่นประมาณ 27.5 มม. ต้องยืนยันว่า annotation 23 มม. ของ supplier หมายถึงตัวถังหรือทั้งชิ้นก่อนใช้ true-scale ทั้งสองไม่ใช่ factory CAD และยังไม่มี canonical ProductMaster pairing สิทธิ์เผยแพร่/likeness ยัง pending-owner-review ไม่มี P2, public integration, commit/push/deploy ในรอบนี้

สกิล `tdd-workflow` ทำให้มี fail-before-implementation และ regression tests ของสิ่งที่พบในภาพ; สกิล `pdf` ทำให้ตรวจ source page จริงก่อนใช้ dimension/color ส่วนการหยุดที่สองรุ่นเป็น approval gate ของ SPEC ไม่ใช่ข้อจำกัดเครื่องมือ

## Version diff

## 12. P4 — Canonical ProductMaster coverage register

Boss อนุมัติ coverage plan สำหรับ ProductMaster 16 รายการตาม schema โดยไม่สร้าง GLB เดาเพื่อให้จำนวนครบ. Generation ต้องสร้าง local-only evidence registry, evidence-request matrix และ category coverage report จาก queue เดียวกัน:

- registry ทุกแถวต้องมี `pm:`/`cat:`/`IN_CATEGORY`, `selected_source_code`, source hash/locator, color/dimension/estimated fields และ lifecycle status; source code ที่ยังไม่ยืนยันเป็น `null` ไม่ใช่ canonical alias
- gate `hold_needs_verified_reference` ต้องเกิดเมื่อขาด owner cross-reference, source hash/locator หรือ dimension/angle package; ไม่มี transition อัตโนมัติจาก family hint, media fallback หรือ review candidate
- `reference-ready` → `geometry-review` → `owner-approved` → `local-ready` เป็นเพียง local asset lifecycle. `local-ready` ไม่ promote registry/graph/public catalog และ unresolved review candidates ไม่เพิ่ม coverage completion
- report แยก total/reference-ready/geometry-review/owner-approved/local-ready/held ต่อ Category พร้อม hold reason; completion ต้อง 16/16 owner-approved และ source traceable ไม่ใช่จำนวน GLB

`0.1.5b beta` → `0.2.0b beta`: อนุมัติ evidence-gated coverage ของ canonical ProductMaster 16 รายการ; ไม่เพิ่ม schema/entity/edge และไม่ขยายไป source projections/offers/bundles.

### ผลสร้าง P4

- สร้าง [evidence registry](../../output/catalog-3d/product_master_evidence_registry.json), [evidence input template](../../output/catalog-3d/product_master_evidence_input.json), [request matrix](../../output/catalog-3d/evidence-request-matrix.md) และ [category coverage report](../../output/catalog-3d/category_coverage_report.json) แบบ local-only จาก queue/schema snapshot
- baseline ที่ตรวจได้คือ 16 canonical `pm:` / 4 `cat:` / 16 `IN_CATEGORY`, `reference-ready=0`, `geometry-review=0`, `owner-approved=0`, `local-ready=0`, `held=16`; output ระบุ required evidence ต่อ ProductMaster และไม่ treat S1033/DW03/W502 เป็น completion
- evidence input เป็น blank template มีเฉพาะ product metadata; runner หยุด hold หาก owner cross-reference, source SHA/locator, body dimensions หรือ front+back/side angles ไม่ครบ. ไม่มีการส่งคำขอหรือข้อมูลออกนอกเครื่อง

`0.2.0b beta` → `0.2.1b beta`: สร้าง P4 artifacts และตรวจ fail-closed lifecycle แล้ว; ยังไม่มี ProductMaster ที่ผ่านหลักฐานเพียงพอสำหรับสร้าง GLB ใหม่.

### P5 — PM-TMB partial evidence capture

`pm:PM-TMB` มี factory mapping ที่บันทึก `mapping_confirmed_by: Boss` ไป `BW00-0`; product manifest มี `source-photo` code เดียวกันและ PDF Business Gift หน้า 77 ยืนยันภาพ, 450ml, temperature display และชื่อสี. บันทึกได้เฉพาะ source cross-reference/hash/locator/colors และต้องคง hold เพราะไม่มี width×height×depth และภาพ front+back/side. Canonical ระบุ SUS316 แต่ source ระบุ 304; เป็น material gap ที่ mapping เดิมบันทึกว่า Boss ยอมรับสำหรับ cost mapping จึงห้ามตีความเป็น factory CAD หรือยกเลิก visual/dimension gate.

`0.2.1b beta` → `0.2.2b beta`: บันทึก PM-TMB partial evidence แล้ว; status ยังคง hold และไม่สร้าง/ promote GLB.

### P6 — BW00-0 estimated visual review candidate

Boss อนุมัติให้ขึ้นรูป `BW00-0` เพื่อดูภาพรวมจากภาพต้นฉบับ Business Gift catalog หน้า 77 แม้ยังไม่มี dimension drawing และภาพหลายมุม จึงกำหนด body estimate เป็น `Ø65 × H230 mm` ตามสัดส่วนภาพ/ความจุ 450ml เท่านั้น และต้องบันทึก `dimension_status: estimated` ทุกจุดที่แสดงผล

- ฝาต้องมีวงกลม temperature display ตามภาพจริง แต่ขนาดฝา, ฐาน, wall thickness, underside และ material finish เป็น estimated regions
- asset เก็บใน `review_candidates` ด้วย `canonical_product_id: null`, `mapping_status: unresolved`, `lifecycle: review-candidate` และ `counts_toward_product_master_completion: false`
- ภาพเทียบใน viewer ใช้ไฟล์ต้นฉบับ hash-pinned `public/assets/catalog-media/source-offer-BW00-0.jpg` ผ่าน allowlist เฉพาะ asset นี้; ไม่เปิด route ไปยังโฟลเดอร์ public หรือ source documents
- `pm:PM-TMB` ต้องคง `hold_needs_verified_reference` จนได้ขนาดจริงและภาพ side/back ตาม P5; estimate นี้ไม่เติม evidence gate และไม่ลด hold reason

`0.2.2b beta` → `0.2.3b beta`: Boss อนุมัติ estimated visual-review candidate BW00-0 แบบ non-canonical; ไม่เปลี่ยน schema, graph, ProductMaster, catalog public หรือ release boundary.

### ผลสร้าง P6

- สร้าง [BW00-0 v001 GLB](../../output/catalog-3d/BW00-0/v001/model.glb) พร้อม preview 4 มุม, metadata, variants และ validation sidecars; SHA-256 `e6fc22ed7a0f242086deb92a1f4c9d8882f0bd06574ad5cd5060beaa470e221f`, 3,200 triangles, 6 meshes, 134,604 bytes
- glTF validator ได้ errors/warnings `0 / 0`; re-import GLB สำเร็จ และ viewer local โหลด/เปลี่ยนสี/เทียบภาพ `source-offer-BW00-0.jpg` ที่ hash-pinned ได้
- generated viewer index มี candidate ที่ผูก `cat:eco-friendly` เท่านั้น ขณะที่ `pm:PM-TMB` และ coverage ยังคง `16 held / 0 local-ready`; asset นี้ไม่ผ่าน identity, geometry หรือ owner approval gate
- ชุด tests ของ catalog3d ได้ **22 ผ่าน / 0 fail / 0 skip** รวม source hash, GLB parse, finite geometry, immutable variants, coverage hold และ viewer allowlist

`0.2.3b beta` → `0.2.4b beta`: บันทึกผลสร้างและตรวจ BW00-0 v001; สถานะและ release boundary ไม่เปลี่ยน.

### P7 — Partial evidence from complete local source audit

Boss สั่งตรวจเอกสารสินค้า/โรงงานทั้งหมดแบบ read-only แล้วพบ factory mapping ที่ยืนยันโดย Boss อยู่เดิม 9 รายการ และภาพต้นฉบับฝังใน workbook สำหรับ 8 รหัส: `TBY17-1`, `TN00-2`, `TNA0014`, `TJS00-1`, `TDK01-1`, `TZJ00-1`, `BW00-0`, `TYS01-1`. การบันทึกเข้าสู่ evidence input ต้องใช้เฉพาะ `pm_code ↔ factory_item_code` จาก mapping ที่มีสถานะ confirmed, SHA-256 ของ binary รูปฝัง และ locator workbook/sheet/row/media member เท่านั้น; ห้ามคัดค่า cost, quote หรือข้อมูลลูกค้าเข้าสู่ 3D artifacts.

- บันทึกมิติเป็น `body_mm` เฉพาะเมื่อ source ระบุครบสามแกนโดยตรง: `PM-MSG` = 150×145×45 mm และ `PM-PB10K` = 146×69×40 mm
- มิติแบบสองแกน/สภาพกาง เช่น CFMUG 145×90 mm, mug 8×8 cm, notebook A4, umbrella 108×53.5 cm หรือความจุอย่างเดียว ต้องเป็น partial reference และไม่ผ่าน dimension gate
- ภาพที่พบเป็นหลักฐานมุมที่เห็นจริงเท่านั้น; front/inside ไม่อนุมานเป็น back/side. ทุกแถวคง hold จนมิติและมุมครบ
- `PM-FLASH` มี factory mapping แบบ material/component แต่ไม่มี factory item code หรือภาพ product ที่ผูกตรง; อีก 7 PM ไม่มี factory mapping จึงไม่เติม evidence จาก keyword match

`0.2.4b beta` → `0.2.5b beta`: เพิ่มกติกา ingest partial evidence จาก complete source audit โดยไม่เปลี่ยน lifecycle gate, schema, graph หรือ public scope.

### ผลสร้าง P7

- เติม evidence input สำหรับ 7 รหัสที่พบใหม่ และคง PM-TMB ที่บันทึกไว้แล้ว รวม 8 ProductMaster ที่มี source code, image hash/locator และ factory mapping เดิมที่ Boss ยืนยัน
- runner สร้าง registry/coverage/matrix ใหม่แล้ว: PM-MSG และ PM-PB10K เหลือเฉพาะ `front_back_or_side_angle_evidence`; PM-BOTTLE-LED, PM-CFMUG, PM-MUG-HEAT, PM-NB, PM-TMB และ PM-UMB ยังขาดทั้ง dimension package และมุมด้านข้าง/หลัง
- coverage ยังเป็น `16 held / 0 local-ready`; ไม่มี GLB ใหม่, schema/graph/public catalog/registry ไม่เปลี่ยน

### P8 — Estimated models from partial factory-image evidence

Boss อนุมัติให้สร้าง 3D จากหลักฐาน P7 แม้ dimension/angle package ยังไม่ครบ โดยจำกัดผลลัพธ์เป็น **local estimated review candidates** สำหรับ 7 source code ที่ยังไม่มี GLB (`TDK01-1`, `TJS00-1`, `TBY17-1`, `TN00-2`, `TNA0014`, `TZJ00-1`, `TYS01-1`) และใช้ `BW00-0 v001` เดิมเป็น candidate ของ PM-TMB. ภาพต้นฉบับที่ extract จาก workbook ต้องคัดลอกเฉพาะ binary ที่ hash ตรงไปยัง local output allowlist เพื่อแสดงเทียบรูปทรง; ไม่เปิด workbook/PDF หรือไดเรกทอรีต้นทางให้ viewer.

- ทุก asset ใช้ source code เป็น `asset_key`, `canonical_product_id: null`, `mapping_status: unresolved`, `lifecycle: review-candidate`, `public_ready: false` และ `counts_toward_product_master_completion: false`
- `PM-MSG` และ `PM-PB10K` ใช้ body dimensions ที่ source ระบุครบสามแกน; อีกห้ารุ่นใช้สัดส่วนภาพ/มิติ partial เป็น estimated geometry พร้อมบันทึกค่าประมาณและส่วนที่มองไม่เห็นใน metadata
- สีที่ source ระบุเป็น material variants เท่านั้น; ทุก variant ต้อง reuse geometry เดิม
- แสดงตาม `cat:`/`IN_CATEGORY` ที่ canonical queue ระบุเพื่อช่วย review แต่ห้ามเปลี่ยน ProductMaster lifecycle, coverage หรือ promote source code เป็น `pm:`
- build ต้องตรวจ hash input ก่อน/ก่อน publish, validate GLB, re-import แล้ว render สี่มุม, และ atomically publish index. ถ้า source/hash/asset version/index เปลี่ยน ให้ล้มเหลวโดยไม่เขียน index ครึ่งชุด

`0.2.5b beta` → `0.2.6b beta`: Boss อนุมัติ P8 สร้าง 7 estimated local review candidates จาก P7 partial evidence; PM-TMB ใช้ BW00-0 ที่มีอยู่แล้ว. ไม่เปลี่ยน schema, graph, canonical completion หรือ public catalog.

### ผลสร้าง P8

- สร้าง `TDK01-1`, `TJS00-1`, `TBY17-1`, `TN00-2`, `TNA0014`, `TZJ00-1` และ `TYS01-1` ที่ `output/catalog-3d/<source-code>/v001/`; ทุกชุดมี GLB, geometry source, variant sidecar, provenance metadata, validator report และ preview สี่มุม
- GLB ทั้ง 7 re-import และ glTF validate ผ่าน `errors=0`, `warnings=0`; size/shape ที่ไม่ครบเป็น `dimension_status: estimated` และ `PM-MSG`/`PM-PB10K` เท่านั้นที่ใช้ three-axis source annotation
- คัดเฉพาะภาพต้นฉบับที่ hash ตรงจาก source audit ไป `output/catalog-3d/reference-images/` แล้ว allowlist ใน viewer; browser ไม่เปิด workbook, PDF, registry, evidence input หรือ source directory
- generated viewer index มี review candidates 11 รายการ (รวม S1033, DW03, W502 และ BW00-0 เดิม) แยกตาม Category; coverage canonical ยัง `16 held / 0 local-ready`
- TDD เริ่มจาก test ที่ยังหา generator ไม่พบ (RED) แล้วผ่านหลังสร้าง; focused suite ได้ 30 ผ่าน / 0 fail / 0 skip. ไม่มี owner likeness/identity approval, canonical mapping, graph/schema/public catalog, commit, push หรือ deploy

`0.2.6b beta` → `0.2.7b beta`: บันทึกผล P8 GLB 7 รุ่น, hash-pinned local comparison images และ verification; lifecycle/release boundary ไม่เปลี่ยน.

## 10. P2 — ทะเบียนคิวตาม Category / ProductMaster

Boss อนุมัติให้ไล่งานตามหมวดและยืนยันให้ยึด GenesisBlock schema ในคำสั่ง “go” และ “genesisblock schema ใช้ตามนั้น” รอบนี้จึงเพิ่ม generated, local-only queue โดยยึด entity/edge ที่ schema มีอยู่เท่านั้น:

```text
cat:<slug> (Category) <- IN_CATEGORY - pm:<code> (ProductMaster)
```

- อ่านเฉพาะ `ProductMaster.json.records` และ `edges.IN_CATEGORY`; ต้องมี `pm:` และ edge ที่ target เป็น `cat:<record.category>` ตรงกัน มิฉะนั้น generation ล้มเหลว
- `product_family` เป็นเพียง hint ที่มีอยู่ใน source projection ไม่ใช่ node ใหม่ ไม่ใช่หลักฐานว่า geometry ใช้ร่วมได้
- สร้าง queue ได้เฉพาะ canonical `pm:` 16 รายการตาม 4 Category; source projections 427 รายการและ business code ที่ยังไม่ resolve เป็น `pm:` ห้ามนำไปเป็น canonical queue item
- ตรวจ media index ด้วย code ตรงตัวเท่านั้น: source-photo ที่ตรงจึง `ready_for_reference_review`; fallback, generated-clean, ไม่มีรูป หรือ code ไม่ตรงเป็น `hold_needs_verified_reference`
- GLB, preview และ model sidecar ยังคงเป็น local artifacts ไม่ได้เพิ่ม node `3DModel`, ID prefix หรือ edge ใหม่ใน GenesisBlock schema
- JSON queue ไม่มี PII, cost, customer, quote หรือ public endpoint; เป็นเครื่องมือจัดลำดับภายในและไม่เปลี่ยน `model_catalog.json`

เกณฑ์ตรวจรับ: count ต้องเท่ากับ canonical records; ทุก item ต้องมี `pm:` / `cat:` / `IN_CATEGORY` ที่ type-correct; หมวดต้องเรียงตาม schema slug; source asset ที่ไม่ resolve ต้องไม่ถูกแทรกเป็น `pm:`; และทุก hold ต้องบอกเหตุผลที่ตรวจย้อนกลับได้

`0.1.2b beta` → `0.1.3b beta`: บันทึก P2 queue contract ตาม schema หลัง Boss อนุมัติ; ยังไม่สร้าง/เผยแพร่ GLB เพิ่มจนผ่าน image and likeness gate.

## 11. P3 — W502 reference candidate

Boss สั่งให้เดินหน้าหลังตรวจ category queue แล้ว งาน P3 เริ่มที่ W502 เท่านั้น เพราะ PDF หน้า 7 ระบุ “Magnetic Wireless Charging Power Bank 10000mAh”, ขนาด 110 × 71 × 18 mm และภาพแสดงขาตั้ง ขณะที่ `pm:PM-PB10K` มีชื่อ MagSafe wireless powerbank 10,000mAh + stand, อยู่ `cat:executive-smart-tech` ผ่าน `IN_CATEGORY`, และ dimensions 105 × 68 × 16 mm ใน canonical source. เป็น evidence-supported candidate ไม่ใช่การ promote identity:

- GLB W502 ต้องยังบันทึก `canonical_product_id: null`, `mapping_status: unresolved` และ `public_ready: false`
- อาจบันทึก `evidence_binding` ภายในโดยมี candidate `pm:PM-PB10K`/`cat:executive-smart-tech`, source locators และสถานะ `evidence-supported-review-candidate`; ห้ามเขียน graph, เปลี่ยน ProductMaster หรือสรุปว่า W502 คือสินค้าตัวเดียวกันแบบ canonical
- model/review index เพิ่ม W502 ได้เฉพาะ `review_candidates`; status owner likeness/identity review ยังเป็น pending
- S1033 และ DW03 มีหลักฐาน class ใกล้เคียง แต่รอบนี้ไม่แก้ metadata เดิม; BST61401 ยังขาด stand/dimension, S-1052 ขาด magnetic/stand, UT3056 เป็น hand warmer จึง hold

### ผลสร้างและตรวจ W502 v001

- สร้าง [W502 v001 GLB](../../output/catalog-3d/W502/v001/model.glb) แยกจาก S1033/DW03 เพื่อไม่ให้ hash ของรุ่นเดิมเปลี่ยน: 6,304 triangles, 10 meshes, 509,840 bytes, SHA-256 `abc67c2c058dfb28769046cba9afab018d83a210f170f90d7c361accc35c9484`
- glTF validation ได้ errors/warnings `0 / 0`; เปิด GLB ที่บันทึกแล้วกลับมาตรวจ และสร้าง preview 1,200 × 1,200 สี่มุม พร้อม geometry-source/variants/metadata/validation sidecars ใน [W502/v001](../../output/catalog-3d/W502/v001/)
- metadata คง `canonical_product_id: null`, `mapping_status: unresolved`, `public_ready: false`; บันทึกเพียง evidence binding ไป `pm:PM-PB10K` → `cat:executive-smart-tech` ด้วย `IN_CATEGORY` และสถานะ `evidence-supported-review-candidate`
- TDD เขียน test W502 ให้ล้มเหลวก่อนมี generator แล้วผ่านหลังสร้าง; ชุด focused ทั้ง asset, queue, viewer และ W502 ได้ **16 ผ่าน / 0 fail / 0 skip**. Browser local ตรวจ W502 ทั้ง White/Black และลากดูด้านข้างจนเห็นขาตั้ง; ไม่พบ console warning/error
- ระหว่างเพิ่ม W502 พบ server สมมติ version เป็น `v004` ทุกโมเดล จึงแก้เป็น allowlist แบบ code→version โดยไม่เปิด path arbitrary และบันทึก RCA ใน [RCA-CATALOG3D-VIEWER-ASSET-VERSION-2026-08-31.md](../../.brain/rca/RCA-CATALOG3D-VIEWER-ASSET-VERSION-2026-08-31.md)

`0.1.3b beta` → `0.1.4b beta`: อนุมัติ P3 W502 local model candidate ตามหลักฐาน PDF/Category/ProductMaster; ไม่เปลี่ยน schema, graph หรือ canonical identity.

`0.1.4b beta` → `0.1.5b beta`: สร้าง W502 v001 แบบ local review candidate, ตรวจ GLB และเพิ่ม viewer allowlist; สถานะ identity ยัง unresolved และไม่เปลี่ยน schema/graph/public contract.

`0.1.1b beta` → `0.1.2b beta`: สร้าง P1 สองรุ่นเป็น GLB v004 พร้อม provenance/materials/preview และ tests 11 ผ่าน; อีก 4 รุ่นรอ owner review ไม่เปลี่ยน canonical/public contract

`0.1.0b candidate` → `0.1.1b beta`: บันทึก approval; P0 ตรวจ PDF พบ DW03 มีขนาด 108.3 × 67.3 × 23 มม. และสี White/Blue/Purple/Orange/Black; S1033 มีขนาดข้อความ 69 × 106 × 17 มม. เทียบภาพ 69.3 × 106.4 × 17.1 มม. เก็บทั้งสองหลักฐานและใช้ภาพละเอียดเป็นตัวถัง ไม่รวมสายที่กางออก

ไม่มีเอกสาร → `0.1.0b candidate`: เพิ่มข้อเสนอ GLB แยกรุ่น, material reuse, provenance sidecars และเกณฑ์ตรวจรับ ยังไม่เพิ่ม code/model/image, ไม่แก้ public catalog/schema/registry และไม่ commit/push

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.2.7b | 2026-08-31 | beta | P8 generated seven estimated GLBs and verified local viewer index | uncommitted | ATHER |
| 0.2.6b | 2026-08-31 | beta | P8 approved: build seven estimated candidates from partial factory-image evidence | uncommitted | ATHER |
| 0.2.5b | 2026-08-31 | beta | P7 partial evidence จาก source audit; ทุก PM ยัง evidence-gated | uncommitted | ATHER |
| 0.2.4b | 2026-08-31 | beta | BW00-0 v001 ผ่าน GLB/viewer checks; PM-TMB ยัง hold | uncommitted | ATHER |
| 0.2.3b | 2026-08-31 | beta | BW00-0 estimated visual-review candidate; PM-TMB ยัง hold | uncommitted | ATHER |
| 0.2.2b | 2026-08-31 | beta | PM-TMB partial evidence; รอ dimensions และ multi-angle | uncommitted | ATHER |
| 0.2.1b | 2026-08-31 | beta | P4 evidence registry/matrix/coverage พร้อม 16 hold | uncommitted | ATHER |
| 0.2.0b | 2026-08-31 | beta | 16 ProductMaster coverage register และ evidence gate | uncommitted | ATHER |
| 0.1.5b | 2026-08-31 | beta | W502 v001 ผ่าน GLB/browser checks; ยังคง candidate ที่ unresolved | uncommitted | ATHER |
| 0.1.4b | 2026-08-31 | beta | อนุมัติ W502 เป็น review candidate ใน Executive Smart Tech | uncommitted | ATHER |
| 0.1.3b | 2026-08-31 | beta | อนุมัติ queue ตาม Category/ProductMaster/IN_CATEGORY โดยไม่เพิ่ม ontology | uncommitted | ATHER |
| 0.1.2b | 2026-08-31 | beta | P0–P1 local evidence, v004 GLBs, 11 tests; likeness review pending | uncommitted | ATHER |
| 0.1.1b | 2026-08-31 | beta | อนุมัติและเริ่ม capability/source checks; ยังรอผลสร้างและ owner review | uncommitted | ATHER |
| 0.1.0b | 2026-08-31 | candidate | เสนอ pilot 6 รุ่นจาก original catalog crops และ approval gates | uncommitted | ATHER |
