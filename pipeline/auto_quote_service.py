"""
SmartGift Headless Auto-Quote & Automation Service
Serves instant multi-tier quotes, volume discounts, and shipping comparisons for AI Agents & LINE OA Webhook.
"""

import sys
import json
import os
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.cascade_engine.pricing_calculator import SmartGiftPricingCalculator

sys.stdout.reconfigure(encoding='utf-8')

class SmartGiftAutoQuoteService:
    def __init__(self, config_path: Optional[str] = None):
        self.calc = SmartGiftPricingCalculator(fx=5.0)
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "..", "config", "shipping_rate_matrix.json")
        self.matrix = None
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.matrix = json.load(f)

    def generate_agent_quote_payload(
        self,
        product_code: str,
        factory_cny: float,
        qty: int = 100,
        cbm: float = 0.05,
        kg: float = 10.0,
        upc: int = 50,
        member_tier: str = "SILVER",
        warehouse: str = "guangzhou_shenzhen",
        shipping_mode: str = "auto",
        custom_logo_thb: float = 0.0,
        logo_method: str = "none"
    ) -> Dict[str, Any]:
        """
        Calculates quotes across multiple order breaks and compares Member Tier shipping rates.
        """
        tier_normalized = member_tier.lower()
        if "guangzhou" in warehouse.lower():
            wh_normalized = "guangzhou_shenzhen"
        else:
            wh_normalized = "yiwu"

        corp_quote = self.calc.generate_quote(
            rmb=factory_cny,
            upc=upc,
            cbm=cbm,
            kg=kg,
            profile_key="corporate",
            warehouse=wh_normalized,
            mode=shipping_mode,
            goods_type="electronic_tisi",
            tier=tier_normalized,
            logo_method=logo_method
        )

        std_quote = self.calc.generate_quote(
            rmb=factory_cny,
            upc=upc,
            cbm=cbm,
            kg=kg,
            profile_key="standard",
            warehouse=wh_normalized,
            mode=shipping_mode,
            goods_type="electronic_tisi",
            tier=tier_normalized,
            logo_method=logo_method
        )

        single_landed = self.calc.calculate_landed_cost(
            rmb=factory_cny,
            qty=qty,
            upc=upc,
            cbm=cbm,
            kg=kg,
            warehouse=wh_normalized,
            mode=shipping_mode,
            goods_type="electronic_tisi",
            tier=tier_normalized,
            custom_ucost=custom_logo_thb,
            logo_method=logo_method
        )

        return {
            "status": "SUCCESS",
            "product_code": product_code,
            "requested_quantity": qty,
            "configuration": {
                "factory_cny": factory_cny,
                "fx_rate": 5.0,
                "member_tier": member_tier.upper(),
                "warehouse": wh_normalized,
                "shipping_mode": shipping_mode,
                "custom_logo_thb": custom_logo_thb
            },
            "single_order_landed_cost": single_landed,
            "corporate_quote_summary": corp_quote,
            "standard_quote_summary": std_quote
        }

if __name__ == "__main__":
    service = SmartGiftAutoQuoteService()
    print("=== Testing SmartGift Headless Auto-Quote Service ===")
    res = service.generate_agent_quote_payload(
        product_code="TDD03-2",
        factory_cny=45.0,
        qty=100,
        cbm=0.04,
        kg=12.0,
        member_tier="ELITE",
        warehouse="guangzhou"
    )
    print(f"Product: {res['product_code']} | Member Tier: {res['configuration']['member_tier']}")
    print("Corporate Price Breaks:")
    for row in res["corporate_quote_summary"]["ladder_quotes"]:
        print(f"  Qty {row['quantity']:>4}: ฿{row['unit_selling_price']:>7,.2f}/unit (Margin: {row['gross_margin_percent']:>5.1f}%)")
