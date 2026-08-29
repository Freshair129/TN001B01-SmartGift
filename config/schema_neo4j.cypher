// ============================================================================
// SmartGift Knowledge Graph & GraphRAG Schema (Neo4j Cypher)
// ============================================================================

// 1. CONSTRAINTS & INDEXES
CREATE CONSTRAINT unique_category_slug IF NOT EXISTS
FOR (c:Category) REQUIRE c.slug IS UNIQUE;

CREATE CONSTRAINT unique_product_code IF NOT EXISTS
FOR (p:ProductMaster) REQUIRE p.code IS UNIQUE;

CREATE CONSTRAINT unique_sku_code IF NOT EXISTS
FOR (s:SKU) REQUIRE s.code IS UNIQUE;

CREATE CONSTRAINT unique_offer_code IF NOT EXISTS
FOR (o:CatalogOffer) REQUIRE o.code IS UNIQUE;

CREATE CONSTRAINT unique_bundle_code IF NOT EXISTS
FOR (b:BundleOffer) REQUIRE b.code IS UNIQUE;

CREATE CONSTRAINT unique_client_id IF NOT EXISTS
FOR (cl:CorporateClient) REQUIRE cl.client_id IS UNIQUE;

// Full-text Index for Keyword & Unboxing Experience Search
CREATE FULLTEXT INDEX offer_search_idx IF NOT EXISTS
FOR (o:CatalogOffer) ON EACH [o.name, o.description, o.unboxing_notes];

// Vector Index for GraphRAG Hybrid Retrieval (Neo4j 5+)
// Embedding Dimension: 1536 (OpenAI text-embedding-3-small) or 768 (Ollama / Nomic / bge-m3)
CREATE VECTOR INDEX offer_embeddings IF NOT EXISTS
FOR (o:CatalogOffer) ON (o.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

// ============================================================================
// 2. SAMPLE SEED DATA CREATION
// ============================================================================

// Top-Level 4 Main Categories (Interest Themes 2026 Blueprint)
MERGE (catPastel:Category {name_th: "ชุดธีมสีพาสเทล (Pastel Series)", name_en: "Pastel Series (Soft & Friendly)", slug: "pastel-series", vibe: "Soft & Friendly"})
MERGE (catOriental:Category {name_th: "ชุดศิลปะร่วมสมัยและตะวันออก (Classic Oriental)", name_en: "Classic Oriental (Mindfulness & Craft)", slug: "classic-oriental", vibe: "Mindfulness & Craft"})
MERGE (catNovelty:Category {name_th: "ชุด Novelty & Self-Care", name_en: "Novelty & Self-Care (Warm & Wellness)", slug: "novelty-self-care", vibe: "Warm & Wellness"})
MERGE (catExecutive:Category {name_th: "ชุดนวัตกรรมทางการทำงานอัจฉริยะ (Executive Smart Tech)", name_en: "Executive Smart Tech (Modern & Work)", slug: "executive-smart-tech", vibe: "Modern & Work"})

MERGE (tierReach:GiftTier {name: "Reach", priority: 1, budget_tier: "Economy/Mass"})
MERGE (tierSelect:GiftTier {name: "Select", priority: 2, budget_tier: "Standard/Team"})
MERGE (tierSignature:GiftTier {name: "Signature", priority: 3, budget_tier: "Premium/Executive"})
MERGE (tierBespoke:GiftTier {name: "Bespoke", priority: 4, budget_tier: "Ultra-VIP"})

// Recipient Segments
MERGE (segVIP:RecipientSegment {name: "VIP / Board of Directors", level: "C-Level"})
MERGE (segExec:RecipientSegment {name: "Executive / Manager", level: "Mid-Management"})
MERGE (segStaff:RecipientSegment {name: "General Staff / Mass Event", level: "Operations"})

MERGE (segVIP)-[:RECOMMENDED_TIER]->(tierBespoke)
MERGE (segExec)-[:RECOMMENDED_TIER]->(tierSignature)
MERGE (segStaff)-[:RECOMMENDED_TIER]->(tierReach)

// Product Masters & SKUs
MERGE (pmNB:ProductMaster {code: "PM-NB-01", name_th: "สมุดโน้ตอัจฉริยะฝังพาวเวอร์แบงก์", name_en: "Smart Powerbank Notebook"})
MERGE (pmNB)-[:IN_CATEGORY]->(catExecutive)

MERGE (pmPen:ProductMaster {code: "PM-PEN-01", name_th: "ปากกาบอดี้ไม้แท้หัวทองเหลือง", name_en: "Brass Wood Executive Pen"})
MERGE (pmPen)-[:IN_CATEGORY]->(catOriental)

MERGE (pmMassage:ProductMaster {code: "PM-MSG-01", name_th: "เครื่องนวดคอพกพาระบบ Low Pulse", name_en: "Portable Low Pulse Neck Massager"})
MERGE (pmMassage)-[:IN_CATEGORY]->(catNovelty)

MERGE (skuNB_Blk:SKU {code: "VAR-NB-TNR003-BLK", color: "Midnight Black", battery: "10000mAh"})
MERGE (skuNB_Blk)-[:VARIANT_OF]->(pmNB)

MERGE (skuPen_Wd:SKU {code: "VAR-PEN-WD-BRS", material: "Solid Walnut & Brass"})
MERGE (skuPen_Wd)-[:VARIANT_OF]->(pmPen)

MERGE (skuMsg_Wht:SKU {code: "VAR-MSG-TJM02-WHT", mode_count: 5, heat_level: "Constant 42C"})
MERGE (skuMsg_Wht)-[:VARIANT_OF]->(pmMassage)

// Catalog Set Offer (Signature Tech x Care: TGC06-4)
MERGE (setTGC06:CatalogOffer {
    code: "TGC06-4",
    name: "Signature Executive & Wellness Set",
    unboxing_notes: "กล่องแม่เหล็กพรีเมียมสี Navy Blue บุโฟม EVA กำมะหยี่สีดำ พร้อมกลิ่นหอมอโรมาโรสเบาๆ เมื่อเปิดฝา",
    base_price: 930.00
})
MERGE (setTGC06)-[:BELONGS_TO_TIER]->(tierSignature)
MERGE (setTGC06)-[:CONTAINS {qty: 1}]->(skuNB_Blk)
MERGE (setTGC06)-[:CONTAINS {qty: 1}]->(skuPen_Wd)
MERGE (setTGC06)-[:CONTAINS {qty: 1}]->(skuMsg_Wht)
MERGE (setTGC06)-[:MATCHES_THEME]->(catExecutive)
MERGE (setTGC06)-[:MATCHES_THEME]->(catNovelty)

// Corporate Bundle (SME Elite Package A)
MERGE (bundleA:BundleOffer {
    code: "PKG-SME-ELITE",
    name: "SME Elite Bundle (Package A)",
    total_price: 46250.00,
    target_count: 35
})
MERGE (bundleA)-[:INCLUDES_OFFER {qty: 10}]->(setTGC06)

// ============================================================================
// 3. ESSENTIAL QUERY PATTERNS FOR GRAPH & GRAPHRAG
// ============================================================================

// Query 1: Set Decomposition (แตกชิ้นส่วนเซ็ตของขวัญ)
MATCH (offer:CatalogOffer {code: "TGC06-4"})-[r:CONTAINS]->(sku:SKU)-[:VARIANT_OF]->(pm:ProductMaster)-[:IN_CATEGORY]->(cat:Category)
RETURN offer.name AS Set_Name,
       sku.code AS SKU_Code,
       pm.name_th AS Product_Name,
       cat.name_th AS Category,
       r.qty AS Quantity;

// Query 2: Bundle Composition Waterfall (แตกแพ็กเกจองค์กรสู่ชิ้นส่วนจริง)
MATCH (b:BundleOffer {code: "PKG-SME-ELITE"})-[br:INCLUDES_OFFER]->(set:CatalogOffer)-[sr:CONTAINS]->(sku:SKU)-[:VARIANT_OF]->(pm:ProductMaster)
RETURN b.name AS Bundle_Name,
       set.name AS Included_Set,
       br.qty AS Set_Quantity,
       sku.code AS Component_SKU,
       pm.name_th AS Component_Name,
       (br.qty * sr.qty) AS Total_Units_Deducted;

// Query 3: Smart Recommendation with History Suppression (หลีกเลี่ยงการให้ของขวัญซ้ำ)
MATCH (client:CorporateClient {client_id: "CLIENT-SCG-001"})
MATCH (segment:RecipientSegment {name: "VIP / Board of Directors"})-[:RECOMMENDED_TIER]->(targetTier:GiftTier)
MATCH (recOffer:CatalogOffer)-[:BELONGS_TO_TIER]->(targetTier)
WHERE NOT (client)-[:ORDERED]->(recOffer)
RETURN recOffer.code AS Code, recOffer.name AS Offer_Name, recOffer.unboxing_notes AS Experience
LIMIT 3;

// Query 4: GraphRAG 2-Hop Context Expansion from Anchor Node
MATCH (anchor:CatalogOffer {code: "TGC06-4"})
OPTIONAL MATCH (anchor)-[:BELONGS_TO_TIER]->(tier:GiftTier)
OPTIONAL MATCH (anchor)-[:CONTAINS]->(sku:SKU)-[:VARIANT_OF]->(pm:ProductMaster)
OPTIONAL MATCH (anchor)-[:MATCHES_THEME]->(cat:Category)
RETURN anchor.name AS OfferName,
       anchor.unboxing_notes AS Unboxing,
       tier.name AS Tier,
       collect(DISTINCT pm.name_th) AS Products,
       collect(DISTINCT cat.name_th) AS Themes;
