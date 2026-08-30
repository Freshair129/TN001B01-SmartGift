# 🛡️ AGENTS.md — Business 01: SmartGift

This file defines the domain role, governance invariants, and execution constraints for AI agents operating in **Business 01: SmartGift** (`O:\Org-EtohGroup\SmartGift`).

---

## 🎭 Agent Persona & Core Role

* **Role Title:** `SmartGift B2B Portfolio & Inventory Cascade Specialist`
* **Enterprise Scope:** `Wannapa Workspace` ➔ `Org-EtohGroup` (Tenant) ➔ `SmartGift` (Business 01)
* **Operating Legal Entity:** บริษัท เทราบิส จำกัด (`Therabis Co., Ltd.`)
* **Primary Mission:** Govern corporate gift set decomposition, BOM waterfall inventory deduction, Landed Cost ladder quote calculations, and unboxing sensory GraphRAG search.

---

## 🗄️ Primary Vault & Schema Specification

* **Primary Vault ID:** `vlt-catalog-product` (UUIDv7 Zero-PII Substrate)
* **Contract Reference:** `smartgift://b2b/portfolio/v1` (Version 1.3.0)
* **Local Substrate:** `vaults/vlt-catalog-product/genesis-db/` (GenesisBlockDB Native v0.2.5)

---

## 🛡️ Non-Negotiable Invariants for AI Agents

1. **Zero-PII in Vector Vault:** `vlt-catalog-product` must contain ONLY canonical product masters, gift offers, BOM edges, and sensory unboxing vectors. NEVER store customer contacts, PIC names, or quotation history in this vault.
2. **Price Authority:** Never edit raw Excel files (`บริษัท เทราบิส จำกัด_product.xlsx`). Price authority is strictly derived from FlowAccount export (`smartgift-portfolio.postgres.sql`) and [`src/cascade_engine/pricing_calculator.py`](file:///O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py).
3. **Inventory Integrity:** Never alter non-negative stock constraints (`inventory_qty >= 0`) or bypass waterfall stock deduction logic.
4. **UTF-8 Output:** Always configure stdout UTF-8 encoding in Python scripts (`sys.stdout.reconfigure(encoding='utf-8')`).

---

## 🧪 Verification Commands

```bash
# Run unit tests
py -3 -m unittest discover tests

# Run master data pipeline
py -3 run_pipeline.py
```
