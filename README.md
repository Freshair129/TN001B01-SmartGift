# SmartGift → smartgift + Price Boss SPA

## Docker Compose

### รันเฉพาะ MySQL บนเครื่องนี้

ใช้ `.env` สำหรับ local ที่ตั้ง `MYSQL_DATABASE=smartgift`, `MYSQL_USER=root`,
`MYSQL_HOST=127.0.0.1`, `MYSQL_PORT=3312` และ `PRICE_BOSS_MYSQL_PORT=3312`;
`MYSQL_ROOT_PASSWORD` และ `MYSQL_PASSWORD` ต้องเป็นรหัสผ่านสุ่มค่าเดียวกัน
ห้ามเผยแพร่ `.env` หรือใช้รหัสผ่านตัวอย่างกับข้อมูลจริง

```powershell
cd O:\price-boss
docker compose config --quiet
docker compose up -d mysql
docker compose ps mysql
docker compose logs mysql
```

เชื่อมต่อที่ `127.0.0.1:3312` / user `root` / database `smartgift`
โดยใช้รหัสผ่านจาก `.env`; เปิดรับเฉพาะ loopback และคำสั่งนี้ไม่เริ่ม API/Web
เปิด SQL client แบบให้ถามรหัสผ่านด้วย `docker compose exec mysql mysql -uroot -p smartgift`
ข้อมูลอยู่ใน named volume `price_boss_price_boss_mysql_data`
หยุดเฉพาะ MySQL ด้วย `docker compose stop mysql`; ห้ามใช้ `down -v`
การเปลี่ยนรหัสผ่านใน `.env` ไม่เปลี่ยนบัญชีใน volume ที่เคย initialize แล้ว
การเริ่ม volume ใหม่ครั้งแรกอาจใช้เวลาหลายนาที; ต้องรอข้อความ init เสร็จและสถานะ `healthy`
แล้วทดสอบ SQL จริง ไม่ใช้แค่สถานะ container `running` เป็นเกณฑ์ผ่าน

ตรวจรับและข้อจำกัด: [MySQL Docker setup](docs/mysql-docker-setup.md)

### รัน PostgreSQL 16 แยกจาก MySQL

เป็นฐานข้อมูลเปล่าสำหรับ local development; API/Web ยังใช้ MySQL เดิม ไม่มีการย้ายข้อมูล
ใช้ `.env` keys `POSTGRES_DB=smartgift`, `POSTGRES_USER=postgres`,
`PRICE_BOSS_POSTGRES_PORT=5432` และรหัสผ่านสุ่มแยกใน `POSTGRES_PASSWORD`
Compose จะปฏิเสธหากไม่มีรหัสผ่าน; บัญชี `postgres` ใช้ดูแลเท่านั้น ไม่ใช้เชื่อมแอป

```powershell
cd O:\price-boss
docker compose -f docker-compose.postgres.yml config --quiet
docker compose -f docker-compose.postgres.yml pull postgres
docker compose -f docker-compose.postgres.yml up -d --wait --wait-timeout 600 postgres
docker compose -f docker-compose.postgres.yml ps
docker compose -f docker-compose.postgres.yml exec postgres psql -h 127.0.0.1 -U postgres -d smartgift -W
```

เชื่อมต่อ `127.0.0.1:5432` / database `smartgift` / admin `postgres` / รหัสผ่านจาก `.env`
ข้อมูลอยู่ใน volume `price_boss_pg_postgres_data`; หยุดโดยรักษาข้อมูลด้วย
`docker compose -f docker-compose.postgres.yml stop postgres` และห้ามใช้ `down -v`
การเปลี่ยน `.env` ไม่เปลี่ยนรหัสผ่านของฐานที่ initialize แล้ว
หากเริ่มครั้งแรกไม่สำเร็จ ให้เก็บ logs และ volume ไว้วิเคราะห์ ไม่ reset อัตโนมัติ

สเปก ผลตรวจ และ image digest: [PostgreSQL Docker setup](docs/postgres-docker-setup.md)

### รันทั้ง stack (นอกขอบเขตการตรวจรับ MySQL-only)

```powershell
cd O:\price-boss
docker compose up -d --build
```

| Service | URL / Port |
|---|---|
| Web | http://localhost:5180 |
| API | http://localhost:3850/api/health |
| MySQL | `127.0.0.1:3312` · root / รหัสผ่านจาก `.env` · `smartgift` |

ใช้ MySQL เดิม (`tms-mysql` :3310):

```powershell
docker compose -f docker-compose.external-mysql.yml up -d --build
```

## Run SPA + API (local without Docker)

หากใช้ `.env` ที่สร้างสำหรับ MySQL local รอบนี้ API จะเชื่อม `127.0.0.1:3312`, db `smartgift`
จึงต้องเปิด `price-boss-mysql` ไว้ก่อน; หากเลือก MySQL เดิม `tms-mysql` ที่ port **3310**
ต้องปรับ `.env` ให้ตรงกับฐานข้อมูลและ credentials ของ instance นั้นก่อน

```powershell
cd O:\price-boss
npm run dev
```

- Web: http://localhost:5175  
- API: http://127.0.0.1:3850  

Login ทดลอง: `admin` · `manager` · `sale01`

## เอกสาร interactive

เมนู **เอกสาร / DataDict** → `/docs`

- Data Dictionary จาก schema จริง (ค้น/กรองโดเมน/คลิกตาม FK)
- Workflow ละเอียด (ใบเสนอราคา, sync, pricelist ID join, RFQ จีน, Quota & แผน)
- Markdown อ้างอิง: [`docs/README.md`](docs/README.md)

## Stack

- **web/** — React + Vite + TypeScript + Tailwind + React Bits–style motion (`SplitText`, `FadeContent`, `SpotlightCard`)
- **server/** — Express API → MySQL `smartgift`

## Schema extras

| Table | Role |
|---|---|
| `catalogs` / `products` | จากเว็บ (sync) |
| `suppliers` / `china_sourcing` | สั่งจีน |
| `tag_*` / `product_tags` | แท็กสินค้า |
| `smartgift_*` | Pricelist จาก Mac |
| `v_smartgift_report` / `_by_type` / `_by_group` | รายงาน join type↔model↔offer↔price |
| `roles` / `permissions` / `role_permissions` / `employees` | RBAC: administrator / manager / sale |
| `customers` / `customer_contacts` | ลูกค้า + ผู้ติดต่อ (`owner_emp_id` = sale scope) |
| `quotations` / `quotation_items` / `quotation_line_breaks` | ใบเสนอราคา + รายการ + บันได qty/ราคา |
| `quotation_status_logs` | audit เปลี่ยนสถานะ |
| `v_employee_access` / `v_quotation_summary` | มุมมองสิทธิ์และสรุปใบเสนอราคา |

### CRM migration (canonical)

```powershell
Get-Content .\sql\migrate_crm_auth_quote.sql -Raw -Encoding UTF8 |
  docker exec -i tms-mysql mysql -uroot -prootpass --default-character-set=utf8mb4
```

Legacy alias: `sql/migrate_customer_quote_rbac.sql` (ยังใช้ได้กับ `price_db` เก่า)

### Docs

- [docs/data-dictionary-crm.md](docs/data-dictionary-crm.md) — data dictionary ทุกคอลัมน์
- [docs/workflow-quotation.md](docs/workflow-quotation.md) — workflow ตามบทบาท

```powershell
python .\sync_smartgift.py
python .\scripts\import_smartgift_postgres.py
```

Navicat สำหรับ MySQL local รอบนี้: `127.0.0.1:3312` / `root` / รหัสผ่านจาก `.env` / `smartgift`
ส่วน `127.0.0.1:3310` เป็น MySQL เดิม `tms-mysql` ซึ่งไม่ได้เริ่มหรือแก้ credentials โดยงานนี้
