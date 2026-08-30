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

    def test_zero_cbm_falls_back_to_volume_charging(self):
        # cbm=0 with a weight must NOT produce infinite density and flip to
        # weight-based charging; it falls back to volume on MIN_CBM (0.01)
        fr = self.calc.calculate_freight(
            qty=100, upc=20, cbm=0.0, kg=12.0,
            warehouse="guangzhou_shenzhen", mode="truck", month=6,
            goods_type="general", tier="gold"
        )
        self.assertEqual(fr["charged_by"], "volume")
        self.assertEqual(fr["density"], 0.0)
        # 5 cartons * MIN_CBM * gold truck rate (6400)
        self.assertAlmostEqual(fr["order_freight"], round(5 * 0.01 * 6400, 2))

    def test_round_up_to_step_ignores_float_noise(self):
        self.assertEqual(self.calc.round_up_to_step(420.00000000000006, 10.0), 420.0)
        self.assertEqual(self.calc.round_up_to_step(411.0, 10.0), 420.0)
        self.assertEqual(self.calc.round_up_to_step(420.0, 10.0), 420.0)


class TestQuoteWarnings(unittest.TestCase):
    """Sanity warnings ported from the price-boss reference engine."""

    def setUp(self):
        self.calc = SmartGiftPricingCalculator(fx=5.0, usd_to_thb=32.5)

    @staticmethod
    def _messages(quote, level=None):
        return [w["message"] for w in quote["warnings"]
                if level is None or w["level"] == level]

    def _contains(self, quote, text, level=None):
        return any(text in m for m in self._messages(quote, level))

    def test_warns_when_floor_drives_price(self):
        # Cheap item at tiny quantities: the profit floor must drive the price
        q = self.calc.generate_quote(rmb=5.0, upc=20, cbm=0.08, kg=12.0,
                                     profile_key="standard")
        self.assertTrue(any(r["price_driven_by"] == "floor" for r in q["ladder_quotes"]))
        self.assertTrue(self._contains(q, "พื้นกำไร", level="warn"))

    def test_warns_on_missing_logo_method(self):
        q = self.calc.generate_quote(rmb=50.0, upc=20, cbm=0.08, kg=12.0,
                                     logo_method="none")
        self.assertTrue(self._contains(q, "สกรีน", level="warn"))

    def test_warns_on_uv_without_rate(self):
        q = self.calc.generate_quote(rmb=50.0, upc=20, cbm=0.08, kg=12.0,
                                     logo_method="uv", logo_uv_rate=0.0)
        self.assertTrue(self._contains(q, "UV", level="warn"))

    def test_info_when_no_weight_given(self):
        q = self.calc.generate_quote(rmb=50.0, upc=20, cbm=0.08, kg=None)
        self.assertTrue(self._contains(q, "ปริมาตร", level="info"))

    def test_info_when_no_extra_costs(self):
        q = self.calc.generate_quote(rmb=50.0, upc=20, cbm=0.08, kg=12.0)
        self.assertTrue(self._contains(q, "กล่องของขวัญ", level="info"))
        q2 = self.calc.generate_quote(rmb=50.0, upc=20, cbm=0.08, kg=12.0,
                                      custom_ucost=5.0)
        self.assertFalse(self._contains(q2, "กล่องของขวัญ", level="info"))

    def test_warns_on_small_order_premium(self):
        # standard profile spans qty 10-1000, so sof > 1 breaks must be flagged
        q = self.calc.generate_quote(rmb=50.0, upc=20, cbm=0.08, kg=12.0,
                                     profile_key="standard")
        self.assertTrue(self._contains(q, "ออเดอร์เล็ก", level="warn"))

    def test_warns_on_mixed_shipping_modes(self):
        # Off-season, 1 unit per carton at 0.06 CBM: big breaks cross the
        # 5-CBM sea threshold while small breaks stay on truck
        q = self.calc.generate_quote(rmb=50.0, upc=1, cbm=0.06, kg=None,
                                     profile_key="standard", mode="auto", month=5)
        modes = {r["shipping_mode"] for r in q["ladder_quotes"]}
        self.assertGreater(len(modes), 1)
        self.assertTrue(self._contains(q, "วิธีส่งไม่เหมือนกัน", level="warn"))

    def test_crit_on_price_inversion(self):
        rows = [
            {"quantity": 100, "unit_selling_price": 400.0, "gross_profit": 10000.0,
             "price_driven_by": "ladder", "shipping_mode": "truck",
             "small_order_factor": 1.0, "min_profit_floor": 3000.0},
            {"quantity": 300, "unit_selling_price": 450.0, "gross_profit": 40000.0,
             "price_driven_by": "ladder", "shipping_mode": "truck",
             "small_order_factor": 1.0, "min_profit_floor": 3000.0},
        ]
        warns = self.calc.build_warnings(rows, kg=12.0, cbm=0.08, custom_ucost=5.0,
                                         order_cost=100.0, logo_method="flat")
        self.assertTrue(any(w["level"] == "crit" and "แพงกว่า" in w["message"]
                            for w in warns))

    def test_crit_on_profit_inversion(self):
        rows = [
            {"quantity": 100, "unit_selling_price": 450.0, "gross_profit": 40000.0,
             "price_driven_by": "ladder", "shipping_mode": "truck",
             "small_order_factor": 1.0, "min_profit_floor": 3000.0},
            {"quantity": 300, "unit_selling_price": 400.0, "gross_profit": 10000.0,
             "price_driven_by": "ladder", "shipping_mode": "truck",
             "small_order_factor": 1.0, "min_profit_floor": 3000.0},
        ]
        warns = self.calc.build_warnings(rows, kg=12.0, cbm=0.08, custom_ucost=5.0,
                                         order_cost=100.0, logo_method="flat")
        self.assertTrue(any(w["level"] == "crit" and "กำไรน้อยกว่า" in w["message"]
                            for w in warns))

    def test_warn_on_steep_price_drop(self):
        rows = [
            {"quantity": 100, "unit_selling_price": 600.0, "gross_profit": 10000.0,
             "price_driven_by": "ladder", "shipping_mode": "truck",
             "small_order_factor": 1.0, "min_profit_floor": 3000.0},
            {"quantity": 300, "unit_selling_price": 400.0, "gross_profit": 40000.0,
             "price_driven_by": "ladder", "shipping_mode": "truck",
             "small_order_factor": 1.0, "min_profit_floor": 3000.0},
        ]
        warns = self.calc.build_warnings(rows, kg=12.0, cbm=0.08, custom_ucost=5.0,
                                         order_cost=100.0, logo_method="flat")
        self.assertTrue(any(w["level"] == "warn" and "ราคาตกลง" in w["message"]
                            for w in warns))


if __name__ == "__main__":
    unittest.main()
