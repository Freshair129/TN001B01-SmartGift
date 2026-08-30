-- ============================================================================
-- SmartGift DB: rename from price_db + ID-centric joins
-- Run via: python scripts/migrate_to_smartgift_db.py
-- ============================================================================
-- This file documents the target schema. The Python migrator applies it.

CREATE DATABASE IF NOT EXISTS smartgift
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smartgift;

-- ── Catalog groups (product family on web) ─────────────────────────────
-- catalogs already exists; add numeric id + products.catalog_id

-- ── Pricelist taxonomy ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS smartgift_group (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  group_code  VARCHAR(64)  NOT NULL,
  name_th     VARCHAR(255) NULL,
  name_en     VARCHAR(255) NULL,
  sort_order  INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_group_code (group_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- smartgift_type: add id PK, type_code (=legacy type_id), group_id FK
-- smartgift_offer: add id PK, keep code UNIQUE
-- smartgift_model: add id PK, type_id/group_id as INT FKs, keep sig_hash UNIQUE
-- smartgift_model_offer: M:N instead of offer_codes JSON
-- smartgift_price: add offer_id FK
-- product_offer_link: catalog product ↔ offer by code match

CREATE TABLE IF NOT EXISTS smartgift_model_offer (
  model_id   INT UNSIGNED NOT NULL,
  offer_id   INT UNSIGNED NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  PRIMARY KEY (model_id, offer_id),
  KEY idx_mo_offer (offer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS product_offer_link (
  product_id   BIGINT UNSIGNED NOT NULL,
  offer_id     INT UNSIGNED NOT NULL,
  match_method ENUM('exact_code') NOT NULL DEFAULT 'exact_code',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id, offer_id),
  KEY idx_pol_offer (offer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
