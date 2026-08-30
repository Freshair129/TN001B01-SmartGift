#!/usr/bin/env python3
"""Convert smartgiftpricelist.postgres.sql → MySQL for price_db."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(r"C:\Users\Admin\Downloads\smartgiftpricelist.postgres.sql")
OUT = Path(r"D:\price_boss\sql\smartgiftpricelist.mysql.sql")

MYSQL_DDL = """
CREATE TABLE smartgift_export_run (
  run_id          VARCHAR(64)   NOT NULL PRIMARY KEY,
  exported_at     VARCHAR(64)   NOT NULL,
  source_path     VARCHAR(1024) NOT NULL,
  commercial_skus INT NOT NULL,
  offers          INT NOT NULL,
  models          INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE smartgift_type (
  type_id    VARCHAR(64)  NOT NULL PRIMARY KEY,
  group_id   VARCHAR(64)  NULL,
  name_th    VARCHAR(255) NULL,
  name_en    VARCHAR(255) NULL,
  aliases_th JSON NULL,
  aliases_en JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE smartgift_offer (
  code         VARCHAR(64)   NOT NULL PRIMARY KEY,
  name_th      VARCHAR(512)  NULL,
  name_en      VARCHAR(512)  NULL,
  description  TEXT NULL,
  offer_kind   VARCHAR(64)   NULL,
  status       VARCHAR(64)   NULL,
  branding     VARCHAR(512)  NULL,
  origin       VARCHAR(64)   NULL,
  rmb          DECIMAL(12,2) NULL,
  image        VARCHAR(512)  NULL,
  price_tiers  JSON NULL,
  source_ref   JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE smartgift_model (
  base_signature VARCHAR(191) NOT NULL PRIMARY KEY,
  display_name   VARCHAR(512) NULL,
  english_name   VARCHAR(512) NULL,
  type_id        VARCHAR(64)  NULL,
  group_id       VARCHAR(64)  NULL,
  status         VARCHAR(64)  NULL,
  price_source   VARCHAR(64)  NULL,
  offer_codes    JSON NULL,
  colors         JSON NULL,
  price_tiers    JSON NULL,
  source_ref     JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE smartgift_price (
  id                    INT NOT NULL PRIMARY KEY,
  offer_code            VARCHAR(64) NULL,
  qty_tier              INT NULL,
  unit_price            DECIMAL(12,2) NULL,
  unit_price_with_vat   DECIMAL(12,2) NULL,
  price_missing         TINYINT(1) NOT NULL,
  price_list_group      VARCHAR(64) NULL,
  flow_account_code     VARCHAR(128) NULL,
  flow_account_name     VARCHAR(512) NULL,
  export_date           VARCHAR(32) NULL,
  source_ref            JSON NULL,
  KEY idx_smartgift_price_offer (offer_code),
  KEY idx_smartgift_price_tier (offer_code, qty_tier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def convert(sql: str) -> str:
    sql = re.sub(r"(?m)^\s*BEGIN\s*;\s*$", "", sql)
    sql = re.sub(r"(?m)^\s*COMMIT\s*;\s*$", "", sql)

    sql = sql.replace("JSONB", "JSON")
    sql = re.sub(r"\bBOOLEAN\b", "TINYINT(1)", sql)
    sql = re.sub(r"\bNUMERIC\b", "DECIMAL", sql)
    sql = re.sub(r"(?<![A-Za-z0-9_'])\bTRUE\b(?![A-Za-z0-9_'])", "1", sql)
    sql = re.sub(r"(?<![A-Za-z0-9_'])\bFALSE\b(?![A-Za-z0-9_'])", "0", sql)
    sql = re.sub(r"\s+ON CONFLICT\s*\([^)]+\)\s+DO\s+NOTHING", "", sql, flags=re.I)

    sql = re.sub(
        r"CREATE TABLE smartgift_export_run\s*\([\s\S]*?\);\s*"
        r"CREATE TABLE smartgift_type\s*\([\s\S]*?\);\s*"
        r"CREATE TABLE smartgift_offer\s*\([\s\S]*?\);\s*"
        r"CREATE TABLE smartgift_model\s*\([\s\S]*?\);\s*"
        r"CREATE TABLE smartgift_price\s*\([\s\S]*?\);",
        MYSQL_DDL.strip() + "\n",
        sql,
        count=1,
    )
    sql = re.sub(r"(?m)^CREATE INDEX idx_smartgift_price_offer.*$", "", sql)
    sql = re.sub(r"(?m)^CREATE INDEX idx_smartgift_price_tier.*$", "", sql)

    header = """-- Converted from smartgiftpricelist.postgres.sql → MySQL price_db
SET NAMES utf8mb4;
USE price_db;
SET SESSION sql_mode = CONCAT(@@sql_mode, ',NO_BACKSLASH_ESCAPES');
SET FOREIGN_KEY_CHECKS=0;

"""
    footer = """
SET FOREIGN_KEY_CHECKS=1;
SELECT 'smartgift_export_run' AS t, COUNT(*) AS n FROM smartgift_export_run
UNION ALL SELECT 'smartgift_type', COUNT(*) FROM smartgift_type
UNION ALL SELECT 'smartgift_offer', COUNT(*) FROM smartgift_offer
UNION ALL SELECT 'smartgift_model', COUNT(*) FROM smartgift_model
UNION ALL SELECT 'smartgift_price', COUNT(*) FROM smartgift_price;
"""
    return header + sql.strip() + "\n" + footer


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT
    text = src.read_text(encoding="utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(convert(text), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
