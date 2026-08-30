#!/usr/bin/env python3
"""
Create database `smartgift` from `price_db`, then normalize joins to use integer IDs.

Changes:
  - DB name: price_db → smartgift
  - catalogs.id + products.catalog_id
  - smartgift_group (id)
  - smartgift_type.id + type_code + group_id (INT FK)
  - smartgift_offer.id (keep code)
  - smartgift_model.id + type_id/group_id (INT FK); offer_codes → smartgift_model_offer
  - smartgift_price.offer_id (INT FK)
  - product_offer_link (products ↔ offers by code)
  - quotation_items.offer_id
  - views rebuilt on ID joins
"""
from __future__ import annotations

import json
import sys

import pymysql

SRC = "price_db"
DST = "smartgift"

CFG = dict(
    host="127.0.0.1",
    port=3310,
    user="root",
    password="rootpass",
    charset="utf8mb4",
    autocommit=False,
)

# Base tables to clone (views rebuilt later)
TABLES = [
    "catalogs",
    "products",
    "suppliers",
    "china_sourcing",
    "china_request_checklist",
    "tag_groups",
    "tags",
    "product_tags",
    "roles",
    "permissions",
    "role_permissions",
    "employees",
    "customers",
    "customer_contacts",
    "quotations",
    "quotation_items",
    "quotation_status_logs",
    "smartgift_export_run",
    "smartgift_type",
    "smartgift_offer",
    "smartgift_model",
    "smartgift_price",
]


def q(cur, sql: str, args=None):
    cur.execute(sql, args or ())


def main() -> int:
    conn = pymysql.connect(**CFG)
    cur = conn.cursor()

    print(f"==> CREATE DATABASE {DST}")
    q(cur, f"DROP DATABASE IF EXISTS `{DST}`")
    q(
        cur,
        f"CREATE DATABASE `{DST}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
    )
    conn.commit()

    # Clone table structures + data
    for t in TABLES:
        print(f"  clone {t}")
        q(cur, f"CREATE TABLE `{DST}`.`{t}` LIKE `{SRC}`.`{t}`")
        q(cur, f"INSERT INTO `{DST}`.`{t}` SELECT * FROM `{SRC}`.`{t}`")
    conn.commit()

    q(cur, f"USE `{DST}`")

    # ── catalogs.id + products.catalog_id ───────────────────────────────
    print("==> catalogs / products numeric IDs")
    q(cur, "ALTER TABLE catalogs ADD COLUMN id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE FIRST")
    # Make id the logical PK while keeping catalog_key unique
    q(cur, "ALTER TABLE catalogs DROP PRIMARY KEY, ADD PRIMARY KEY (id), ADD UNIQUE KEY uk_catalog_key (catalog_key)")
    q(cur, "ALTER TABLE products ADD COLUMN catalog_id INT UNSIGNED NULL AFTER id")
    q(
        cur,
        """
        UPDATE products p
        JOIN catalogs c ON c.catalog_key = p.catalog_key
        SET p.catalog_id = c.id
        """,
    )
    # CREATE TABLE LIKE may omit FKs — drop only if present
    q(
        cur,
        """
        SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME='products' AND CONSTRAINT_TYPE='FOREIGN KEY'
        """,
        (DST,),
    )
    for (cname,) in cur.fetchall():
        q(cur, f"ALTER TABLE products DROP FOREIGN KEY `{cname}`")
    q(
        cur,
        """
        ALTER TABLE products
          ADD CONSTRAINT fk_products_catalog_id
            FOREIGN KEY (catalog_id) REFERENCES catalogs (id)
            ON UPDATE CASCADE ON DELETE CASCADE
        """,
    )

    # ── smartgift_group ─────────────────────────────────────────────────
    print("==> smartgift_group")
    q(
        cur,
        """
        CREATE TABLE smartgift_group (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          group_code VARCHAR(64) NOT NULL,
          name_th VARCHAR(255) NULL,
          name_en VARCHAR(255) NULL,
          sort_order INT NOT NULL DEFAULT 0,
          UNIQUE KEY uk_group_code (group_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
    )
    q(
        cur,
        """
        INSERT INTO smartgift_group (group_code, name_th, name_en, sort_order)
        SELECT g.group_code,
               g.group_code,
               g.group_code,
               ROW_NUMBER() OVER (ORDER BY g.group_code) * 10
        FROM (
          SELECT DISTINCT group_id AS group_code
          FROM smartgift_type
          WHERE group_id IS NOT NULL AND group_id <> ''
          UNION
          SELECT DISTINCT group_id
          FROM smartgift_model
          WHERE group_id IS NOT NULL AND group_id <> ''
        ) g
        """,
    )

    # ── smartgift_type: id + type_code + group_id INT ───────────────────
    print("==> smartgift_type IDs")
    q(cur, "ALTER TABLE smartgift_type ADD COLUMN id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE FIRST")
    q(cur, "ALTER TABLE smartgift_type CHANGE type_id type_code VARCHAR(64) NOT NULL")
    q(cur, "ALTER TABLE smartgift_type ADD COLUMN group_code VARCHAR(64) NULL AFTER type_code")
    q(cur, "UPDATE smartgift_type SET group_code = group_id")
    q(cur, "ALTER TABLE smartgift_type DROP PRIMARY KEY, ADD PRIMARY KEY (id)")
    q(cur, "ALTER TABLE smartgift_type ADD UNIQUE KEY uk_type_code (type_code)")
    q(cur, "ALTER TABLE smartgift_type DROP COLUMN group_id")
    q(cur, "ALTER TABLE smartgift_type ADD COLUMN group_id INT UNSIGNED NULL AFTER type_code")
    q(
        cur,
        """
        UPDATE smartgift_type t
        LEFT JOIN smartgift_group g ON g.group_code = t.group_code
        SET t.group_id = g.id
        """,
    )
    q(
        cur,
        """
        ALTER TABLE smartgift_type
          ADD CONSTRAINT fk_type_group
            FOREIGN KEY (group_id) REFERENCES smartgift_group (id)
            ON UPDATE CASCADE ON DELETE SET NULL
        """,
    )

    # ── smartgift_offer: id ─────────────────────────────────────────────
    print("==> smartgift_offer.id")
    q(cur, "ALTER TABLE smartgift_offer ADD COLUMN id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE FIRST")
    q(cur, "ALTER TABLE smartgift_offer DROP PRIMARY KEY, ADD PRIMARY KEY (id), ADD UNIQUE KEY uk_offer_code (code)")

    # ── smartgift_model: id + INT FKs ───────────────────────────────────
    print("==> smartgift_model IDs")
    q(cur, "ALTER TABLE smartgift_model ADD COLUMN id INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE FIRST")
    q(cur, "ALTER TABLE smartgift_model ADD COLUMN type_code VARCHAR(64) NULL AFTER english_name")
    q(cur, "ALTER TABLE smartgift_model ADD COLUMN group_code VARCHAR(64) NULL AFTER type_code")
    q(cur, "UPDATE smartgift_model SET type_code = type_id, group_code = group_id")
    q(cur, "ALTER TABLE smartgift_model DROP PRIMARY KEY, ADD PRIMARY KEY (id)")
    q(cur, "ALTER TABLE smartgift_model ADD UNIQUE KEY uk_sig_hash (sig_hash)")
    q(cur, "ALTER TABLE smartgift_model DROP COLUMN type_id, DROP COLUMN group_id")
    q(cur, "ALTER TABLE smartgift_model ADD COLUMN type_id INT UNSIGNED NULL AFTER english_name")
    q(cur, "ALTER TABLE smartgift_model ADD COLUMN group_id INT UNSIGNED NULL AFTER type_id")
    q(
        cur,
        """
        UPDATE smartgift_model m
        LEFT JOIN smartgift_type t ON t.type_code = m.type_code
        LEFT JOIN smartgift_group g ON g.group_code = COALESCE(m.group_code, t.group_code)
        SET m.type_id = t.id, m.group_id = g.id
        """,
    )
    q(
        cur,
        """
        ALTER TABLE smartgift_model
          ADD KEY idx_model_type (type_id),
          ADD KEY idx_model_group (group_id),
          ADD CONSTRAINT fk_model_type
            FOREIGN KEY (type_id) REFERENCES smartgift_type (id)
            ON UPDATE CASCADE ON DELETE SET NULL,
          ADD CONSTRAINT fk_model_group
            FOREIGN KEY (group_id) REFERENCES smartgift_group (id)
            ON UPDATE CASCADE ON DELETE SET NULL
        """,
    )

    # ── smartgift_model_offer from JSON ─────────────────────────────────
    print("==> smartgift_model_offer")
    q(
        cur,
        """
        CREATE TABLE smartgift_model_offer (
          model_id INT UNSIGNED NOT NULL,
          offer_id INT UNSIGNED NOT NULL,
          sort_order INT NOT NULL DEFAULT 0,
          PRIMARY KEY (model_id, offer_id),
          KEY idx_mo_offer (offer_id),
          CONSTRAINT fk_mo_model FOREIGN KEY (model_id) REFERENCES smartgift_model (id)
            ON UPDATE CASCADE ON DELETE CASCADE,
          CONSTRAINT fk_mo_offer FOREIGN KEY (offer_id) REFERENCES smartgift_offer (id)
            ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
    )

    q(cur, "SELECT id, offer_codes FROM smartgift_model WHERE offer_codes IS NOT NULL")
    rows = cur.fetchall()
    offer_map: dict[str, int] = {}
    q(cur, "SELECT id, code FROM smartgift_offer")
    for oid, code in cur.fetchall():
        offer_map[code] = oid

    insert_mo = []
    missing_codes = set()
    for model_id, offer_codes in rows:
        if offer_codes is None:
            continue
        if isinstance(offer_codes, (bytes, bytearray)):
            offer_codes = offer_codes.decode("utf-8")
        if isinstance(offer_codes, str):
            codes = json.loads(offer_codes)
        else:
            codes = offer_codes
        if not isinstance(codes, list):
            continue
        for i, code in enumerate(codes):
            if not code:
                continue
            oid = offer_map.get(str(code))
            if oid is None:
                missing_codes.add(str(code))
                continue
            insert_mo.append((model_id, oid, i))

    if insert_mo:
        cur.executemany(
            "INSERT IGNORE INTO smartgift_model_offer (model_id, offer_id, sort_order) VALUES (%s,%s,%s)",
            insert_mo,
        )
    print(f"  model_offer links: {len(insert_mo)}  missing offer codes: {len(missing_codes)}")
    if missing_codes:
        print(f"  sample missing: {list(sorted(missing_codes))[:10]}")

    # Keep offer_codes JSON for audit but joins use junction table

    # ── smartgift_price.offer_id ────────────────────────────────────────
    print("==> smartgift_price.offer_id")
    q(cur, "ALTER TABLE smartgift_price ADD COLUMN offer_id INT UNSIGNED NULL AFTER id")
    q(
        cur,
        """
        UPDATE smartgift_price p
        JOIN smartgift_offer o ON o.code = p.offer_code
        SET p.offer_id = o.id
        """,
    )
    q(cur, "ALTER TABLE smartgift_price MODIFY offer_id INT UNSIGNED NOT NULL")
    q(
        cur,
        """
        ALTER TABLE smartgift_price
          ADD KEY idx_price_offer_id (offer_id),
          ADD CONSTRAINT fk_price_offer
            FOREIGN KEY (offer_id) REFERENCES smartgift_offer (id)
            ON UPDATE CASCADE ON DELETE CASCADE
        """,
    )

    # ── product_offer_link ──────────────────────────────────────────────
    print("==> product_offer_link")
    q(
        cur,
        """
        CREATE TABLE product_offer_link (
          product_id BIGINT UNSIGNED NOT NULL,
          offer_id INT UNSIGNED NOT NULL,
          match_method ENUM('exact_code') NOT NULL DEFAULT 'exact_code',
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (product_id, offer_id),
          KEY idx_pol_offer (offer_id),
          CONSTRAINT fk_pol_product FOREIGN KEY (product_id) REFERENCES products (id)
            ON UPDATE CASCADE ON DELETE CASCADE,
          CONSTRAINT fk_pol_offer FOREIGN KEY (offer_id) REFERENCES smartgift_offer (id)
            ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
    )
    q(
        cur,
        """
        INSERT IGNORE INTO product_offer_link (product_id, offer_id, match_method)
        SELECT p.id, o.id, 'exact_code'
        FROM products p
        JOIN smartgift_offer o ON o.code = p.code
        """,
    )
    q(cur, "SELECT COUNT(*) FROM product_offer_link")
    print(f"  product-offer links: {cur.fetchone()[0]}")

    # ── quotation_items.offer_id ────────────────────────────────────────
    print("==> quotation_items.offer_id")
    q(cur, "ALTER TABLE quotation_items ADD COLUMN offer_id INT UNSIGNED NULL AFTER line_no")
    q(
        cur,
        """
        UPDATE quotation_items qi
        JOIN smartgift_offer o ON o.code = qi.offer_code
        SET qi.offer_id = o.id
        WHERE qi.offer_code IS NOT NULL
        """,
    )
    q(
        cur,
        """
        ALTER TABLE quotation_items
          ADD KEY idx_qi_offer_id (offer_id),
          ADD CONSTRAINT fk_qi_offer
            FOREIGN KEY (offer_id) REFERENCES smartgift_offer (id)
            ON UPDATE CASCADE ON DELETE SET NULL
        """,
    )

    # ── Views (ID joins) ────────────────────────────────────────────────
    print("==> views")
    q(
        cur,
        """
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
          (
            SELECT MIN(p.unit_price)
            FROM smartgift_price p
            WHERE p.offer_id = o.id AND p.price_missing = 0
          ) AS price_min,
          (
            SELECT MAX(p.unit_price)
            FROM smartgift_price p
            WHERE p.offer_id = o.id AND p.price_missing = 0
          ) AS price_max,
          (
            SELECT MIN(p.unit_price_with_vat)
            FROM smartgift_price p
            WHERE p.offer_id = o.id AND p.price_missing = 0
          ) AS price_vat_min,
          (
            SELECT MAX(p.unit_price_with_vat)
            FROM smartgift_price p
            WHERE p.offer_id = o.id AND p.price_missing = 0
          ) AS price_vat_max,
          (
            SELECT COUNT(*)
            FROM smartgift_price p
            WHERE p.offer_id = o.id AND p.price_missing = 0
          ) AS price_tier_count,
          pol.product_id
        FROM smartgift_model m
        LEFT JOIN smartgift_type t ON t.id = m.type_id
        LEFT JOIN smartgift_group g ON g.id = COALESCE(m.group_id, t.group_id)
        LEFT JOIN smartgift_model_offer mo ON mo.model_id = m.id
        LEFT JOIN smartgift_offer o ON o.id = mo.offer_id
        LEFT JOIN product_offer_link pol ON pol.offer_id = o.id
        """,
    )
    q(
        cur,
        """
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
        GROUP BY type_group, type_id, type_code, type_th, type_en
        """,
    )
    q(
        cur,
        """
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
        GROUP BY type_group, group_id
        """,
    )
    q(
        cur,
        """
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
          (
            SELECT MIN(sp.unit_price)
            FROM smartgift_price sp
            WHERE sp.offer_id = o.id AND sp.price_missing = 0
          ) AS price_min,
          (
            SELECT MAX(sp.unit_price)
            FROM smartgift_price sp
            WHERE sp.offer_id = o.id AND sp.price_missing = 0
          ) AS price_max
        FROM product_offer_link pol
        JOIN products p ON p.id = pol.product_id
        JOIN smartgift_offer o ON o.id = pol.offer_id
        """,
    )

    # Recreate other useful views from source if present
    for view_sql in [
        """
        CREATE OR REPLACE VIEW v_product_sourcing AS
        SELECT
          p.id AS product_id,
          p.catalog_id,
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
        LEFT JOIN suppliers s ON s.id = cs.supplier_id
        """,
        """
        CREATE OR REPLACE VIEW v_product_tags AS
        SELECT
          p.id AS product_id,
          p.catalog_id,
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
        LEFT JOIN tag_groups g ON g.id = t.tag_group_id
        """,
        """
        CREATE OR REPLACE VIEW v_product_tag_summary AS
        SELECT
          p.id AS product_id,
          p.code,
          p.name,
          GROUP_CONCAT(DISTINCT t.code ORDER BY t.code SEPARATOR ',') AS tag_codes,
          COUNT(DISTINCT t.id) AS tag_count
        FROM products p
        LEFT JOIN product_tags pt ON pt.product_id = p.id
        LEFT JOIN tags t ON t.id = pt.tag_id
        GROUP BY p.id, p.code, p.name
        """,
        """
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
        WHERE e.is_active = 1 AND r.is_active = 1
        """,
        """
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
        JOIN roles r ON r.id = e.role_id
        """,
    ]:
        try:
            q(cur, view_sql)
        except Exception as e:  # noqa: BLE001
            print(f"  view warn: {e}")

    conn.commit()

    # ── Verify ──────────────────────────────────────────────────────────
    print("==> verify")
    checks = [
        "SELECT COUNT(*) FROM smartgift_group",
        "SELECT COUNT(*) FROM smartgift_type",
        "SELECT COUNT(*) FROM smartgift_offer",
        "SELECT COUNT(*) FROM smartgift_model",
        "SELECT COUNT(*) FROM smartgift_model_offer",
        "SELECT COUNT(*) FROM smartgift_price",
        "SELECT COUNT(*) FROM product_offer_link",
        "SELECT COUNT(*) FROM products WHERE catalog_id IS NULL",
        "SELECT COUNT(*) FROM smartgift_price WHERE offer_id IS NULL",
        "SELECT COUNT(*) FROM v_smartgift_report",
        "SELECT COUNT(*) FROM v_product_offer",
    ]
    for sql in checks:
        q(cur, sql)
        print(f"  {sql} => {cur.fetchone()[0]}")

    # Sample ID join
    q(
        cur,
        """
        SELECT m.id, m.display_name, o.id, o.code, t.id, t.type_code, g.group_code
        FROM smartgift_model m
        JOIN smartgift_model_offer mo ON mo.model_id = m.id
        JOIN smartgift_offer o ON o.id = mo.offer_id
        LEFT JOIN smartgift_type t ON t.id = m.type_id
        LEFT JOIN smartgift_group g ON g.id = m.group_id
        LIMIT 5
        """,
    )
    print("  sample joins:", cur.fetchall())

    cur.close()
    conn.close()
    print("DONE: database `smartgift` ready (price_db left untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
