# ADR-001 — Refactoring pastel-series category to Eco-Friendly & Sustainability

**Status:** Approved  
**Date:** 2026-08-30  
**Decided by:** Boss ("เปลี่ยนเป็น eco friendly ดีไหม pastel-series มันดูหลุดจากอีก 3 อย่าง" → "ลุย", 2026-08-30)  
**Relates to:** [`smartgift_catalog_master.json`](file:///o:/Org-EtohGroup/SmartGift/data-pipeline/02_prepared/smartgift_catalog_master.json), [`pipeline/01_intake.py`](file:///o:/Org-EtohGroup/SmartGift/pipeline/01_intake.py), [`seed_genesisblock.mjs`](file:///o:/Org-EtohGroup/SmartGift/seed_genesisblock.mjs), [`config/schema_postgresql.sql`](file:///o:/Org-EtohGroup/SmartGift/config/schema_postgresql.sql)

---

## Context

In the SmartGift B2B product portfolio blueprint (2026), the top-level catalog originally defined 4 main categories:
1. `pastel-series` ("ชุดธีมสีพาสเทล")
2. `classic-oriental` ("ชุดศิลปะร่วมสมัยและตะวันออก")
3. `novelty-self-care` ("ชุด Novelty & Self-Care")
4. `executive-smart-tech` ("ชุดนวัตกรรมทางการทำงานอัจฉริยะ")

During catalog audit, a taxonomy inconsistency was identified: `pastel-series` was organized by **visual aesthetic/color tone (Pastel)**, whereas the remaining 3 categories were organized by **lifestyle, recipient persona, and functional purpose**:
- `executive-smart-tech`: Work & IT innovation persona
- `novelty-self-care`: Wellness & relaxation persona
- `classic-oriental`: Cultural craft, mindfulness & VIP recipient persona

Furthermore, B2B corporate gift buyers and enterprise procurement teams overwhelmingly prioritize **ESG & Sustainability (Green Procurement)**. Having a dedicated Eco-Friendly category directly aligns with corporate ESG budget allocations, whereas pastel-colored items fit naturally as a visual sub-variant within Eco or Wellness product lines.

---

## Decision

1. **Refactor `pastel-series` slug to `eco-friendly`.** Update the top-level category master definition:
   * **Slug:** `eco-friendly`
   * **Name (TH):** `ชุดผลิตภัณฑ์รักษ์โลกและสิ่งแวดล้อม (Eco-Friendly Series)`
   * **Name (EN):** `Eco-Friendly & Sustainability (Green & Earth)`
   * **Vibe:** `ยั่งยืน รักษ์โลก เป็นมิตรต่อธรรมชาติ`
   * **Target Recipient:** `องค์กรสาย ESG, แคมเปญเพื่อสิ่งแวดล้อม`
   * **Guardrail:** `เน้นใช้วัสดุรีไซเคิล ย่อยสลายได้ หรือลดขยะพลาสติก`
   * **Core Signatures:** `["กระบอกน้ำฟางข้าวพกพา", "สมุดปกกระดาษรีไซเคิล", "กระเป๋าผ้าแคนวาสออร์แกนิก", "ชุดช้อนส้อมพกพาวัสดุชีวภาพ"]`

2. **Cascading Data & Engine Refactoring:**
   * Update canonical products (`PM-TMB`, `PM-UMB`, `PM-BOTTLE-LED`, `PM-FAN`) and catalog offers (`TDD03-2`) in `data-pipeline/02_prepared/smartgift_catalog_master.json`.
   * Update intake script keyword mapping (`pipeline/01_intake.py`) to recognize `eco`, `รักษ์โลก`, `pastel`, `พาสเทล`.
   * Update GraphRAG agent keyword mapping (`src/graphrag_agent/smartgift_graphrag_agent.py`) and terminal UI menu (`demo_app.py`).
   * Update PostgreSQL schema DDL seed (`config/schema_postgresql.sql`).
   * Re-seed GenesisBlockDB graph nodes (`cat:eco-friendly`) and vector embeddings via `seed_genesisblock.mjs`.

---

## Consequences

- The 4 top-level categories now form a consistent 4-pillar B2B persona taxonomy:
  1. 💻 **Tech & Work** (`executive-smart-tech`)
  2. 🌿 **Wellness & Care** (`novelty-self-care`)
  3. 🎨 **Culture & Craft** (`classic-oriental`)
  4. ♻️ **Sustainability & Earth** (`eco-friendly`)
- AI GraphRAG search queries for ESG, eco-friendly, green, and sustainable corporate gifts route cleanly to `cat:eco-friendly`.
- Legacy `pastel` keywords continue to map gracefully to `eco-friendly` for backwards search compatibility.
