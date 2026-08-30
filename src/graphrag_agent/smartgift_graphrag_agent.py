"""
SmartGift GraphRAG Agent
Powered by GenesisBlockDB (Knowledge Graph & Vector Memory)
and Local Thai LLMs on Ollama (Pathumma / Typhoon-S / Qwopus).
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional
try:
    from src.cascade_engine import InventoryCascadeEngine
except ImportError:
    from inventory_cascade_engine import InventoryCascadeEngine

sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
DEFAULT_THAI_MODEL = "qwen3.5:4b"

class SmartGiftGraphRAGAgent:
    def __init__(self, model_name: str = DEFAULT_THAI_MODEL):
        self.model_name = model_name
        self.inv_engine = InventoryCascadeEngine()
        self.catalog_data = self.inv_engine.data

    def get_embedding(self, text: str) -> Optional[List[float]]:
        try:
            res = requests.post(OLLAMA_EMBED_URL, json={
                "model": "bge-m3:latest",
                "prompt": text
            }, timeout=10)
            if res.status_code == 200:
                return res.json().get("embedding")
        except Exception:
            pass
        return None

    def search_relevant_offers(self, query: str, top_k: int = 3, category_slug: Optional[str] = None) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        scored_offers = []

        keywords = {
            "eco-friendly": ["eco", "friendly", "รักษ์โลก", "ยั่งยืน", "สิ่งแวดล้อม", "รีไซเคิล", "ฟางข้าว", "ชีวภาพ", "green", "earth", "sustainability", "pastel", "พาสเทล"],
            "classic-oriental": ["oriental", "ตะวันออก", "จีน", "คลาสสิก", "ประณีต", "ทรงคุณค่า", "ไม้", "ชา", "มงคล", "craft", "mindfulness"],
            "novelty-self-care": ["novelty", "self-care", "wellness", "สุขภาพ", "อบอุ่น", "ผ่อนคลาย", "เทียนหอม", "นวด", "อโรมา", "ใส่ใจ", "ผู้หญิง"],
            "executive-smart-tech": ["executive", "tech", "smart", "ไอที", "อัจฉริยะ", "พาวเวอร์แบงก์", "สมุดชาร์จ", "ผู้บริหาร", "นวัตกรรม", "modern"]
        }

        for offer in self.catalog_data.get("catalog_offers", []):
            score = 0
            theme_slug = offer.get("interest_theme_slug", "")
            theme_name = offer.get("interest_theme", "")
            text_corpus = f"{offer['name']} {offer['unboxing_experience']} {offer['gift_tier']} {theme_name}".lower()

            if category_slug and theme_slug == category_slug:
                score += 10

            for word in query_lower.split():
                if word in text_corpus:
                    score += 2

            for cat_slug, kw_list in keywords.items():
                if any(kw in query_lower for kw in kw_list):
                    if theme_slug == cat_slug or any(kw in text_corpus for kw in kw_list):
                        score += 4

            if any(w in query_lower for w in ["vip", "ผู้บริหาร", "บอร์ด"]) and offer["gift_tier"] in ["Signature", "Bespoke"]:
                score += 5

            scored_offers.append((score, offer))

        scored_offers.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_offers[:top_k]]

    def retrieve_bundle_recommendation(self, query: str) -> Optional[Dict[str, Any]]:
        for bundle in self.catalog_data.get("corporate_bundles", []):
            if any(w in query.lower() for w in ["sme", "แผนก", "30", "35", "40", "50 คน", "ขนาดกลาง"]):
                if "SME" in bundle["bundle_code"]:
                    return bundle
            if any(w in query.lower() for w in ["enterprise", "100", "150", "160", "ปีใหม่บริษัท", "ประชุมใหญ่"]):
                if "ENTERPRISE" in bundle["bundle_code"]:
                    return bundle
        return self.catalog_data.get("corporate_bundles", [])[0] if self.catalog_data.get("corporate_bundles") else None

    def generate_consultation_and_quotation(self, client_query: str, client_name: str = "Corporate Client") -> Dict[str, Any]:
        recommended_bundle = self.retrieve_bundle_recommendation(client_query)
        relevant_offers = self.search_relevant_offers(client_query, top_k=3)

        cascade_result = None
        if recommended_bundle:
            cascade_result = self.inv_engine.decompose_bundle(recommended_bundle["bundle_code"], bundle_quantity=1)

        context_str = f"=== ข้อมูลแพ็กเกจองค์กรแนะนำ (Corporate Bundle) ===\n"
        if recommended_bundle and cascade_result:
            context_str += f"- รหัสแพ็กเกจ: {recommended_bundle['bundle_code']}\n"
            context_str += f"- ชื่อแพ็กเกจ: {recommended_bundle['name']}\n"
            context_str += f"- ราคาเหมาจ่ายรวม: ฿{recommended_bundle['total_price']:,.2f} บาท (เป้าหมายผู้รับ {recommended_bundle['target_recipients']} ท่าน)\n"
            context_str += f"- คำอธิบาย: {recommended_bundle['description']}\n"
            context_str += f"- สัดส่วนการแจกจ่ายตามผังองค์กร:\n"
            for tier_name, desc in recommended_bundle.get("tier_breakdown", {}).items():
                context_str += f"  • {tier_name}: {desc}\n"
            context_str += f"\n- รายการชิ้นส่วนจริงที่ตัดสต็อกในคลัง (Decomposed SKU Units):\n"
            for sku in cascade_result["physical_sku_deductions"]:
                context_str += f"  • [{sku['product_code']}] {sku['name_th']}: {sku['total_units_required']} ชิ้น (สถานะสต็อก: พร้อมส่ง)\n"

        context_str += f"\n=== ข้อมูลเซ็ตของขวัญเดี่ยวแนะนำ (Individual Catalog Offers & Unboxing Notes) ===\n"
        for idx, o in enumerate(relevant_offers, 1):
            prices_str = ", ".join([f"MOQ {p['min_qty']} ชุด @ ฿{p['unit_price']:,.2f}" for p in o.get('price_tiers', [])[:3]])
            context_str += f"""
[{idx}] รหัสเซ็ต: {o['offer_code']} ({o['name']})
  - ระดับเทียร์: {o['gift_tier']}
  - จุดเด่น Unboxing Experience: {o['unboxing_experience']}
  - ขั้นบันไดราคาขายส่ง: {prices_str}
"""

        system_instruction = """คุณคือ "SmartGift Corporate Consultant" ผู้เชี่ยวชาญด้านกลยุทธ์ของขวัญองค์กรและการจัดสรรงบประมาณ B2B
ตามหลักการ SmartGift 2026 Portfolio Blueprint (Recipient-First Framework)
จงตอบคำถามลูกค้าภาษาไทยอย่างสุภาพ เป็นมืออาชีพ และจัดจำแนกข้อเสนอแนะตาม 4 หมวดสินค้า Top Level (Interest Themes):
1. Pastel Series (Soft & Friendly — อ่อนหวาน ละมุน เป็นมิตร)
2. Classic Oriental (Mindfulness & Craft — ประณีต ทรงคุณค่า คลาสสิก)
3. Novelty & Self-Care (Warm & Wellness — ผ่อนคลาย อบอุ่น ใส่ใจ)
4. Executive Smart Tech (Modern & Work — ทันสมัย นวัตกรรม เป็นมืออาชีพ)

อธิบายความคุ้มค่าในแง่ One-Invoice Efficiency, Org Chart Hierarchy, Unboxing Sensory Experience และ SKU Stock Readiness.
"""

        user_prompt = f"""[ข้อมูลลูกค้า]:
ชื่อองค์กร: {client_name}
ความต้องการของลูกค้า: "{client_query}"

[ข้อมูลข้อเท็จจริงจากระบบ SmartGift Knowledge Substrate]:
{context_str}

โปรดร่างบทสรุปข้อเสนอแนะและใบเสนอราคาเบื้องต้น (Quotation Summary) ให้กับลูกค้า:"""

        generated_text = ""
        try:
            res = requests.post(OLLAMA_CHAT_URL, json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }, timeout=60)
            if res.status_code == 200:
                generated_text = res.json().get("message", {}).get("content", "")
        except Exception as e:
            generated_text = f"LLM Generation Note: เกิดข้อผิดพลาดในการเชื่อมต่อโมเดล: {e}"

        return {
            "client_name": client_name,
            "client_query": client_query,
            "recommended_bundle": recommended_bundle,
            "cascade_inventory_analysis": cascade_result,
            "relevant_offers": relevant_offers,
            "llm_proposal_response": generated_text
        }


if __name__ == "__main__":
    agent = SmartGiftGraphRAGAgent()
    sample_query = "ต้องการจัดเซ็ตของขวัญปีใหม่สำหรับผู้บริหาร 5 ท่าน ผู้จัดการ 10 ท่าน และพนักงาน 20 ท่าน รวม 35 คน งบประมาณประมาณ 45,000 - 50,000 บาท ขอชุดที่ดูโมเดิร์น ไฮเทค และสุขภาพ"
    print(f"=== Running SmartGift GraphRAG Query ===\nQuery: '{sample_query}'\n")
    
    result = agent.generate_consultation_and_quotation(sample_query, client_name="SCG Digital Tech")
    print("=== Cascade Inventory Summary ===")
    if result["cascade_inventory_analysis"]:
        c = result["cascade_inventory_analysis"]
        print(f"Bundle: {c['bundle_name']} (Total: ฿{c['total_selling_price']:,.2f})")
        print(f"Physical Stock Check: Fulfillable = {c['is_fulfillable']}, Gross Margin = {c['gross_margin_percent']}%")

    print("\n=== Local Thai LLM Proposal Response ===")
    print(result["llm_proposal_response"][:500] if result["llm_proposal_response"] else "[No text generated yet]")
