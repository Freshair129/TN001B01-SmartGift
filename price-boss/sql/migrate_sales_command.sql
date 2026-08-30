-- SmartGift Sales Command: Quota & Plan (+ related sales ops)
USE smartgift;
SET NAMES utf8mb4;

-- Period (เดือนเป้า)
CREATE TABLE IF NOT EXISTS sales_period (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  period_code  VARCHAR(16)  NOT NULL COMMENT 'YYYY-MM',
  label_th     VARCHAR(64)  NOT NULL,
  year_num     SMALLINT NOT NULL,
  month_num    TINYINT NOT NULL,
  quota_pre_vat DECIMAL(14,2) NOT NULL DEFAULT 0,
  is_current   TINYINT(1) NOT NULL DEFAULT 0,
  note         VARCHAR(512) NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_period_code (period_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- แหล่งรายได้ของเป้า (donut)
CREATE TABLE IF NOT EXISTS sales_revenue_source (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  source_code VARCHAR(64) NOT NULL,
  name_th     VARCHAR(128) NOT NULL,
  name_en     VARCHAR(128) NULL,
  color_hex   CHAR(7) NULL,
  sort_order  INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_source_code (source_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sales_period_quota_split (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  period_id   INT UNSIGNED NOT NULL,
  source_id   INT UNSIGNED NOT NULL,
  amount      DECIMAL(14,2) NOT NULL DEFAULT 0,
  pct         DECIMAL(6,2) NULL COMMENT 'เก็บ snapshot %',
  UNIQUE KEY uk_period_source (period_id, source_id),
  CONSTRAINT fk_pqs_period FOREIGN KEY (period_id) REFERENCES sales_period (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_pqs_source FOREIGN KEY (source_id) REFERENCES sales_revenue_source (id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KPI definitions + monthly targets / actuals
CREATE TABLE IF NOT EXISTS sales_kpi_def (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  kpi_code    VARCHAR(64) NOT NULL,
  name_th     VARCHAR(255) NOT NULL,
  unit        VARCHAR(32) NULL COMMENT 'THB / count / ...',
  direction   ENUM('maximize','minimize','exact') NOT NULL DEFAULT 'maximize',
  sort_order  INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_kpi_code (kpi_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sales_period_kpi (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  period_id    INT UNSIGNED NOT NULL,
  kpi_id       INT UNSIGNED NOT NULL,
  target_value DECIMAL(14,2) NULL,
  target_op    ENUM('eq','gte','lte') NOT NULL DEFAULT 'eq',
  actual_value DECIMAL(14,2) NULL,
  actual_note  VARCHAR(255) NULL COMMENT 'เช่น 43/43',
  measure_note VARCHAR(128) NULL COMMENT 'วัดทุกศุกร์',
  UNIQUE KEY uk_period_kpi (period_id, kpi_id),
  CONSTRAINT fk_spk_period FOREIGN KEY (period_id) REFERENCES sales_period (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_spk_kpi FOREIGN KEY (kpi_id) REFERENCES sales_kpi_def (id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Weekly plan
CREATE TABLE IF NOT EXISTS sales_week_plan (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  period_id    INT UNSIGNED NOT NULL,
  week_no      TINYINT NOT NULL COMMENT '1-5',
  theme_th     VARCHAR(128) NOT NULL,
  date_range   VARCHAR(64) NULL,
  revenue_goal DECIMAL(14,2) NULL COMMENT 'เป้าสะสม / ปิดเดือน',
  sort_order   INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_period_week (period_id, week_no),
  CONSTRAINT fk_swp_period FOREIGN KEY (period_id) REFERENCES sales_period (id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sales_week_task (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  week_plan_id INT UNSIGNED NOT NULL,
  task_th      VARCHAR(512) NOT NULL,
  sort_order   INT NOT NULL DEFAULT 0,
  is_done      TINYINT(1) NOT NULL DEFAULT 0,
  CONSTRAINT fk_swt_week FOREIGN KEY (week_plan_id) REFERENCES sales_week_plan (id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customer tier (สำหรับโมดูลลูกค้า & Tiers)
CREATE TABLE IF NOT EXISTS sales_customer_tier (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tier_code  VARCHAR(32) NOT NULL,
  name_th    VARCHAR(64) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_tier_code (tier_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ขยาย customers ให้รองรับ sales command (nullable = ยังไม่ใช้)
-- MySQL 8 ไม่รองรับ ADD COLUMN IF NOT EXISTS — ข้าม error ถ้ามีคอลัมน์แล้ว
SET @db := DATABASE();
SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE customers ADD COLUMN tier_id INT UNSIGNED NULL AFTER id',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA=@db AND TABLE_NAME='customers' AND COLUMN_NAME='tier_id'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE customers ADD COLUMN is_anchor TINYINT(1) NOT NULL DEFAULT 0 AFTER customer_type',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA=@db AND TABLE_NAME='customers' AND COLUMN_NAME='is_anchor'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE customers ADD COLUMN is_winback TINYINT(1) NOT NULL DEFAULT 0 AFTER is_anchor',
    'SELECT 1'
  )
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA=@db AND TABLE_NAME='customers' AND COLUMN_NAME='is_winback'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Views
CREATE OR REPLACE VIEW v_sales_quota_split AS
SELECT
  p.id AS period_id,
  p.period_code,
  p.label_th AS period_label,
  p.quota_pre_vat,
  s.id AS source_id,
  s.source_code,
  s.name_th AS source_th,
  s.color_hex,
  q.amount,
  COALESCE(
    q.pct,
    ROUND(100 * q.amount / NULLIF(p.quota_pre_vat, 0), 1)
  ) AS pct
FROM sales_period p
JOIN sales_period_quota_split q ON q.period_id = p.id
JOIN sales_revenue_source s ON s.id = q.source_id;

CREATE OR REPLACE VIEW v_sales_period_kpi AS
SELECT
  p.id AS period_id,
  p.period_code,
  p.label_th AS period_label,
  k.id AS kpi_id,
  k.kpi_code,
  k.name_th AS kpi_th,
  k.unit,
  k.direction,
  sp.target_value,
  sp.target_op,
  sp.actual_value,
  sp.actual_note,
  sp.measure_note,
  k.sort_order
FROM sales_period p
JOIN sales_period_kpi sp ON sp.period_id = p.id
JOIN sales_kpi_def k ON k.id = sp.kpi_id;

CREATE OR REPLACE VIEW v_sales_week_plan AS
SELECT
  p.id AS period_id,
  p.period_code,
  w.id AS week_plan_id,
  w.week_no,
  w.theme_th,
  w.date_range,
  w.revenue_goal,
  t.id AS task_id,
  t.task_th,
  t.sort_order AS task_sort,
  t.is_done
FROM sales_period p
JOIN sales_week_plan w ON w.period_id = p.id
LEFT JOIN sales_week_task t ON t.week_plan_id = w.id;
