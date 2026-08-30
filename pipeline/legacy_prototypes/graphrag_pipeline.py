"""
SmartGift GraphRAG Hybrid Retrieval Pipeline
Combines Vector Similarity Search (Unboxing/Sensory Experience)
with Neo4j Knowledge Graph Traversal (Set Decomposition & Tier Rules).
"""

import os
from typing import Dict, Any, List
from neo4j import GraphDatabase

class SmartGiftGraphRAG:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_pass: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))

    def close(self):
        self.driver.close()

    def hybrid_retrieve(self, query_text: str, client_id: str = None, top_k: int = 3) -> Dict[str, Any]:
        """
        1. Semantic / Full-Text search to identify Anchor Offer nodes
        2. 2-Hop Graph Traversal to expand context (Components, MOQ, Tiers, Unboxing Notes)
        3. History Filtering (Avoid duplicate gifts for same client)
        """
        cypher_query = """
        // Step 1: Search relevant offers via Full-Text / Keyword on unboxing & description
        CALL db.index.fulltext.queryNodes("offer_search_idx", $query_text) YIELD node AS offer, score
        
        // Step 2: History Suppression (if client_id is provided)
        OPTIONAL MATCH (client:CorporateClient {client_id: $client_id})
        WHERE ($client_id IS NULL) OR NOT (client)-[:ORDERED]->(offer)

        // Step 3: Graph Traversal - Expand structured relationships
        OPTIONAL MATCH (offer)-[:BELONGS_TO_TIER]->(tier:GiftTier)
        OPTIONAL MATCH (offer)-[:CONTAINS]->(sku:SKU)-[:VARIANT_OF]->(pm:ProductMaster)-[:IN_CATEGORY]->(cat:Category)
        
        WITH offer, score, tier, 
             collect({
                 sku: sku.code, 
                 product_name: pm.name_th, 
                 category: cat.name_th
             }) AS components
        
        RETURN offer.code AS offer_code,
               offer.name AS offer_name,
               offer.unboxing_notes AS unboxing_experience,
               offer.base_price AS base_price,
               tier.name AS gift_tier,
               components,
               score
        ORDER BY score DESC
        LIMIT $top_k
        """

        with self.driver.session() as session:
            result = session.run(cypher_query, query_text=query_text, client_id=client_id, top_k=top_k)
            records = [record.data() for record in result]

        return records

    def build_llm_prompt(self, user_query: str, retrieved_context: List[Dict[str, Any]]) -> str:
        """
        Constructs a structured prompt for LLM generation
        """
        context_str = ""
        for idx, item in enumerate(retrieved_context, 1):
            comp_list = ", ".join([f"{c['product_name']} ({c['sku']})" for c in item['components']])
            context_str += f"""
---
[ตัวเลือกที่ {idx}]
- รหัสข้อเสนอ: {item['offer_code']}
- ชื่อชุดของขวัญ: {item['offer_name']}
- ระดับเทียร์: {item['gift_tier']}
- ราคาฐาน: {item['base_price']:,.2f} บาท
- ประสบการณ์เปิดกล่อง (Unboxing): {item['unboxing_experience']}
- รายการชิ้นส่วนจริงข้างใน: {comp_list}
"""

        prompt = f"""คุณคือผู้เชี่ยวชาญด้านการจัดสรรแคมเปญของขวัญองค์กร (Corporate Gift Consultant) ของ SmartGift
โปรดตอบคำถามของลูกค้าโดยใช้ข้อมูลความสัมพันธ์จริงจาก Knowledge Graph ด้านล่างนี้:

[คำถาม/ความต้องการของลูกค้า]:
"{user_query}"

[ข้อมูลบริบทจาก Knowledge Graph & Unboxing Engineering]:
{context_str}

[คำแนะนำในการตอบ]:
1. แนะนำชุดของขวัญที่ตรงกับความต้องการและระดับตำแหน่งผู้รับ
2. อธิบายจุดเด่นเรื่อง Unboxing Experience (สัมผัส กลิ่น การเปิดกล่อง) ให้เห็นภาพชัดเจน
3. แจกแจงชิ้นส่วนของขวัญจริงในเซ็ต พร้อมระบุเงื่อนไขราคาอย่างเป็นมืออาชีพ
"""
        return prompt


# Example Usage (Demo Simulation)
if __name__ == "__main__":
    print("SmartGift GraphRAG Pipeline Initialized.")
    print("Ready to connect to Neo4j and execute hybrid contextual retrieval.")
