---
version: "0.1.1b"
created_at: "2026-08-30T10:12:21+07:00,ATHER,uncommitted"
last_update: "2026-08-30T10:19:54+07:00,ATHER"
status: beta
superseded_by: null
attributes:
  domain: local-development
  scope: PostgreSQL 16 standalone Docker setup
  language: th
---

# PostgreSQL 16 แยกจาก MySQL เดิม

ผู้ใช้อนุมัติแผนใน task นี้แล้ว; Complexity C-2 / Risk LOW
Parent: `README.md` ระบุแอปเดิมใช้ MySQL; peer: `docker-compose.yml` และ `docs/mysql-docker-setup.md`
งานนี้เพิ่มฐานเปล่าแยกกัน ไม่ migrate/import ข้อมูล ไม่แก้ API/Web หรือ plugin

## สัญญาการตั้งค่า

- Compose: `docker-compose.postgres.yml`, project `price_boss_pg`, service `postgres`, container `price-boss-postgres`
- Official image `postgres:16-bookworm`; ไม่มี Dockerfile เพิ่ม และบันทึก digest หลัง pull
- Host `127.0.0.1:5432` → container `5432`; database `smartgift`, admin `postgres`
- Volume `price_boss_pg_postgres_data` → `/var/lib/postgresql/data`; ไม่แชร์ volume กับ MySQL หรือ G-Maiden
- `restart: unless-stopped`, TCP `pg_isready` healthcheck, host authentication `scram-sha-256`
- เพิ่ม `.env` เฉพาะ `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `PRICE_BOSS_POSTGRES_PORT`
- รหัสผ่านสุ่ม 32 bytes แยกจาก MySQL; Compose validation ต้อง fail เมื่อไม่มีรหัสผ่าน; ไม่พิมพ์ secret
- ใช้ `supabase-postgres-best-practices`: postgres เป็น admin เท่านั้น ไม่มี application connection ด้วย superuser; รักษา connection/memory defaults เพราะยังไม่มี workload
- ไม่เพิ่ม Supabase stack, pgAdmin, extensions หรือ connection pooler

## ขั้นตอนและเกณฑ์ตรวจรับ

1. ตรวจชื่อ container/volume/port และข้อมูลเดิมก่อนสร้าง หากชนให้หยุด ไม่ลบหรือย้ายพอร์ตเอง
2. Compose validation ผ่าน แล้ว `pull postgres` และ `up -d --wait --wait-timeout 600 postgres` ด้วย Compose แยก
3. Healthy และ authenticated `SELECT 1`, `DATABASE`/user/version ถูกต้องผ่าน published port; server major ต้องเป็น16
4. Client จากภายนอก container ที่ไม่มีรหัสหรือรหัสผิดต้องถูกปฏิเสธ
5. ไม่มี user/business tables; recreate เฉพาะ container ใหม่แล้ว cluster identifier, database และ volume เดิมยังอยู่
6. MySQL เดิมยัง healthy มี container ID/start time เดิม; ไม่มี Price Boss API/Web ถูกเริ่ม และไม่เปลี่ยนไฟล์แอปเดิม
7. หาก init ล้มเหลว ให้เก็บ logs/data เพื่อ RCA ไม่ reset volume อัตโนมัติ

## คำสั่งใช้งาน

```powershell
cd O:\price-boss
docker compose -f docker-compose.postgres.yml config --quiet
docker compose -f docker-compose.postgres.yml pull postgres
docker compose -f docker-compose.postgres.yml up -d --wait --wait-timeout 600 postgres
docker compose -f docker-compose.postgres.yml ps
docker compose -f docker-compose.postgres.yml exec postgres psql -h 127.0.0.1 -U postgres -d smartgift -W
docker compose -f docker-compose.postgres.yml stop postgres
```

รหัสผ่านดูใน `.env`; ห้ามใช้ `down -v`. เปลี่ยนค่า env ไม่ได้เปลี่ยนรหัสของ cluster ที่ initialize แล้ว
PostgreSQL และ MySQL ใช้ชื่อ database `smartgift` เหมือนกันแต่เป็นคนละ server/port/data volume

## หลักฐานก่อนเริ่ม

- Docker Engine29.6.1ทำงานอยู่; ไม่ต้อง restart engine
- ไม่พบ `price-boss-postgres`, `price_boss_pg_postgres_data` หรือ listener5432
- `price-boss-mysql` healthy ที่127.0.0.1:3312; G-Maiden PostgreSQL17ใช้54322และอยู่นอกขอบเขต
- `.env` ยังไม่มีPOSTGRES keys; ไม่มีCompose/เอกสารPostgreSQLนี้ก่อนรอบดำเนินการ
- ไม่มีGit repository; เก็บ SHA256ไฟล์ก่อนเปลี่ยนเพื่อเทียบขอบเขต

## ผลตรวจรับ

ตรวจจริงวันที่ 2026-08-30 เวลา 10:17–10:19 ICT: **ผ่านสำหรับ PostgreSQL local standalone**

| เกณฑ์ | ผลตรวจ |
|---|---|
| Compose configuration | `config --quiet` exit 0; มีเฉพาะ service `postgres`, project `price_boss_pg` |
| ไม่มีรหัสผ่านใน Compose | override `POSTGRES_PASSWORD` เป็นค่าว่างใน child process แล้ว validation exit 1 พร้อม `POSTGRES_PASSWORD must be set` |
| Image / server | `postgres:16-bookworm`; server `16.15 (Debian 16.15-1.pgdg12+2)`, major 16 |
| สถานะ / port / restart | healthy, `127.0.0.1:5432`, `unless-stopped`; Windows host TCP connect ผ่าน |
| Authenticated SQL | Client container ชั่วคราวบน Docker default network เชื่อม `host.docker.internal:5432` ผ่าน published host port; `SELECT 1` = 1, database `smartgift`, user `postgres` |
| ไม่ส่งรหัสผ่าน | External client exit 2: `fe_sendauth: no password supplied` |
| รหัสผ่านผิด | External client exit 2: `password authentication failed for user "postgres"` |
| SCRAM | `password_encryption=scram-sha-256`; ตรวจเฉพาะ boolean ว่า admin password เป็น SCRAM และ host rules ทั้งหมดใช้ SCRAM ไม่แสดง password hash |
| ฐานเปล่า | user tables/views/foreign tables/materialized views = 0; ไม่มี extension เพิ่มนอกเหนือจาก `plpgsql` ที่มีตาม default |
| Persistence | force-recreate เฉพาะ PostgreSQL แล้ว healthy; container ID เปลี่ยน แต่ cluster identifier, database OID และ volume เดิมไม่เปลี่ยน; authenticated SQL ผ่านซ้ำ |
| MySQL เดิม | healthy, container ID/start time เดิม, restart count 0 |
| G-Maiden | ไม่เปลี่ยน container ID/start time/restart count; healthy เหมือนก่อนเริ่ม |
| API/Web | ไม่ได้เริ่ม service; ไฟล์ `server/` และ `web/` ตรงกับ SHA256 ก่อนงานนี้ |
| Credentials | เพิ่มเฉพาะ 4 PG keys; เนื้อหา `.env` เดิมคงเดิม, รหัสสุ่ม 32 bytes แยกจาก MySQL |
| Connection limits | คงค่า default ที่ตรวจได้ `max_connections=100`; ไม่ปรับ tuning โดยไม่มี workload |

Client ทดสอบเป็น container ชั่วคราวแยกจาก server และถูกลบอัตโนมัติด้วย `--rm` หลังจบคำสั่ง
SQL authentication ข้างต้นผ่าน Docker Desktop host gateway ไม่ใช่ native Windows psql;
ตรวจ Windows `127.0.0.1:5432` เพิ่มด้วย TCP connection และตรวจ binding จาก Docker inspect
healthcheck เป็นเพียง readiness ไม่ใช้แทนการตรวจ authentication

### Image provenance

Digest หลัง pull:

```text
postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825
```

Compose ยังคงใช้ tag `postgres:16-bookworm` ตามแผน; การ pull ครั้งต่อไปอาจได้ patch/digest ใหม่

### หลักฐาน persistence และ isolation

```text
PostgreSQL container before: b9d2dc5c04a962fdff241af3a6a827e0337149a1c333c3aa5330a98c96a1d622
PostgreSQL container after:  3fe00b3fd909221290791d968ac866b28ef2993769164caa018722d99e7e5c71
Cluster system_identifier:  7679658623982432294 (before = after)
Database / OID:              smartgift / 16384 (before = after)
Volume:                     price_boss_pg_postgres_data (before = after)
Volume created:             2026-08-30T03:17:30Z
Volume mount:               /var/lib/postgresql/data
MySQL container:            386bc15d56fdad2c06afa2669555e06bb18a1abf9e38a1d4b32d9bdc2456cba6
MySQL started:              2026-08-30T02:44:13.765878279Z (unchanged)
```

คำสั่งตรวจ persistence ที่รันแล้ว (หยุดชั่วคราวเฉพาะ PostgreSQL, ไม่ลบ volume):

```powershell
docker compose -f docker-compose.postgres.yml up -d --no-deps --force-recreate --wait --wait-timeout 600 postgres
```

หลังสร้าง container ใหม่ logs ระบุว่าพบฐานเดิมและข้าม initialization; ไม่มีการสร้างตารางสำหรับทดสอบ
ไฟล์ `pricing.html` มี SHA256 เปลี่ยนระหว่างงานนี้โดยไม่ใช่การแก้ของงาน PostgreSQL;
รักษาไฟล์นั้นไว้ ไม่ revert และไม่นับเป็น version diff ของงานนี้

## ข้อจำกัดการตรวจรับ

- เป็น PostgreSQL local พร้อมเชื่อมต่อเท่านั้น ไม่ใช่การย้ายแอปจาก MySQLหรือ production-ready
- บัญชี `postgres` เป็น admin สำหรับ setup/ตรวจสอบ; ยังไม่มี application role หรือการเชื่อมแอป
- ไม่ย้ายข้อมูล ไม่ใช้ SQL/business schema เดิม และไม่แก้ connector/plugin
- การ recreate container พิสูจน์การใช้ volume เดิม ไม่ใช่การทดสอบ backup/restore หรือ disaster recovery
- ไม่พบ initialization failure; ข้อความ startup ชั่วคราวระหว่าง init ไม่ทำให้เกณฑ์ healthy/SQL สุดท้ายล้มเหลว
- ไม่มี Git repository จึงไม่มี commit; ใช้ SHA256 baseline ตรวจไฟล์เดิม และไม่ย้อนทับงานที่เปลี่ยนพร้อมกัน

## Version diff

- ไม่มีเอกสาร → 0.1.0b: บันทึกแผนที่อนุมัติและเกณฑ์ตรวจรับก่อนสร้างบริการ
- 0.1.0b → 0.1.1b: เพิ่มผลตรวจรับจริง, digest และหลักฐาน authentication/persistence/isolation
- เพิ่ม `docker-compose.postgres.yml` และเอกสารนี้; แก้ `README.md` เฉพาะคู่มือ PostgreSQL; เพิ่ม 4 PG keys ใน `.env`
- ไม่มีการแก้ Compose MySQL, API/Web, schema, import scripts หรือ connector/plugin

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | beta | บันทึกแผนที่อนุมัติสำหรับ PostgreSQL16 standalone | uncommitted | ATHER |
| 0.1.1b | 2026-08-30 | beta | เพิ่มผลตรวจจริงและ digest; ยืนยัน SCRAM, ฐานเปล่า, persistence และ MySQL isolation | uncommitted | ATHER |
