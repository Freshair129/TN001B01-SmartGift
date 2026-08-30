-- Product tagging system for price_db
USE price_db;
SET NAMES utf8mb4;

-- ── กลุ่มแท็ก (หมวด) ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tag_groups (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  code        VARCHAR(64)  NOT NULL,
  label_th    VARCHAR(128) NOT NULL,
  label_en    VARCHAR(128) NULL,
  sort_order  INT NOT NULL DEFAULT 0,
  is_active   TINYINT(1) NOT NULL DEFAULT 1,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_tag_groups_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── แท็ก ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tags (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tag_group_id  INT UNSIGNED NULL,
  code          VARCHAR(64)  NOT NULL,
  label_th      VARCHAR(128) NOT NULL,
  label_en      VARCHAR(128) NULL,
  color         VARCHAR(32)  NULL COMMENT 'เช่น #92642A สำหรับ UI',
  description   VARCHAR(512) NULL,
  sort_order    INT NOT NULL DEFAULT 0,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_tags_code (code),
  KEY idx_tags_group (tag_group_id),
  CONSTRAINT fk_tags_group
    FOREIGN KEY (tag_group_id) REFERENCES tag_groups (id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── ผูกสินค้า ↔ แท็ก (หลายต่อหลาย) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS product_tags (
  product_id  BIGINT UNSIGNED NOT NULL,
  tag_id      INT UNSIGNED NOT NULL,
  tagged_by   VARCHAR(128) NULL,
  note        VARCHAR(512) NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id, tag_id),
  KEY idx_product_tags_tag (tag_id),
  CONSTRAINT fk_product_tags_product
    FOREIGN KEY (product_id) REFERENCES products (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_product_tags_tag
    FOREIGN KEY (tag_id) REFERENCES tags (id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Seed กลุ่มแท็ก ────────────────────────────────────────────────────
INSERT INTO tag_groups (code, label_th, label_en, sort_order) VALUES
  ('catalog',   'หมวดแคตตาล็อก',     'Catalog',          10),
  ('feature',   'คุณสมบัติสินค้า',   'Product feature',  20),
  ('oem',       'งาน OEM / โลโก้',   'OEM / Logo',       30),
  ('sourcing',  'สถานะ sourcing',    'Sourcing status',  40),
  ('customer',  'กลุ่มลูกค้า',       'Customer segment', 50),
  ('priority',  'ความสำคัญ',         'Priority',         60)
ON DUPLICATE KEY UPDATE
  label_th = VALUES(label_th),
  label_en = VALUES(label_en),
  sort_order = VALUES(sort_order);

-- ── Seed แท็กเริ่มต้น ─────────────────────────────────────────────────
INSERT INTO tags (tag_group_id, code, label_th, label_en, color, sort_order)
SELECT g.id, v.code, v.label_th, v.label_en, v.color, v.sort_order
FROM (
  SELECT 'catalog' AS gcode, 'cat-giftset'   AS code, 'ชุดของขวัญออฟฟิศ' AS label_th, 'Gift set' AS label_en, '#235049' AS color, 10 AS sort_order UNION ALL
  SELECT 'catalog', 'cat-powerbank', 'พาวเวอร์แบงก์ / โน้ตบุ๊ก', 'Power bank / Notebook', '#235049', 20 UNION ALL
  SELECT 'feature', 'feat-exclusive', 'สินค้า Exclusive', 'Exclusive', '#92642A', 10 UNION ALL
  SELECT 'feature', 'feat-battery', 'มีแบตเตอรี่', 'Has battery', '#963232', 20 UNION ALL
  SELECT 'feature', 'feat-wireless', 'ชาร์จไร้สาย', 'Wireless charge', '#2C6B4F', 30 UNION ALL
  SELECT 'feature', 'feat-set', 'เป็นชุด (หลายชิ้น)', 'Multi-item set', '#3A4C48', 40 UNION ALL
  SELECT 'oem', 'oem-silk', 'Silk Screen', 'Silk Screen', '#6A7B76', 10 UNION ALL
  SELECT 'oem', 'oem-uv', 'UV Print', 'UV Print', '#6A7B76', 20 UNION ALL
  SELECT 'oem', 'oem-laser', 'Laser', 'Laser', '#6A7B76', 30 UNION ALL
  SELECT 'oem', 'oem-fullcolor', 'Full Color', 'Full Color', '#6A7B76', 40 UNION ALL
  SELECT 'sourcing', 'src-need-quote', 'รอขอราคาจีน', 'Need China quote', '#8A5A17', 10 UNION ALL
  SELECT 'sourcing', 'src-quoted', 'ได้ราคาแล้ว', 'Quoted', '#2C6B4F', 20 UNION ALL
  SELECT 'sourcing', 'src-sample', 'มีตัวอย่างแล้ว', 'Sample ready', '#2C6B4F', 30 UNION ALL
  SELECT 'sourcing', 'src-ready-order', 'พร้อมสั่งผลิต', 'Ready to order', '#235049', 40 UNION ALL
  SELECT 'customer', 'cust-b2b', 'ลูกค้าองค์กร', 'B2B / Corporate', '#92642A', 10 UNION ALL
  SELECT 'customer', 'cust-event', 'งานอีเวนต์', 'Event / Promo', '#92642A', 20 UNION ALL
  SELECT 'priority', 'prio-hot', 'Hot / ด่วน', 'Hot', '#963232', 10 UNION ALL
  SELECT 'priority', 'prio-watch', 'เฝ้าดู', 'Watch', '#8A5A17', 20
) v
JOIN tag_groups g ON g.code = v.gcode
ON DUPLICATE KEY UPDATE
  tag_group_id = VALUES(tag_group_id),
  label_th = VALUES(label_th),
  label_en = VALUES(label_en),
  color = VALUES(color),
  sort_order = VALUES(sort_order);

-- ── แท็กเริ่มต้นจาก catalog + exclusive ───────────────────────────────
INSERT IGNORE INTO product_tags (product_id, tag_id, tagged_by, note)
SELECT p.id, t.id, 'system', 'auto from catalog_key'
FROM products p
JOIN tags t ON t.code = CONCAT('cat-', p.catalog_key);

INSERT IGNORE INTO product_tags (product_id, tag_id, tagged_by, note)
SELECT p.id, t.id, 'system', 'auto from exclusive_flag'
FROM products p
JOIN tags t ON t.code = 'feat-exclusive'
WHERE p.exclusive_flag = 1;

INSERT IGNORE INTO product_tags (product_id, tag_id, tagged_by, note)
SELECT p.id, t.id, 'system', 'auto powerbank = battery'
FROM products p
JOIN tags t ON t.code = 'feat-battery'
WHERE p.catalog_key = 'powerbank';

INSERT IGNORE INTO product_tags (product_id, tag_id, tagged_by, note)
SELECT p.id, t.id, 'system', 'default sourcing status'
FROM products p
JOIN tags t ON t.code = 'src-need-quote';

-- ── มุมมองรวม ─────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_product_tags AS
SELECT
  p.id AS product_id,
  p.catalog_key,
  p.code,
  p.name,
  p.rmb,
  p.exclusive_flag,
  t.id AS tag_id,
  t.code AS tag_code,
  t.label_th AS tag_th,
  t.label_en AS tag_en,
  t.color AS tag_color,
  g.code AS group_code,
  g.label_th AS group_th,
  pt.tagged_by,
  pt.note AS tag_note,
  pt.created_at AS tagged_at
FROM product_tags pt
JOIN products p ON p.id = pt.product_id
JOIN tags t ON t.id = pt.tag_id
LEFT JOIN tag_groups g ON g.id = t.tag_group_id;

CREATE OR REPLACE VIEW v_product_tag_summary AS
SELECT
  p.id AS product_id,
  p.catalog_key,
  p.code,
  p.name,
  COUNT(pt.tag_id) AS tag_count,
  GROUP_CONCAT(t.code ORDER BY g.sort_order, t.sort_order SEPARATOR ',') AS tag_codes,
  GROUP_CONCAT(t.label_th ORDER BY g.sort_order, t.sort_order SEPARATOR ' · ') AS tags_th
FROM products p
LEFT JOIN product_tags pt ON pt.product_id = p.id
LEFT JOIN tags t ON t.id = pt.tag_id
LEFT JOIN tag_groups g ON g.id = t.tag_group_id
GROUP BY p.id, p.catalog_key, p.code, p.name;
