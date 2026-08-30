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
* **GenesisBlock Schema Authority:** `config/schema_genesisblock.yaml` is the canonical authority for SmartGift entity names, required properties, ID prefixes, and graph relationships. Any JSON, API, web catalog, offline catalog, pipeline output, or database projection must map back to this schema before it is treated as canonical.

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
5. **Zero-PII in Version Control — customer data never goes to GitHub.** This is invariant #1 with the scope it was missing. #1 forbids customer contacts, PIC names and quotation history in the *vector vault*; it says nothing about git, and on 2026-08-30 that exact data — a named legal entity's contact list, its quotation report, and a per-customer purchase history — was found tracked in this repository and live on a **public** remote. The rule was right and could not reach the failure, because a vault is not a repository. So: **no customer or personally identifying data is ever committed, in any lane, in any format.** Not in `01_raw`, not in a prepared JSON, not in a review report, not in a test fixture. The store of record is zuri-ai's CRM domain, behind its scope chain and PDPA consent controls (FR-103/SEC-005) — anything under `data-pipeline/01_raw/` is an intake artifact, never a store.

6. **GenesisBlock schema is the canonical data contract.** Before adding or changing a catalog entity, validate it against `config/schema_genesisblock.yaml` and preserve the schema identity and edge semantics:
   - `Category` → `cat:`
   - `ProductMaster` → `pm:`
   - `CatalogOffer` → `offer:`
   - `BundleOffer` → `bundle:` (a serialized `pkg` array is only an alias; `PKG-*` is a business code, not the canonical primary key)
   - `GiftTier` → `tier:`
   - `RecipientSegment` → `seg:`

   Canonical IDs are the primary keys; business codes and presentation field names are not substitutes. Serialized aliases such as `portfolio_catalogs`, `customer_tiers`, and `pkg` must record their mapping to the schema entity. `product_families` is an extension/helper unless a reviewed schema revision adds a `ProductFamily` node. Keep `IN_CATEGORY`, `CONTAINS`, `BELONGS_TO_TIER`, `RECOMMENDED_TIER`, and `INCLUDES_OFFER` references type-correct, and fail closed when required properties or referenced canonical IDs are missing. A schema or ontology change requires a documented decision in `docs/decisions/` before implementation.

   **Two mechanics that fail silently, and the reason this invariant exists rather than a `.gitignore` line existing:**

   - **`.gitignore` does not untrack anything.** A rule added after the first commit changes nothing: the file keeps being staged, committed and pushed while the rule sits there looking like it works. Untracking is `git rm --cached`; the rule only stops it returning. Both are needed and they are not interchangeable.
   - **`git status` will not warn you.** A tracked file with no local edits is neither untracked nor modified, so nothing appears. Silence there is not evidence of safety. To check a specific path, use `git ls-files <path>` (lists it → tracked) and `git check-ignore <path>` (exit 1 → not ignored). Those two disagree with each other in exactly the case that matters, which is why both are named here.

   `data-pipeline/01_raw/05_crm_customer_data/` was untracked and ignored on 2026-08-30 (commit `4c818e2`). The files remain on disk. **The history still contains them**, and the repository was public during the exposure window, so that data must be treated as disclosed rather than as at-risk — see `docs/change-requests/CR-006-PII-IN-VERSION-CONTROL-AND-ZURI-FILE-INTAKE-READINESS.md`. Before adding any new file under `data-pipeline/`, ask what is inside it, not what its folder is called.

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
