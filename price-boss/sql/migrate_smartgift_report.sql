-- SmartGift joined report (ID-centric)
-- Applied by scripts/migrate_to_smartgift_db.py
USE smartgift;
SET NAMES utf8mb4;

CREATE OR REPLACE VIEW v_smartgift_report AS
SELECT
  g.id AS group_id,
  g.group_code AS type_group,
  t.id AS type_id,
  t.type_code,
  t.name_th AS type_th,
  t.name_en AS type_en,
  m.id AS model_id,
  m.sig_hash,
  m.display_name AS model_name,
  m.english_name AS model_name_en,
  m.status AS model_status,
  m.price_source,
  o.id AS offer_id,
  o.code AS offer_code,
  o.name_th AS offer_th,
  o.name_en AS offer_en,
  o.offer_kind,
  o.status AS offer_status,
  o.branding,
  o.origin,
  o.rmb AS catalog_rmb,
  o.image AS offer_image,
  (SELECT MIN(p.unit_price) FROM smartgift_price p WHERE p.offer_id = o.id AND p.price_missing = 0) AS price_min,
  (SELECT MAX(p.unit_price) FROM smartgift_price p WHERE p.offer_id = o.id AND p.price_missing = 0) AS price_max,
  (SELECT MIN(p.unit_price_with_vat) FROM smartgift_price p WHERE p.offer_id = o.id AND p.price_missing = 0) AS price_vat_min,
  (SELECT MAX(p.unit_price_with_vat) FROM smartgift_price p WHERE p.offer_id = o.id AND p.price_missing = 0) AS price_vat_max,
  (SELECT COUNT(*) FROM smartgift_price p WHERE p.offer_id = o.id AND p.price_missing = 0) AS price_tier_count,
  pol.product_id
FROM smartgift_model m
LEFT JOIN smartgift_type t ON t.id = m.type_id
LEFT JOIN smartgift_group g ON g.id = COALESCE(m.group_id, t.group_id)
LEFT JOIN smartgift_model_offer mo ON mo.model_id = m.id
LEFT JOIN smartgift_offer o ON o.id = mo.offer_id
LEFT JOIN product_offer_link pol ON pol.offer_id = o.id;

CREATE OR REPLACE VIEW v_smartgift_report_by_type AS
SELECT
  COALESCE(type_group, '(ไม่มีกลุ่ม)') AS type_group,
  type_id,
  COALESCE(type_code, '(ไม่มีประเภท)') AS type_code,
  COALESCE(type_th, type_en, type_code, '(ไม่มีชื่อ)') AS type_label,
  COUNT(DISTINCT model_id) AS model_count,
  COUNT(DISTINCT offer_id) AS offer_count,
  SUM(CASE WHEN price_tier_count > 0 THEN 1 ELSE 0 END) AS offers_with_price,
  MIN(price_min) AS price_min,
  MAX(price_max) AS price_max
FROM v_smartgift_report
GROUP BY type_group, type_id, type_code, type_th, type_en;

CREATE OR REPLACE VIEW v_smartgift_report_by_group AS
SELECT
  COALESCE(type_group, '(ไม่มีกลุ่ม)') AS type_group,
  group_id,
  COUNT(DISTINCT type_id) AS type_count,
  COUNT(DISTINCT model_id) AS model_count,
  COUNT(DISTINCT offer_id) AS offer_count,
  SUM(CASE WHEN price_tier_count > 0 THEN 1 ELSE 0 END) AS offers_with_price,
  MIN(price_min) AS price_min,
  MAX(price_max) AS price_max
FROM v_smartgift_report
GROUP BY type_group, group_id;

CREATE OR REPLACE VIEW v_product_offer AS
SELECT
  p.id AS product_id,
  p.catalog_id,
  p.catalog_key,
  p.code AS product_code,
  p.name AS product_name,
  p.rmb AS catalog_rmb,
  o.id AS offer_id,
  o.code AS offer_code,
  o.name_th AS offer_th,
  o.name_en AS offer_en,
  o.offer_kind,
  o.status AS offer_status,
  o.rmb AS offer_rmb,
  (SELECT MIN(sp.unit_price) FROM smartgift_price sp WHERE sp.offer_id = o.id AND sp.price_missing = 0) AS price_min,
  (SELECT MAX(sp.unit_price) FROM smartgift_price sp WHERE sp.offer_id = o.id AND sp.price_missing = 0) AS price_max
FROM product_offer_link pol
JOIN products p ON p.id = pol.product_id
JOIN smartgift_offer o ON o.id = pol.offer_id;
