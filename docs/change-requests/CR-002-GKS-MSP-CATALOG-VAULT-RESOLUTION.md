---
doc_type: change-request
id: CR-002
status: proposed
version: "1.0.0"
created_at: "2026-08-30T07:30:00+07:00"
updated_at: "2026-08-30T07:30:00+07:00"
owner: "SmartGift Data Architecture Team"
impacted_domains:
  - agent
  - tenant
  - workspace
  - knowledge
  - memory
proposed_domains:
  - catalog-vault
---

# CR-002 — Multi-Tier Scope Chain to GKS/MSP Catalog Vault Resolution

## 1. Change Summary

Establish the formal resolution bridge from **Zuri Application Scope Chain (`Workspace` / `Project`)** to **MSP (Tier 2)** and **GKS (Tier 3)** Catalog Knowledge Vaults, enabling AI Agents to query domain-specific product catalogs with sub-millisecond latency while enforcing a strict **Zero-PII Vector Vault Invariant**.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 1: Application & Scope Authority (zuri-ai)                                         │
│  • Scope Chain: Portfolio → Tenant (Org-EtohGroup) → Business (SmartGift) → Workspace    │
│  • Manages: CRM, Client PII, Financial Ledger Orders, Row Level Security (RLS)           │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (AuthContext / Server-Resolved Scope)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 2: Session, Memory & Vault Gatekeeper (MSP)                                        │
│  • API-010 (msp_vault_resolve): Maps workspace/project scope to Authorized Vault IDs     │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (Authorized Vault Set: [vlt-catalog-product])
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Canonical Knowledge & GraphRAG Orchestrator (GKS)                               │
│  • Governs: Entity Ontology, Schema Contracts (smartgift://b2b/portfolio/v1)             │
│  • GraphRAG Engine: Hybrid Dense Vector (bge-m3 1024-dim) + Graph Traversal (query-ir.v1)│
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ (In-Process Native Rust C-ABI)
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 4: Local Storage Substrate (GenesisBlockDB Native / SmartGift Vault)                │
│  • 6-Lane Substrate: Vector, Lexical, Graph, SQLite, Bitemporal, Provenance             │
│  • Invariant: Stores ONLY Product Masters, Gift Offers & Sensory Vectors (Zero-PII)      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Target Repositories & Action Items

### A. `D:\zuri-ai` (Tier 1: Prisma Schema & AuthContext)
1. **Extend `Workspace` model in `prisma/schema.prisma`:**
   ```prisma
   model Workspace {
     // ... existing fields ...
     catalogVaultId   String?   // UUIDv7 / vlt-catalog-product
     vaultNamespace   String?   // e.g. "smartgift://b2b/portfolio/v1"
   }
   ```
2. **Update AuthContext Resolver (`src/modules/agent/auth-context.js`):**
   * Pass `catalogVaultId` into request envelopes for B2B Catalog agent conversations.

### B. `D:\msp` (Tier 2: Memory Gatekeeper)
1. **Update API-010 `msp_vault_resolve`:**
   * Resolve `catalogVaultId` into the `Authorized Vault Set` for the active conversation turn.
   * Apply Security Ceilings (H0-H4) and Token Budget constraints.

### C. `D:\gks` (Tier 3: Knowledge Authority)
1. **Register Schema Contract:**
   * Register `smartgift://b2b/portfolio/v1` (v1.3.0) with Vector Spaces: `unboxing_sensory` (1024-dim `bge-m3`) and `product_features`.
2. **Query IR Routing:**
   * Dispatch compiled `query-ir.v1` requests directly to Edge Substrate.

---

## 3. Non-Negotiable Invariants

1. **Zero-PII in Vector Vaults:** `vlt-catalog-product` must store ONLY canonical product masters, gift offers, BOMs, and sensory vectors. NEVER store customer contacts or order histories in Vector Vaults.
2. **Canonical Identity Authority:** Never mint `gks:` prefixed references outside GKS.
