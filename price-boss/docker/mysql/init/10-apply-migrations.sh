#!/bin/bash
# Runs once on first MySQL data volume init.
set -euo pipefail

ROOT_PASS="${MYSQL_ROOT_PASSWORD:-rootpass}"
MYSQL=(mysql -uroot -p"${ROOT_PASS}" --default-character-set=utf8mb4)

echo "[price-boss] applying schema + migrations → smartgift"

apply() {
  local file="$1"
  local soft="${2:-0}"
  if [[ ! -f "$file" ]]; then
    echo "[price-boss] skip missing $file"
    return 0
  fi
  echo "[price-boss] → $(basename "$file")"
  if sed -e 's/USE price_db;/USE smartgift;/Ig' \
         -e 's/USE `price_db`;/USE `smartgift`;/Ig' \
         "$file" | "${MYSQL[@]}"; then
    return 0
  fi
  if [[ "$soft" == "1" ]]; then
    echo "[price-boss] WARN: $(basename "$file") failed (continued)"
    return 0
  fi
  return 1
}

apply /migrations/schema.sql
apply /migrations/migrate_crm_auth_quote.sql
apply /migrations/migrate_product_tags.sql 1
apply /migrations/migrate_china_sourcing.sql 1
apply /migrations/migrate_sales_command.sql
# pricelist views need smartgift_* tables — soft until import
apply /migrations/migrate_smartgift_report.sql 1
apply /migrations/fix_checklist_th.sql 1

"${MYSQL[@]}" smartgift <<'SQL'
SET NAMES utf8mb4;

INSERT INTO sales_revenue_source (source_code, name_th, name_en, color_hex, sort_order)
VALUES
  ('anchor', 'Anchor accounts', 'Anchor accounts', '#0F766E', 10),
  ('pending_quote', 'Quote ค้าง', 'Pending quotes', '#CA8A04', 20),
  ('winback', 'Win-back', 'Win-back', '#C2410C', 30),
  ('inbound_other', 'อื่น ๆ / inbound', 'Other / inbound', '#64748B', 40)
ON DUPLICATE KEY UPDATE name_th=VALUES(name_th), color_hex=VALUES(color_hex);

INSERT INTO sales_customer_tier (tier_code, name_th, sort_order) VALUES
  ('P1', 'ผู้มุ่งหวัง P1', 10),
  ('A', 'Tier A', 20),
  ('B', 'Tier B', 30),
  ('C', 'Tier C', 40),
  ('WINBACK', 'Win-back', 50)
ON DUPLICATE KEY UPDATE name_th=VALUES(name_th);

INSERT INTO sales_kpi_def (kpi_code, name_th, unit, direction, sort_order) VALUES
  ('billing_pre_vat', 'ยอดวางบิล pre-VAT', 'THB', 'maximize', 10),
  ('new_quotes', 'Quote ใหม่', 'count', 'maximize', 20),
  ('winback_contacted', 'Win-back ติดต่อครบ', 'count', 'exact', 30),
  ('winback_converted', 'Win-back กลับมาซื้อ/ขอ quote', 'count', 'maximize', 40),
  ('call_list_round1', 'Call list คลีน 1 โทรครบ', 'count', 'exact', 50),
  ('stale_quote_7d', 'Quote เกิน 7 วันไม่มี follow-up', 'count', 'minimize', 60),
  ('sku_price_approved', 'SKU ราคา approved', 'count', 'maximize', 70)
ON DUPLICATE KEY UPDATE name_th=VALUES(name_th);

INSERT INTO sales_period (period_code, label_th, year_num, month_num, quota_pre_vat, is_current, note)
VALUES ('2026-08', 'สิงหาคม 2026', 2026, 8, 873000, 1, 'docker compose seed')
ON DUPLICATE KEY UPDATE quota_pre_vat=VALUES(quota_pre_vat), is_current=1, note=VALUES(note);

SET @pid := (SELECT id FROM sales_period WHERE period_code='2026-08' LIMIT 1);
DELETE FROM sales_period_quota_split WHERE period_id=@pid;
INSERT INTO sales_period_quota_split (period_id, source_id, amount, pct)
SELECT @pid, s.id, x.amount, x.pct FROM (
  SELECT 'anchor' c, 400000 amount, 46.0 pct UNION ALL
  SELECT 'pending_quote', 250000, 29.0 UNION ALL
  SELECT 'winback', 150000, 17.0 UNION ALL
  SELECT 'inbound_other', 73000, 8.0
) x JOIN sales_revenue_source s ON s.source_code=x.c;
SQL

echo "[price-boss] MySQL init done"
