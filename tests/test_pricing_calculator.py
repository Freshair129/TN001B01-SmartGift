"""
Unit tests for SmartGift Advanced Pricing Calculator
"""

import unittest
from src.cascade_engine.pricing_calculator import SmartGiftPricingCalculator

class TestSmartGiftPricingCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = SmartGiftPricingCalculator(fx=5.0)

    def test_small_order_factors(self):
        self.assertEqual(self.calc.get_small_order_factor(10), 1.5)
        self.assertEqual(self.calc.get_small_order_factor(50), 1.4)
        self.assertEqual(self.calc.get_small_order_factor(100), 1.3)
        self.assertEqual(self.calc.get_small_order_factor(500), 1.0)

    def test_landed_cost_calculation(self):
        landed = self.calc.calculate_landed_cost(
            rmb=50.0, qty=100, upc=20, cbm=0.08, kg=12.0,
            warehouse="guangzhou_shenzhen", mode="truck", goods_type="general"
        )
        self.assertGreater(landed["total_landed_cost"], 0)
        self.assertIn("freight_details", landed)

    def test_corporate_quote_generation(self):
        quote = self.calc.generate_quote(
            rmb=50.0, upc=20, cbm=0.08, kg=12.0, profile_key="corporate"
        )
        self.assertEqual(quote["profile"], "องค์กร")
        self.assertEqual(quote["applied_markup"], 1.47)
        self.assertEqual(len(quote["ladder_quotes"]), 4)  # 100, 300, 500, 1000
        for q in quote["ladder_quotes"]:
            self.assertGreater(q["unit_selling_price"], q["unit_landed_cost"])
            self.assertGreater(q["gross_margin_percent"], 0)

if __name__ == "__main__":
    unittest.main()
