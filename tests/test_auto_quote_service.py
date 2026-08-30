"""
Unit tests for SmartGift Headless Auto-Quote Service & Member Tier Shipping
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.auto_quote_service import SmartGiftAutoQuoteService
from src.cascade_engine.pricing_calculator import SmartGiftPricingCalculator

class TestAutoQuoteService(unittest.TestCase):
    def setUp(self):
        self.service = SmartGiftAutoQuoteService()
        self.calc = SmartGiftPricingCalculator(fx=5.0)

    def test_member_tier_pricing_differences(self):
        # Elite tier should have lower freight cost than Member tier
        freight_elite = self.calc.calculate_freight(
            qty=100, upc=50, cbm=0.05, kg=10.0,
            warehouse="guangzhou_shenzhen", mode="truck", month=6,
            goods_type="electronic_tisi", tier="elite"
        )
        freight_member = self.calc.calculate_freight(
            qty=100, upc=50, cbm=0.05, kg=10.0,
            warehouse="guangzhou_shenzhen", mode="truck", month=6,
            goods_type="electronic_tisi", tier="member"
        )
        self.assertLess(freight_elite["order_freight"], freight_member["order_freight"])

    def test_auto_quote_service_payload(self):
        res = self.service.generate_agent_quote_payload(
            product_code="TEST-SKU",
            factory_cny=50.0,
            qty=100,
            member_tier="GOLD"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["configuration"]["member_tier"], "GOLD")
        self.assertIn("corporate_quote_summary", res)
        self.assertIn("standard_quote_summary", res)

    def test_flat_logo_rate_flows_through_service(self):
        res = self.service.generate_agent_quote_payload(
            product_code="TEST-SKU",
            factory_cny=50.0,
            qty=100,
            logo_method="flat",
            logo_positions=2,
            logo_rate=3.0
        )
        # flat = qty * positions * rate → per unit = 2 * 3.0
        self.assertAlmostEqual(res["single_order_landed_cost"]["logo_per_unit"], 6.0)

    def test_logo_rate_raises_ladder_quotes(self):
        base = dict(product_code="TEST-SKU", factory_cny=50.0, qty=100)
        without = self.service.generate_agent_quote_payload(**base)
        with_logo = self.service.generate_agent_quote_payload(
            **base, logo_method="flat", logo_positions=2, logo_rate=3.0
        )
        self.assertGreater(
            with_logo["corporate_quote_summary"]["ladder_quotes"][0]["unit_landed_cost"],
            without["corporate_quote_summary"]["ladder_quotes"][0]["unit_landed_cost"]
        )

    def test_custom_logo_thb_included_in_ladder_quotes(self):
        base = dict(product_code="TEST-SKU", factory_cny=50.0, qty=100)
        without = self.service.generate_agent_quote_payload(**base)
        with_cost = self.service.generate_agent_quote_payload(**base, custom_logo_thb=10.0)
        for summary in ("corporate_quote_summary", "standard_quote_summary"):
            self.assertAlmostEqual(
                with_cost[summary]["ladder_quotes"][0]["unit_landed_cost"],
                without[summary]["ladder_quotes"][0]["unit_landed_cost"] + 10.0
            )

    def test_logo_config_echoed_in_payload(self):
        res = self.service.generate_agent_quote_payload(
            product_code="TEST-SKU", factory_cny=50.0,
            logo_method="uv", logo_uv_rate=0.05
        )
        self.assertEqual(res["configuration"]["logo_method"], "uv")
        self.assertEqual(res["configuration"]["logo_uv_rate"], 0.05)


if __name__ == "__main__":
    unittest.main()
