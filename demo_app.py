"""
SmartGift B2B Interactive Terminal & Demonstration App
Integrated with GenesisBlockDB Knowledge Graph, Cascade Waterfall Inventory Engine,
and Local Thai LLMs on Ollama.
"""

import os
import sys
import json
try:
    from src.cascade_engine import InventoryCascadeEngine
    from src.graphrag_agent import SmartGiftGraphRAGAgent
except ImportError:
    from inventory_cascade_engine import InventoryCascadeEngine
    from smartgift_graphrag_agent import SmartGiftGraphRAGAgent

sys.stdout.reconfigure(encoding='utf-8')

def print_header(title: str):
    print("\n" + "="*70)
    print(f"  🎁 {title.upper()}")
    print("="*70)

def main():
    print_header("SmartGift B2B Intelligent Portfolio & Inventory System")
    print("  Architecture Pattern: Option B (Supabase Cloud PostgreSQL + GenesisBlock Edge)")
    print("  Search Engine: GenesisBlockDB (Embedded Native Graph + HNSW Substrate < 1ms)")
    print("  Transactional Engine: Supabase / PostgreSQL Cascade Waterfall Inventory")
    print("  AI Model: Local Thai LLM (Pathumma / Typhoon-S via Ollama)")
    
    inv_engine = InventoryCascadeEngine()
    agent = SmartGiftGraphRAGAgent()

    while True:
        print("\n" + "-"*70)
        print("กรุณาเลือกฟังก์ชันที่ต้องการทดสอบ:")
        print("  [1] ค้นหาชุดของขวัญตามความรู้สึก & Unboxing Experience (GraphRAG Search)")
        print("  [2] จำลองการสั่งซื้อ Corporate Bundle & ตัดสต็อก Cascade Waterfall")
        print("  [3] ปรึกษาและออกใบเสนอราคาอัตโนมัติด้วย Local Thai LLM (AI Consultant)")
        print("  [4] ตรวจสอบยอดสต็อกชิ้นส่วนจริงคงเหลือในคลัง (Physical SKU Inventory)")
        print("  [0] ออกจากโปรแกรม (Exit)")
        print("-"*70)

        try:
            choice = input("ป้อนหมายเลขเมนู (0-4): ").strip()
        except EOFError:
            break

        if choice == "0":
            print("\nขอบคุณที่ใช้งาน SmartGift Architecture System ครับ!")
            break

        elif choice == "1":
            print_header("ค้นหาและคัดกรองสินค้าตาม Top Level 4 หมวดหลัก (Interest Themes 2026 Blueprint)")
            print("  หมวดสินค้าหลัก 4 ธีม:")
            print("    [1] Pastel Series (Soft & Friendly — ชุดสีพาสเทล อ่อนหวาน ละมุน)")
            print("    [2] Classic Oriental (Mindfulness & Craft — ชุดศิลปะร่วมสมัยและตะวันออก)")
            print("    [3] Novelty & Self-Care (Warm & Wellness — ชุดผ่อนคลาย อบอุ่น สุขภาพ)")
            print("    [4] Executive Smart Tech (Modern & Work — ชุดนวัตกรรมไอทีอัจฉริยะ)")
            print("    [Enter] ค้นหาอิสระทุกหมวดสินค้า")
            
            cat_choice = input("\nเลือกหมวดสินค้า (1-4) หรือกด Enter เพื่อค้นหาอิสระ: ").strip()
            cat_map = {
                "1": ("pastel-series", "Pastel Series (Soft & Friendly)"),
                "2": ("classic-oriental", "Classic Oriental (Mindfulness & Craft)"),
                "3": ("novelty-self-care", "Novelty & Self-Care (Warm & Wellness)"),
                "4": ("executive-smart-tech", "Executive Smart Tech (Modern & Work)")
            }
            selected_slug, selected_name = cat_map.get(cat_choice, (None, "ทุกหมวดสินค้า"))

            query = input("ป้อนคำค้นหาเพิ่มเติม (เช่น 'เครื่องนวดคอ สมุดอัจฉริยะ ร่มพาสเทล'): ").strip()
            if not query:
                query = selected_name if selected_name != "ทุกหมวดสินค้า" else "เครื่องนวดคอ สมุดอัจฉริยะ"
            
            results = agent.search_relevant_offers(query, top_k=4, category_slug=selected_slug)
            print(f"\nผลลัพธ์การค้นหาในหมวด '{selected_name}' ({len(results)} รายการ):")
            for idx, r in enumerate(results, 1):
                print(f"\n  [{idx}] {r['offer_code']} — {r['name']}")
                print(f"      หมวดหลัก (Top Level): {r.get('interest_theme', 'General')}")
                print(f"      ระดับเทียร์: {r['gift_tier']}")
                print(f"      ความรู้สึกเปิดกล่อง (Unboxing): {r['unboxing_experience']}")
                print("      ขั้นบันไดราคาขายส่ง (MOQ Price Tiers):")
                for pt in r.get("price_tiers", [])[:3]:
                    print(f"        • ขั้นต่ำ {pt['min_qty']} ชุด: ราคา ฿{pt['unit_price']:,.2f}/ชุด")

        elif choice == "2":
            print_header("จำลองการสั่งซื้อ Corporate Bundle & ตัดสต็อก Cascade Waterfall")
            print("แพ็กเกจที่มีให้เลือก:")
            for b in inv_engine.data.get("corporate_bundles", []):
                print(f"  • {b['bundle_code']}: {b['name']} (฿{b['total_price']:,.2f} สำหรับ {b['target_recipients']} ท่าน)")
            
            bcode = input("\nป้อนรหัสแพ็กเกจ (กด Enter สำหรับ PKG-SME-ELITE): ").strip()
            if not bcode:
                bcode = "PKG-SME-ELITE"
            
            qty_str = input("ป้อนจำนวนแพ็กเกจที่ต้องการสั่งซื้อ (กด Enter สำหรับ 1): ").strip()
            qty = int(qty_str) if qty_str.isdigit() else 1

            print(f"\nกำลังประมวลผล Cascade Waterfall สำหรับ {bcode} x {qty} แพ็กเกจ...")
            try:
                order_res = inv_engine.execute_order_deduction(bcode, qty)
                print(f"\n✅ สถานะคำสั่งซื้อ: {order_res['order_status']}")
                print(f"   ยอดรวมทั้งสิ้น: ฿{order_res['total_selling_price']:,.2f}")
                print(f"   ต้นทุนชิ้นส่วนจริงรวม: ฿{order_res['total_cost_price']:,.2f}")
                print(f"   กำไรขั้นต้น (Gross Margin): ฿{order_res['gross_profit']:,.2f} ({order_res['gross_margin_percent']}%)")
                
                print("\n📦 รายการตัดสต็อกสินค้าจริงระดับชิ้นส่วนในคลัง (Real-time SKU Deduction):")
                for sku in order_res["physical_sku_deductions"]:
                    print(f"   • [{sku['product_code']}] {sku['name_th']}: หักออก {sku['total_units_required']} ชิ้น -> คงเหลือ {sku['remaining_stock']} ชิ้น")
            except Exception as e:
                print(f"\n❌ เกิดข้อผิดพลาดในการตัดสต็อก: {e}")

        elif choice == "3":
            print_header("AI Corporate Consultant & Quotation Generator (Local Thai LLM)")
            client_name = input("ป้อนชื่อบริษัทลูกค้า (เช่น บริษัท เทค โซลูชั่น จำกัด): ").strip()
            if not client_name:
                client_name = "บริษัท เทค โซลูชั่น จำกัด"
            
            query = input("ป้อนโจทย์ความต้องการ (เช่น ต้องการของขวัญปีใหม่ผู้บริหาร 5 คน หัวหน้า 10 คน ทีมงาน 20 คน งบ 45,000): ").strip()
            if not query:
                query = "ต้องการของขวัญปีใหม่ผู้บริหาร 5 คน หัวหน้า 10 คน ทีมงาน 20 คน รวม 35 คน งบประมาณ 45,000-50,000 บาท ขอชุดที่ดูโมเดิร์น ไฮเทค และสุขภาพ"

            print(f"\nกำลังเรียกใช้ Knowledge Substrate และ Local Thai LLM เพื่อร่างใบเสนอราคา...")
            result = agent.generate_consultation_and_quotation(query, client_name=client_name)
            
            print("\n" + "="*70)
            print(f"📄 ร่างใบเสนอราคาและบทสรุปแคมเปญ (เรียน {client_name}):")
            print("="*70)
            print(result["llm_proposal_response"])

        elif choice == "4":
            print_header("ยอดสต็อกชิ้นส่วนจริงคงเหลือในคลัง (Physical SKU Stock)")
            print(f"{'รหัสสินค้า':<15} {'ชื่อสินค้าจริง':<45} {'จำนวนคงเหลือ':<10}")
            print("-" * 70)
            for pcode, stock in inv_engine.inventory.items():
                pinfo = inv_engine.products.get(pcode, {})
                name = pinfo.get("name_th", pcode)[:42]
                print(f"{pcode:<15} {name:<45} {stock:<10} ชิ้น")

        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาเลือกใหม่ครับ")

if __name__ == "__main__":
    main()
