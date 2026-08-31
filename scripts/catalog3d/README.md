# SmartGift local catalog 3D pilot

เครื่องมือขึ้นรูปจากภาพอ้างอิงตาม [ADR-008](../../docs/decisions/ADR-008-PRODUCT-3D-ASSET-PIPELINE.md) ไม่ใช่ image-to-3D AI หรือ factory CAD ผลปัจจุบันมี review candidates 11 รายการ: S1033/DW03/W502/BW00-0 และ P8 factory-image candidates 7 รหัส; ทุกตัว unresolved กับ canonical ProductMaster และ coverage register ของ 16 `pm:` ยังไม่มี `local-ready` asset

## ไฟล์ส่งมอบ

ดู `output/catalog-3d/model_catalog.json`: `review_candidates` ชี้ version สำหรับตรวจล่าสุด ส่วน `models` ยังว่างจน owner อนุมัติ ไม่ใช่รายการสินค้าที่เผยแพร่แล้ว

แต่ละ version มี `model.glb`, `geometry-source.json`, `variants.json`, `metadata.json`, `validation.json` และ PNG 4 มุม (`preview.png`, `preview-back.png`, `preview-side.png`, `preview-straight.png`) ภาพทั้งหมด render จาก GLB ที่บันทึกและเปิดกลับ ไม่ได้ดัดแปลง source crop

`v001` เก็บเป็นหลักฐานรอบที่พบ corner artifact, `v002` เป็นรอบแก้ geometry, `v003` เพิ่มการทดสอบ material variants จริง, `v004` คือชุดสำหรับ review หลังแก้ coplanar overlap ที่พบในภาพตรง ไม่ใช้รุ่นเก่าแทน current index

## ข้อจำกัด

- Body dimensions อิง annotation ใน PDF; สายที่กาง ขาตั้ง ความลึกพอร์ต และวัสดุบางส่วนประมาณ ไม่ใช่แบบวัดจากโรงงาน
- สี S1033 4 ชื่อและ DW03 5 ชื่อมาจาก PDF แต่ค่า RGB/finish เป็นค่าประมาณ ไม่ใช่สีที่ผ่าน color calibration
- `variants.json` เป็น sidecar ต้องใช้ consumer ที่อ่าน material slots; เปิด GLB อย่างเดียวแสดงสี default ได้ ไม่เปลี่ยนสีอัตโนมัติ
- ไม่มี canonical ProductMaster pairing หรือ registry ID ของ inputs เหล่านี้ที่ resolve ได้ จึงเก็บ null/unresolved ไม่สร้าง ID เอง
- ไม่มี public catalog integration, cloud upload, customer data, ราคา, commit/push หรือ deploy

## เปิด viewer หมุนสินค้าได้จริง

ตาม [viewer spec ที่อนุมัติ](../../docs/specs/SPEC-PRODUCT-3D-VIEWER-2026-08-31.md):

```powershell
node scripts/catalog3d/viewer-server.mjs
```

เปิด [local viewer](http://127.0.0.1:5190/) เลือก DW03/S1033 ลากเพื่อหมุน เลื่อนล้อเมาส์หรือกด +/− เพื่อซูม เลือกวงกลมสีเพื่อเปลี่ยนวัสดุ และกดคืนมุมเริ่มต้นได้ Canvas รองรับลูกศร, +/− และ Home เมื่อ focus อยู่ที่โมเดล ไม่มี auto-rotate

Canvas โปร่งใสจริง; พื้นสีอ่อนที่เห็นคือหน้าเว็บ ไม่ใช่พื้นติดโมเดล ปุ่มดาวน์โหลดส่ง GLB เดิมสี default ไม่ export สีที่เลือกใหม่ และไม่ได้สร้างไฟล์ `.max` การเปลี่ยนสีเกิดในหน่วยความจำ ไม่แก้ไฟล์ v004

Server bind เฉพาะ loopback และ allowlist ไฟล์ ไม่มี directory browsing ไม่เผย raw sources หรือ metadata กด Ctrl+C ใน terminal ที่รัน viewer เพื่อปิด หาก 5190 ถูกใช้งานอยู่ เลือกพอร์ตอื่นด้วย `node scripts/catalog3d/viewer-server.mjs 5191` ไม่หยุด process อื่น

## จัดคิวตาม GenesisBlock schema

```powershell
node scripts/catalog3d/product-master-queue.mjs
```

สร้าง [product_master_queue.json](../../output/catalog-3d/product_master_queue.json) แบบ local-only โดยรับเฉพาะ `pm:` ใน `ProductMaster.json` ที่มี `IN_CATEGORY` ไปยัง `cat:<slug>` ถูกต้องตาม schema เป็นเครื่องมือจัดคิว ไม่เขียน graph, ไม่สร้าง ID/ontology สำหรับโมเดล และไม่อนุมานรหัสต้นทางเป็น ProductMaster

เฉพาะภาพ `source-photo` ที่มี code ตรงกับ `pm:` จึงเข้าสถานะ `ready_for_reference_review`; ทุกกรณีอื่นเป็น `hold_needs_verified_reference` ก่อนขึ้นรูป GLB เพื่อไม่ใช้ภาพผิดรุ่น

## Coverage ของ 16 ProductMaster

```powershell
node scripts/catalog3d/product-master-coverage.mjs
```

คำสั่งนี้สร้าง `product_master_evidence_input.json` ครั้งแรกแบบ blank template และอ่าน template เดิมในรอบถัดไป จากนั้นสร้าง registry, request matrix, coverage report และ generated `viewer_index.json` โดย atomically publish. ก่อนสร้าง GLB ใหม่ต้องมี owner-verified source-code cross-reference, source image hash/locator, ขนาดกว้าง×สูง×ลึก และภาพหน้า+หลังหรือด้านข้างครบ; ขาดรายการใดจะคง hold. ไม่ใส่ customer, cost, quote หรือ PII ลง template.

viewer อ่าน `viewer_index.json` เท่านั้น: แสดง coverage ตาม Category และ review candidate ที่ยัง unresolved ได้เพื่อการเทียบภาพ แต่ candidate ไม่เพิ่ม `local-ready` หรือ canonical completion. Server ไม่เปิด registry/template/matrix/report ให้ browser request.

P8 ใช้ `build-evidence-estimated.mjs` สำหรับ factory-image candidates เจ็ดรุ่น และเก็บภาพอ้างอิงที่ hash-pinned ไว้ใน `output/catalog-3d/reference-images/` เพื่อ viewer local เท่านั้น:

```powershell
$env:PLAYWRIGHT_MODULE = 'C:\Users\freshair\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright\index.mjs'
$env:CATALOG3D_CHROMIUM = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
node scripts/catalog3d/build-evidence-estimated.mjs v001
node scripts/catalog3d/product-master-coverage.mjs
```

ทุก directory version immutable; หากมีอยู่แล้วต้องเลือก version ใหม่ ไม่ overwrite. โมเดล P8 คือ estimated visual review—not supplier CAD or canonical completion.

```powershell
node --test tests/catalog3d.test.mjs tests/catalog3d-artifacts.test.mjs tests/catalog3d-viewer.test.mjs tests/catalog3d-product-master-queue.test.mjs
```

## ติดตั้งเฉพาะเครื่องมือในโฟลเดอร์นี้

ต้องมี Node, Three.js `0.160.0`, glTF validator `2.0.0-dev.3.10` (pin ใน package-lock.json) และ Playwright/Chromium ที่มีอยู่บนเครื่อง

```powershell
npm ci --prefix scripts/catalog3d --ignore-scripts --no-audit --no-fund
node --test tests/catalog3d.test.mjs
```

ตั้งค่า `PLAYWRIGHT_MODULE` ให้เป็น absolute path ของ `playwright/index.mjs` และ `CATALOG3D_CHROMIUM` ให้เป็น browser executable ที่ติดตั้งอยู่ ไม่ดาวน์โหลด browser หรือเพิ่ม global package เอง ตัวอย่าง environment ที่ตรวจจริงบันทึกใน SPEC implementation evidence

```powershell
node scripts/catalog3d/build.mjs v005
node --test tests/catalog3d-artifacts.test.mjs
```

เลือก version ใหม่เสมอ; existing version ทำให้คำสั่งล้มเหลวโดยตั้งใจ ไม่มี overwrite ผลที่เคยสร้าง pipeline ตรวจ input hashes ทั้ง 6 รุ่นก่อนและก่อนเปลี่ยน index; หากเปลี่ยน source ต้อง review source snapshot ใหม่ ไม่เพียงเปลี่ยน hash ให้ผ่าน

ตัวสร้างอ่าน shape parameters จาก `RECIPES` ใน `models.mjs` และบันทึกค่าเดียวกันลง `geometry-source.json` พร้อม hash ของ generator เพื่อ rebuild โดยแก้รูปทรงต่อได้ ไม่ใช่ `.blend` หากต้อง rebuild version เก่าใช้ generator ที่ hash ตรง ไม่ใช้ source ล่าสุดแล้วอ้างเป็นผลเดิม

## การตรวจและ runtime boundary

1. Unit tests ตรวจ input mismatch/missing/path escape, canonical boundary, atomic index, finite meshes, geometry reuse และ rejected GLB
2. Build เปิด Chromium headless ชั่วคราวผ่าน Playwright library เพื่อ export/import/render ไม่ใช้บัญชีหรือ profile Chrome ของผู้ใช้; HTTP worker bind `127.0.0.1` port ชั่วคราว เผยเฉพาะ Three modules และ GLB ของ run ไม่ serve repo root หรือ raw sources
3. glTF validator ตรวจทุก GLB; worker เปิดไฟล์ saved bytes กลับผ่าน URI ใหม่ render 4 มุม และทดลองทุก material variant
4. Artifact tests อ่านแพ็กเกจจริง ตรวจ hashes, source references, GLB re-import และ material switching
5. ปิด browser/worker หลังงานจบ มี owner likeness gate แยกจาก automated tests

Code ภายนอกที่ดาวน์โหลดมีเฉพาะ dependencies สาธารณะ ไม่มีภาพสินค้าออกจากเครื่อง registry/public catalog ไม่ถูกแก้ เพิ่มเพียง local viewer แยกตาม approval
