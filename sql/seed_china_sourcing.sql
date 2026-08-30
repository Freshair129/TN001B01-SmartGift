USE price_db;
SET NAMES utf8mb4;

INSERT INTO china_sourcing (
  product_id,
  supplier_id,
  status,
  currency,
  carton_qty,
  carton_l_cm,
  carton_w_cm,
  carton_h_cm
)
SELECT
  p.id,
  NULL,
  "draft",
  "CNY",
  p.upc,
  p.dim_l,
  p.dim_w,
  p.dim_h
FROM products p
LEFT JOIN china_sourcing cs
  ON cs.product_id = p.id AND cs.supplier_id IS NULL
WHERE cs.id IS NULL;

SELECT COUNT(*) AS sourcing_rows FROM china_sourcing;
SELECT status, COUNT(*) AS n FROM china_sourcing GROUP BY status;
SELECT
  cs.id,
  cs.product_id,
  p.catalog_key,
  p.code,
  LEFT(p.name, 40) AS name,
  cs.status,
  cs.carton_qty,
  cs.carton_l_cm,
  cs.carton_w_cm,
  cs.carton_h_cm
FROM china_sourcing cs
JOIN products p ON p.id = cs.product_id
ORDER BY cs.id
LIMIT 5;