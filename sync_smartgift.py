#!/usr/bin/env python3
"""Sync SmartGift pricing catalogs into MySQL smartgift."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from base64 import b64encode
from datetime import datetime, timezone
from typing import Any

import pymysql

DEFAULT_BASE = "https://smartgift-pricing.vercel.app"
DEFAULT_CATALOGS = ("giftset", "powerbank")


def env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if val is None or val == "":
        raise SystemExit(f"Missing env: {name}")
    return val


def fetch_json(url: str, user: str, password: str) -> dict[str, Any]:
    token = b64encode(f"{user}:{password}".encode()).decode()
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {token}",
            "User-Agent": "price-boss-sync/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        raise SystemExit(f"HTTP {e.code} for {url}: {body}") from e


def dims(product: dict[str, Any]) -> tuple[Any, Any, Any]:
    raw = product.get("dims")
    if not isinstance(raw, list) or len(raw) < 3:
        return None, None, None
    return raw[0], raw[1], raw[2]


def sync(conn: pymysql.Connection, base: str, user: str, password: str, keys: list[str]) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with conn.cursor() as cur:
        for key in keys:
            url = f"{base.rstrip('/')}/catalog/{key}.json"
            data = fetch_json(url, user, password)
            label = str(data.get("label") or key)
            products = data.get("products") or []
            if not isinstance(products, list):
                raise SystemExit(f"{key}: products is not a list")

            # Catalog JSON can list the same code more than once — keep last.
            by_code: dict[str, tuple] = {}
            for p in products:
                if not isinstance(p, dict):
                    continue
                code = p.get("code")
                if not code:
                    continue
                d_l, d_w, d_h = dims(p)
                by_code[str(code)] = (
                    key,
                    str(code),
                    p.get("name"),
                    p.get("rmb"),
                    p.get("upc"),
                    d_l,
                    d_w,
                    d_h,
                    p.get("kg"),
                    1 if p.get("e") else 0,
                    p.get("img"),
                    now,
                )
            rows = list(by_code.values())
            skipped = len(products) - len(rows)

            cur.execute(
                """
                INSERT INTO catalogs (catalog_key, label, product_count, source_url, synced_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  label=VALUES(label),
                  product_count=VALUES(product_count),
                  source_url=VALUES(source_url),
                  synced_at=VALUES(synced_at)
                """,
                (key, label, len(rows), url, now),
            )
            cur.execute("DELETE FROM products WHERE catalog_key=%s", (key,))

            if rows:
                cur.executemany(
                    """
                    INSERT INTO products (
                      catalog_key, code, name, rmb, upc,
                      dim_l, dim_w, dim_h, kg, exclusive_flag, img, synced_at
                    ) VALUES (
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    rows,
                )
            print(
                f"OK {key}: {len(rows)} products ({label})"
                + (f", skipped {skipped} duplicate codes" if skipped else "")
            )
    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync SmartGift catalogs → smartgift")
    parser.add_argument("--base", default=os.environ.get("SG_BASE", DEFAULT_BASE))
    parser.add_argument("--user", default=os.environ.get("SG_USER", "admin"))
    parser.add_argument("--password", default=os.environ.get("SG_PASSWORD", "1234"))
    parser.add_argument(
        "--catalogs",
        default=",".join(DEFAULT_CATALOGS),
        help="Comma-separated catalog keys",
    )
    parser.add_argument("--host", default=os.environ.get("MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MYSQL_PORT", "3310")))
    parser.add_argument("--db", default=os.environ.get("MYSQL_DATABASE", "smartgift"))
    parser.add_argument("--mysql-user", default=os.environ.get("MYSQL_USER", "root"))
    parser.add_argument(
        "--mysql-password",
        default=os.environ.get("MYSQL_PASSWORD", "rootpass"),
    )
    args = parser.parse_args()
    keys = [k.strip() for k in args.catalogs.split(",") if k.strip()]

    conn = pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.mysql_user,
        password=args.mysql_password,
        database=args.db,
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        sync(conn, args.base, args.user, args.password, keys)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
