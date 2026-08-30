#!/usr/bin/env node
/**
 * Export SmartGift catalog JSON → SQL dump.
 *
 * Usage (same as Mac):
 *   node scripts/export-pricelist-sql.mjs --dialect postgres --out ราคา.sql
 *   node scripts/export-pricelist-sql.mjs --dialect mysql --out price_mysql.sql
 *
 * Env:
 *   SG_BASE, SG_USER, SG_PASSWORD
 *   Or place catalog/*.json next to this project (giftset.json, powerbank.json)
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const DEFAULT_BASE = process.env.SG_BASE || "https://smartgift-pricing.vercel.app";
const DEFAULT_USER = process.env.SG_USER || "admin";
const DEFAULT_PASS = process.env.SG_PASSWORD || "1234";
const DEFAULT_KEYS = ["giftset", "powerbank"];

function parseArgs(argv) {
  const out = { dialect: "postgres", out: "ราคา.sql", catalogs: DEFAULT_KEYS, base: DEFAULT_BASE };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dialect") out.dialect = argv[++i];
    else if (a === "--out") out.out = argv[++i];
    else if (a === "--base") out.base = argv[++i];
    else if (a === "--catalogs") out.catalogs = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (a === "--help" || a === "-h") out.help = true;
  }
  return out;
}

function sqlStr(v) {
  if (v == null) return "NULL";
  return `'${String(v).replace(/'/g, "''")}'`;
}

function sqlNum(v) {
  if (v == null || v === "") return "NULL";
  const n = Number(v);
  return Number.isFinite(n) ? String(n) : "NULL";
}

function sqlBool(v, dialect) {
  if (v == null) return "NULL";
  if (dialect === "postgres") return v ? "TRUE" : "FALSE";
  return v ? "1" : "0";
}

function dims(p) {
  const d = p?.dims;
  if (!Array.isArray(d) || d.length < 3) return [null, null, null];
  return [d[0], d[1], d[2]];
}

async function loadCatalog(key, base, auth) {
  const localCandidates = [
    path.join(ROOT, "catalog", `${key}.json`),
    path.join(ROOT, `${key}.json`),
  ];
  for (const p of localCandidates) {
    if (fs.existsSync(p)) {
      return JSON.parse(fs.readFileSync(p, "utf8"));
    }
  }
  const url = `${base.replace(/\/$/, "")}/catalog/${key}.json`;
  const res = await fetch(url, {
    headers: {
      Authorization: `Basic ${Buffer.from(auth).toString("base64")}`,
      Accept: "application/json",
      "User-Agent": "export-pricelist-sql/1.0",
    },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.json();
}

function ddl(dialect) {
  if (dialect === "postgres") {
    return `-- SmartGift pricelist export (postgres)
-- generated: ${new Date().toISOString()}

CREATE TABLE IF NOT EXISTS catalogs (
  catalog_key   TEXT PRIMARY KEY,
  label         TEXT NOT NULL,
  product_count INTEGER NOT NULL DEFAULT 0,
  source_url    TEXT NOT NULL,
  synced_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
  id             BIGSERIAL PRIMARY KEY,
  catalog_key    TEXT NOT NULL REFERENCES catalogs(catalog_key) ON DELETE CASCADE,
  code           TEXT NOT NULL,
  name           TEXT,
  rmb            NUMERIC(12,4),
  upc            INTEGER,
  dim_l          NUMERIC(10,2),
  dim_w          NUMERIC(10,2),
  dim_h          NUMERIC(10,2),
  kg             NUMERIC(10,3),
  exclusive_flag BOOLEAN NOT NULL DEFAULT FALSE,
  img            TEXT,
  synced_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (catalog_key, code)
);

TRUNCATE products RESTART IDENTITY CASCADE;
TRUNCATE catalogs CASCADE;
`;
  }

  return `-- SmartGift pricelist export (mysql)
-- generated: ${new Date().toISOString()}

CREATE TABLE IF NOT EXISTS catalogs (
  catalog_key   VARCHAR(64) NOT NULL PRIMARY KEY,
  label         VARCHAR(255) NOT NULL,
  product_count INT NOT NULL DEFAULT 0,
  source_url    VARCHAR(512) NOT NULL,
  synced_at     DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
  id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  catalog_key    VARCHAR(64) NOT NULL,
  code           VARCHAR(64) NOT NULL,
  name           VARCHAR(512) NULL,
  rmb            DECIMAL(12,4) NULL,
  upc            INT NULL,
  dim_l          DECIMAL(10,2) NULL,
  dim_w          DECIMAL(10,2) NULL,
  dim_h          DECIMAL(10,2) NULL,
  kg             DECIMAL(10,3) NULL,
  exclusive_flag TINYINT(1) NOT NULL DEFAULT 0,
  img            VARCHAR(255) NULL,
  synced_at      DATETIME NOT NULL,
  UNIQUE KEY uk_catalog_code (catalog_key, code),
  CONSTRAINT fk_products_catalog FOREIGN KEY (catalog_key) REFERENCES catalogs(catalog_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE products;
TRUNCATE TABLE catalogs;
SET FOREIGN_KEY_CHECKS=1;
`;
}

function emitCatalog(dialect, key, label, count, url, now) {
  if (dialect === "postgres") {
    return `INSERT INTO catalogs (catalog_key, label, product_count, source_url, synced_at) VALUES (${sqlStr(key)}, ${sqlStr(label)}, ${count}, ${sqlStr(url)}, ${sqlStr(now)}::timestamptz);\n`;
  }
  return `INSERT INTO catalogs (catalog_key, label, product_count, source_url, synced_at) VALUES (${sqlStr(key)}, ${sqlStr(label)}, ${count}, ${sqlStr(url)}, ${sqlStr(now)});\n`;
}

function emitProduct(dialect, key, p, now) {
  const [l, w, h] = dims(p);
  const cols = "catalog_key, code, name, rmb, upc, dim_l, dim_w, dim_h, kg, exclusive_flag, img, synced_at";
  const vals = [
    sqlStr(key),
    sqlStr(p.code),
    sqlStr(p.name ?? null),
    sqlNum(p.rmb),
    sqlNum(p.upc),
    sqlNum(l),
    sqlNum(w),
    sqlNum(h),
    sqlNum(p.kg),
    sqlBool(!!p.e, dialect),
    sqlStr(p.img ?? null),
    dialect === "postgres" ? `${sqlStr(now)}::timestamptz` : sqlStr(now),
  ].join(", ");
  return `INSERT INTO products (${cols}) VALUES (${vals});\n`;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(`Usage: node scripts/export-pricelist-sql.mjs --dialect postgres|mysql --out ราคา.sql`);
    process.exit(0);
  }
  if (!["postgres", "mysql"].includes(args.dialect)) {
    throw new Error(`Unsupported dialect: ${args.dialect}`);
  }

  const auth = `${DEFAULT_USER}:${DEFAULT_PASS}`;
  const now = new Date().toISOString().replace("T", " ").replace(/\.\d+Z$/, "");
  let sql = ddl(args.dialect);
  let total = 0;

  for (const key of args.catalogs) {
    const data = await loadCatalog(key, args.base, auth);
    const label = data.label || key;
    const products = Array.isArray(data.products) ? data.products : [];
    // dedupe by code (keep last)
    const byCode = new Map();
    for (const p of products) {
      if (p?.code) byCode.set(String(p.code), p);
    }
    const rows = [...byCode.values()];
    const url = `${args.base.replace(/\/$/, "")}/catalog/${key}.json`;
    sql += `\n-- catalog: ${key} (${rows.length} products)\n`;
    sql += emitCatalog(args.dialect, key, label, rows.length, url, now);
    for (const p of rows) {
      sql += emitProduct(args.dialect, key, p, now);
    }
    total += rows.length;
    console.error(`OK ${key}: ${rows.length} products`);
  }

  const outPath = path.isAbsolute(args.out) ? args.out : path.join(ROOT, args.out);
  fs.writeFileSync(outPath, sql, "utf8");
  console.error(`Wrote ${outPath} (${total} products, dialect=${args.dialect})`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
