#!/usr/bin/env python3
"""Export smartgift schema → web/src/data/schemaCatalog.json for interactive datadict."""
from __future__ import annotations

import json
from pathlib import Path

import pymysql

OUT = Path(__file__).resolve().parents[1] / "web" / "src" / "data" / "schemaCatalog.json"

META = {
    "roles": {
        "domain": "rbac",
        "title_th": "บทบาท",
        "purpose": "กำหนดบทบาท administrator / manager / sale",
    },
    "permissions": {
        "domain": "rbac",
        "title_th": "สิทธิ์",
        "purpose": "สิทธิ์แบบละเอียด แยกตาม module",
    },
    "role_permissions": {
        "domain": "rbac",
        "title_th": "แมปสิทธิ์",
        "purpose": "many-to-many บทบาท ↔ สิทธิ์",
    },
    "employees": {
        "domain": "rbac",
        "title_th": "พนักงาน",
        "purpose": "บัญชีเข้าสู่ระบบ + บทบาท + หัวหน้า",
    },
    "customers": {
        "domain": "crm",
        "title_th": "ลูกค้า",
        "purpose": "ลูกค้าองค์กร + owner_emp_id สำหรับ scope ของ sale",
    },
    "customer_contacts": {
        "domain": "crm",
        "title_th": "ผู้ติดต่อ",
        "purpose": "ผู้ติดต่อหลายคนต่อลูกค้า",
    },
    "quotations": {
        "domain": "quote",
        "title_th": "ใบเสนอราคา (หัว)",
        "purpose": "หัวใบ ยอดรวม สถานะ เงื่อนไขการค้า",
    },
    "quotation_items": {
        "domain": "quote",
        "title_th": "รายการในใบ",
        "purpose": "บรรทัดสินค้า อ้าง offer_id / product_id",
    },
    "quotation_line_breaks": {
        "domain": "quote",
        "title_th": "บันไดราคา",
        "purpose": "qty → unit_price ต่อบรรทัด",
    },
    "quotation_status_logs": {
        "domain": "quote",
        "title_th": "ประวัติสถานะ",
        "purpose": "audit ทุกครั้งที่เปลี่ยนสถานะใบ",
    },
    "catalogs": {
        "domain": "catalog",
        "title_th": "แคตตาล็อก",
        "purpose": "แหล่ง sync จากเว็บ pricing (giftset / powerbank)",
    },
    "products": {
        "domain": "catalog",
        "title_th": "สินค้าแคตตาล็อก",
        "purpose": "SKU จากโรงงาน + catalog_id",
    },
    "suppliers": {
        "domain": "sourcing",
        "title_th": "ซัพพลายเออร์จีน",
        "purpose": "โรงงาน / ผู้ขาย",
    },
    "china_sourcing": {
        "domain": "sourcing",
        "title_th": "ใบขอราคาจีน",
        "purpose": "RFQ ต่อ product (+ supplier) รวม MOQ/ราคา/แบต",
    },
    "china_request_checklist": {
        "domain": "sourcing",
        "title_th": "เช็กลิสต์ถามโรงงาน",
        "purpose": "รายการสิ่งที่ต้องขอจากโรงงาน (อ้างอิง UI)",
    },
    "tag_groups": {
        "domain": "catalog",
        "title_th": "กลุ่มแท็ก",
        "purpose": "จัดกลุ่มแท็กสินค้า",
    },
    "tags": {
        "domain": "catalog",
        "title_th": "แท็ก",
        "purpose": "แท็กสำหรับกรอง/รายงาน",
    },
    "product_tags": {
        "domain": "catalog",
        "title_th": "แท็กสินค้า",
        "purpose": "many-to-many product ↔ tag",
    },
    "product_offer_link": {
        "domain": "pricelist",
        "title_th": "ผูก Product↔Offer",
        "purpose": "จับคู่ catalog product กับ smartgift_offer ด้วย ID",
    },
    "smartgift_group": {
        "domain": "pricelist",
        "title_th": "กลุ่มประเภท",
        "purpose": "care_wellness / home_travel / office / smart_tech",
    },
    "smartgift_type": {
        "domain": "pricelist",
        "title_th": "ประเภทสินค้า",
        "purpose": "taxonomy ของรุ่น (type_code + group_id)",
    },
    "smartgift_model": {
        "domain": "pricelist",
        "title_th": "รุ่น (model)",
        "purpose": "ลายเซ็นรุ่น + type_id; ลิงก์ offer ผ่าน junction",
    },
    "smartgift_offer": {
        "domain": "pricelist",
        "title_th": "Offer / SKU ราคา",
        "purpose": "รหัสสินค้าใน pricelist (code) + id สำหรับ join",
    },
    "smartgift_model_offer": {
        "domain": "pricelist",
        "title_th": "Model↔Offer",
        "purpose": "แทน offer_codes JSON ด้วย ID join",
    },
    "smartgift_price": {
        "domain": "pricelist",
        "title_th": "ขั้นราคา",
        "purpose": "qty_tier / unit_price ผูก offer_id",
    },
    "smartgift_export_run": {
        "domain": "pricelist",
        "title_th": "รอบนำเข้า pricelist",
        "purpose": "เมตาการ export จาก Mac",
    },
    "sales_period": {
        "domain": "sales",
        "title_th": "งวดเป้าขาย",
        "purpose": "เดือนเป้า เช่น 2026-08 + quota_pre_vat",
    },
    "sales_revenue_source": {
        "domain": "sales",
        "title_th": "แหล่งรายได้",
        "purpose": "Anchor / Quote ค้าง / Win-back / inbound",
    },
    "sales_period_quota_split": {
        "domain": "sales",
        "title_th": "แจกเป้าตามแหล่ง",
        "purpose": "amount + % ต่อ period × source",
    },
    "sales_kpi_def": {
        "domain": "sales",
        "title_th": "นิยาม KPI",
        "purpose": "รหัส KPI ที่วัดทุกศุกร์",
    },
    "sales_period_kpi": {
        "domain": "sales",
        "title_th": "KPI รายเดือน",
        "purpose": "เป้า/จริง ต่องวด",
    },
    "sales_week_plan": {
        "domain": "sales",
        "title_th": "แผนรายสัปดาห์",
        "purpose": "W1–W4 theme + เป้าสะสม",
    },
    "sales_week_task": {
        "domain": "sales",
        "title_th": "งานในสัปดาห์",
        "purpose": "task checklist ภายใต้ week_plan",
    },
    "sales_customer_tier": {
        "domain": "sales",
        "title_th": "Tier ลูกค้า",
        "purpose": "P1 / A / B / C / WINBACK",
    },
    "v_smartgift_report": {
        "domain": "view",
        "title_th": "รายงาน join pricelist",
        "purpose": "group→type→model↔offer→price (+product)",
    },
    "v_smartgift_report_by_type": {
        "domain": "view",
        "title_th": "สรุปตามประเภท",
        "purpose": "aggregate จาก v_smartgift_report",
    },
    "v_smartgift_report_by_group": {
        "domain": "view",
        "title_th": "สรุปตามกลุ่ม",
        "purpose": "aggregate ตาม type_group",
    },
    "v_product_offer": {
        "domain": "view",
        "title_th": "Product+Offer",
        "purpose": "catalog ที่ผูก offer พร้อมช่วงราคา",
    },
    "v_product_sourcing": {
        "domain": "view",
        "title_th": "สินค้า+sourcing",
        "purpose": "สถานะ RFQ จีนต่อสินค้า",
    },
    "v_product_tags": {
        "domain": "view",
        "title_th": "สินค้า+แท็ก",
        "purpose": "รายละเอียดแท็กต่อสินค้า",
    },
    "v_product_tag_summary": {
        "domain": "view",
        "title_th": "สรุปแท็ก",
        "purpose": "GROUP_CONCAT tag_codes",
    },
    "v_employee_access": {
        "domain": "view",
        "title_th": "พนักงาน×สิทธิ์",
        "purpose": "ใช้ตรวจ permission ตอน login",
    },
    "v_quotation_summary": {
        "domain": "view",
        "title_th": "สรุปใบเสนอราคา",
        "purpose": "หัวใบ + ลูกค้า + เจ้าของ + จำนวนรายการ",
    },
    "v_sales_quota_split": {
        "domain": "view",
        "title_th": "มุมมองแจกเป้า",
        "purpose": "period + source + amount/%",
    },
    "v_sales_period_kpi": {
        "domain": "view",
        "title_th": "มุมมอง KPI",
        "purpose": "period + kpi def + target/actual",
    },
    "v_sales_week_plan": {
        "domain": "view",
        "title_th": "มุมมองแผนสัปดาห์",
        "purpose": "week + tasks แบบ flatten",
    },
}

DOMAINS = {
    "rbac": {"label": "สิทธิ์ / พนักงาน", "order": 1},
    "crm": {"label": "ลูกค้า", "order": 2},
    "quote": {"label": "ใบเสนอราคา", "order": 3},
    "catalog": {"label": "แคตตาล็อก / แท็ก", "order": 4},
    "pricelist": {"label": "Pricelist SmartGift", "order": 5},
    "sourcing": {"label": "สั่งจีน", "order": 6},
    "sales": {"label": "Sales Command / เป้า", "order": 7},
    "view": {"label": "Views", "order": 8},
}


def main() -> None:
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3310,
        user="root",
        password="rootpass",
        database="smartgift",
        charset="utf8mb4",
    )
    cur = conn.cursor()
    cur.execute(
        """
        SELECT TABLE_NAME, TABLE_TYPE, IFNULL(TABLE_COMMENT,'')
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA='smartgift'
        ORDER BY TABLE_NAME
        """
    )
    tables_raw = cur.fetchall()

    cur.execute(
        """
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY,
               IFNULL(COLUMN_DEFAULT,''), IFNULL(EXTRA,''), IFNULL(COLUMN_COMMENT,''),
               ORDINAL_POSITION
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA='smartgift'
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
    )
    cols = {}
    for t, c, ctype, nullable, key, default, extra, comment, ord_ in cur.fetchall():
        cols.setdefault(t, []).append(
            {
                "name": c,
                "type": ctype,
                "nullable": nullable == "YES",
                "key": key or "",
                "default": None if default == "" and default is not None else default,
                "extra": extra,
                "comment": comment,
                "ordinal": ord_,
            }
        )

    cur.execute(
        """
        SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
               REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA='smartgift' AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY TABLE_NAME, CONSTRAINT_NAME, ORDINAL_POSITION
        """
    )
    fks = {}
    for t, c, cons, rt, rc in cur.fetchall():
        fks.setdefault(t, []).append(
            {
                "constraint": cons,
                "column": c,
                "ref_table": rt,
                "ref_column": rc,
            }
        )

    tables = []
    for name, ttype, comment in tables_raw:
        meta = META.get(name, {})
        domain = meta.get("domain", "other")
        tables.append(
            {
                "name": name,
                "kind": "VIEW" if ttype == "VIEW" else "BASE TABLE",
                "domain": domain,
                "title_th": meta.get("title_th", name),
                "purpose": meta.get("purpose", comment or ""),
                "columns": cols.get(name, []),
                "foreign_keys": fks.get(name, []),
            }
        )

    payload = {
        "database": "smartgift",
        "generated_note": "Exported from live MySQL; regenerate with scripts/export_schema_catalog.py",
        "domains": DOMAINS,
        "tables": tables,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} tables={len(tables)} cols={sum(len(t['columns']) for t in tables)}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
