"""
SmartGift Advanced Landed Cost & Ladder Pricing Engine
Ported and enhanced from smartgift-pricing.vercel.app / zuri-command-agent pricing engine.
Calculates Landed Costs (Freight, Density, Logo, Inland, Small-Order Factors) and Quotes (Standard & Corporate).
"""

import math
import sys
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding='utf-8')

MIN_CBM = 0.01
SEA_THRESHOLD = 5.0
SEASON_MONTHS = [9, 10, 11, 12, 1]  # Peak season
DENSITY_SWITCH = 400.0  # kg/CBM

FLOORS = [
    {"max_qty": 20, "thb": 5000.0},
    {"max_qty": float("inf"), "thb": 3000.0}
]

SMALL_ORDER_FACTORS = [
    {"max_qty": 20, "sof": 1.5},
    {"max_qty": 50, "sof": 1.4},
    {"max_qty": 100, "sof": 1.3},
    {"max_qty": 300, "sof": 1.2},
    {"max_qty": 499, "sof": 1.1},
    {"max_qty": float("inf"), "sof": 1.0}
]

MARKUP_BANDS_STANDARD = [
    {"max_cost": 250.0, "markup": 3.00},
    {"max_cost": 350.0, "markup": 2.73},
    {"max_cost": 500.0, "markup": 2.62},
    {"max_cost": 650.0, "markup": 2.45},
    {"max_cost": float("inf"), "markup": 2.14}
]

PROFILES = {
    "standard": {
        "name": "ทั่วไป",
        "breaks": [10, 20, 50, 100, 300, 500, 1000],
        "factors": [1.00, 0.90, 0.85, 0.80, 0.77, 0.75, 0.73],
        "anchor": 500,
        "basis": "factory",
        "markup_bands": MARKUP_BANDS_STANDARD
    },
    "corporate": {
        "name": "องค์กร",
        "breaks": [100, 300, 500, 1000],
        "factors": [0.80, 0.77, 0.75, 0.73],
        "anchor": 1000,
        "basis": "landed",
        "flat_markup": 1.47,
        "ref_goods": "electronic_tisi"
    }
}

RATES = {
    "guangzhou_shenzhen": {
        "truck": {
            "general": {"elite": {"cbm": 5900, "kg": 15}, "gold": {"cbm": 6400, "kg": 16}, "silver": {"cbm": 6900, "kg": 18}, "member": {"cbm": 7400, "kg": 19}},
            "electronic_tisi": {"elite": {"cbm": 6400, "kg": 16}, "gold": {"cbm": 6900, "kg": 18}, "silver": {"cbm": 7400, "kg": 19}, "member": {"cbm": 7900, "kg": 20}}
        },
        "sea": {
            "general": {"elite": {"cbm": 3900, "kg": 10}, "gold": {"cbm": 4400, "kg": 11}, "silver": {"cbm": 4900, "kg": 13}, "member": {"cbm": 5400, "kg": 14}},
            "electronic_tisi": {"elite": {"cbm": 4400, "kg": 11}, "gold": {"cbm": 4900, "kg": 13}, "silver": {"cbm": 5400, "kg": 14}, "member": {"cbm": 5900, "kg": 15}}
        }
    },
    "yiwu": {
        "truck": {
            "general": {"elite": {"cbm": 6400, "kg": 16}, "gold": {"cbm": 6900, "kg": 18}, "silver": {"cbm": 7400, "kg": 19}, "member": {"cbm": 7900, "kg": 20}},
            "electronic_tisi": {"elite": {"cbm": 6900, "kg": 18}, "gold": {"cbm": 7400, "kg": 19}, "silver": {"cbm": 7900, "kg": 20}, "member": {"cbm": 8400, "kg": 21}}
        },
        "sea": {
            "general": {"elite": {"cbm": 3900, "kg": 10}, "gold": {"cbm": 4400, "kg": 11}, "silver": {"cbm": 4900, "kg": 13}, "member": {"cbm": 5400, "kg": 14}},
            "electronic_tisi": {"elite": {"cbm": 4400, "kg": 11}, "gold": {"cbm": 4900, "kg": 13}, "silver": {"cbm": 5400, "kg": 14}, "member": {"cbm": 5900, "kg": 15}}
        }
    }
}

import os
import json
try:
    import yaml
except ImportError:
    yaml = None

class SmartGiftPricingCalculator:
    def __init__(self, fx: float = 5.0, config_path: Optional[str] = None):
        self.fx = fx
        self.rates = RATES
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        candidate_paths = [
            self.config_path,
            os.path.join(os.path.dirname(__file__), "..", "..", "config", "pricing_rules_formula.yaml"),
            "config/pricing_rules_formula.yaml",
            os.path.join(os.path.dirname(__file__), "..", "..", "config", "shipping_rate_matrix.yaml"),
            "config/shipping_rate_matrix.yaml",
            "config/shipping_rate_matrix.json"
        ]
        for path in candidate_paths:
            if path and os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        if path.endswith(".yaml") or path.endswith(".yml"):
                            data = yaml.safe_load(f) if yaml else None
                        else:
                            data = json.load(f)
                    if data:
                        if "currency_fx" in data and "cny_to_thb" in data["currency_fx"]:
                            self.fx = data["currency_fx"]["cny_to_thb"]
                        if "shipping_rates" in data:
                            self._merge_rates(data["shipping_rates"])
                        elif "rates" in data:
                            self._merge_rates(data["rates"])
                        break
                except Exception:
                    pass

    def _merge_rates(self, new_rates: Dict[str, Any]):
        # Normalize and merge rates table
        for wh, wh_data in new_rates.items():
            wh_key = "guangzhou_shenzhen" if "guangzhou" in wh.lower() else "yiwu"
            if wh_key not in self.rates:
                self.rates[wh_key] = {}
            for mode, mode_data in wh_data.items():
                if mode not in self.rates[wh_key]:
                    self.rates[wh_key][mode] = {}
                for cat, cat_data in mode_data.items():
                    cat_key = "electronic_tisi" if ("electronic" in cat.lower() or "tis" in cat.lower()) else cat.lower()
                    self.rates[wh_key][mode][cat_key] = {k.lower(): v for k, v in cat_data.items()}

    def get_small_order_factor(self, qty: int) -> float:
        for tier in SMALL_ORDER_FACTORS:
            if qty <= tier["max_qty"]:
                return tier["sof"]
        return 1.0

    def get_floor_profit(self, qty: int) -> float:
        for f in FLOORS:
            if qty <= f["max_qty"]:
                return f["thb"]
        return 3000.0

    def resolve_shipping_mode(self, mode: str, month: int, volume_cbm: float) -> str:
        if mode != "auto":
            return mode
        if month in SEASON_MONTHS:
            return "truck"
        if volume_cbm > SEA_THRESHOLD:
            return "sea"
        return "truck"

    def calculate_freight(self, qty: int, upc: int, cbm: float, kg: Optional[float],
                          warehouse: str, mode: str, month: int, goods_type: str, tier: str) -> Dict[str, Any]:
        cartons = math.ceil(qty / max(upc, 1))
        volume_cbm = round(cartons * max(cbm, MIN_CBM), 2)
        weight_kg = round(cartons * kg, 2) if kg else None
        
        density = (kg / cbm) if (kg and cbm > 0) else 0.0
        charged_by = "weight" if density >= DENSITY_SWITCH else "volume"
        resolved_mode = self.resolve_shipping_mode(mode, month, volume_cbm)

        rate_table = self.rates.get(warehouse, {}).get(resolved_mode, {}).get(goods_type, {}).get(tier, {"cbm": 6400, "kg": 16})
        
        if charged_by == "weight" and weight_kg:
            order_freight = round(weight_kg * rate_table["kg"], 2)
        else:
            order_freight = round(volume_cbm * rate_table["cbm"], 2)

        return {
            "cartons": cartons,
            "volume_cbm": volume_cbm,
            "weight_kg": weight_kg,
            "density": round(density, 2),
            "charged_by": charged_by,
            "resolved_mode": resolved_mode,
            "rate": rate_table,
            "order_freight": order_freight,
            "per_unit_freight": round(order_freight / qty, 4)
        }

    def calculate_logo_cost(self, method: str, qty: int, positions: int = 1, colors: int = 1,
                            rate: float = 0.0, uv_rate: float = 0.0) -> float:
        usd_to_thb = self.fx * 6.5
        if method == "none":
            return 0.0
        elif method == "flat":
            return qty * positions * rate
        elif method == "hotstamp":
            per = 0.0 if qty <= 100 else (0.081 if qty <= 499 else (0.065 if qty <= 999 else 0.048))
            return (11.3 + max(0, qty - 100) * per) * positions * usd_to_thb
        elif method == "hotstamp_text":
            return 4.84 * positions * usd_to_thb
        elif method == "engrave":
            per = 0.17 if qty <= 9 else (0.081 if qty <= 99 else (0.05 if qty <= 299 else (0.035 if qty <= 499 else 0.02)))
            return qty * per * positions * usd_to_thb
        elif method == "silk":
            base = 13.0 if qty <= 350 else (qty * 0.04)
            return base * positions * colors * usd_to_thb
        elif method == "uv":
            return qty * positions * uv_rate * usd_to_thb
        return 0.0

    def calculate_landed_cost(self, rmb: float, qty: int, upc: int, cbm: float, kg: Optional[float],
                              warehouse: str = "guangzhou_shenzhen", mode: str = "auto", month: int = 8,
                              goods_type: str = "general", tier: str = "gold",
                              inland_rmb: float = 2.0, custom_ucost: float = 0.0,
                              logo_method: str = "none", logo_positions: int = 1, logo_colors: int = 1) -> Dict[str, Any]:
        sof = self.get_small_order_factor(qty)
        factory_cost_thb = round(rmb * self.fx * sof, 4)
        
        fr = self.calculate_freight(qty, upc, cbm, kg, warehouse, mode, month, goods_type, tier)
        order_logo_thb = self.calculate_logo_cost(logo_method, qty, logo_positions, logo_colors)
        logo_per_unit = round(order_logo_thb / qty, 4) if qty > 0 else 0.0
        inland_cost_thb = round(inland_rmb * self.fx, 4)

        total_landed = round(factory_cost_thb + fr["per_unit_freight"] + logo_per_unit + inland_cost_thb + custom_ucost, 4)

        return {
            "qty": qty,
            "factory_cost_thb": factory_cost_thb,
            "freight_per_unit": fr["per_unit_freight"],
            "logo_per_unit": logo_per_unit,
            "inland_cost_thb": inland_cost_thb,
            "custom_ucost": custom_ucost,
            "total_landed_cost": total_landed,
            "freight_details": fr
        }

    def generate_quote(self, rmb: float, upc: int, cbm: float, kg: Optional[float],
                       profile_key: str = "corporate", warehouse: str = "guangzhou_shenzhen",
                       mode: str = "auto", month: int = 8, goods_type: str = "general",
                       tier: str = "gold", logo_method: str = "none", logo_positions: int = 1,
                       order_cost: float = 0.0) -> Dict[str, Any]:
        prof = PROFILES.get(profile_key, PROFILES["corporate"])
        anchor = prof["anchor"]
        ref_goods = prof.get("ref_goods", goods_type)

        # Calculate Anchor
        anchor_landed = self.calculate_landed_cost(
            rmb=rmb, qty=anchor, upc=upc, cbm=cbm, kg=kg,
            warehouse=warehouse, mode=mode, month=month, goods_type=ref_goods,
            tier=tier, logo_method=logo_method, logo_positions=logo_positions
        )

        basis_type = prof["basis"]
        anchor_basis = anchor_landed["total_landed_cost"] if basis_type == "landed" else anchor_landed["factory_cost_thb"]

        if "flat_markup" in prof:
            markup = prof["flat_markup"]
        else:
            markup = 2.14
            for band in prof["markup_bands"]:
                if anchor_basis <= band["max_cost"]:
                    markup = band["markup"]
                    break

        anchor_price = anchor_basis * markup
        anchor_factor_idx = prof["breaks"].index(anchor)
        anchor_factor = prof["factors"][anchor_factor_idx]

        ladder_quotes = []
        for idx, q in enumerate(prof["breaks"]):
            L = self.calculate_landed_cost(
                rmb=rmb, qty=q, upc=upc, cbm=cbm, kg=kg,
                warehouse=warehouse, mode=mode, month=month, goods_type=goods_type,
                tier=tier, logo_method=logo_method, logo_positions=logo_positions
            )
            factor = prof["factors"][idx]
            ladder_price = anchor_price * (factor / anchor_factor)
            min_profit = self.get_floor_profit(q)
            floor_price = L["total_landed_cost"] + (min_profit + order_cost) / q

            final_price = math.ceil(max(ladder_price, floor_price) / 10.0) * 10.0
            profit = (final_price - L["total_landed_cost"]) * q - order_cost
            margin_pct = (profit / (final_price * q) * 100.0) if final_price > 0 else 0.0

            ladder_quotes.append({
                "quantity": q,
                "unit_landed_cost": L["total_landed_cost"],
                "unit_selling_price": final_price,
                "total_order_amount": final_price * q,
                "gross_profit": round(profit, 2),
                "gross_margin_percent": round(margin_pct, 2),
                "price_driven_by": "floor" if floor_price > ladder_price else "ladder"
            })

        return {
            "profile": prof["name"],
            "anchor_quantity": anchor,
            "anchor_basis_cost": anchor_basis,
            "applied_markup": markup,
            "ladder_quotes": ladder_quotes
        }


if __name__ == "__main__":
    calc = SmartGiftPricingCalculator(fx=5.0)
    print("=== Testing SmartGift Advanced Pricing Engine ===")
    sample_quote = calc.generate_quote(
        rmb=50.0, upc=20, cbm=0.08, kg=12.0,
        profile_key="corporate", logo_method="silk", logo_positions=2
    )
    print(f"Profile: {sample_quote['profile']} | Applied Markup: {sample_quote['applied_markup']}x")
    print("-" * 65)
    for q in sample_quote["ladder_quotes"]:
        print(f"📦 Qty: {q['quantity']:>4} | Landed: ฿{q['unit_landed_cost']:>7.2f} | Price: ฿{q['unit_selling_price']:>7.2f} | Margin: {q['gross_margin_percent']:>5.2f}% ({q['price_driven_by']})")
