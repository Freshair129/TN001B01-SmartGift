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
        # config/pricing_rules_formula.yaml declares currency_exchange_rates.usd_to_thb.
        # Asserting the value alone would also pass on the fx * 6.5 fallback (5 * 6.5 =
        # 32.5), which is how this test passed while the loader read key names the file
        # never had — so assert the block was actually applied too.
        calc = SmartGiftPricingCalculator()
        self.assertIn("currency_exchange_rates.usd_to_thb", calc.describe_config()["applied"])
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


class TestConfigDrivenConstants(unittest.TestCase):
    """The formula config, not the module defaults, must be what prices the ladder."""

    BLOCKS = (
        "currency_exchange_rates.cny_to_thb", "logistics_density_and_freight",
        "price_rounding", "profit_floors", "small_order_factors",
        "markup_bands_standard", "standard_quote_profile", "corporate_quote_profile",
        "logo_methods", "logo_positions_rule", "lead_time_working_days",
        "shipping_rate_matrix",
    )

    def setUp(self):
        self.calc = SmartGiftPricingCalculator()

    def test_every_block_is_applied_from_the_repo_config(self):
        applied = self.calc.describe_config()["applied"]
        for block in self.BLOCKS:
            self.assertIn(block, applied, f"{block} was not read from the config file")

    def test_config_source_is_reported(self):
        source = self.calc.describe_config()
        self.assertTrue(source["path"].endswith("pricing_rules_formula.yaml"))
        self.assertEqual(len(source["sha256"]), 64)
        self.assertTrue(source["version"])

    def _with_overrides(self, **changes):
        """Write a modified copy of the repo config and load a calculator from it."""
        import copy, os, tempfile, yaml
        with open("config/pricing_rules_formula.yaml", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        for path, value in changes.items():
            node = data
            keys = path.split(".")
            for key in keys[:-1]:
                node = node[int(key)] if key.isdigit() else node[key]
            last = keys[-1]
            node[int(last) if last.isdigit() else last] = value
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        self.addCleanup(os.unlink, path)
        with open(path, "w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, allow_unicode=True)
        return SmartGiftPricingCalculator(config_path=path)

    def test_markup_band_change_moves_the_price(self):
        quote_args = dict(rmb=32.0, upc=20, cbm=0.11, kg=None, profile_key="standard")
        before = self.calc.generate_quote(**quote_args)
        after = self._with_overrides(**{"markup_bands_standard.0.markup_multiplier": 4.00}).generate_quote(**quote_args)
        self.assertGreater(after["ladder_quotes"][-1]["unit_selling_price"],
                           before["ladder_quotes"][-1]["unit_selling_price"])

    def test_rounding_step_comes_from_config(self):
        calc = self._with_overrides(**{"price_rounding.ladder_price_step_thb": 25.0})
        self.assertEqual(calc.price_step_thb, 25.0)
        quote = calc.generate_quote(rmb=32.0, upc=20, cbm=0.11, kg=None, profile_key="standard")
        for row in quote["ladder_quotes"]:
            self.assertEqual(row["unit_selling_price"] % 25, 0)

    def test_floor_and_sof_come_from_config(self):
        calc = self._with_overrides(**{"profit_floors.0.thb": 9000.0,
                                       "small_order_factors.0.sof": 2.0})
        self.assertEqual(calc.get_floor_profit(10), 9000.0)
        self.assertEqual(calc.get_small_order_factor(10), 2.0)

    def test_logo_rate_table_comes_from_config(self):
        calc = self._with_overrides(**{"logo_methods.silk.flat_usd": 26.0})
        self.assertAlmostEqual(calc.calculate_logo_cost("silk", 100, positions=1),
                               26.0 * calc.usd_to_thb)

    def test_positions_rule_comes_from_config(self):
        self.assertEqual(self.calc.positions_for_code("TJS23-7"), 9)   # 7 ชิ้น + กล่อง + ถุง
        calc = self._with_overrides(**{"logo_positions_rule.extra_positions": 0})
        self.assertEqual(calc.positions_for_code("TJS23-7"), 7)

    def test_explicit_arguments_still_beat_the_config(self):
        calc = SmartGiftPricingCalculator(fx=6.0, usd_to_thb=40.0)
        self.assertEqual(calc.fx, 6.0)
        self.assertEqual(calc.usd_to_thb, 40.0)

    def test_malformed_profile_is_rejected_not_half_applied(self):
        # factors shorter than breaks would price the ladder silently wrong
        calc = self._with_overrides(**{"standard_quote_profile.factors": [1.0, 0.9]})
        self.assertNotIn("standard_quote_profile", calc.describe_config()["applied"])
        self.assertEqual(len(calc.profiles["standard"]["factors"]),
                         len(calc.profiles["standard"]["breaks"]))

    def test_missing_config_falls_back_to_module_defaults(self):
        calc = SmartGiftPricingCalculator(config_path="does/not/exist.yaml")
        self.assertEqual(calc.get_small_order_factor(10), 1.5)
        self.assertEqual(calc.price_step_thb, 10.0)

    def test_instances_do_not_share_mutated_rate_tables(self):
        first = SmartGiftPricingCalculator()
        first.rates["guangzhou_shenzhen"]["truck"]["general"]["gold"]["cbm"] = 1
        second = SmartGiftPricingCalculator()
        self.assertEqual(second.rates["guangzhou_shenzhen"]["truck"]["general"]["gold"]["cbm"], 6400)




class TestDomesticShippingCalculator(unittest.TestCase):
    """Unit tests for Domestic Thailand Shipping & Delivery calculation."""

    def setUp(self):
        self.calc = SmartGiftPricingCalculator(fx=5.0)

    def test_bulk_bkk_free_above_threshold(self):
        # Order 20,000 THB >= 15,000 THB -> Free shipping
        res = self.calc.calculate_domestic_shipping(
            mode="bulk", destination="bkk", qty=50, total_order_thb=20000.0
        )
        self.assertTrue(res["is_free"])
        self.assertEqual(res["total_shipping_fee_thb"], 0.0)
        self.assertEqual(res["flowaccount_service_item"]["unit_price"], 0.0)

    def test_bulk_bkk_charged_below_threshold(self):
        # Order 8,000 THB < 15,000 THB -> 800 THB flat fee
        res = self.calc.calculate_domestic_shipping(
            mode="bulk", destination="bkk", qty=10, total_order_thb=8000.0
        )
        self.assertFalse(res["is_free"])
        self.assertEqual(res["total_shipping_fee_thb"], 800.0)
        self.assertEqual(res["unit_shipping_fee_thb"], 80.0)

    def test_bulk_upcountry_courier(self):
        # 60 items = 3 cartons (20 items/carton) -> 3 * 150 = 450 THB
        res = self.calc.calculate_domestic_shipping(
            mode="bulk", destination="upcountry", qty=60, upcountry_method="courier"
        )
        self.assertEqual(res["total_shipping_fee_thb"], 450.0)
        self.assertIn("3 ลังใหญ่", res["details"])

    def test_bulk_upcountry_charter(self):
        # Explicit charter truck -> 2,500 THB base
        res = self.calc.calculate_domestic_shipping(
            mode="bulk", destination="upcountry", qty=500, upcountry_method="charter"
        )
        self.assertEqual(res["total_shipping_fee_thb"], 2500.0)

    def test_individual_fulfilment_rates(self):
        # Box S (45 bkk + 20 pack) = 65 THB / unit
        res_s = self.calc.calculate_domestic_shipping(
            mode="individual", destination="bkk", qty=10, box_size="box_s"
        )
        self.assertEqual(res_s["unit_shipping_fee_thb"], 65.0)
        self.assertEqual(res_s["total_shipping_fee_thb"], 650.0)

        # Box M upcountry (75 upcountry + 20 pack) = 95 THB / unit
        res_m = self.calc.calculate_domestic_shipping(
            mode="individual", destination="upcountry", qty=20, box_size="box_m"
        )
        self.assertEqual(res_m["unit_shipping_fee_thb"], 95.0)
        self.assertEqual(res_m["total_shipping_fee_thb"], 1900.0)

        # Box L remote (105 upcountry + 50 remote + 20 pack) = 175 THB / unit
        res_l = self.calc.calculate_domestic_shipping(
            mode="individual", destination="remote", qty=5, box_size="box_l"
        )
        self.assertEqual(res_l["unit_shipping_fee_thb"], 175.0)
        self.assertEqual(res_l["total_shipping_fee_thb"], 875.0)

if __name__ == "__main__":
    unittest.main()
