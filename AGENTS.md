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

## 📐 Documentation & Architecture Decision Records (ADRs)

* **ADR Directory:** `docs/decisions/`
* **Template Standard:** Strictly follows the zuri-ai decision template (`D:\zuri-ai\docs\decisions`).
* **Naming Convention:** `ADR-XXX-TITLE.md` (e.g. `ADR-001-ECO-FRIENDLY-CATEGORY-REFACTOR.md`).
* **Governance Invariant:** Any strategic changes to top-level product categories, portfolio blueprints, data pipeline mappings, or vault substrate bindings must be documented in `docs/decisions/`.

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

---

## 🤝 Cross-Repo Protocol (added 2026-08-30 by the zuri-ai/GKS/MSP session)

You (the Antigravity agent) work outside the Claude session mesh, so files are
our shared channel. Three rules keep your CRs landable:

1. **CR files you write into `D:\zuri-ai\docs\change-requests\` are proposals,
   not landings.** They sit untracked in a shared checkout (preserved on tag
   `archive/cr-002-003-004-untracked`). To land: a zuri-ai session takes them
   through governance — every new route/UI/model needs an `FR-xxx` declared in
   `docs/PRD-SDD-v1.0.md` + id-ledger pin BEFORE code (preflight fails
   otherwise). Never write application code into `D:\zuri-ai` directly; propose
   via CR and let a governed lane build it.

2. **Corrections to CR-002 as written (from the team that ships GKS/MSP):**
   - `msp_vault_resolve` belongs to **API-009** (MSP's contract,
     `D:\msp\docs\API-009-Persistent-Memory-Contract.md`), not API-010. New MSP
     tools go through that doc + MSP's rkoi review.
   - **GKS has no vector spaces by accepted decision** (ADR-GKS-ENTITY-RESOLUTION,
     2026-08-30, deliberately excluded embedding). Registering `bge-m3` spaces
     in GKS reverses an ADR and needs its own ADR in `D:\gks`.
   - **GKS never calls outward** (ADR-GKS-BOUNDARY). Your Tier 3/4 diagram
     describes THIS project's embedded GenesisBlockDB engine — legitimate, but
     it is not GKS the service, despite sharing the npm binding and vocabulary.

3. **Zero-PII vault invariant is yours to keep provable:** `vlt-customer-client`
   must never feed vectors into `vlt-catalog-product`, and nothing from either
   goes into `D:\workspace\zuri-edge-device\data\genesis_smartgift_store_v4\`
   (governed store, atomic cutover) or carries a `gks:` ref (reserved namespace,
   GKS rejects caller-assigned identity).

Questions for the Claude side: write them into your CR under an
`## Open questions` heading — zuri-ai sessions review these files.
