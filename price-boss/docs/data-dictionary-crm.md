# Data Dictionary — Price Boss CRM / Quotation / RBAC

**Database:** `smartgift` (MySQL 8+)  
**Canonical DDL:** [`sql/migrate_crm_auth_quote.sql`](../sql/migrate_crm_auth_quote.sql)  
**Interactive (แนะนำ):** ในแอป เมนู **เอกสาร / DataDict** → `/docs` (schema สดจาก `schemaCatalog.json`)

> เอกสาร Markdown นี้เน้นรายละเอียดธุรกิจ CRM/Quote — สำหรับทั้งฐานข้อมูลรวมถึง pricelist/sales ให้ใช้หน้า interactive

## 1. Entity overview

| Table | Thai | PK | Purpose |
|---|---|---|---|
| `roles` | บทบาท | `id` | administrator / manager / sale |
| `permissions` | สิทธิ์ | `id` | fine-grained codes |
| `role_permissions` | แมปสิทธิ์ | `(role_id, permission_id)` | many-to-many |
| `employees` | พนักงาน | `id` | login + role + manager tree |
| `customers` | ลูกค้า | `id` | ลูกค้า + `owner_emp_id` (sale scope) |
| `customer_contacts` | ผู้ติดต่อ | `id` | หลายผู้ติดต่อต่อลูกค้า |
| `quotations` | ใบเสนอราคา (หัว) | `id` | สถานะ + ยอดรวม + เงื่อนไข |
| `quotation_items` | รายการสินค้า | `id` | บรรทัดในใบ |
| `quotation_line_breaks` | บันไดราคา | `id` | qty → unit_price ต่อบรรทัด |
| `quotation_status_logs` | ประวัติสถานะ | `id` | audit trail |
| `v_employee_access` | (view) | — | พนักงาน × สิทธิ์ |
| `v_quotation_summary` | (view) | — | สรุปใบ + ลูกค้า + เจ้าของ |

### Row-level scope (ธุรกิจ)

| Role | Customer / Quotation visibility |
|---|---|
| **sale** | เฉพาะแถวที่ `owner_emp_id` = employee.id ของตน |
| **manager** | ทุกแถว (`customer.read_all` / `quote.read_all`) |
| **administrator** | ทุกแถว + จัดการพนักงาน/บทบาท |

---

## 2. `roles`

| Column | Type | Null | Default | Key | Meaning (TH) | Example |
|---|---|---|---|---|---|---|
| `id` | INT UNSIGNED | N | AI | PK | รหัสภายใน | `1` |
| `code` | VARCHAR(32) | N | — | UQ | รหัสบทบาท | `sale` |
| `name_th` | VARCHAR(64) | N | — | | ชื่อไทย | `พนักงานขาย` |
| `name_en` | VARCHAR(64) | Y | NULL | | ชื่ออังกฤษ | `Sale` |
| `description` | VARCHAR(512) | Y | NULL | | คำอธิบายขอบเขต | … |
| `is_active` | TINYINT(1) | N | `1` | | เปิดใช้บทบาท | `1` |
| `created_at` | DATETIME | N | CURRENT_TIMESTAMP | | วันที่สร้าง | |
| `updated_at` | DATETIME | N | ON UPDATE | | วันที่แก้ | |

**Business rules**

- `code` ต้องเป็นหนึ่งใน `administrator` | `manager` | `sale` (enforce ที่แอป; DB เก็บเป็น VARCHAR)
- ห้ามลบ role ที่มี employee อ้างอิง (FK RESTRICT)

---

## 3. `permissions`

| Column | Type | Null | Default | Key | Meaning (TH) | Example |
|---|---|---|---|---|---|---|
| `id` | INT UNSIGNED | N | AI | PK | รหัสภายใน | |
| `code` | VARCHAR(64) | N | — | UQ | รหัสสิทธิ์ | `quote.approve` |
| `module` | VARCHAR(64) | N | — | IDX | กลุ่มโมดูล | `quote` |
| `name_th` | VARCHAR(128) | N | — | | ชื่อไทย | `อนุมัติ/ตีกลับ` |
| `description` | VARCHAR(512) | Y | NULL | | รายละเอียด | |

### Permission catalog (seed)

| code | module | admin | manager | sale |
|---|---|---|---|---|
| `customer.read` | customer | Y | Y | Y |
| `customer.read_all` | customer | Y | Y | |
| `customer.write` | customer | Y | Y | Y |
| `customer.write_all` | customer | Y | Y | |
| `customer.delete` | customer | Y | | |
| `quote.read` | quote | Y | Y | Y |
| `quote.read_all` | quote | Y | Y | |
| `quote.write` | quote | Y | Y | Y |
| `quote.submit` | quote | Y | Y | Y |
| `quote.approve` | quote | Y | Y | |
| `quote.send` | quote | Y | Y | Y |
| `quote.cancel` | quote | Y | Y | |
| `product.read` | product | Y | Y | Y |
| `product.write` | product | Y | Y | |
| `sourcing.write` | sourcing | Y | Y | |
| `employee.read` | employee | Y | Y | |
| `employee.write` | employee | Y | | |
| `employee.manage` | employee | Y | | |
| `role.manage` | admin | Y | | |
| `admin.access` | admin | Y | | |

---

## 4. `role_permissions`

| Column | Type | Null | Key | Meaning |
|---|---|---|---|---|
| `role_id` | INT UNSIGNED | N | PK, FK→roles | บทบาท |
| `permission_id` | INT UNSIGNED | N | PK, FK→permissions | สิทธิ์ |

ON DELETE CASCADE ทั้งสองฝั่ง

---

## 5. `employees`

| Column | Type | Null | Default | Key | Meaning (TH) | Example / rule |
|---|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | AI | PK | รหัสพนักงาน | |
| `emp_code` | VARCHAR(32) | N | — | UQ | รหัสพนักงานธุรกิจ | `SAL001` |
| `username` | VARCHAR(64) | N | — | UQ | ชื่อเข้าสู่ระบบ | `sale01` |
| `password_hash` | VARCHAR(255) | Y | NULL | | hash เท่านั้น | ว่าง = ยังไม่ตั้งรหัส (dev) |
| `full_name` | VARCHAR(128) | N | — | | ชื่อเต็ม | `Sales Rep 01` |
| `email` | VARCHAR(255) | Y | NULL | | อีเมล | |
| `phone` | VARCHAR(64) | Y | NULL | | โทร | |
| `role_id` | INT UNSIGNED | N | — | FK→roles | บทบาท | RESTRICT delete |
| `manager_id` | BIGINT UNSIGNED | Y | NULL | FK→employees | หัวหน้า | SET NULL on delete |
| `is_active` | TINYINT(1) | N | `1` | | ใช้งานได้ | `0` = ล็อกอินไม่ได้ |
| `last_login_at` | DATETIME | Y | NULL | | ล็อกอินล่าสุด | |
| `created_at` / `updated_at` | DATETIME | N | | | audit | |

**Seed demo:** `admin` / `manager` / `sale01` — ต้องตั้ง `password_hash` ก่อน production

---

## 6. `customers`

| Column | Type | Null | Default | Key | Meaning (TH) | Example |
|---|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | AI | PK | | |
| `customer_code` | VARCHAR(32) | N | — | UQ | รหัสลูกค้า | `C-0001` |
| `name_th` | VARCHAR(255) | N | — | IDX | ชื่อไทย | |
| `name_en` | VARCHAR(255) | Y | NULL | | ชื่ออังกฤษ | |
| `customer_type` | ENUM | N | `company` | | company / individual / government | |
| `tax_id` | VARCHAR(32) | Y | NULL | | เลขผู้เสียภาษี | |
| `branch` | VARCHAR(64) | Y | NULL | | สำนักงานใหญ่/สาขา | |
| `billing_address` | TEXT | Y | NULL | | ที่อยู่เรียกเก็บ | |
| `shipping_address` | TEXT | Y | NULL | | ที่อยู่จัดส่ง | |
| `province` | VARCHAR(128) | Y | NULL | | จังหวัด | |
| `phone` / `email` | VARCHAR | Y | NULL | | ติดต่อหลัก | |
| `contact_name` / `_phone` / `_email` | VARCHAR | Y | NULL | | ผู้ติดต่อหลัก (สรุป) | |
| `credit_days` | INT | Y | `0` | | เครดิต (วัน) | `30` |
| `price_list_group` | VARCHAR(32) | Y | NULL | | กลุ่มราคา P-xx | `P-01` |
| `owner_emp_id` | BIGINT UNSIGNED | Y | NULL | FK→employees | เจ้าของ (sale) | scope key |
| `status` | ENUM | N | `active` | IDX | active / inactive / blacklist | |
| `note` | TEXT | Y | NULL | | โน้ตภายใน | |
| `created_by` | BIGINT UNSIGNED | Y | NULL | FK→employees | ผู้สร้าง | |
| `created_at` / `updated_at` | DATETIME | N | | | | |

**Rules**

- sale สร้างลูกค้า → ตั้ง `owner_emp_id` = ตน
- sale แก้ได้เฉพาะลูกค้าที่ตนเป็น owner (ไม่มี `customer.write_all`)
- `blacklist` → ห้ามสร้างใบเสนอราคาใหม่ (enforce ที่แอป)

---

## 7. `customer_contacts`

| Column | Type | Null | Default | Key | Meaning |
|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | AI | PK | |
| `customer_id` | BIGINT UNSIGNED | N | — | FK CASCADE | ลูกค้า |
| `name` | VARCHAR(128) | N | — | | ชื่อผู้ติดต่อ |
| `title` | VARCHAR(128) | Y | NULL | | ตำแหน่ง |
| `phone` / `email` / `line_id` | VARCHAR | Y | NULL | | ช่องทาง |
| `is_primary` | TINYINT(1) | N | `0` | | ผู้ติดต่อหลัก |
| `note` | VARCHAR(512) | Y | NULL | | |
| `created_at` | DATETIME | N | CURRENT_TIMESTAMP | | |

---

## 8. `quotations`

| Column | Type | Null | Default | Key | Meaning (TH) | Rule |
|---|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | AI | PK | | |
| `quote_no` | VARCHAR(32) | N | — | UQ | เลขที่ใบ | เช่น `SG-20260830-001` |
| `customer_id` | BIGINT UNSIGNED | N | — | FK RESTRICT | ลูกค้า | ต้อง active |
| `contact_id` | BIGINT UNSIGNED | Y | NULL | FK SET NULL | ผู้ติดต่อบนใบ | |
| `owner_emp_id` | BIGINT UNSIGNED | N | — | FK RESTRICT | เจ้าของใบ | sale scope |
| `status` | ENUM | N | `draft` | IDX | ดู §10 | |
| `quote_date` | DATE | N | — | IDX | วันที่ออกใบ | |
| `valid_until` | DATE | Y | NULL | | ยืนราคาถึง | มัก +30 วัน |
| `currency` | CHAR(3) | N | `THB` | | สกุลเงิน | |
| `price_list_group` | VARCHAR(32) | Y | NULL | | กลุ่มราคาที่ใช้คำนวณ | |
| `payment_term` | VARCHAR(255) | Y | NULL | | เงื่อนไขชำระ | |
| `delivery_term` | VARCHAR(255) | Y | NULL | | เงื่อนไขส่ง | |
| `trade_term` | VARCHAR(64) | Y | NULL | | EXW/FOB/DDP | |
| `subtotal` | DECIMAL(14,2) | N | `0` | | ก่อนส่วนลด/VAT | |
| `discount_amt` | DECIMAL(14,2) | N | `0` | | ส่วนลดเงิน | |
| `discount_pct` | DECIMAL(5,2) | Y | NULL | | ส่วนลด % | |
| `vat_pct` | DECIMAL(5,2) | N | `7.00` | | อัตรา VAT | |
| `vat_amt` | DECIMAL(14,2) | N | `0` | | ยอด VAT | |
| `grand_total` | DECIMAL(14,2) | N | `0` | | ยอดสุทธิ | |
| `customer_note` | TEXT | Y | NULL | | เงื่อนไขพิมพ์ถึงลูกค้า | |
| `internal_note` | TEXT | Y | NULL | | โน้ตภายใน | |
| `approved_by` / `approved_at` | | Y | NULL | | ผู้/เวลาอนุมัติ | |
| `sent_at` | DATETIME | Y | NULL | | เวลาส่งลูกค้า | |
| `created_by` | BIGINT UNSIGNED | Y | NULL | FK | ผู้สร้าง | |
| `created_at` / `updated_at` | DATETIME | N | | | | |

**Totals rule:** `grand_total ≈ (subtotal − discount_amt) + vat_amt` (คำนวณที่แอป แล้วเขียนกลับ)

---

## 9. `quotation_items`

| Column | Type | Null | Default | Key | Meaning (TH) |
|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | AI | PK | |
| `quotation_id` | BIGINT UNSIGNED | N | — | FK CASCADE | หัวใบ |
| `line_no` | INT | N | `1` | | ลำดับบรรทัด |
| `offer_code` | VARCHAR(64) | Y | NULL | IDX | รหัส offer SmartGift |
| `product_id` | BIGINT UNSIGNED | Y | NULL | | อ้าง catalog `products.id` |
| `sku_code` | VARCHAR(64) | Y | NULL | | SKU แสดงบนใบ |
| `item_name` | VARCHAR(512) | N | — | | ชื่อสินค้า |
| `description` | TEXT | Y | NULL | | สเปคเพิ่ม |
| `qty` | DECIMAL(12,2) | N | `1` | | จำนวนหลักที่เสนอ |
| `qty_tier` | INT | Y | NULL | | ขั้นราคาที่เลือก |
| `unit` | VARCHAR(32) | N | `ชิ้น` | | หน่วย |
| `unit_price` | DECIMAL(14,2) | N | `0` | | ราคาต่อหน่วยของขั้นที่เลือก |
| `discount_amt` | DECIMAL(14,2) | N | `0` | | ส่วนลดบรรทัด |
| `line_total` | DECIMAL(14,2) | N | `0` | | `qty * unit_price − discount` |
| `branding_note` | VARCHAR(512) | Y | NULL | | โลโก้/สี/packing |
| `carton_note` | VARCHAR(255) | Y | NULL | | กล่อง/CBM |
| `profile_code` | VARCHAR(32) | Y | NULL | | `standard` / `corporate` |
| `sort_order` | INT | N | `0` | | เรียง UI |
| `created_at` | DATETIME | N | CURRENT_TIMESTAMP | | |

---

## 10. `quotation_line_breaks`

บันไดราคาต่อบรรทัด (ตรงใบเสนอราคาที่พิมพ์จากเครื่องคำนวณ)

| Column | Type | Null | Default | Key | Meaning |
|---|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | AI | PK | |
| `quotation_item_id` | BIGINT UNSIGNED | N | — | FK CASCADE, UQ(item,qty) | บรรทัดแม่ |
| `qty` | INT | N | — | | จำนวนชุด เช่น 100, 500, 1000 |
| `unit_price` | DECIMAL(14,2) | N | — | | ราคาต่อชุด (THB) |
| `sort_order` | INT | N | `0` | | เรียงคอลัมน์ตาราง |
| `created_at` | DATETIME | N | CURRENT_TIMESTAMP | | |

**Rule:** อย่างน้อย 1 break ต่อ item ก่อน `submit` (แนะนำที่แอป)

---

## 11. `quotation_status_logs`

| Column | Type | Null | Key | Meaning |
|---|---|---|---|---|
| `id` | BIGINT UNSIGNED | N | PK | |
| `quotation_id` | BIGINT UNSIGNED | N | FK CASCADE | ใบ |
| `from_status` | VARCHAR(32) | Y | | สถานะก่อน (NULL = สร้างใหม่) |
| `to_status` | VARCHAR(32) | N | | สถานะหลัง |
| `emp_id` | BIGINT UNSIGNED | Y | FK SET NULL | ผู้กระทำ |
| `note` | VARCHAR(512) | Y | | เหตุผล (จำเป็นเมื่อ reject/cancel) |
| `created_at` | DATETIME | N | | |

ทุกครั้งที่เปลี่ยน `quotations.status` ต้อง insert log 1 แถว

---

## 12. Status values & transitions

| Status | TH | Terminal? |
|---|---|---|
| `draft` | ร่าง | |
| `submitted` | รออนุมัติ | |
| `approved` | อนุมัติแล้ว | |
| `rejected` | ตีกลับ | soft ได้ → draft |
| `sent` | ส่งลูกค้าแล้ว | |
| `accepted` | ลูกค้ารับ | เกือบ terminal |
| `expired` | หมดอายุยืนราคา | terminal |
| `cancelled` | ยกเลิก | terminal |

ดูตาราง transition ละเอียดใน [`workflow-quotation.md`](workflow-quotation.md)

---

## 13. Views

### `v_employee_access`

คอลัมน์: `employee_id`, `emp_code`, `username`, `full_name`, `is_active`, `role_code`, `role_th`, `permission_code`, `module`, `permission_th`  
กรองเฉพาะ employee/role ที่ `is_active = 1`

### `v_quotation_summary`

คอลัมน์: หัวใบ + `customer_code` / `customer_name` / `customer_owner_emp_id` + `owner_code` / `owner_name` / `owner_role` + `item_count` + `break_count`

---

## 14. Naming notes

| Plan name | Actual table |
|---|---|
| `quotation_lines` | `quotation_items` |
| `quotation_status_log` | `quotation_status_logs` |
| `owner_employee_id` | `owner_emp_id` |
| `employee.manage` | มีทั้ง `employee.write` และ `employee.manage` (alias) |
