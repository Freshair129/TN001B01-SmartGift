"""
SmartGift B2B Inventory Cascade Waterfall Engine
Decomposes Corporate Bundles and Gift Sets down to physical SKU stock levels,
verifies inventory availability, and calculates real-time profit margins.
"""

import json
import os
from typing import Dict, Any, List, Tuple

CATALOG_JSON_PATH = "smartgift_catalog_master.json"

class InventoryCascadeEngine:
    def __init__(self, catalog_path: str = CATALOG_JSON_PATH):
        self.catalog_path = catalog_path
        self.load_catalog()
        self.init_virtual_inventory()

    def load_catalog(self):
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"Catalog file not found: {self.catalog_path}")
        
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.products = {p["code"]: p for p in self.data.get("canonical_products", [])}
        self.offers = {o["offer_code"]: o for o in self.data.get("catalog_offers", [])}
        self.bundles = {b["bundle_code"]: b for b in self.data.get("corporate_bundles", [])}

    def init_virtual_inventory(self):
        """Initializes simulated in-stock physical units for all canonical products"""
        self.inventory: Dict[str, int] = {
            "PM-TMB": 500,       # แก้วทัมเบลอร์ SUS316
            "PM-SPK": 350,       # ลำโพงบลูทูธ 5W
            "PM-PB10K": 400,     # พาวเวอร์แบงก์ 10,000mAh
            "PM-CFMUG": 450,     # แก้วกาแฟ 3-Way
            "PM-UMB": 600,       # ร่มพับ UPF50+
            "PM-MSG": 250,       # เครื่องนวดคอ Low Pulse
            "PM-NB": 300,        # สมุดโน้ตอัจฉริยะ Powerbank
            "PM-PEN": 800,       # ปากกาไม้แท้หัวทองเหลือง
            "PM-MUG-HEAT": 300,  # แก้วอุ่น 55C
            "PM-FLASH": 500,     # แฟลชไดรฟ์หมุน Dual
            "PM-BOTTLE-LED": 400,# กระบอกน้ำ Smart LED
            "PM-CUTLERY": 600,   # ชุดช้อนส้อมพกพา
            "PM-TEA-INF": 250,   # กระบอกชงชาแก้ว
            "PM-AROMA": 200,     # เครื่องอโรมาเปลวไฟ
            "PM-FAN": 350,       # พัดลมมินิมอลดิจิทัล
            "PM-DESK-MAT": 200   # แผ่นรองโต๊ะชาร์จไร้สาย
        }

    def decompose_set(self, offer_code: str, set_quantity: int = 1) -> List[Dict[str, Any]]:
        """
        Decomposes a Gift Set into its physical item components.
        Returns: list of {product_code, name_th, unit_qty, total_needed, unit_cost, total_cost}
        """
        offer = self.offers.get(offer_code)
        if not offer:
            raise ValueError(f"CatalogOffer '{offer_code}' not found.")

        breakdown = []
        for comp in offer.get("components", []):
            pcode = comp["product_code"]
            unit_qty = comp.get("qty", 1)
            total_needed = unit_qty * set_quantity
            prod_info = self.products.get(pcode, {})
            unit_cost = prod_info.get("base_cost", 0.0)

            breakdown.append({
                "product_code": pcode,
                "name_th": prod_info.get("name_th", pcode),
                "category": prod_info.get("category", "General"),
                "unit_qty_per_set": unit_qty,
                "total_qty_needed": total_needed,
                "unit_cost": unit_cost,
                "total_cost": unit_cost * total_needed
            })
        return breakdown

    def decompose_bundle(self, bundle_code: str, bundle_quantity: int = 1) -> Dict[str, Any]:
        """
        Decomposes a Corporate Meta-Bundle into its child sets,
        and cascades down to individual physical SKU/Product items.
        """
        bundle = self.bundles.get(bundle_code)
        if not bundle:
            raise ValueError(f"CorporateBundle '{bundle_code}' not found.")

        included_offers = bundle.get("included_offers", [])
        sets_breakdown = []
        aggregated_skus: Dict[str, Dict[str, Any]] = {}

        total_physical_cost = 0.0

        for inc in included_offers:
            offer_code = inc["offer_code"]
            qty_per_bundle = inc["qty"]
            total_sets = qty_per_bundle * bundle_quantity

            # Decompose each set
            comps = self.decompose_set(offer_code, total_sets)
            set_info = self.offers.get(offer_code, {})

            set_cost = sum(c["total_cost"] for c in comps)
            total_physical_cost += set_cost

            sets_breakdown.append({
                "offer_code": offer_code,
                "offer_name": set_info.get("name", offer_code),
                "tier": set_info.get("gift_tier", "Standard"),
                "sets_count": total_sets,
                "components": comps,
                "subtotal_cost": set_cost
            })

            # Aggregate to SKU level
            for c in comps:
                pcode = c["product_code"]
                if pcode not in aggregated_skus:
                    aggregated_skus[pcode] = {
                        "product_code": pcode,
                        "name_th": c["name_th"],
                        "category": c["category"],
                        "total_units_required": 0,
                        "unit_cost": c["unit_cost"],
                        "total_cost": 0.0,
                        "current_stock": self.inventory.get(pcode, 0)
                    }
                aggregated_skus[pcode]["total_units_required"] += c["total_qty_needed"]
                aggregated_skus[pcode]["total_cost"] += c["total_cost"]

        # Check stock availability
        is_fulfillable = True
        shortages = []
        for pcode, sku_data in aggregated_skus.items():
            if sku_data["total_units_required"] > sku_data["current_stock"]:
                is_fulfillable = False
                shortages.append({
                    "product_code": pcode,
                    "name_th": sku_data["name_th"],
                    "required": sku_data["total_units_required"],
                    "available": sku_data["current_stock"],
                    "shortage": sku_data["total_units_required"] - sku_data["current_stock"]
                })

        total_selling_price = bundle.get("total_price", 0.0) * bundle_quantity
        gross_profit = total_selling_price - total_physical_cost
        margin_percent = (gross_profit / total_selling_price * 100) if total_selling_price > 0 else 0

        return {
            "bundle_code": bundle_code,
            "bundle_name": bundle["name"],
            "order_quantity": bundle_quantity,
            "total_recipients": bundle.get("target_recipients", 0) * bundle_quantity,
            "total_selling_price": total_selling_price,
            "total_cost_price": total_physical_cost,
            "gross_profit": gross_profit,
            "gross_margin_percent": round(margin_percent, 2),
            "is_fulfillable": is_fulfillable,
            "stock_shortages": shortages,
            "sets_breakdown": sets_breakdown,
            "physical_sku_deductions": list(aggregated_skus.values())
        }

    def execute_order_deduction(self, bundle_code: str, bundle_quantity: int = 1, order_id: str = None) -> Dict[str, Any]:
        """
        Executes real physical stock deduction if fulfillable,
        recording ID-bound audit provenance logs for traceability.
        """
        import uuid
        from datetime import datetime, timezone

        result = self.decompose_bundle(bundle_code, bundle_quantity)
        if not result["is_fulfillable"]:
            raise RuntimeError(f"Cannot fulfill order: Stock shortage for items: {result['stock_shortages']}")

        deduction_id = str(uuid.uuid4())
        resolved_order_id = order_id if order_id else f"ORD-{uuid.uuid4().hex[:8].upper()}"
        timestamp_iso = datetime.now(timezone.utc).isoformat()

        # Deduct from inventory
        deduction_logs = []
        for sku_data in result["physical_sku_deductions"]:
            pcode = sku_data["product_code"]
            qty = sku_data["total_units_required"]
            self.inventory[pcode] -= qty
            sku_data["remaining_stock"] = self.inventory[pcode]

            deduction_logs.append({
                "deduction_id": deduction_id,
                "order_id": resolved_order_id,
                "tenant_id": "Org-EtohGroup",
                "business_id": "SmartGift",
                "vault_id": "vlt-catalog-product",
                "bundle_code": bundle_code,
                "product_code": pcode,
                "qty_deducted": qty,
                "remaining_stock": self.inventory[pcode],
                "timestamp": timestamp_iso
            })

        result["deduction_id"] = deduction_id
        result["order_id"] = resolved_order_id
        result["tenant_id"] = "Org-EtohGroup"
        result["business_id"] = "SmartGift"
        result["vault_id"] = "vlt-catalog-product"
        result["order_status"] = "CONFIRMED_AND_DEDUCTED"
        result["deduction_audit_logs"] = deduction_logs
        return result


if __name__ == "__main__":
    engine = InventoryCascadeEngine()
    print("=== Testing Set Decomposition (TDD03-2 x 10) ===")
    comps = engine.decompose_set("TDD03-2", 10)
    for c in comps:
        print(f"  - {c['name_th']}: {c['total_qty_needed']} units (Cost: ฿{c['total_cost']:,.2f})")

    print("\n=== Testing Bundle Decomposition (PKG-SME-ELITE x 1) ===")
    bundle_res = engine.decompose_bundle("PKG-SME-ELITE", 1)
    print(f"Bundle: {bundle_res['bundle_name']}")
    print(f"Selling Price: ฿{bundle_res['total_selling_price']:,.2f}")
    print(f"Total Physical Cost: ฿{bundle_res['total_cost_price']:,.2f}")
    print(f"Gross Margin: ฿{bundle_res['gross_profit']:,.2f} ({bundle_res['gross_margin_percent']}%)")
    print(f"Fulfillable: {bundle_res['is_fulfillable']}")
    print("SKU Level Deductions:")
    for sku in bundle_res['physical_sku_deductions']:
        print(f"  [{sku['product_code']}] {sku['name_th']}: Needs {sku['total_units_required']} (In Stock: {sku['current_stock']})")

    print("\n=== Executing Cascade Stock Deduction ===")
    order_res = engine.execute_order_deduction("PKG-SME-ELITE", 1)
    print("Order Status:", order_res["order_status"])
    for sku in order_res['physical_sku_deductions']:
        print(f"  [{sku['product_code']}] Stock after deduction: {sku['remaining_stock']}")
