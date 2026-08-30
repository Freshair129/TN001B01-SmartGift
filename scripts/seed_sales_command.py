#!/usr/bin/env python3
"""Apply Sales Command schema + seed Aug 2026 Quota & Plan from dashboard screenshot."""
from __future__ import annotations

import pymysql

CFG = dict(
    host="127.0.0.1",
    port=3310,
    user="root",
    password="rootpass",
    database="smartgift",
    charset="utf8mb4",
    autocommit=True,
)


def col_exists(cur, table: str, col: str) -> bool:
    cur.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s
        """,
        ("smartgift", table, col),
    )
    return cur.fetchone()[0] > 0


def main() -> None:
    conn = pymysql.connect(**CFG)
    cur = conn.cursor()

    stmts = [
        """
        CREATE TABLE IF NOT EXISTS sales_period (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          period_code VARCHAR(16) NOT NULL,
          label_th VARCHAR(64) NOT NULL,
          year_num SMALLINT NOT NULL,
          month_num TINYINT NOT NULL,
          quota_pre_vat DECIMAL(14,2) NOT NULL DEFAULT 0,
          is_current TINYINT(1) NOT NULL DEFAULT 0,
          note VARCHAR(512) NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_period_code (period_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_revenue_source (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          source_code VARCHAR(64) NOT NULL,
          name_th VARCHAR(128) NOT NULL,
          name_en VARCHAR(128) NULL,
          color_hex CHAR(7) NULL,
          sort_order INT NOT NULL DEFAULT 0,
          UNIQUE KEY uk_source_code (source_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_period_quota_split (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          period_id INT UNSIGNED NOT NULL,
          source_id INT UNSIGNED NOT NULL,
          amount DECIMAL(14,2) NOT NULL DEFAULT 0,
          pct DECIMAL(6,2) NULL,
          UNIQUE KEY uk_period_source (period_id, source_id),
          CONSTRAINT fk_pqs_period FOREIGN KEY (period_id) REFERENCES sales_period (id)
            ON UPDATE CASCADE ON DELETE CASCADE,
          CONSTRAINT fk_pqs_source FOREIGN KEY (source_id) REFERENCES sales_revenue_source (id)
            ON UPDATE CASCADE ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_kpi_def (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          kpi_code VARCHAR(64) NOT NULL,
          name_th VARCHAR(255) NOT NULL,
          unit VARCHAR(32) NULL,
          direction ENUM('maximize','minimize','exact') NOT NULL DEFAULT 'maximize',
          sort_order INT NOT NULL DEFAULT 0,
          UNIQUE KEY uk_kpi_code (kpi_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_period_kpi (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          period_id INT UNSIGNED NOT NULL,
          kpi_id INT UNSIGNED NOT NULL,
          target_value DECIMAL(14,2) NULL,
          target_op ENUM('eq','gte','lte') NOT NULL DEFAULT 'eq',
          actual_value DECIMAL(14,2) NULL,
          actual_note VARCHAR(255) NULL,
          measure_note VARCHAR(128) NULL,
          UNIQUE KEY uk_period_kpi (period_id, kpi_id),
          CONSTRAINT fk_spk_period FOREIGN KEY (period_id) REFERENCES sales_period (id)
            ON UPDATE CASCADE ON DELETE CASCADE,
          CONSTRAINT fk_spk_kpi FOREIGN KEY (kpi_id) REFERENCES sales_kpi_def (id)
            ON UPDATE CASCADE ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_week_plan (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          period_id INT UNSIGNED NOT NULL,
          week_no TINYINT NOT NULL,
          theme_th VARCHAR(128) NOT NULL,
          date_range VARCHAR(64) NULL,
          revenue_goal DECIMAL(14,2) NULL,
          sort_order INT NOT NULL DEFAULT 0,
          UNIQUE KEY uk_period_week (period_id, week_no),
          CONSTRAINT fk_swp_period FOREIGN KEY (period_id) REFERENCES sales_period (id)
            ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_week_task (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          week_plan_id INT UNSIGNED NOT NULL,
          task_th VARCHAR(512) NOT NULL,
          sort_order INT NOT NULL DEFAULT 0,
          is_done TINYINT(1) NOT NULL DEFAULT 0,
          CONSTRAINT fk_swt_week FOREIGN KEY (week_plan_id) REFERENCES sales_week_plan (id)
            ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS sales_customer_tier (
          id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          tier_code VARCHAR(32) NOT NULL,
          name_th VARCHAR(64) NOT NULL,
          sort_order INT NOT NULL DEFAULT 0,
          UNIQUE KEY uk_tier_code (tier_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
    ]
    for s in stmts:
        cur.execute(s)

    # customers extras (MySQL 8 may not support ADD IF NOT EXISTS)
    alters = [
        ("tier_id", "ADD COLUMN tier_id INT UNSIGNED NULL AFTER id"),
        ("is_anchor", "ADD COLUMN is_anchor TINYINT(1) NOT NULL DEFAULT 0 AFTER customer_type"),
        ("is_winback", "ADD COLUMN is_winback TINYINT(1) NOT NULL DEFAULT 0 AFTER is_anchor"),
    ]
    for col, ddl in alters:
        if not col_exists(cur, "customers", col):
            cur.execute(f"ALTER TABLE customers {ddl}")

    # Seed sources
    sources = [
        ("anchor", "Anchor accounts", "Anchor accounts", "#0F766E", 10),
        ("pending_quote", "Quote ค้าง", "Pending quotes", "#CA8A04", 20),
        ("winback", "Win-back", "Win-back", "#C2410C", 30),
        ("inbound_other", "อื่น ๆ / inbound", "Other / inbound", "#64748B", 40),
    ]
    cur.executemany(
        """
        INSERT INTO sales_revenue_source (source_code, name_th, name_en, color_hex, sort_order)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE name_th=VALUES(name_th), color_hex=VALUES(color_hex), sort_order=VALUES(sort_order)
        """,
        sources,
    )

    tiers = [
        ("P1", "ผู้มุ่งหวัง P1", 10),
        ("A", "Tier A", 20),
        ("B", "Tier B", 30),
        ("C", "Tier C", 40),
        ("WINBACK", "Win-back", 50),
    ]
    cur.executemany(
        """
        INSERT INTO sales_customer_tier (tier_code, name_th, sort_order)
        VALUES (%s,%s,%s)
        ON DUPLICATE KEY UPDATE name_th=VALUES(name_th), sort_order=VALUES(sort_order)
        """,
        tiers,
    )

    kpis = [
        ("billing_pre_vat", "ยอดวางบิล pre-VAT", "THB", "maximize", 10),
        ("new_quotes", "Quote ใหม่", "count", "maximize", 20),
        ("winback_contacted", "Win-back ติดต่อครบ", "count", "exact", 30),
        ("winback_converted", "Win-back กลับมาซื้อ/ขอ quote", "count", "maximize", 40),
        ("call_list_round1", "Call list คลีน 1 โทรครบ", "count", "exact", 50),
        ("stale_quote_7d", "Quote เกิน 7 วันไม่มี follow-up", "count", "minimize", 60),
        ("sku_price_approved", "SKU ราคา approved", "count", "maximize", 70),
    ]
    cur.executemany(
        """
        INSERT INTO sales_kpi_def (kpi_code, name_th, unit, direction, sort_order)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE name_th=VALUES(name_th), unit=VALUES(unit),
          direction=VALUES(direction), sort_order=VALUES(sort_order)
        """,
        kpis,
    )

    # Period Aug 2026
    cur.execute(
        """
        INSERT INTO sales_period (period_code, label_th, year_num, month_num, quota_pre_vat, is_current, note)
        VALUES ('2026-08', 'สิงหาคม 2026', 2026, 8, 873000, 1, 'จาก Sales Command dashboard screenshot')
        ON DUPLICATE KEY UPDATE label_th=VALUES(label_th), quota_pre_vat=VALUES(quota_pre_vat),
          is_current=VALUES(is_current), note=VALUES(note)
        """
    )
    cur.execute("UPDATE sales_period SET is_current=0 WHERE period_code <> '2026-08'")
    cur.execute("SELECT id FROM sales_period WHERE period_code='2026-08'")
    period_id = cur.fetchone()[0]

    # Clear dependent for reseed
    cur.execute("DELETE FROM sales_period_quota_split WHERE period_id=%s", (period_id,))
    cur.execute("DELETE FROM sales_period_kpi WHERE period_id=%s", (period_id,))
    cur.execute(
        """
        DELETE t FROM sales_week_task t
        JOIN sales_week_plan w ON w.id = t.week_plan_id
        WHERE w.period_id=%s
        """,
        (period_id,),
    )
    cur.execute("DELETE FROM sales_week_plan WHERE period_id=%s", (period_id,))

    cur.execute("SELECT id, source_code FROM sales_revenue_source")
    src = {code: sid for sid, code in cur.fetchall()}
    splits = [
        (period_id, src["anchor"], 400000, 46.0),
        (period_id, src["pending_quote"], 250000, 29.0),
        (period_id, src["winback"], 150000, 17.0),
        (period_id, src["inbound_other"], 73000, 8.0),
    ]
    cur.executemany(
        """
        INSERT INTO sales_period_quota_split (period_id, source_id, amount, pct)
        VALUES (%s,%s,%s,%s)
        """,
        splits,
    )

    cur.execute("SELECT id, kpi_code FROM sales_kpi_def")
    kpi = {code: kid for kid, code in cur.fetchall()}
    period_kpis = [
        (period_id, kpi["billing_pre_vat"], 873000, "eq", None, None, "วัดทุกศุกร์"),
        (period_id, kpi["new_quotes"], 20, "gte", None, None, "วัดทุกศุกร์"),
        (period_id, kpi["winback_contacted"], 43, "eq", 43, "43/43", "วัดทุกศุกร์"),
        (period_id, kpi["winback_converted"], 5, "gte", None, None, "วัดทุกศุกร์"),
        (period_id, kpi["call_list_round1"], 39, "eq", 39, "39/39", "วัดทุกศุกร์"),
        (period_id, kpi["stale_quote_7d"], 0, "eq", None, None, "วัดทุกศุกร์"),
        (period_id, kpi["sku_price_approved"], 30, "gte", None, None, "วัดทุกศุกร์"),
    ]
    cur.executemany(
        """
        INSERT INTO sales_period_kpi
          (period_id, kpi_id, target_value, target_op, actual_value, actual_note, measure_note)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        period_kpis,
    )

    weeks = [
        (1, "เปิดเดือน", "1–7 ส.ค.", 200000, [
            "Refresh data + audit list",
            "Follow-up Top 10 Quote ค้าง",
            "Win-back wave 1",
        ]),
        (2, "คุมจังหวะ", "8–14 ส.ค.", 450000, [
            "Win-back wave 2",
            "Call list รอบ 2",
            "ติดต่อโรงไฟฟ้า / องค์กรใหญ่ (เช่น กฟผ.)",
        ]),
        (3, "เตรียม Q4", "15–21 ส.ค.", 650000, [
            "เจรจา / ปิดดีลค้าง",
            "Price approval ≥ 15 SKU",
            "อัปเดต battle card คู่แข่ง",
        ]),
        (4, "ปิดเดือน", "22–31 ส.ค.", 873000, [
            "เร่งวางบิล / เก็บเงิน",
            "ทบทวน variance เป้า vs จริง",
            "อัปเดต scoreboard ทีม",
        ]),
    ]
    for week_no, theme, drange, goal, tasks in weeks:
        cur.execute(
            """
            INSERT INTO sales_week_plan (period_id, week_no, theme_th, date_range, revenue_goal, sort_order)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (period_id, week_no, theme, drange, goal, week_no * 10),
        )
        wid = cur.lastrowid
        cur.executemany(
            """
            INSERT INTO sales_week_task (week_plan_id, task_th, sort_order)
            VALUES (%s,%s,%s)
            """,
            [(wid, t, i * 10) for i, t in enumerate(tasks, 1)],
        )

    # Views
    cur.execute(
        """
        CREATE OR REPLACE VIEW v_sales_quota_split AS
        SELECT
          p.id AS period_id, p.period_code, p.label_th AS period_label, p.quota_pre_vat,
          s.id AS source_id, s.source_code, s.name_th AS source_th, s.color_hex,
          q.amount,
          COALESCE(q.pct, ROUND(100 * q.amount / NULLIF(p.quota_pre_vat, 0), 1)) AS pct
        FROM sales_period p
        JOIN sales_period_quota_split q ON q.period_id = p.id
        JOIN sales_revenue_source s ON s.id = q.source_id
        """
    )
    cur.execute(
        """
        CREATE OR REPLACE VIEW v_sales_period_kpi AS
        SELECT
          p.id AS period_id, p.period_code, p.label_th AS period_label,
          k.id AS kpi_id, k.kpi_code, k.name_th AS kpi_th, k.unit, k.direction,
          sp.target_value, sp.target_op, sp.actual_value, sp.actual_note, sp.measure_note,
          k.sort_order
        FROM sales_period p
        JOIN sales_period_kpi sp ON sp.period_id = p.id
        JOIN sales_kpi_def k ON k.id = sp.kpi_id
        """
    )
    cur.execute(
        """
        CREATE OR REPLACE VIEW v_sales_week_plan AS
        SELECT
          p.id AS period_id, p.period_code,
          w.id AS week_plan_id, w.week_no, w.theme_th, w.date_range, w.revenue_goal,
          t.id AS task_id, t.task_th, t.sort_order AS task_sort, t.is_done
        FROM sales_period p
        JOIN sales_week_plan w ON w.period_id = p.id
        LEFT JOIN sales_week_task t ON t.week_plan_id = w.id
        """
    )

    print("period_id", period_id)
    cur.execute("SELECT source_th, amount, pct FROM v_sales_quota_split WHERE period_id=%s", (period_id,))
    print("quota", cur.fetchall())
    cur.execute("SELECT kpi_th, target_value, actual_note FROM v_sales_period_kpi WHERE period_id=%s ORDER BY sort_order", (period_id,))
    print("kpis", cur.fetchall())
    cur.execute("SELECT week_no, theme_th, COUNT(task_id) FROM v_sales_week_plan WHERE period_id=%s GROUP BY week_no, theme_th", (period_id,))
    print("weeks", cur.fetchall())
    cur.close()
    conn.close()
    print("DONE sales command seed")


if __name__ == "__main__":
    main()
