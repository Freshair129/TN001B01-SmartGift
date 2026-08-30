-- Customer / Quotation / Employee / RBAC for price_db
-- Roles: administrator, manager, sale
USE price_db;
SET NAMES utf8mb4;

-- ═══════════════════════════════════════════════════════════════════════
-- 1) สิทธิ์และบทบาท
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS roles (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  code        VARCHAR(32)  NOT NULL COMMENT 'administrator|manager|sale',
  name_th     VARCHAR(64)  NOT NULL,
  name_en     VARCHAR(64)  NULL,
  description VARCHAR(512) NULL,
  is_active   TINYINT(1) NOT NULL DEFAULT 1,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_roles_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS permissions (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  code        VARCHAR(64)  NOT NULL COMMENT 'เช่น customer.read, quote.approve',
  module      VARCHAR(64)  NOT NULL COMMENT 'customer|quote|product|employee|admin',
  name_th     VARCHAR(128) NOT NULL,
  description VARCHAR(512) NULL,
  UNIQUE KEY uk_permissions_code (code),
  KEY idx_permissions_module (module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS role_permissions (
  role_id       INT UNSIGNED NOT NULL,
  permission_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_rp_perm FOREIGN KEY (permission_id) REFERENCES permissions (id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════════════════
-- 2) พนักงาน
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS employees (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  emp_code      VARCHAR(32)  NOT NULL,
  username      VARCHAR(64)  NOT NULL,
  password_hash VARCHAR(255) NULL COMMENT 'เก็บ hash เท่านั้น ห้าม plain text',
  full_name     VARCHAR(128) NOT NULL,
  email         VARCHAR(255) NULL,
  phone         VARCHAR(64)  NULL,
  role_id       INT UNSIGNED NOT NULL,
  manager_id    BIGINT UNSIGNED NULL COMMENT 'หัวหน้าโดยตรง',
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  last_login_at DATETIME NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_employees_code (emp_code),
  UNIQUE KEY uk_employees_username (username),
  KEY idx_employees_role (role_id),
  CONSTRAINT fk_employees_role FOREIGN KEY (role_id) REFERENCES roles (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_employees_manager FOREIGN KEY (manager_id) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════════════════
-- 3) ลูกค้า
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS customers (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_code   VARCHAR(32)  NOT NULL,
  name_th         VARCHAR(255) NOT NULL,
  name_en         VARCHAR(255) NULL,
  customer_type   ENUM('company','individual','government') NOT NULL DEFAULT 'company',
  tax_id          VARCHAR(32)  NULL,
  branch          VARCHAR(64)  NULL COMMENT 'สำนักงานใหญ่ / สาขา',
  billing_address TEXT NULL,
  shipping_address TEXT NULL,
  province        VARCHAR(128) NULL,
  phone           VARCHAR(64)  NULL,
  email           VARCHAR(255) NULL,
  contact_name    VARCHAR(128) NULL,
  contact_phone   VARCHAR(64)  NULL,
  contact_email   VARCHAR(255) NULL,
  credit_days     INT NULL DEFAULT 0,
  price_list_group VARCHAR(32) NULL COMMENT 'อ้างอิง P-xx จาก smartgift_price',
  owner_emp_id    BIGINT UNSIGNED NULL COMMENT 'พนักงานขายเจ้าของลูกค้า',
  status          ENUM('active','inactive','blacklist') NOT NULL DEFAULT 'active',
  note            TEXT NULL,
  created_by      BIGINT UNSIGNED NULL,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_customers_code (customer_code),
  KEY idx_customers_owner (owner_emp_id),
  KEY idx_customers_status (status),
  KEY idx_customers_name (name_th(191)),
  CONSTRAINT fk_customers_owner FOREIGN KEY (owner_emp_id) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_customers_created FOREIGN KEY (created_by) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS customer_contacts (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_id  BIGINT UNSIGNED NOT NULL,
  name         VARCHAR(128) NOT NULL,
  title        VARCHAR(128) NULL,
  phone        VARCHAR(64)  NULL,
  email        VARCHAR(255) NULL,
  line_id      VARCHAR(64)  NULL,
  is_primary   TINYINT(1) NOT NULL DEFAULT 0,
  note         VARCHAR(512) NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_cc_customer (customer_id),
  CONSTRAINT fk_cc_customer FOREIGN KEY (customer_id) REFERENCES customers (id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════════════════
-- 4) ใบเสนอราคา
-- ═══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS quotations (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  quote_no        VARCHAR(32)  NOT NULL,
  customer_id     BIGINT UNSIGNED NOT NULL,
  contact_id      BIGINT UNSIGNED NULL,
  owner_emp_id    BIGINT UNSIGNED NOT NULL COMMENT 'พนักงานขายที่ออกใบ',
  status          ENUM(
                    'draft',
                    'submitted',
                    'approved',
                    'sent',
                    'accepted',
                    'rejected',
                    'expired',
                    'cancelled'
                  ) NOT NULL DEFAULT 'draft',
  quote_date      DATE NOT NULL,
  valid_until     DATE NULL,
  currency        CHAR(3) NOT NULL DEFAULT 'THB',
  price_list_group VARCHAR(32) NULL,
  payment_term    VARCHAR(255) NULL,
  delivery_term   VARCHAR(255) NULL,
  trade_term      VARCHAR(64) NULL COMMENT 'EXW/FOB/DDP ฯลฯ',
  subtotal        DECIMAL(14,2) NOT NULL DEFAULT 0,
  discount_amt    DECIMAL(14,2) NOT NULL DEFAULT 0,
  discount_pct    DECIMAL(5,2)  NULL,
  vat_pct         DECIMAL(5,2)  NOT NULL DEFAULT 7.00,
  vat_amt         DECIMAL(14,2) NOT NULL DEFAULT 0,
  grand_total     DECIMAL(14,2) NOT NULL DEFAULT 0,
  customer_note   TEXT NULL COMMENT 'ข้อความถึงลูกค้า',
  internal_note   TEXT NULL,
  approved_by     BIGINT UNSIGNED NULL,
  approved_at     DATETIME NULL,
  sent_at         DATETIME NULL,
  created_by      BIGINT UNSIGNED NULL,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_quotations_no (quote_no),
  KEY idx_quotations_customer (customer_id),
  KEY idx_quotations_owner (owner_emp_id),
  KEY idx_quotations_status (status),
  KEY idx_quotations_date (quote_date),
  CONSTRAINT fk_quotations_customer FOREIGN KEY (customer_id) REFERENCES customers (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_quotations_contact FOREIGN KEY (contact_id) REFERENCES customer_contacts (id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_quotations_owner FOREIGN KEY (owner_emp_id) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_quotations_approved FOREIGN KEY (approved_by) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_quotations_created FOREIGN KEY (created_by) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS quotation_items (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  quotation_id    BIGINT UNSIGNED NOT NULL,
  line_no         INT NOT NULL DEFAULT 1,
  offer_code      VARCHAR(64) NULL COMMENT 'อ้างอิง smartgift_offer.code',
  product_id      BIGINT UNSIGNED NULL COMMENT 'อ้างอิง products.id (catalog จีน)',
  sku_code        VARCHAR(64) NULL,
  item_name       VARCHAR(512) NOT NULL,
  description     TEXT NULL,
  qty             DECIMAL(12,2) NOT NULL DEFAULT 1,
  qty_tier        INT NULL COMMENT 'ขั้นราคา 10/20/50/100/500',
  unit            VARCHAR(32) NOT NULL DEFAULT 'ชิ้น',
  unit_price      DECIMAL(14,2) NOT NULL DEFAULT 0,
  discount_amt    DECIMAL(14,2) NOT NULL DEFAULT 0,
  line_total      DECIMAL(14,2) NOT NULL DEFAULT 0,
  branding_note   VARCHAR(512) NULL COMMENT 'โลโก้ / สี / packing',
  sort_order      INT NOT NULL DEFAULT 0,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_qi_quote (quotation_id),
  KEY idx_qi_offer (offer_code),
  KEY idx_qi_product (product_id),
  CONSTRAINT fk_qi_quote FOREIGN KEY (quotation_id) REFERENCES quotations (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_qi_product FOREIGN KEY (product_id) REFERENCES products (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS quotation_status_logs (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  quotation_id  BIGINT UNSIGNED NOT NULL,
  from_status   VARCHAR(32) NULL,
  to_status     VARCHAR(32) NOT NULL,
  emp_id        BIGINT UNSIGNED NULL,
  note          VARCHAR(512) NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_qsl_quote (quotation_id),
  CONSTRAINT fk_qsl_quote FOREIGN KEY (quotation_id) REFERENCES quotations (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_qsl_emp FOREIGN KEY (emp_id) REFERENCES employees (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════════════════
-- 5) Seed บทบาท
-- ═══════════════════════════════════════════════════════════════════════

INSERT INTO roles (code, name_th, name_en, description) VALUES
  ('administrator', 'ผู้ดูแลระบบ', 'Administrator', 'จัดการสิทธิ์ พนักงาน ลูกค้า ใบเสนอราคา และข้อมูลทั้งระบบ'),
  ('manager',       'ผู้จัดการ',   'Manager',       'อนุมัติใบเสนอราคา ดูทีมขาย จัดการลูกค้าในทีม'),
  ('sale',          'พนักงานขาย', 'Sale',          'สร้าง/แก้ไขใบเสนอราคาของตนเอง และดูแลลูกค้าที่รับผิดชอบ')
ON DUPLICATE KEY UPDATE
  name_th = VALUES(name_th),
  name_en = VALUES(name_en),
  description = VALUES(description);

INSERT INTO permissions (code, module, name_th, description) VALUES
  ('customer.read',     'customer', 'ดูลูกค้า',           'ดูรายชื่อและรายละเอียดลูกค้า'),
  ('customer.write',    'customer', 'แก้ลูกค้า',          'สร้าง/แก้ไขลูกค้า'),
  ('customer.delete',   'customer', 'ลบลูกค้า',           'ลบหรือปิดใช้งานลูกค้า'),
  ('quote.read',        'quote',    'ดูใบเสนอราคา',       'ดูใบเสนอราคา'),
  ('quote.write',       'quote',    'แก้ใบเสนอราคา',      'สร้าง/แก้ไขใบเสนอราคา draft'),
  ('quote.submit',      'quote',    'ส่งอนุมัติใบเสนอราคา','ส่งใบเสนอราคาให้ manager อนุมัติ'),
  ('quote.approve',     'quote',    'อนุมัติใบเสนอราคา',  'อนุมัติ/ตีกลับใบเสนอราคา'),
  ('quote.send',        'quote',    'ส่งให้ลูกค้า',       'เปลี่ยนสถานะเป็น sent'),
  ('quote.read_all',    'quote',    'ดูใบเสนอราคาทุกคน',  'ดูใบเสนอราคาของพนักงานอื่น'),
  ('product.read',      'product',  'ดูสินค้า/ราคา',      'ดู catalog และ smartgift price'),
  ('product.write',     'product',  'แก้สินค้า',          'แก้แท็ก / sourcing'),
  ('employee.read',     'employee', 'ดูพนักงาน',          'ดูรายชื่อพนักงาน'),
  ('employee.write',    'employee', 'จัดการพนักงาน',      'สร้าง/แก้พนักงานและบทบาท'),
  ('admin.access',      'admin',    'เข้าถึงระบบสิทธิ์',  'จัดการ roles / permissions')
ON DUPLICATE KEY UPDATE
  module = VALUES(module),
  name_th = VALUES(name_th),
  description = VALUES(description);

-- administrator = ทุกสิทธิ์
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permissions p WHERE r.code = 'administrator';

-- manager
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p ON p.code IN (
  'customer.read','customer.write',
  'quote.read','quote.write','quote.submit','quote.approve','quote.send','quote.read_all',
  'product.read','product.write',
  'employee.read'
) WHERE r.code = 'manager';

-- sale
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p ON p.code IN (
  'customer.read','customer.write',
  'quote.read','quote.write','quote.submit','quote.send',
  'product.read'
) WHERE r.code = 'sale';

-- พนักงานตัวอย่าง (รหัสผ่านต้องตั้ง hash จริงก่อนใช้งาน login)
INSERT INTO employees (emp_code, username, full_name, email, role_id, is_active)
SELECT 'ADM001', 'admin', 'System Administrator', 'admin@trantech.local', r.id, 1
FROM roles r WHERE r.code = 'administrator'
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), role_id = VALUES(role_id);

INSERT INTO employees (emp_code, username, full_name, email, role_id, is_active)
SELECT 'MGR001', 'manager', 'Sales Manager', 'manager@trantech.local', r.id, 1
FROM roles r WHERE r.code = 'manager'
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), role_id = VALUES(role_id);

INSERT INTO employees (emp_code, username, full_name, email, role_id, manager_id, is_active)
SELECT 'SAL001', 'sale01', 'Sales Rep 01', 'sale01@trantech.local', r.id,
       (SELECT id FROM employees WHERE emp_code = 'MGR001' LIMIT 1), 1
FROM roles r WHERE r.code = 'sale'
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name), role_id = VALUES(role_id);

-- ═══════════════════════════════════════════════════════════════════════
-- 6) Views
-- ═══════════════════════════════════════════════════════════════════════

CREATE OR REPLACE VIEW v_employee_access AS
SELECT
  e.id AS employee_id,
  e.emp_code,
  e.username,
  e.full_name,
  e.is_active,
  r.code AS role_code,
  r.name_th AS role_th,
  p.code AS permission_code,
  p.module,
  p.name_th AS permission_th
FROM employees e
JOIN roles r ON r.id = e.role_id
JOIN role_permissions rp ON rp.role_id = r.id
JOIN permissions p ON p.id = rp.permission_id
WHERE e.is_active = 1 AND r.is_active = 1;

CREATE OR REPLACE VIEW v_quotation_summary AS
SELECT
  q.id,
  q.quote_no,
  q.status,
  q.quote_date,
  q.valid_until,
  q.currency,
  q.subtotal,
  q.vat_amt,
  q.grand_total,
  c.customer_code,
  c.name_th AS customer_name,
  e.emp_code AS owner_code,
  e.full_name AS owner_name,
  r.code AS owner_role,
  (SELECT COUNT(*) FROM quotation_items qi WHERE qi.quotation_id = q.id) AS item_count
FROM quotations q
JOIN customers c ON c.id = q.customer_id
JOIN employees e ON e.id = q.owner_emp_id
JOIN roles r ON r.id = e.role_id;
