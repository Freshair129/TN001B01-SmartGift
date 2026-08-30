---
version: "0.1.2b"
created_at: "2026-08-30T22:03:00+07:00,ATHER,uncommitted"
last_update: "2026-08-30T22:19:00+07:00,ATHER"
status: "beta"
superseded_by: null
attributes:
  domain: "repository-data-governance"
  doc_type: "architecture-decision"
  scope: "Approved private-repository exception for existing cost workbooks and customer intake files"
  language: "th"
---

# ADR-006 — ข้อเสนอเก็บไฟล์ต้นทุนและข้อมูลลูกค้าใน private repository

**สถานะ:** ผู้ใช้ตอบ “approve” อนุมัติ v0.1.0b เมื่อ 2026-08-30; อัปโหลดชุดที่อนุมัติและตรวจ remote retrieval/hash สำเร็จแล้วตามหลักฐานด้านล่าง ไม่มีการ deploy หรือขยายสิทธิ์

**Complexity / Risk:** C-3 / HIGH — เปลี่ยนขอบเขตการเก็บข้อมูลลูกค้าและเพิ่ม large-file storage

**Parent / peer:** AGENTS.md ข้อ 5, CR-006, ADR-004 (public boundary), ADR-005 (factory intake)

## Context และหลักฐานก่อนอนุมัติ

ผู้ใช้ขอให้นำ Excel ต้นทุนและข้อมูลลูกค้าขึ้น repository เพราะตั้ง private แล้ว คำขอนี้มีเจตนาให้อัปโหลด แต่ขัดกฎเดิมที่ห้าม customer PII เข้า Git ทุกกรณี จึงเสนอข้อยกเว้นเฉพาะงานก่อนปรับกฎตาม Doc-first

- ตรวจ GitHub ผ่าน `gh repo view Freshair129/TN001B01-SmartGift --json nameWithOwner,visibility,isPrivate,url` เมื่อ 2026-08-30 ประมาณ 21:59 ICT: `visibility=PRIVATE`, `isPrivate=true`
- ปลายทาง origin: `https://github.com/Freshair129/TN001B01-SmartGift.git`; ไม่เปลี่ยนปลายทาง/สิทธิ์ผู้เข้าถึง
- ตรวจ metadata และ hash เท่านั้น ไม่เปิดเผยชื่อบุคคล ชื่อลูกค้า ชื่อไฟล์ที่ระบุลูกค้า หรือข้อมูลใน workbook ลงเอกสารนี้
- ไฟล์ที่ตรงกับกฎ ignore ที่ผู้ใช้กล่าวถึงมี 13 ไฟล์ เนื้อหาไม่ซ้ำตาม SHA256 จำนวน 8 ชุด; ความซ้ำทาง byte ไม่ใช่เหตุให้ลบหรือรวมไฟล์เอง

| กลุ่มไฟล์ที่มีอยู่ขณะตรวจ | จำนวน | Bytes รวม |
|---|---:|---:|
| `01_raw/08_factory_costs/*.xlsx` | 2 | 471733807 |
| `01_raw/archive/factory_costs/*.xlsx` | 2 | 471733807 |
| `01_raw/05_crm_customer_data/` | 3 | 1500282 |
| Customer exports ที่ซ้ำอยู่ใน `01_raw/01_flowaccount_exports/` | 3 | 1205632 |
| Customer exports ที่ซ้ำอยู่ใน `01_raw/archive/` | 3 | 1205632 |

ทุก path ในตารางอยู่ใต้ `data-pipeline/` เท่านั้น; ไม่รวมไฟล์อนาคตหรือข้อมูลลูกค้าในที่อื่นโดยอัตโนมัติ

ไฟล์ใหญ่สุด 376612464 bytes (ประมาณ 377 MB / 359 MiB) เกินข้อจำกัด GitHub Git ปกติ 100 MiB จึงต้องใช้ Git LFS หรือปลายทางเก็บไฟล์ขนาดใหญ่ที่ผู้ใช้อนุมัติ เครื่องมี git-lfs 3.7.1 แต่ `git lfs ls-files` ยังไม่มีไฟล์ และยังไม่มี root `.gitattributes`

อ้างอิง: [GitHub large-file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github), [Git LFS storage](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)

## Decision ที่เสนอให้อนุมัติ

รายการต่อไปนี้ได้รับอนุมัติแล้วด้วยคำตอบ “approve”; ไม่ขยายขอบเขตนอก 13 ไฟล์ที่ตรวจไว้

1. **ข้อยกเว้นเฉพาะ repository และชุดไฟล์ปัจจุบัน:** อนุญาตให้เก็บไฟล์ต้นทุนและ customer intake 13 ไฟล์ที่ตรวจพบใน private origin นี้ ไม่ยกเลิก Zero-PII ทั่วองค์กร และไม่อนุญาตให้ข้อมูลลูกค้าเข้า product vault, public artifacts หรือระบบอื่น
2. **Large-file handling:** ใช้ Git LFS สำหรับ Excel ต้นทุน 4 ไฟล์ในขอบเขต ส่วนไฟล์ลูกค้าใช้ Git ตามปกติเฉพาะที่ตรวจรับแล้ว; ตรวจ quota/billing และไม่มีการเปิดจ่ายเงิน ซื้อโควตา หรือเพิ่ม spending limit โดยอัตโนมัติ หากต้องเสียค่าใช้จ่ายใหม่ให้หยุดถามก่อน
3. **ปรับ governance ให้ตรงกันก่อนเพิ่มไฟล์:** แก้ AGENTS.md ข้อ 5 และสถานะ follow-up ของ CR-006 ให้บันทึกข้อยกเว้นนี้ โดยรักษาประวัติ public exposure เดิมไว้; ปรับ `.gitignore` ด้วย scoped allowlist เฉพาะไฟล์ปัจจุบัน ไม่ปลด ignore ข้อมูลลูกค้าทุกไฟล์/ทุกตำแหน่งแบบเหมารวม
4. **คงขอบเขต public deployment:** รักษา `.vercelignore` และ public API allowlist ตาม ADR-004 ข้อมูลลูกค้าและต้นทุนห้ามไป `public/`, API responses, build logs หรือ published artifacts; ต้องตรวจ automatic CI/integration ที่อาจอ่าน repo ก่อน push ไม่ถือว่า private repo ทำให้เว็บไซต์หรือ integrations กลายเป็น private
5. **ไม่มีการแปลงหรือย้ายต้นฉบับ:** ไม่แก้ workbook, ไม่ลบไฟล์ซ้ำ, ไม่เปลี่ยน source of record ของ CRM, ไม่รัน ingestion/pricing pipeline และไม่ rewrite Git history
6. **Commit แบบเจาะจง:** stage เฉพาะ allowlist ที่ตรวจแล้วและเอกสาร/กฎที่เกี่ยวข้อง แยกจาก dirty manifests ของงานอื่น ไม่ใช้ `git add .` หรือ force push; ตรวจ commits ที่จะตามขึ้นไปทั้งช่วงก่อน push

## ขอบเขตการเข้าถึงและความเสี่ยงที่ต้องยอมรับ

Private จำกัดการเข้าถึง repository แต่ข้อมูลยังอยู่ใน Git history, clones และอาจเข้าถึงได้โดย collaborators, GitHub Apps หรือ CI ที่มีสิทธิ์อยู่แล้ว การลบใน commit ภายหลังไม่ถอนสำเนาที่ถูกดาวน์โหลดหรือ history ก่อนหน้า การเปลี่ยนเป็น private วันนี้ไม่ย้อนลบ public exposure ที่ CR-006 บันทึกไว้

การอนุมัติข้อเสนอนี้ให้ยืนยันว่าผู้ใช้มีอำนาจอนุญาตการเก็บและเปิดให้ผู้มีสิทธิ์ของ private repository นี้เข้าถึงข้อมูลลูกค้าชุดที่ระบุ ไม่ถือเป็นการเพิ่มสิทธิ์บุคคล/app ใหม่หรืออนุมัติข้อยกเว้นด้านกฎหมายโดยตัวเอกสารนี้

```text
ไฟล์ต้นฉบับในเครื่อง
  ├─ Excel ต้นทุน 4 ไฟล์ → Git LFS ของ private origin
  └─ Customer intake/copies 9 ไฟล์ → Git ของ private origin

ห้ามส่งต่อ → public site/API, product vault, repo อื่น, CI artifact/log
```

## Verification / Acceptance / Exit criteria

ก่อนอัปโหลด:

- ผู้ใช้อนุมัติข้อยกเว้นและวิธี LFS ในเอกสารนี้; ถ้าจำนวนหรือขอบเขตไฟล์เปลี่ยน ให้ทบทวน allowlist ใหม่
- ตรวจสิทธิ์/กลุ่มผู้เข้าถึงและ repo integrations ที่เกี่ยวข้อง; ตรวจชนิดข้อมูลในไฟล์โดยไม่พิมพ์ค่าข้อมูลส่วนตัวลง logs และหยุดหากพบ secrets หรือข้อมูลนอกขอบเขตที่อนุมัติ
- ตรวจ remote เป็น private ซ้ำทันที ก่อน push/LFS upload; ถ้าอ่านสถานะไม่ได้หรือไม่ใช่ private ให้หยุด
- ตรวจ LFS configuration, available quota/billing, file pointers และ original SHA256; ไม่ rewrite history เพื่อแก้ large-file error โดยพลการ
- ตรวจ staged paths/commit range ทั้งหมด, public exclusion และ CI/integration exposure; ไม่รวมสอง manifests ที่มีงานอื่นแก้ค้างอยู่

หลังอัปโหลด:

- ตรวจ remote commit และไฟล์/LFS objects เฉพาะชุดที่อนุมัติว่าดึงกลับได้และ SHA256 ตรงต้นฉบับ โดยไม่เผยเนื้อหาลูกค้าในรายงาน
- ตรวจ repo ยัง private และไม่มี customer/raw assets ใน public artifact ที่เกี่ยวข้อง
- รายงานผลแยก Git commit/push, LFS upload, CI/deployment boundary และสิ่งที่ยังไม่ได้ยืนยัน ไม่กล่าวว่า uploaded แล้วจากการแก้ ignore เพียงอย่างเดียว

## Implementation evidence

### Pre-upload verification หลังอนุมัติ

- Inventory คงเดิม: 13 paths, 8 unique SHA256; current/archive cost ใช้ LFS 4 paths / 2 unique contents รวม unique cost bytes 471733807
- API ยืนยัน private และผู้เข้าถึงเดิม 3 บัญชี (admin 1/write 2); ไม่มีการเปลี่ยนสิทธิ์
- API ไม่พบ workflows, webhooks, deployments หรือ check-run/status contexts ใน repo ขณะตรวจ; ไม่ใช่การรับรองสิทธิ์ของทุก account-level GitHub App
- Billing API อ่านไม่ได้ด้วย token ปัจจุบัน จึงตรวจผ่าน signed-in GitHub Billing UI แบบ read-only: GitHub Free, LFS storage 0 GB/10 GB และ bandwidth 0 GB/10 GB, billable LFS $0; ไม่เพิ่ม OAuth scopes, ซื้อโควตาหรือแก้ budget/payment
- Office ZIP/XML scan ทั้ง 13 ไฟล์ไม่พบรูปแบบ credentials ที่ตรวจ, credential labels, VBA หรือ embedded OLE parts; เป็น scoped pattern scan ไม่ใช่หลักฐานว่าข้อมูลไม่มี PII (ไฟล์ลูกค้ามี PII ตามขอบเขตที่อนุมัติ)
- `.vercelignore` คงกฎกัน `data-pipeline/**`; ไม่มีการเปลี่ยน `public/`, API, workbook หรือ pipeline จากงานนี้
- ตรวจ allowlist 13 paths และ SHA256 ต้นฉบับตรงทั้งหมด; 5 future-path probes ยังถูก ignore; 4 cost paths ได้ LFS filter และ 9 customer paths ไม่มี LFS filter
- ตรวจ index ก่อน commit มี 18 paths ตรงรายการอนุมัติ (13 data + 5 governance/config); customer blobs 9/9 hash ตรง, LFS pointers 4/4 มี size/OID ตรงและ local objects 2/2 hash ตรง; สอง dirty manifests ไม่อยู่ใน index
- ตรวจ `git diff --cached --check` ผ่าน; ก่อน commit ไม่มี local commits ที่รอ push และ remote main ตรงฐาน `56241fbc0f23ba2bda28058d5cd3fde105181ad7`

### Post-upload verification — 2026-08-30 ประมาณ 22:19 ICT

- Data/governance commit `b23fb4e92a3bcd42e8aa8c9d4de063f77bef54aa` มีเฉพาะ 18 paths ที่ตรวจไว้; push ไป `origin/main` สำเร็จและ `git ls-remote` ยืนยัน commit ตรงกัน
- Git LFS upload สำเร็จ 2 unique objects / 471733807 bytes สำหรับ cost paths ทั้ง 4; ไม่มีการแก้ billing, quota, collaborators หรือ repository visibility
- ตรวจหลัง push ผ่าน API อีกครั้ง: `visibility=PRIVATE`, `isPrivate=true`
- ดึง remote Git tree และ 8 unique Git blobs ผ่าน GitHub API: paths ทั้ง 13 ตรง commit, customer files ทั้ง 9 มี SHA256/size ตรงต้นฉบับ และ LFS pointers ทั้ง 4 มี OID/size ตรงรายการอนุมัติ
- `git lfs fetch --refetch origin b23fb4e92a3bcd42e8aa8c9d4de063f77bef54aa` สำเร็จ; ตรวจ SHA256/size ของ LFS objects ที่ดึงกลับทั้ง 2 ตรงต้นฉบับ และ `git lfs fsck --objects --pointers` ผ่าน
- SHA256 ของไฟล์ต้นฉบับบนดิสก์ทั้ง 13 ยังตรง baseline; ไม่แก้เนื้อหา workbook และไม่ลบไฟล์ซ้ำ
- สอง dirty manifests ของงานอื่นไม่ได้อยู่ใน commit และยังคงอยู่ใน working tree; index ว่างหลัง data commit
- งานนี้ไม่เปลี่ยน `public/`, `src/`, `.github/` หรือ `.vercelignore`; กฎกัน `data-pipeline/**` ยังอยู่ ไม่รัน pipeline/build/deploy และไม่ตรวจรับ public deployment เดิมแทนงานอื่น
- API ที่ source commit พบ check-runs 0, status contexts ว่าง (combined state `pending`) และ deployments 0: ไม่มี CI result ให้รายงานว่าผ่าน; verification งานนี้เป็น Git/LFS integrity และ scope checks ไม่ใช่ application test หรือการรับรอง account-level integrations ทั้งหมด

## Version diff

`0.1.1b → 0.1.2b beta`: บันทึกผล push, private status และ remote Git/LFS retrieval/hash ที่ตรวจผ่าน; ไม่มีการขยาย allowlist หรือเปลี่ยนข้อมูล

`0.1.0b candidate → 0.1.1b beta`: บันทึกอนุมัติและ pre-upload evidence พร้อมเริ่ม scoped allowlist/LFS setup; push และ remote verification ต้องตรวจแยก

ไม่มีเอกสารเดิม → `0.1.0b candidate`: เสนอข้อยกเว้น private-repo source storage และ LFS สำหรับไฟล์ใหญ่; ยังไม่เปลี่ยน AGENTS.md, CR-006, `.gitignore`, `.gitattributes`, index หรือ remote

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.2b | 2026-08-30 | beta | บันทึก private upload และ remote Git/LFS hash verification สำเร็จ | source: b23fb4e | ATHER |
| 0.1.1b | 2026-08-30 | beta | บันทึกอนุมัติและ private/quota/security preflight; เริ่ม implementation แบบ scoped | b23fb4e | ATHER |
| 0.1.0b | 2026-08-30 | candidate | ตรวจ private/ขนาดไฟล์ และเสนอ scoped customer-data exception + LFS ก่อนอัปโหลด | uncommitted | ATHER |
