# AGENTS.md

This file provides context, architectural guidelines, and execution instructions for AI agents working in this repository (`o:\cat`).

---

## 🎁 Project Overview

**SmartGift B2B E-commerce & Intelligent Portfolio System** is an enterprise-grade corporate gift set allocation, set decomposition, and inventory waterfall deduction engine. It features a hybrid GraphRAG AI Search pipeline for unboxing sensory experiences and corporate recipient matching.

---

## 🏛️ Architecture Pattern: 100% Local Multi-Engine Architecture (Local DB + GenesisBlock Edge)

This project currently operates on a **100% Local Multi-Engine Architecture** (No Cloud dependencies required):

```
                                 ┌─────────────────────────────────────────────────────────┐
                                 │                   Supabase Cloud Tier                   │
                                 │                 (Managed PostgreSQL)                    │
                                 ├─────────────────────────────────────────────────────────┤
                                 │ • Master Catalog Tables & Constraints                   │
                                 │ • Granular Physical Stock Inventory & Cascade Engine    │
                                 │ • `pgvector` Extension (Cloud Vector Backup)            │
                                 │ • Row Level Security (RLS) & Financial Ledger           │
                                 └────────────────────────────┬────────────────────────────┘
                                                              │
                                            Catalog Sync      │ (Polling / Webhook Sync)
                                            Bridge Engine     │
                                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             Edge / Local AI Search Tier                                  │
│                              (GenesisBlockDB Native)                                     │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ • In-Process Native Rust Embedded Hybrid Graph + Vector Search (`query-ir.v1`)           │
│ • Ultra-low Latency HNSW Vector Index (`bge-m3` 1024-dim)                                │
│ • Serves Real-time GraphRAG Context directly to LLM Agents (< 1ms Latency)              │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Key Files & Components

| File Path | Description |
| :--- | :--- |
| [`demo_app.py`](file:///o:/cat/demo_app.py) | Interactive CLI terminal demonstrating GraphRAG search, cascade inventory deduction, and AI consultant. |
| [`inventory_cascade_engine.py`](file:///o:/cat/inventory_cascade_engine.py) | Core engine decomposing gift bundles into SKU components and calculating real-time gross margins. |
| [`smartgift_graphrag_agent.py`](file:///o:/cat/smartgift_graphrag_agent.py) | GraphRAG AI agent connecting Local Thai LLMs (Ollama) with GenesisBlockDB search. |
| [`supabase_genesis_sync.py`](file:///o:/cat/supabase_genesis_sync.py) | Sync bridge fetching Master Catalog from Supabase/SSOT and seeding GenesisBlockDB Edge Engine. |
| [`seed_genesisblock.mjs`](file:///o:/cat/seed_genesisblock.mjs) | Node.js script loading `@freshair129/gks-genesis-block-native` to seed nodes, edges, and 1024-dim vectors. |
| [`test_genesis.mjs`](file:///o:/cat/test_genesis.mjs) | Test harness verifying native GenesisBlockDB NAPI binding and database opening. |
| [`schema_postgresql.sql`](file:///o:/cat/schema_postgresql.sql) | DDL for PostgreSQL/Supabase including `pgvector` extension, categories, product masters, and inventory logs. |
| [`schema_genesisblock.yaml`](file:///o:/cat/schema_genesisblock.yaml) | GenesisBlock DB Schema Specification contract (`smartgift://b2b/portfolio/v1`). |
| [`smartgift_catalog_master.json`](file:///o:/cat/smartgift_catalog_master.json) | Master Catalog Dataset (Single Source of Truth). |

---

## ⚙️ Dependencies & Environment Setup

* **Node.js Package:** `@freshair129/gks-genesis-block-native` (`v0.2.5`) installed via npm in `node_modules`.
* **Environment Fallback:** Native binding defaults to installed package, with optional override via `process.env.GENESIS_BINDING_PATH`.
* **Python Runtime:** Python 3 (run commands via `py -3`).

---

## 🧪 Verification & Running Commands

```bash
# 1. Run Python Unit Tests
py -3 -m unittest discover tests

# 2. Test GenesisBlockDB Native NAPI Binding
node test_genesis.mjs

# 3. Run Supabase ➔ GenesisBlockDB Sync Bridge
py -3 supabase_genesis_sync.py

# 4. Launch Interactive Application Terminal
py -3 demo_app.py
```

---

## 🛡️ Coding Guidelines & Rules for Agents

1. **UTF-8 Support:** Always configure stdout UTF-8 encoding in Python scripts (`sys.stdout.reconfigure(encoding='utf-8')`).
2. **Inventory Integrity:** Never alter non-negative inventory check constraints (`inventory_qty >= 0`) or bypass waterfall stock deduction logic.
3. **Query IR Specification:** Prefer `Query IR` (`query-ir.v1`) for GenesisBlockDB operations.
4. **Dependency Resolution:** Respect `@freshair129/gks-genesis-block-native` npm dependency over manual absolute path bindings.

---

## 🔗 Upstream & Data Provenance (added 2026-08-30 — read before touching prices)

This project is **downstream** of an existing SmartGift data chain. Two facts
were not written anywhere in this repository before, and both change what an
agent here may treat as truth:

### 1. Price truth does NOT come from the PDF

`smartgift_catalog_master.json` is extracted from a **PDF blueprint /
translated price-sheet PDF** (`extract_catalog_dataset.py:19`). That PDF is
presentation material — prior art, not the price authority. The actual
upstream chain is:

```
FlowAccount export (flowaccount-product-2026-06-21.xlsx)
  → ingest pipeline → genesis_smartgift_store_v4 (CURRENT run, schema v4.3)
  → zuri-rag-service :8888  (/api/rag/price, /api/rag/search)
  → D:\workspace\zuri-rag-service\exports\smartgift-pricelist.{postgres,sqlite}.sql
```

The `.sql` exports (5 tables: `smartgift_price` 669 rows, `smartgift_offer`
1110, `smartgift_model` 427, `smartgift_type` 32, `smartgift_export_run` 1)
carry a **per-row `source_ref`** (source file + rowKey + sha256) and the ingest
**run id**. When this project loads prices — into Supabase via
`schema_postgresql.sql` or anywhere else — load from that export, keep the run
id, and keep `source_ref`. If a price here disagrees with the export, **the
export wins**; if the export is stale, regenerate it
(`node scripts/export-pricelist-sql.mjs` in `D:\workspace\zuri-rag-service`)
rather than falling back to the PDF.

**`price_missing` is a real flag, not a formatting detail.** 102 of 669 price
rows carry `unit_price = 0` with `price_missing = true`. Zero is never a
price; filter on `price_missing = false` before any margin or quote math.

### 2. This project is NOT part of the knowledge-authority chain

The governed chain is `Zuri / GoVibe → MSP → GKS → GenesisBlockDB`. This
project uses GenesisBlockDB as an **embedded engine for its own store**
(`./smartgift-genesis-db`), which is legitimate — GenesisBlockDB is a
standalone database product. Three boundaries follow:

- **Never open or write** `D:\workspace\zuri-edge-device\data\genesis_smartgift_store_v4\`.
  That store belongs to the ingest pipeline and the RAG service; it is
  cut over atomically via its `CURRENT` pointer, and an outside write corrupts
  a governed store.
- **Never mint `gks:`-prefixed references.** That namespace is reserved by the
  Genesis Knowledge System, which rejects caller-assigned canonical identity
  (fails closed as of 2026-08-30, Stage 9).
- The node vocabulary here (`CatalogOffer`, tiers, BOM edges) **overlaps by
  name** with the v4 catalog graph but the stores are separate and the ids are
  not interchangeable. Same words, different databases — never join across
  them by label.

### 3. Product ID Normalization: Extract & Transform (Do NOT Edit Upstream FlowAccount)

Upstream FlowAccount Excel data (`บริษัท เทราบิส จำกัด_product.xlsx` / `flowaccount-product-2026-06-21.xlsx`) **must NEVER be edited directly at the source file**.
Many product records in FlowAccount lack explicit Product IDs in code fields, embedding them directly within product name strings (`name_th`), e.g.:
- `Model : MC00-1`
- `THB03-2(P-20)`
- `TYD0762(P-PT)`
- `444` / `445`

**Pipeline Rule for Agents:** In the data pipeline preparation stage, AI Agents must perform Entity Extraction & Normalization using [`pipeline/02_normalize_mapper.py`](file:///o:/cat/pipeline/02_normalize_mapper.py). Extract embedded Product IDs, Model Codes, and Supplier Tags (`P-xx`) via regex parsing and output the normalized SQL tables into `smartgift-portfolio.postgres.sql` (alias: `smartgift-pricelist.postgres.sql`) and [`product_id_mapping_report.json`](file:///o:/cat/data-pipeline/04_review_reports/product_id_mapping_report.json) without ever mutating the raw `บริษัท เทราบิส จำกัด_product.xlsx` source export.

---

### 4. FlowAccount Export Registry & Immutable Archiving (SHA-256 Fingerprints)

FlowAccount export files always share identical file names upon export. To maintain complete auditability and prevent accidental overwrites:
- Every incoming export must be processed via [`pipeline/flowaccount_registry_archiver.py`](file:///o:/cat/pipeline/flowaccount_registry_archiver.py).
- Content SHA-256 hashes must be calculated. Duplicate exports with identical hashes are skipped (`UNCHANGED_DUPLICATE_SKIPPED`).
- New versions must be immutably archived in `data-pipeline/01_raw/archive/` using the naming convention: `YYYYMMDDTHHMMSSZ_{sha256[:12]}_{filename}`.
- All versions and row-level diffs (`+N` rows) must be tracked in `data-pipeline/01_raw/exports_registry.json`.

---

### 5. ID-Bound Provenance & Audit Trail Invariant

All pipeline events, inventory cascade deductions, and normalization steps must produce structured JSONL audit logs bound to:
- **`event_id`**: Unique UUIDv4 per audit event.
- **`pipeline_run_id`**: Ingest execution batch run ID (`run-YYYYMMDDTHHMMSSZ-xxxxxx`).
- **`tenant_id`**: `Org-EtohGroup`
- **`business_id`**: `SmartGift`
- **`vault_id`**: `vlt-catalog-product` (or `vlt-customer-client`)
- **`source_ref`**: `{ "file": "...", "row_key": "...", "line_number": N, "sha256": "..." }`
- **`action` & `timestamp`**: Full UTC ISO-8601 timestamps recorded in `data-pipeline/04_review_reports/provenance_audit_log.jsonl`.

---

### 6. Catalog Versioning & Automated Diff Tracking

All modifications to the catalog must be versioned via [`pipeline/04_audit_review.py`](file:///o:/cat/pipeline/04_audit_review.py):
- Produces immutable catalog versions (e.g. `catalog-v2026.08.29-fe2bf21f`).
- Computes content-level diffs (`added_offers`, `removed_offers`, `price_changed`, `bom_drift`).
- Generates `data-pipeline/04_review_reports/catalog_version_diff_report.json` for human-in-the-loop review and approval before cloud sync.

---

### 7. Landed Cost & Ladder Pricing Engine

Price and margin calculations must use [`src/cascade_engine/pricing_calculator.py`](file:///o:/cat/src/cascade_engine/pricing_calculator.py):
- **Landed Cost**: Factory RMB $\times$ FX $\times$ Small Order Factor ($1.0\times$ to $1.5\times$) $+$ Freight (Volume vs Weight Density $\ge 400$ kg/CBM) $+$ Logo Print $+$ Inland Transport.
- **Profiles**: Standard Profile ($2.14\times$ to $3.00\times$ markup on factory cost) & Corporate Profile ($1.47\times$ flat markup on Landed Cost).
- **Floor Guardrail**: Enforces minimum gross profit floor $\ge 5,000$ THB (small orders) or $\ge 3,000$ THB, rounded up to the nearest 10 THB.

