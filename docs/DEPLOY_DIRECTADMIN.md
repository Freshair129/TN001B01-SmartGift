# อัป Catalog ขึ้น DirectAdmin (smartgiftthailand.com)

## ตอบสั้น ๆ: ไม่ต้องใช้ PHP

Catalog เป็น **static site** ล้วน — HTML + CSS + JS + ไฟล์ JSON
ช่อง `PHP Version` ใน DirectAdmin เป็นแค่เวอร์ชันที่จะใช้ *ถ้า* มีไฟล์ `.php` ถูกเรียก
ถ้าไม่มีไฟล์ `.php` เลย ค่านั้นก็ไม่มีผลอะไร

ยืนยันแล้วด้วยการเสิร์ฟ `public/` ผ่าน `python -m http.server` (ไม่มี backend ใด ๆ ทั้งสิ้น)
→ หน้าเว็บโหลดครบ **1,110 รายการ** พร้อมรูป

## ทำไมเมื่อก่อนดูเหมือนต้องมี backend

`public/index.html` เรียก `/api/catalog`, `/api/pricelist`, `/api/media` ก่อน
ซึ่งเป็น **Vercel serverless function** (Node ไม่ใช่ PHP) ใน `api/`

แต่ไฟล์พวกนั้นทำหน้าที่แค่ส่งต่อ JSON ที่อยู่ใน `public/data/` อยู่แล้ว:

| endpoint | ที่จริงคือไฟล์ |
|---|---|
| `/api/catalog` · `/api/pricelist` | `public/data/pricelist_public.json` |
| `/api/media` | `public/data/catalog_media.json` |

จึงเพิ่ม fallback ให้หน้าเว็บอ่านไฟล์ตรง ๆ เมื่อ `/api/*` ตอบ 404
บน Vercel ยังใช้ API เหมือนเดิม บน DirectAdmin จะตกไปใช้ไฟล์ static อัตโนมัติ

## ขั้นตอนอัป

1. อัปเนื้อใน `public/` **ทั้งโฟลเดอร์** ไปวางที่ document root ของ subdomain
   เช่น `/domains/<subdomain>/public_html/`
   (อัปสิ่งที่อยู่ *ข้างใน* `public/` ไม่ใช่ตัวโฟลเดอร์ `public` เอง)
2. ตรวจว่า `.htaccess` ติดไปด้วย — FTP/File Manager มักซ่อนไฟล์ขึ้นต้นด้วยจุด
   ต้องเปิด "show hidden files" ก่อน
3. เปิดหน้าเว็บ ถ้าขึ้นรายการสินค้าและมุมขวาบนไม่ฟ้อง error ถือว่าผ่าน

ขนาดที่ต้องอัป: **~9.6 MB / 219 ไฟล์** (ส่วนใหญ่คือรูปใน `assets/`)

## ⚠️ ห้ามอัป `internal.html` ขึ้น host สาธารณะ

`public/internal.html` คือ Internal Dashboard แสดง **ต้นทุนโรงงานจีน · Landed Cost ·
กำไรขั้นต่ำ · ต้นทุน/หน่วย** ถ้าขึ้นเว็บสาธารณะเท่ากับเปิดต้นทุนให้ลูกค้าและคู่แข่งดู

`.htaccess` ที่ให้มาบล็อกไฟล์นี้ไว้แล้ว (`Require all denied`) แต่ทางที่ปลอดภัยกว่าคือ
**ลบทิ้งตอนอัป** อย่าพึ่งพา .htaccess อย่างเดียว

## เรื่องที่ต่างจาก Vercel

`vercel.json` ตั้ง `cleanUrls: true` ทำให้เข้า `/internal` ได้โดยไม่ต้องใส่ `.html`
บน Apache ไม่มีพฤติกรรมนี้ ต้องใส่นามสกุลเต็ม เช่น `/index.html`
(หน้าแรกไม่มีปัญหาเพราะ `DirectoryIndex index.html`)

## ถ้าอยากได้ `/api/*` จริง ๆ

ไม่จำเป็น แต่ถ้าต้องการ: DirectAdmin แบบ shared ปกติรัน **Node ไม่ได้** ทางเลือกคือ
เขียน `api/catalog.php` ที่ `readfile()` ไฟล์ JSON เดิมออกมาพร้อม header
`Content-Type: application/json` — **อันนี้แหละคือกรณีเดียวที่ต้องใช้ PHP**
แต่ผลลัพธ์เหมือนกับอ่านไฟล์ตรง ๆ ทุกประการ จึงไม่คุ้มที่จะทำ

---

# ย้ายหลังบ้าน (Price Calculator) จาก Vercel มา DirectAdmin

## `smartgift-expo.vercel.app` คืออะไร

คือ `public/internal.html` — **Internal Dashboard** ไม่ใช่หน้า catalog ลูกค้า
มี 6 view: Anatomy Explorer · Offers · Bundles & BOM · Seasonal Expo ·
**คำนวณราคา (Price Calculator)** · Data Governance & Logs

## 🔴 ด่วน: ตอนนี้เปิดสาธารณะอยู่ ไม่มีล็อกอิน

เปิด `https://smartgift-expo.vercel.app/#/calculator` ได้เลยโดยไม่ต้องล็อกอิน หน้านั้นแสดง:

* หัวข้อ **DYNAMIC LANDED COST ENGINE**
* ช่องกรอกต้นทุนโรงงานจีน (EXW RMB) · เรตแลกเงิน · CBM/น้ำหนักต่อกล่อง
* **Markup ที่ใช้: 1.47x** (Corporate) — ตัวเลขกำไรของบริษัทโชว์ตรง ๆ
* เกณฑ์ค่าขนส่งจีน–ไทย จุดสวิตช์ความหนาแน่น 400 kg/CBM
* ค่าสกรีน/เลเซอร์/ปั๊มฟอยล์ และตารางบันไดราคา

> ตัวไฟล์ **ไม่มีตารางต้นทุนรายสินค้า** (ต้นทุนเป็นค่าที่ผู้ใช้พิมพ์เอง)
> สิ่งที่รั่วคือ **สูตรตั้งราคา** ซึ่งคู่แข่งใช้ถอดโครงสร้างกำไรได้

**ต้องปิดที่ Vercel ด้วย** — ย้ายมา DirectAdmin แล้ว URL เดิมยังเปิดอยู่จนกว่าจะ
เปิด Deployment Protection หรือลบ project ทิ้ง

## ย้ายได้ไหม — ได้ ไม่ต้องใช้ PHP

หน้านี้เป็น static เหมือน catalog ทดสอบแล้วด้วย `python -m http.server`
ไม่มี backend ใด ๆ → คำนวณได้ปกติ (฿294.10/ชุด ที่ 1,000 ชุด, ตารางบันไดครบ)

เดิมมันเรียก `/api/catalog` `/api/pricelist` จึงเพิ่ม fallback ไปอ่าน
`./data/pricelist_public.json` ตรง ๆ แบบเดียวกับหน้า catalog

## วิธีทำ

```bash
python scripts/build_backend.py
```

ได้ `dist/backend/` — **217 ไฟล์ 8.9 MB** จัดไว้ให้พร้อมอัป:

| | |
|---|---|
| `index.html` | คือ `internal.html` เปลี่ยนชื่อ เพื่อให้เปิด root ของ subdomain ได้เลย |
| `data/` `assets/` | ข้อมูลและรูป |
| `.htaccess` | `Require valid-user` + `X-Robots-Tag: noindex` |
| `robots.txt` | `Disallow: /` |

**ไม่มี** `index.html` ของหน้า catalog ลูกค้าปนไปด้วย — คนละ docroot กันคนละ subdomain

ขั้นตอน:

1. สร้าง subdomain สำหรับหลังบ้าน (เช่น `admin.smartgiftthailand.com`) หรือใช้
   `zuri.smartgiftthailand.com` ที่มีอยู่แล้ว
2. อัป **เนื้อใน** `dist/backend/` ไปที่ docroot ของ subdomain นั้น
   (เปิด show hidden files ให้ `.htaccess` ติดไปด้วย)
3. DirectAdmin → **Advanced → Password Protected Directories** → เลือกโฟลเดอร์ →
   ตั้ง user/password เอง **(อย่าส่งรหัสผ่านมาให้ผม)**
4. ดู path ของ `.htpasswd` ที่ DirectAdmin สร้าง แล้วแก้บรรทัด `AuthUserFile`
   ใน `.htaccess` ให้ตรง — ค่าเริ่มต้นเป็น `CHANGE_ME` ไว้ตั้งใจให้พัง
   จะได้ไม่เผลอเปิดหน้านี้ทิ้งไว้แบบไม่มีรหัส
5. ทดสอบด้วยหน้าต่าง incognito — ต้องเจอกล่องขอรหัสก่อนเห็นหน้าเว็บ
6. กลับไปที่ Vercel: ปิด `smartgift-expo` (Settings → Deployment Protection
   หรือลบ project)

## เช็กลิสต์ก่อนถือว่าเสร็จ

- [ ] เปิด subdomain หลังบ้านใน incognito แล้ว **ขอรหัสก่อน**
- [ ] `https://smartgift-expo.vercel.app` **เข้าไม่ได้แล้ว**
- [ ] หน้า catalog สาธารณะ **ไม่มี** `internal.html` อยู่ใน docroot
