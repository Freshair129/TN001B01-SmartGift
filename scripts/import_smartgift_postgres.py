#!/usr/bin/env python3
"""Import smartgiftpricelist.postgres.sql into MySQL smartgift (legacy flat tables).

Prefer: import into staging then run scripts/migrate_to_smartgift_db.py for ID joins.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pymysql

SRC = Path(r"C:\Users\Admin\Downloads\smartgiftpricelist.postgres.sql")

DDL = """
SET NAMES utf8mb4;
USE smartgift;
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS smartgift_price;
DROP TABLE IF EXISTS smartgift_offer;
DROP TABLE IF EXISTS smartgift_model;
DROP TABLE IF EXISTS smartgift_type;
DROP TABLE IF EXISTS smartgift_export_run;
CREATE TABLE smartgift_export_run (
  run_id VARCHAR(64) NOT NULL PRIMARY KEY,
  exported_at VARCHAR(64) NOT NULL,
  source_path VARCHAR(1024) NOT NULL,
  commercial_skus INT NOT NULL,
  offers INT NOT NULL,
  models INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE smartgift_type (
  type_id VARCHAR(64) NOT NULL PRIMARY KEY,
  group_id VARCHAR(64) NULL,
  name_th VARCHAR(255) NULL,
  name_en VARCHAR(255) NULL,
  aliases_th JSON NULL,
  aliases_en JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE smartgift_offer (
  code VARCHAR(64) NOT NULL PRIMARY KEY,
  name_th VARCHAR(512) NULL,
  name_en VARCHAR(512) NULL,
  description TEXT NULL,
  offer_kind VARCHAR(64) NULL,
  status VARCHAR(64) NULL,
  branding VARCHAR(512) NULL,
  origin VARCHAR(64) NULL,
  rmb DECIMAL(12,2) NULL,
  image VARCHAR(512) NULL,
  price_tiers JSON NULL,
  source_ref JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE smartgift_model (
  sig_hash CHAR(64) NOT NULL PRIMARY KEY,
  base_signature TEXT NOT NULL,
  display_name VARCHAR(512) NULL,
  english_name VARCHAR(512) NULL,
  type_id VARCHAR(64) NULL,
  group_id VARCHAR(64) NULL,
  status VARCHAR(64) NULL,
  price_source VARCHAR(64) NULL,
  offer_codes JSON NULL,
  colors JSON NULL,
  price_tiers JSON NULL,
  source_ref JSON NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE smartgift_price (
  id INT NOT NULL PRIMARY KEY,
  offer_code VARCHAR(64) NULL,
  qty_tier INT NULL,
  unit_price DECIMAL(12,2) NULL,
  unit_price_with_vat DECIMAL(12,2) NULL,
  price_missing TINYINT(1) NOT NULL,
  price_list_group VARCHAR(64) NULL,
  flow_account_code VARCHAR(128) NULL,
  flow_account_name VARCHAR(512) NULL,
  export_date VARCHAR(32) NULL,
  source_ref JSON NULL,
  KEY idx_smartgift_price_offer (offer_code),
  KEY idx_smartgift_price_tier (offer_code, qty_tier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
SET FOREIGN_KEY_CHECKS=1;
"""


def split_sql_values(values_sql: str) -> list:
    out = []
    i = 0
    s = values_sql
    n = len(s)
    while i < n:
        while i < n and s[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        if s.startswith("NULL", i) and (i + 4 >= n or s[i + 4] in ",)"):
            out.append(None)
            i += 4
            continue
        if s.startswith("TRUE", i) and (i + 4 >= n or s[i + 4] in ",)"):
            out.append(1)
            i += 4
            continue
        if s.startswith("FALSE", i) and (i + 5 >= n or s[i + 5] in ",)"):
            out.append(0)
            i += 5
            continue
        if s[i] == "'":
            i += 1
            buf = []
            while i < n:
                ch = s[i]
                if ch == "'" and i + 1 < n and s[i + 1] == "'":
                    buf.append("'")
                    i += 2
                    continue
                if ch == "'":
                    i += 1
                    break
                buf.append(ch)
                i += 1
            out.append("".join(buf))
            continue
        j = i
        while j < n and s[j] not in ",)":
            j += 1
        token = s[i:j].strip()
        out.append(token)
        i = j
    return out


def parse_insert(line: str) -> tuple[str, list[str], list] | None:
    if not line.startswith("INSERT INTO "):
        return None
    # strip trailing ON CONFLICT ... and ;
    line = line.rstrip().rstrip(";")
    oc = line.upper().find(" ON CONFLICT ")
    if oc > 0:
        line = line[:oc].rstrip()

    # INSERT INTO table (
    rest = line[len("INSERT INTO ") :]
    sp = rest.find("(")
    if sp < 0:
        return None
    table = rest[:sp].strip()
    # find matching ) for columns
    depth = 0
    i = sp
    while i < len(rest):
        if rest[i] == "(":
            depth += 1
        elif rest[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        return None
    cols = [c.strip() for c in rest[sp + 1 : i].split(",")]
    after = rest[i + 1 :].lstrip()
    if not after.upper().startswith("VALUES"):
        return None
    after = after[6:].lstrip()
    if not after.startswith("("):
        return None
    # extract VALUES (...) with string-aware paren matching
    vals_body = after[1:]
    depth = 1
    j = 0
    in_str = False
    while j < len(vals_body) and depth > 0:
        ch = vals_body[j]
        if in_str:
            if ch == "'" and j + 1 < len(vals_body) and vals_body[j + 1] == "'":
                j += 2
                continue
            if ch == "'":
                in_str = False
            j += 1
            continue
        if ch == "'":
            in_str = True
            j += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    if depth != 0:
        return None
    vals = split_sql_values(vals_body[:j])
    return table, cols, vals


def is_insert_end(line: str) -> bool:
    """True when line finishes an INSERT (closing paren of VALUES, optional ON CONFLICT)."""
    s = line.rstrip()
    return bool(
        re.search(r"\)\s*(ON CONFLICT\b[\s\S]*)?(DO NOTHING)?;?\s*$", s, re.I)
    )


def iter_insert_statements(text: str):
    """Yield full INSERT statements (may span multiple lines)."""
    buf: list[str] = []
    collecting = False
    abandoned = 0
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.lstrip()
        if collecting and stripped.startswith("INSERT INTO"):
            abandoned += 1
            buf = []
            collecting = False
        if not collecting:
            if stripped.startswith("INSERT INTO"):
                collecting = True
                buf = [line]
                if is_insert_end(line):
                    stmt = "\n".join(buf).strip()
                    if not stmt.endswith(";"):
                        stmt += ";"
                    yield stmt
                    collecting = False
                    buf = []
            continue
        buf.append(line)
        if is_insert_end(line):
            stmt = "\n".join(buf).strip()
            if not stmt.endswith(";"):
                stmt += ";"
            yield stmt
            collecting = False
            buf = []
    if collecting:
        abandoned += 1
    if abandoned:
        print(f"note: abandoned {abandoned} truncated INSERT(s) in dump")


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    text = src.read_text(encoding="utf-8")

    conn = pymysql.connect(
        host="127.0.0.1",
        port=3310,
        user="root",
        password="rootpass",
        database="smartgift",
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        with conn.cursor() as cur:
            for stmt in DDL.split(";"):
                s = stmt.strip()
                if s:
                    cur.execute(s)
            conn.commit()

            counts: dict[str, int] = {}
            skipped = 0
            for stmt in iter_insert_statements(text):
                line = stmt.strip().rstrip(";").strip()
                # normalize ON CONFLICT ending
                if line.upper().endswith("DO NOTHING"):
                    pass
                parsed = parse_insert(line if line.endswith(";") else line + ";")
                if not parsed:
                    # try without forcing semicolon handling
                    parsed = parse_insert(line)
                if not parsed:
                    skipped += 1
                    print("SKIP:", line[:120].replace("\n", " "))
                    continue
                table, cols, vals = parsed
                if len(cols) != len(vals):
                    skipped += 1
                    print(f"SKIP mismatch {table} {len(cols)}!={len(vals)}:", line[:100])
                    continue
                row = dict(zip(cols, vals))
                if table == "smartgift_model":
                    sig = row.get("base_signature") or ""
                    row = {
                        "sig_hash": hashlib.sha256(sig.encode("utf-8")).hexdigest(),
                        **row,
                    }
                    cols = list(row.keys())
                    vals = [row[c] for c in cols]

                ph = ", ".join(["%s"] * len(cols))
                col_sql = ", ".join(f"`{c}`" for c in cols)
                cur.execute(f"INSERT INTO `{table}` ({col_sql}) VALUES ({ph})", vals)
                counts[table] = counts.get(table, 0) + 1

            conn.commit()
            print("Imported:", counts, "skipped:", skipped)
            cur.execute(
                """
                SELECT 'smartgift_export_run', COUNT(*) FROM smartgift_export_run
                UNION ALL SELECT 'smartgift_type', COUNT(*) FROM smartgift_type
                UNION ALL SELECT 'smartgift_offer', COUNT(*) FROM smartgift_offer
                UNION ALL SELECT 'smartgift_model', COUNT(*) FROM smartgift_model
                UNION ALL SELECT 'smartgift_price', COUNT(*) FROM smartgift_price
                """
            )
            for r in cur.fetchall():
                print(r[0], r[1])
            cur.execute(
                "SELECT code, name_th FROM smartgift_offer WHERE name_th IS NOT NULL ORDER BY code LIMIT 3"
            )
            for r in cur.fetchall():
                print("sample:", r[0], r[1])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
