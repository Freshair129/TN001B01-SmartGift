-- SmartGift catalog + China sourcing RFQ schema
CREATE DATABASE IF NOT EXISTS smartgift
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smartgift;

-- ── Catalog จากเว็บ SmartGift (sync อัตโนมัติ) ──────────────────────────
CREATE TABLE IF NOT EXISTS catalogs (
  catalog_key   VARCHAR(64)  NOT NULL PRIMARY KEY,
  label         VARCHAR(255) NOT NULL,
  product_count INT          NOT NULL DEFAULT 0,
  source_url    VARCHAR(512) NOT NULL,
  synced_at     DATETIME     NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS products (
  id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  catalog_key    VARCHAR(64)  NOT NULL,
  code           VARCHAR(64)  NOT NULL,
  name           VARCHAR(512) NULL,
  rmb            DECIMAL(12,4) NULL COMMENT 'ราคา catalog จากโรงงาน (อ้างอิง)',
  upc            INT NULL,
  dim_l          DECIMAL(10,2) NULL,
  dim_w          DECIMAL(10,2) NULL,
  dim_h          DECIMAL(10,2) NULL,
  kg             DECIMAL(10,3) NULL,
  exclusive_flag TINYINT(1) NOT NULL DEFAULT 0,
  img            VARCHAR(255) NULL,
  synced_at      DATETIME NOT NULL,
  UNIQUE KEY uk_catalog_code (catalog_key, code),
  KEY idx_catalog (catalog_key),
  KEY idx_name (name(191)),
  CONSTRAINT fk_products_catalog
    FOREIGN KEY (catalog_key) REFERENCES catalogs (catalog_key)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── ผู้ขาย / โรงงานจีน ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(255) NOT NULL,
  contact_name VARCHAR(128) NULL,
  wechat       VARCHAR(128) NULL,
  email        VARCHAR(255) NULL,
  phone        VARCHAR(64)  NULL,
  city         VARCHAR(128) NULL,
  note         TEXT NULL,
  is_active    TINYINT(1) NOT NULL DEFAULT 1,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── ใบขอราคา / สเปคสั่งจากจีน (1 แถวต่อสินค้า+ซัพพลายเออร์) ───────────
-- ฟิลด์ว่าง = ยังไม่ได้ขอ / ยังไม่มีคำตอบ
CREATE TABLE IF NOT EXISTS china_sourcing (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  product_id      BIGINT UNSIGNED NOT NULL,
  supplier_id     BIGINT UNSIGNED NULL,
  status          ENUM('draft','requested','quoted','confirmed','rejected')
                    NOT NULL DEFAULT 'draft',
  currency        CHAR(3) NOT NULL DEFAULT 'CNY',

  -- Unit Price: ราคาต่อชิ้นที่ 100 / 500 / 1,000 / 3,000
  unit_price_100    DECIMAL(12,4) NULL COMMENT 'ราคา @ 100 ชิ้น',
  unit_price_500    DECIMAL(12,4) NULL COMMENT 'ราคา @ 500 ชิ้น',
  unit_price_1000   DECIMAL(12,4) NULL COMMENT 'ราคา @ 1,000 ชิ้น',
  unit_price_3000   DECIMAL(12,4) NULL COMMENT 'ราคา @ 3,000 ชิ้น',
  unit_price_note   VARCHAR(512) NULL,

  -- MOQ: ขั้นต่ำต่อรุ่น / ต่อสี / ต่อโลโก้
  moq_model         INT NULL COMMENT 'MOQ ต่อรุ่น',
  moq_color         INT NULL COMMENT 'MOQ ต่อสี',
  moq_logo          INT NULL COMMENT 'MOQ ต่อโลโก้',
  moq_note          VARCHAR(512) NULL,

  -- Sample: ราคาตัวอย่าง + ค่าขนส่ง
  sample_price      DECIMAL(12,4) NULL,
  sample_shipping   DECIMAL(12,4) NULL,
  sample_note       VARCHAR(512) NULL,

  -- OEM Logo: Silk Screen / UV Print / Laser / Full Color
  logo_silk_screen  TINYINT(1) NULL COMMENT '1=ทำได้ 0=ไม่ได้ NULL=ยังไม่ถาม',
  logo_uv_print     TINYINT(1) NULL,
  logo_laser        TINYINT(1) NULL,
  logo_full_color   TINYINT(1) NULL,
  logo_setup_fee    DECIMAL(12,4) NULL COMMENT 'ค่าเซ็ตอัพโลโก้ (ถ้ามี)',
  logo_note         VARCHAR(512) NULL,

  -- Custom Color: MOQ + ค่าทำสี Pantone
  custom_color_moq  INT NULL,
  pantone_fee       DECIMAL(12,4) NULL,
  custom_color_note VARCHAR(512) NULL,

  -- Packaging: กล่องธรรมดา / พรีเมียม / คู่มือ / อุปกรณ์ในกล่อง
  pkg_standard_box  VARCHAR(255) NULL,
  pkg_premium_box   VARCHAR(255) NULL,
  pkg_manual        VARCHAR(255) NULL,
  pkg_accessories   TEXT NULL COMMENT 'รายการอุปกรณ์ในกล่อง',
  pkg_note          VARCHAR(512) NULL,

  -- Production Lead Time: วันผลิตหลังอนุมัติตัวอย่าง
  production_lead_days INT NULL,
  production_lead_note VARCHAR(512) NULL,

  -- Carton Data
  carton_qty        INT NULL COMMENT 'จำนวนชิ้นต่อกล่อง',
  carton_l_cm       DECIMAL(10,2) NULL,
  carton_w_cm       DECIMAL(10,2) NULL,
  carton_h_cm       DECIMAL(10,2) NULL,
  carton_nw_kg      DECIMAL(10,3) NULL COMMENT 'Net Weight',
  carton_gw_kg      DECIMAL(10,3) NULL COMMENT 'Gross Weight',
  carton_cbm        DECIMAL(12,6) NULL,
  carton_note       VARCHAR(512) NULL,

  -- Battery Data (power bank / อุปกรณ์มีแบต)
  cell_maker        VARCHAR(128) NULL COMMENT 'ผู้ผลิตเซลล์',
  cell_model        VARCHAR(128) NULL COMMENT 'รุ่นเซลล์',
  capacity_real_mah INT NULL COMMENT 'ความจุจริง (mAh)',
  cycle_life        INT NULL COMMENT 'จำนวนรอบชาร์จ',
  battery_note      VARCHAR(512) NULL,

  -- Test Documents
  doc_battery_test  TINYINT(1) NULL COMMENT 'มีเอกสารทดสอบแบต',
  doc_safety        TINYINT(1) NULL COMMENT 'มีเอกสารความปลอดภัย',
  doc_transport     TINYINT(1) NULL COMMENT 'มีเอกสารการขนส่ง (UN38.3 ฯลฯ)',
  docs_file_refs    TEXT NULL COMMENT 'ลิงก์/ชื่อไฟล์เอกสาร',
  docs_note         VARCHAR(512) NULL,

  -- Warranty
  warranty_months   INT NULL,
  warranty_terms    TEXT NULL COMMENT 'เงื่อนไขเมื่อสินค้ามีปัญหา',

  -- Trade Term: EXW / FOB / DDP Bangkok
  trade_term        ENUM('EXW','FOB','DDP_Bangkok','OTHER') NULL,
  trade_term_port   VARCHAR(128) NULL COMMENT 'เช่น Shenzhen, Ningbo',
  trade_term_note   VARCHAR(512) NULL,

  -- Payment: มัดจำ + ยอดก่อนส่ง
  deposit_pct               DECIMAL(5,2) NULL COMMENT '% เงินมัดจำ',
  balance_before_ship_pct   DECIMAL(5,2) NULL COMMENT '% ชำระก่อนส่ง',
  payment_note              VARCHAR(512) NULL,

  -- Meta
  requested_at    DATETIME NULL,
  quoted_at       DATETIME NULL,
  confirmed_at    DATETIME NULL,
  internal_note   TEXT NULL,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uk_product_supplier (product_id, supplier_id),
  KEY idx_status (status),
  KEY idx_supplier (supplier_id),
  CONSTRAINT fk_sourcing_product
    FOREIGN KEY (product_id) REFERENCES products (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_sourcing_supplier
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── เช็กลิสต์สิ่งที่ต้องขอจากโรงงาน (อ้างอิง / UI) ──────────────────────
CREATE TABLE IF NOT EXISTS china_request_checklist (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  group_code   VARCHAR(64)  NOT NULL,
  group_label  VARCHAR(128) NOT NULL COMMENT 'หัวข้อภาษาไทย',
  field_code   VARCHAR(64)  NOT NULL,
  ask_th       VARCHAR(512) NOT NULL COMMENT 'สิ่งที่ต้องขอ',
  sort_order   INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_group_field (group_code, field_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO china_request_checklist (group_code, group_label, field_code, ask_th, sort_order) VALUES
  ('unit_price', 'Unit Price', 'tiers', 'ราคา 100 / 500 / 1,000 / 3,000 ชิ้น', 10),
  ('moq', 'MOQ', 'tiers', 'ขั้นต่ำต่อรุ่น ต่อสี และต่อโลโก้', 20),
  ('sample', 'Sample', 'price_ship', 'ราคาตัวอย่างและค่าขนส่ง', 30),
  ('oem_logo', 'OEM Logo', 'methods', 'Silk Screen, UV Print, Laser หรือ Full Color', 40),
  ('custom_color', 'Custom Color', 'moq_pantone', 'MOQ และค่าทำสี Pantone', 50),
  ('packaging', 'Packaging', 'options', 'กล่องธรรมดา กล่องพรีเมียม คู่มือ และอุปกรณ์ในกล่อง', 60),
  ('lead_time', 'Production Lead Time', 'days', 'ระยะเวลาผลิตหลังอนุมัติตัวอย่าง', 70),
  ('carton', 'Carton Data', 'pack', 'จำนวนต่อกล่อง, ขนาดกล่อง, NW, GW และ CBM', 80),
  ('battery', 'Battery Data', 'cell', 'ผู้ผลิตเซลล์ รุ่นเซลล์ ความจุจริง และ Cycle Life', 90),
  ('test_docs', 'Test Documents', 'docs', 'เอกสารทดสอบแบตเตอรี่ ความปลอดภัย และการขนส่ง', 100),
  ('warranty', 'Warranty', 'terms', 'ระยะรับประกันและเงื่อนไขสินค้ามีปัญหา', 110),
  ('trade', 'Trade Term', 'incoterm', 'EXW, FOB หรือ DDP Bangkok', 120),
  ('payment', 'Payment', 'terms', 'เงินมัดจำและยอดชำระก่อนส่งสินค้า', 130)
ON DUPLICATE KEY UPDATE
  group_label = VALUES(group_label),
  ask_th = VALUES(ask_th),
  sort_order = VALUES(sort_order);

-- ── มุมมองรวมสินค้า + สถานะ sourcing ───────────────────────────────────
CREATE OR REPLACE VIEW v_product_sourcing AS
SELECT
  p.id AS product_id,
  p.catalog_key,
  p.code,
  p.name,
  p.rmb AS catalog_rmb,
  p.exclusive_flag,
  cs.id AS sourcing_id,
  cs.status,
  cs.currency,
  cs.unit_price_100,
  cs.unit_price_500,
  cs.unit_price_1000,
  cs.unit_price_3000,
  cs.moq_model,
  cs.moq_color,
  cs.moq_logo,
  cs.sample_price,
  cs.sample_shipping,
  cs.production_lead_days,
  cs.carton_qty,
  cs.carton_cbm,
  cs.cell_maker,
  cs.capacity_real_mah,
  cs.trade_term,
  cs.deposit_pct,
  cs.balance_before_ship_pct,
  s.name AS supplier_name,
  cs.updated_at AS sourcing_updated_at
FROM products p
LEFT JOIN china_sourcing cs ON cs.product_id = p.id
LEFT JOIN suppliers s ON s.id = cs.supplier_id;

-- ── CRM / RBAC / Quotation (canonical migration) ───────────────────────
-- Full DDL + seed: sql/migrate_crm_auth_quote.sql  (database: smartgift)
-- Docs: docs/data-dictionary-crm.md · docs/workflow-quotation.md
