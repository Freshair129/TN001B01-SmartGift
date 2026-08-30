---
version: "0.1.0b"
created_at: "2026-08-30T10:12:21+07:00,ATHER,uncommitted"
last_update: "2026-08-30T10:12:21+07:00,ATHER"
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

กำลังดำเนินการ ยังไม่อ้างว่า PostgreSQL พร้อมใช้งานจนกว่าเกณฑ์ด้านบนผ่าน

## Version diff

- ไม่มีเอกสาร → 0.1.0b: บันทึกแผนที่อนุมัติและเกณฑ์ตรวจรับก่อนสร้างบริการ
- ขอบเขตไฟล์: Compose PostgreSQLใหม่, เพิ่มPG keysใน.env, คู่มือREADMEและเอกสารนี้เท่านั้น

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-08-30 | beta | บันทึกแผนที่อนุมัติสำหรับ PostgreSQL16 standalone | uncommitted | ATHER |
