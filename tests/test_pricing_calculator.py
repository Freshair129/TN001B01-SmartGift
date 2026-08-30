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

class TestPricingBugFixes(unittest.TestCase):
    """Regression tests for logo-cost plumbing, USD rate, and price rounding."""

    def setUp(self):
        self.calc = SmartGiftPricingCalculator(fx=5.0, usd_to_thb=32.5)

    def test_flat_logo_rate_flows_into_landed_cost(self):
        landed = self.calc.calculate_landed_cost(
            rmb=50.0, qty=100, upc=20, cbm=0.08, kg=12.0,
            logo_method="flat", logo_positions=2, logo_rate=3.0
        )
        # flat = qty * positions * rate, per unit = positions * rate
        self.assertAlmostEqual(landed["logo_per_unit"], 6.0)

    def test_uv_logo_rate_flows_into_landed_cost(self):
        landed = self.calc.calculate_landed_cost(
            rmb=50.0, qty=100, upc=20, cbm=0.08, kg=12.0,
            logo_method="uv", logo_positions=1, logo_uv_rate=0.05
        )
        # uv = qty * positions * uv_rate * usd_to_thb, per unit = 0.05 * 32.5
        self.assertAlmostEqual(landed["logo_per_unit"], round(0.05 * 32.5, 4))

    def test_generate_quote_passes_logo_colors(self):
        base = dict(rmb=50.0, upc=20, cbm=0.08, kg=12.0,
                    profile_key="corporate", logo_method="silk", logo_positions=2)
        one = self.calc.generate_quote(**base, logo_colors=1)
        two = self.calc.generate_quote(**base, logo_colors=2)
        self.assertGreater(
            two["ladder_quotes"][0]["unit_landed_cost"],
            one["ladder_quotes"][0]["unit_landed_cost"]
        )

    def test_usd_rate_from_constructor(self):
        calc = SmartGiftPricingCalculator(fx=5.0, usd_to_thb=36.0)
        self.assertAlmostEqual(
            calc.calculate_logo_cost("hotstamp_text", 100, positions=1),
            4.84 * 36.0
        )

    def test_usd_rate_loaded_from_config(self):
        # config/pricing_rules_formula.yaml declares currency_fx.usd_to_thb: 32.50
        calc = SmartGiftPricingCalculator()
        self.assertAlmostEqual(calc.usd_to_thb, 32.5)

    def test_generate_quote_includes_custom_ucost_in_ladder(self):
        base = dict(rmb=50.0, upc=20, cbm=0.08, kg=12.0, profile_key="corporate")
        without = self.calc.generate_quote(**base)
        with_ucost = self.calc.generate_quote(**base, custom_ucost=10.0)
        for w, wo in zip(with_ucost["ladder_quotes"], without["ladder_quotes"]):
            self.assertAlmostEqual(w["unit_landed_cost"], wo["unit_landed_cost"] + 10.0)
        # corporate basis is landed, so the anchor basis must carry the cost too
        self.assertAlmostEqual(
            with_ucost["anchor_basis_cost"], without["anchor_basis_cost"] + 10.0
        )

    def test_round_up_to_step_ignores_float_noise(self):
        self.assertEqual(self.calc.round_up_to_step(420.00000000000006, 10.0), 420.0)
        self.assertEqual(self.calc.round_up_to_step(411.0, 10.0), 420.0)
        self.assertEqual(self.calc.round_up_to_step(420.0, 10.0), 420.0)


if __name__ == "__main__":
    unittest.main()
