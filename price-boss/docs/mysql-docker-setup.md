---
version: "0.2.0b"
created_at: "2026-08-30T09:36:47+07:00,ATHER,uncommitted"
last_update: "2026-08-30T09:53:25+07:00,ATHER"
status: beta
superseded_by: null
attributes:
  domain: local-development
  scope: MySQL Docker setup
  language: th
---

# การรัน MySQL Server ผ่าน Docker

ผู้ใช้อนุมัติข้อเสนอ `0.1.0b` แล้วใน task นี้; ดำเนินการเฉพาะ MySQL local ตามขอบเขตเดิม

## ขอบเขตและสมมติฐาน

- [ASSUMPTIONS] ผู้ใช้ต้องการ MySQL ไม่ใช่ Microsoft SQL Server และใช้งานบนเครื่องนี้เท่านั้น
- รันเฉพาะ MySQL ของ Price Boss ไม่รัน API/Web และไม่เชื่อมต่อบริการภายนอก
- ใช้ฐานข้อมูล `smartgift` และ init scripts ที่มีอยู่ ไม่ออกแบบ schema ใหม่
- Complexity: C-2; Risk: MEDIUM เพราะการเริ่ม volume ใหม่จะรัน migrations และ seed data เดิม

## หลักฐานที่ตรวจแล้ว

- Parent: `README.md` ระบุ MySQL ใน Docker ที่พอร์ต 3312
- Peer: `docker-compose.yml` มี service `mysql`, image `mysql:8.0.36`, container `price-boss-mysql` และ named volume อยู่แล้ว
- `docker-compose.external-mysql.yml` เป็นทางเลือกใช้ฐานข้อมูลภายนอก ไม่อยู่ในขอบเขตนี้
- `docker/mysql/init/10-apply-migrations.sh` สร้าง schema และ seed เมื่อเริ่ม data volume ใหม่ บาง migration อนุญาตให้ล้มเหลวแล้วทำต่อ จึงต้องตรวจ logs เพิ่มจาก healthcheck
- ก่อนอนุมัติ `docker compose config --quiet` ผ่าน แต่ Docker CLI เชื่อมต่อ Linux Engine ไม่ได้เพราะไม่พบ named pipe; รอบดำเนินการเปิด Docker Desktop แล้วเชื่อมต่อสำเร็จตามผลตรวจรับด้านล่าง
- โฟลเดอร์ปัจจุบันไม่ใช่ Git repository จึงยังรายงาน Git diff/commit ไม่ได้

## แผนหลังอนุมัติ

1. เปิด Docker Engine หากจำเป็น แล้วตรวจ container, volume และพอร์ต 3312 ก่อนเปลี่ยนแปลง หากพบข้อมูลเดิมหรือชื่อชนให้หยุดประเมินก่อน ห้ามลบหรือเขียนทับเพื่อให้รันผ่าน
2. ใช้ Compose เดิม ปรับเฉพาะ host binding ของ MySQL เป็น `127.0.0.1` เพื่อจำกัดการเชื่อมต่อจากเครื่องนี้
3. สร้าง `.env` สำหรับ local หากยังไม่มี โดยใช้รหัสผ่านสุ่มแทนค่าเริ่มต้น เก็บ `MYSQL_ROOT_PASSWORD` และ `MYSQL_PASSWORD` ให้ตรงกัน พร้อมตั้งฐานข้อมูล `smartgift` และ host port 3312; ไม่แสดงรหัสผ่านในรายงานและไม่เขียนทับค่าที่มีอยู่
4. รันเฉพาะ service `mysql` ด้วย Docker Compose; อาจต้องดาวน์โหลด image หากยังไม่มีในเครื่อง
5. ตรวจ health, initialization logs และ SQL แบบ authenticated; ปรับคู่มือเฉพาะส่วนการรัน MySQL ให้ตรงกับผลจริง

## เกณฑ์ยอมรับและจบงาน

- Compose validation ผ่าน และ container `price-boss-mysql` เป็น `healthy`
- host port 3312 ถูก publish ที่ `127.0.0.1` เท่านั้น
- เชื่อมต่อด้วยรหัสผ่านได้และ `SELECT 1` สำเร็จ
- พบฐานข้อมูล `smartgift` และตารางจาก migrations หลัก พร้อมรายงาน initialization warning/error ตามจริง
- data directory ใช้ named volume; การหยุด container ไม่ลบ volume และไม่ใช้ `down -v`
- API/Web และฐานข้อมูลของโปรเจกต์อื่นไม่ถูกเริ่ม หยุด หรือลบโดยงานนี้
- รายงานไฟล์ที่เปลี่ยนและผลตรวจจริง ไม่อ้างว่า production-ready หรือผ่านการทดสอบทั้งแอป

## Version diff

- `0.1.0b` (candidate) → `0.2.0b` (beta): บันทึกการอนุมัติและผลดำเนินการ/ตรวจรับจริง
- `docker-compose.yml`: MySQL host binding จากทุก interface → `127.0.0.1` เท่านั้น; ไม่แก้ image, migrations หรือบริการ API/Web
- `.env`: เพิ่มไฟล์ local ด้วยรหัสผ่านสุ่มจาก cryptographic RNG 32 bytes; `MYSQL_ROOT_PASSWORD` และ `MYSQL_PASSWORD` ตรงกัน โดยไม่แสดงค่าในเอกสาร
- `README.md`: เพิ่มคำสั่ง MySQL-only, วิธีหยุดโดยเก็บ volume และการอ่านรหัสผ่านจาก `.env`
- ไม่มี Git repository จึงไม่มี commit/hash หรือ Git diff; ไม่แก้ pricing engine

## ผลดำเนินการและตรวจรับ

สถานะ ณ `2026-08-30T09:53:25+07:00`: MySQL local ใช้งานได้และผ่าน runtime checks ด้านล่าง
แต่ pricelist report views ยังไม่พร้อมเพราะไม่มีการ import ข้อมูลต้นทาง ซึ่งอยู่นอกขอบเขตนี้

| รายการ | ผลตรวจจริง |
|---|---|
| Docker Engine | เปิด Docker Desktop จาก `G:\Docker\Docker\Docker Desktop.exe` แบบ hidden; engine `29.6.1` พร้อมใช้งาน |
| ตรวจชื่อ/ข้อมูลก่อนเริ่ม | ไม่พบ `price-boss-*` container, `price_boss*` volume หรือ listener ที่ 3312 ก่อนสร้าง |
| Compose validation | `docker compose config --quiet` ผ่าน |
| บริการที่สั่งเริ่ม | `docker compose up -d mysql` เท่านั้น |
| Image | `mysql:8.0.36`; digest `sha256:a532724022429812ec797c285c1b540a644c15e248579c6bfdf12a8fbaab4964` |
| Port | Docker inspect/config ยืนยัน `127.0.0.1:3312 -> 3306/tcp` |
| Persistence | volume `price_boss_price_boss_mysql_data` mount ที่ `/var/lib/mysql`; init และ migrations เป็น bind mount แบบ read-only |
| Health | `running / healthy`, `RestartCount=0`; final server พร้อมที่ port 3306 เมื่อ `09:52:54 ICT` |
| SQL แบบ authenticated | TCP ภายใน container ด้วยรหัสผ่านจาก environment: `SELECT 1` ได้ `1`, version `8.0.36`, database `smartgift` |
| ไม่ใส่รหัสผ่าน | หลัง final server พร้อมแล้ว ทดสอบ TCP root แบบ `--skip-password` ถูกปฏิเสธด้วย `ERROR 1045`, exit code 1 |
| เชื่อมต่อจาก host | TCP `127.0.0.1:3312` สำเร็จและได้รับ MySQL handshake protocol 10 / server version `8.0.36`; ไม่ใช่เพียงตรวจว่าเปิด port |
| Schema | 26 base tables + 8 views; พบ `products`, CRM/quotation, tags และ sales command tables |
| Seed | period `2026-08`, quota `873000.00`, ผลรวม quota split `873000.00` |
| ข้อมูลสินค้า | `products` มี 0 rows ตามสภาพฐานข้อมูลใหม่; ไม่ได้ import/sync ข้อมูลต้นทาง |

First bootstrap เริ่ม `09:44:15 ICT`; InnoDB initialization จบ `09:44:59 ICT`;
ณ `09:48:14 ICT` ยังสร้าง system tables โดย block writes เพิ่มจาก 117 MB เป็น 176 MB
และ `mysql.ibd` เพิ่มจาก 16 MB เป็น 24 MB จึงมีหลักฐานว่ากระบวนการยังเดินหน้า
จากนั้นเริ่ม migrations `09:49:29 ICT`, script จบ `09:51:43 ICT`, entrypoint จบ `09:52:43 ICT`
และ final server พร้อม `09:52:54 ICT` (ประมาณ 8 นาที 39 วินาทีหลังเริ่ม initialize)
มีช่วง `unhealthy` ระหว่าง bootstrap เพราะเกินช่วงรอเดิม แต่กลับเป็น `healthy` หลัง initialization เสร็จ
ไม่ reset volume, restart container หรือเปลี่ยน healthcheck เพื่อกลบสถานะ

### Initialization warnings ที่ยังคงอยู่

- `migrate_smartgift_report.sql` มี soft failure 1 รายการ: `ERROR 1146 (42S02) at line 6: Table 'smartgift.smartgift_model' doesn't exist`
  เพราะ init script เดิมไม่ได้ import `sql/smartgiftpricelist.mysql.sql` ก่อนสร้าง report views;
  script ระบุให้ทำต่อได้และ logs ยืนยัน `[price-boss] MySQL init done`
  ดังนั้นยังไม่มี `smartgift_*` pricelist tables และ `v_smartgift_report*` views; ไม่แก้ migrations หรือ import โดยพลการ
- ภาพ MySQL/การตั้งค่าเดิมแจ้ง deprecation ของ `--skip-host-cache`, `default_authentication_plugin` และ `mysql_native_password`,
  self-signed CA, pid-file directory permission, timezone metadata บางไฟล์ที่ถูกข้าม และคำเตือนการใช้ password argument ใน init script
- คำเตือน empty root password เกิดเฉพาะช่วง `--initialize-insecure` ก่อน entrypoint ตั้ง credentials;
  หลัง final startup ยืนยันแล้วว่าล็อกอินไม่ใส่รหัสผ่านไม่ได้
- `healthy` ไม่ได้ยืนยันว่ามีข้อมูล Pricelist, ว่า report views พร้อม หรือว่าทั้งแอปใช้งานได้

### ขอบเขตผลกระทบและข้อจำกัด

- Docker Desktop restore container เดิม `supabase_db_G-Maiden` อัตโนมัติขณะเปิด engine ตาม backend log; งานนี้ไม่ได้สั่ง start/stop/delete container นั้น จึงไม่อ้างว่า engine startup ไม่มีผลต่อโปรเจกต์อื่นเลย
- ไม่ได้เริ่ม Price Boss API/Web, ไม่ import/sync ข้อมูลจากบริการภายนอก และไม่ลบข้อมูลหรือ volume ใด
- ยังไม่อ้างว่า production-ready หรือผ่านการทดสอบทั้งแอป

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---------|------|--------|---------|-------------|-------|
| 0.2.0b | 2026-08-30 | beta | ดำเนินการตามอนุมัติ: loopback binding, local credentials และบันทึกผลรันจริง | uncommitted | ATHER |
| 0.1.0b | 2026-08-30 | candidate | เสนอการรัน MySQL ผ่าน Compose เดิมแบบ local-only | uncommitted | ATHER |
