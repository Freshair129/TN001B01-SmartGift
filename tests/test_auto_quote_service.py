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

if __name__ == "__main__":
    unittest.main()
