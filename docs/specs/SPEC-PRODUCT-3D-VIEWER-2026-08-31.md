---
version: "0.2.1b"
created_at: "2026-08-31T05:06:00+07:00,ATHER,uncommitted"
last_update: "2026-08-31T10:45:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "product-3d-viewer"
  scope: "approved local viewer only"
  language: "th"
---

# Viewer โมเดล 3D โปร่งใสบนเครื่อง

Boss อนุมัติด้วย “ok” หลังข้อเสนอให้เพิ่ม viewer แบบลากหมุน 360°, ซูม, เลือกรุ่นและเปลี่ยนสี โดยไม่มีพื้น/ฉาก และไม่แก้ catalog เดิม นี่คือบันทึกขอบเขตที่อนุมัติแล้ว ไม่ใช่ proposal ใหม่

Complexity C-2 / risk MEDIUM สำหรับ UI แบบ read-only แยก local จาก catalog; parent [ADR-008](../decisions/ADR-008-PRODUCT-3D-ASSET-PIPELINE.md), peer [asset spec](SPEC-PRODUCT-3D-ASSETS-2026-08-31.md) และ [AGENTS.md](../../AGENTS.md) ขอบเขต runtime server ต้องจำกัดไฟล์และไม่เพิ่ม public exposure

## สัญญาที่อนุมัติ

- โหลด GLB ที่อยู่ใน generated local viewer index ผ่าน allowlist ที่ server ตรวจ hash เท่านั้น; ปัจจุบัน S1033/DW03 v004 และ W502 v001 ยังเป็น unresolved review candidates ไม่ใช่ canonical completion
- มี filter Category จาก `cat:` และแสดง coverage/hold ของ 16 `pm:` โดยไม่เปิด raw registry, queue, metadata หรือ source directory ให้ browser
- หน้า viewer local แยกจาก port 5180; ลากเมาส์/สัมผัสเพื่อหมุน, scroll/pinch เพื่อซูม มีปุ่มคืนมุมเริ่มต้นและทางเลือกคีย์บอร์ด
- เลือกรุ่นและ material variant จาก sidecar ที่มีแล้ว; ค่า RGB ยังประมาณจาก source ไม่รับรองสีจริง
- แสดงภาพ crop ต้นฉบับของรุ่นที่เลือกสำหรับเทียบรูปทรงผ่านปุ่มเปิด/ปิด; ภาพต้องมาจาก allowlist `single-<code>-source.png` ที่ hash ตรง snapshot เท่านั้น และเปลี่ยนตามรุ่น ไม่ยอมรับ filename/query จากผู้ใช้
- Canvas alpha โปร่งใส ไม่มี background image, floor mesh, shadow plane หรือ skybox; UI พื้นเว็บไม่ใช่ geometry และไม่มีผลต่อไฟล์ GLB
- ใช้แสง/environment สำหรับให้เห็นวัสดุได้ แต่ไม่แสดงเป็นฉาก ไม่ auto-rotate เพื่อไม่รบกวนผู้ใช้
- HTTP server bind เฉพาะ 127.0.0.1; serve เฉพาะ viewer/modules, GLB+variants และ PNG crop ต้นฉบับที่ hash-verified ของสามรุ่น ห้าม serve repo root, raw PDF, metadata provenance, prepared JSON, CRM หรือ source costs
- โหลดจาก same-origin เท่านั้น ไม่ upload, ติดตั้งใหม่, commit/push หรือ deploy
- คืน error state แทนหน้าขาวเมื่อ WebGL/ไฟล์ล้มเหลว และป้องกันผลโหลดเก่าทับรุ่นล่าสุด

## เกณฑ์ตรวจรับ

1. Server tests: endpoints อนุญาตเปิดได้; unknown path, traversal, source metadata, cross-origin และ non-GET/HEAD ถูกปฏิเสธ
2. UI tests: เปิดทั้งสองรุ่นได้; ลากเปลี่ยนภาพ/มุมจริง; zoom เปลี่ยนขนาด; reset คืนมุม; เปลี่ยนสีโดย mesh count/geometry ไม่เปลี่ยน
3. ตรวจ canvas alpha=0 ที่พื้นที่ว่าง และไม่มี floor/background mesh; GLB hashes เท่าเดิมหลังทดสอบ
4. Loading/error/retry ใช้งานได้, ไม่มี uncaught errors; keyboard/focus และ narrow viewport ไม่ล้น
5. ส่งลิงก์ local ที่เปิดได้และคง server ให้ผู้ใช้ทดลอง ปิดด้วย Ctrl+C ที่ process viewer แยก ไม่แตะ server catalog
6. ภาพต้นฉบับต้องตรงรุ่นที่เลือก, เปิด/ปิดได้, ระบุว่าใช้เทียบรูปทรงเท่านั้น และ route raw PDF/metadata/path นอก allowlist ต้องถูกปฏิเสธ

## แผนและ rollback

Tests ก่อน implementation → viewer/limited server → browser checks → ส่งลิงก์พร้อมผลตรวจ การย้อนกลับคือหยุด process viewer ไม่ต้องย้ายไฟล์หรือ rollback schema

## ผลตรวจบนเครื่อง 2026-08-31

- เพิ่ม `viewer-server.mjs`, `viewer.html`, `viewer.css`, `viewer.mjs` และ `tests/catalog3d-viewer.test.mjs`; ไม่แก้ generator หรือ GLB v004
- TDD: test ล้มเหลวเพราะยังไม่มี module server ก่อน implementation แล้วผ่านหลังเพิ่ม server; ชุด unit/artifact/server รวม 12 tests ผ่าน ไม่มีรัน pipeline ที่เขียน manifest
- Browser จริง 1280×720: DW03/S1033 เปิดได้ ลากจากด้านหน้าไปด้านหลังได้ ปุ่มซูมและล้อเมาส์เปลี่ยนขนาด คืนมุมกลับได้; ลูกศรและ +/Home ใช้งานได้
- อ่าน WebGL framebuffer: alpha context=true และสี่มุมมี alpha `[0,0,0,0]`; DW03 ค่า nontransparent pixels 66,527 ก่อนเปลี่ยนสีและเท่าเดิมหลังเปลี่ยน Orange→Blue ส่วน RGB hash เปลี่ยน; S1033 White→Black มี pixels 60,778 เท่าเดิมและขอบเขตเท่าเดิม ประกอบกับ artifact tests ตรวจ geometry reuse ของทุก variant
- Narrow viewport 390×844: page scrollWidth=390 เท่ากับ viewport ไม่มีล้นแนวนอน ปุ่มและโมเดลแสดงครบ; คืน viewport เดิมหลังทดสอบ ไม่มี physical touch-device verification
- จำลอง network block เฉพาะ DW03: แสดงข้อความไทยและปุ่มลองใหม่ ปุ่มควบคุมถูกปิด; ยกเลิก block แล้วกดลองใหม่ เปิดโมเดลได้ คืน network override ทั้งหมดก่อนส่งมอบ
- ก่อน fault injection ไม่พบ browser error/warn; network error ระหว่างจำลองเป็น expected failure ไม่ใช่ runtime ปกติ
- SHA256 หลังทดสอบ: S1033 `53c627d127c0576fe0f750bb658815728bc7e8eb79dcbdec06f6fa72b39439c2`; DW03 `25e25b5162ef8cad4086a9e38bcf79bec9b75293d26b63b5a4c5bd96d0b55240` เท่าเดิม
- `impeccable` ช่วยจำกัดหน้าตาให้เป็นเครื่องมือเรียบตาม SmartGift เดิม ไม่ทำ rebrand; `native-data-fetching` ใช้ response checks, abort และ stale-result guard; `tdd-workflow` ใช้ RED→GREEN ก่อน browser verification
- Local runtime `http://127.0.0.1:5190/` เท่านั้น ไม่ deploy/commit/push; geometry likeness, สีจริงและ factory dimensions ยังรอ owner review ตาม asset spec

## ผลตรวจภาพต้นฉบับเพื่อเทียบ 2026-08-31

- เพิ่มเฉพาะ route `/reference/S1033.png`, `/reference/DW03.png`, `/reference/W502.png`; server อ่าน source crop ที่กำหนดใน code, ตรวจ SHA-256 ก่อนเปิด server และไม่รับ filename หรือ query จากผู้ใช้
- TDD: test ใหม่ล้มเหลวเพราะยังไม่มี `reference-toggle` แล้ว GREEN หลังเพิ่ม UI/allowlist; test ตรวจ PNG signature ของทั้งสามรุ่น และปฏิเสธ unknown, extension ผิด, query/path traversal, metadata, raw PDF, cross-origin และ non-GET
- Browser จริง: W502 แสดงคู่กับ `single-W502-source.png`, สลับสี White/Black และกดซ่อน/แสดงได้; มีข้อความกำกับว่าเป็นภาพ catalog สำหรับเทียบรูปทรง ไม่ใช่ factory CAD หรือ canonical identity; ไม่พบ console warning/error
- local viewer ยังคง bind เฉพาะ `127.0.0.1:5190/`; ไม่ย้ายหรือคัดลอก source crop, ไม่ expose directory หรือ PDF และไม่แก้ GLB/schema/registry/catalog หลัก

## Version diff / CHANGELOG

ไม่มีเอกสาร → 0.1.0b: บันทึก approval ของ local interactive viewer เพิ่มจาก asset-only pilot; GLB v004 และ public catalog ไม่เปลี่ยน

0.1.0b → 0.1.1b: เพิ่ม implementation/verification evidence ของ local viewer; ขอบเขต approval และสถานะ review-only ของโมเดลไม่เปลี่ยน

0.1.1b → 0.1.2b: เพิ่ม W502 v001 ผ่าน explicit static allowlist ตาม P3; แก้ server ที่สมมติทุกโมเดลเป็น `v004` โดยผูก version ต่อ model และมี regression test. W502 ยังเป็น review candidate ที่ `canonical_product_id: null`.

0.1.2b → 0.1.3b: Boss อนุมัติให้เพิ่มภาพ crop ต้นฉบับสำหรับเทียบกับโมเดล 3D ใน local viewer. เพิ่มได้เฉพาะ PNG code-matched ที่ hash-verified ผ่าน allowlist; ไม่ expose raw PDF หรือเปลี่ยน canonical identity/schema.

0.1.3b → 0.1.4b: สร้างและตรวจ local comparison panel สำหรับ S1033/DW03/W502; รัน server/browser negative checks แล้ว ไม่มีการขยาย source exposure นอก allowlist.

0.1.4b → 0.2.0b: อนุมัติ generated local viewer index และ Category coverage display สำหรับ 16 ProductMaster. Server เปิดเฉพาะ projection ที่ปลอดภัยและ asset ของ candidate/local-ready; ไม่เปิด raw evidence register หรือ source paths.

0.2.0b → 0.2.1b: server อ่าน [generated viewer index](../../output/catalog-3d/viewer_index.json) ตอนเริ่ม, ตรวจ model/reference SHA และ serve เฉพาะ safe projection. Browser ตรวจ All review candidates และ Eco-Friendly hold state; ไม่มี stale model, console warning/error หรือ raw registry route.

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.2.1b | 2026-08-31 | beta | generated index/category hold state ผ่าน local browser checks | uncommitted | ATHER |
| 0.2.0b | 2026-08-31 | beta | viewer ใช้ generated index และแสดง Category coverage แบบ local | uncommitted | ATHER |
| 0.1.4b | 2026-08-31 | beta | ภาพต้นฉบับแบบ local comparison ผ่าน server/browser checks | uncommitted | ATHER |
| 0.1.3b | 2026-08-31 | beta | อนุมัติภาพต้นฉบับแบบ local allowlist สำหรับเทียบโมเดล | uncommitted | ATHER |
| 0.1.2b | 2026-08-31 | beta | เพิ่ม W502 v001 ใน local allowlist พร้อม regression check ของ asset version | uncommitted | ATHER |
| 0.1.1b | 2026-08-31 | beta | viewer ใช้งานได้บนเครื่อง พร้อมผลทดสอบ UI/alpha/error retry | uncommitted | ATHER |
| 0.1.0b | 2026-08-31 | beta | อนุมัติ viewer หมุน/ซูม/เปลี่ยนสีแบบโปร่งใส | uncommitted | ATHER |
