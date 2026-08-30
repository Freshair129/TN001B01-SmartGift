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
    def __init__(self, fx: float = 5.0, config_path: Optional[str] = None,
                 usd_to_thb: Optional[float] = None):
        self.fx = fx
        self.rates = RATES
        self.config_path = config_path
        self.usd_to_thb = usd_to_thb
        self._load_config()
        if self.usd_to_thb is None:
            # Last-resort estimate when no explicit rate and no config: ~6.5 CNY per USD
            self.usd_to_thb = self.fx * 6.5

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
                        if (self.usd_to_thb is None and "currency_fx" in data
                                and "usd_to_thb" in data["currency_fx"]):
                            self.usd_to_thb = data["currency_fx"]["usd_to_thb"]
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

    @staticmethod
    def round_up_to_step(value: float, step: float) -> float:
        # Round value/step to 6 dp before ceil so float noise (e.g. 42.000000000000006)
        # does not bump the price to the next step.
        return round(math.ceil(round(value / step, 6)) * step, 6)

    def calculate_logo_cost(self, method: str, qty: int, positions: int = 1, colors: int = 1,
                            rate: float = 0.0, uv_rate: float = 0.0) -> float:
        usd_to_thb = self.usd_to_thb
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
                              logo_method: str = "none", logo_positions: int = 1, logo_colors: int = 1,
                              logo_rate: float = 0.0, logo_uv_rate: float = 0.0) -> Dict[str, Any]:
        sof = self.get_small_order_factor(qty)
        factory_cost_thb = round(rmb * self.fx * sof, 4)

        fr = self.calculate_freight(qty, upc, cbm, kg, warehouse, mode, month, goods_type, tier)
        order_logo_thb = self.calculate_logo_cost(logo_method, qty, logo_positions, logo_colors,
                                                  rate=logo_rate, uv_rate=logo_uv_rate)
        logo_per_unit = round(order_logo_thb / qty, 4) if qty > 0 else 0.0
        inland_cost_thb = round(inland_rmb * self.fx, 4)

        total_landed = round(factory_cost_thb + fr["per_unit_freight"] + logo_per_unit + inland_cost_thb + custom_ucost, 4)

        return {
            "qty": qty,
            "sof": sof,
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
                       logo_colors: int = 1, logo_rate: float = 0.0, logo_uv_rate: float = 0.0,
                       custom_ucost: float = 0.0, order_cost: float = 0.0) -> Dict[str, Any]:
        prof = PROFILES.get(profile_key, PROFILES["corporate"])
        anchor = prof["anchor"]
        ref_goods = prof.get("ref_goods", goods_type)
        logo_kwargs = {"logo_method": logo_method, "logo_positions": logo_positions,
                       "logo_colors": logo_colors, "logo_rate": logo_rate,
                       "logo_uv_rate": logo_uv_rate}

        # Calculate Anchor
        anchor_landed = self.calculate_landed_cost(
            rmb=rmb, qty=anchor, upc=upc, cbm=cbm, kg=kg,
            warehouse=warehouse, mode=mode, month=month, goods_type=ref_goods,
            tier=tier, custom_ucost=custom_ucost, **logo_kwargs
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
                tier=tier, custom_ucost=custom_ucost, **logo_kwargs
            )
            factor = prof["factors"][idx]
            ladder_price = anchor_price * (factor / anchor_factor)
            min_profit = self.get_floor_profit(q)
            floor_price = L["total_landed_cost"] + (min_profit + order_cost) / q

            final_price = self.round_up_to_step(max(ladder_price, floor_price), 10.0)
            profit = (final_price - L["total_landed_cost"]) * q - order_cost
            margin_pct = (profit / (final_price * q) * 100.0) if final_price > 0 else 0.0

            ladder_quotes.append({
                "quantity": q,
                "unit_landed_cost": L["total_landed_cost"],
                "unit_selling_price": final_price,
                "total_order_amount": final_price * q,
                "gross_profit": round(profit, 2),
                "gross_margin_percent": round(margin_pct, 2),
                "price_driven_by": "floor" if floor_price > ladder_price else "ladder",
                "shipping_mode": L["freight_details"]["resolved_mode"],
                "small_order_factor": L["sof"],
                "min_profit_floor": min_profit
            })

        return {
            "profile": prof["name"],
            "anchor_quantity": anchor,
            "anchor_basis_cost": anchor_basis,
            "applied_markup": markup,
            "ladder_quotes": ladder_quotes,
            "warnings": self.build_warnings(
                ladder_quotes, logo_method=logo_method, logo_uv_rate=logo_uv_rate,
                kg=kg, cbm=cbm, custom_ucost=custom_ucost, order_cost=order_cost
            )
        }

    def build_warnings(self, rows: List[Dict[str, Any]], logo_method: str = "none",
                       logo_uv_rate: float = 0.0, kg: Optional[float] = None,
                       cbm: float = 0.0, custom_ucost: float = 0.0,
                       order_cost: float = 0.0) -> List[Dict[str, str]]:
        """Sanity checks on a quote ladder, ported from the price-boss engine."""
        fmt = lambda v: f"{v:,.0f}"
        warns: List[Dict[str, str]] = []

        for prev, cur in zip(rows, rows[1:]):
            if cur["unit_selling_price"] > prev["unit_selling_price"]:
                warns.append({"level": "crit", "message":
                    f"สั่ง {cur['quantity']} ชุดแพงกว่าสั่ง {prev['quantity']} ชุด — ตรวจการบรรจุกล่อง"})
            if cur["gross_profit"] < prev["gross_profit"]:
                warns.append({"level": "crit", "message":
                    f"ออเดอร์ {cur['quantity']} ชุดได้กำไรน้อยกว่า {prev['quantity']} ชุด "
                    f"({fmt(cur['gross_profit'])} เทียบ {fmt(prev['gross_profit'])} บาท) — "
                    f"สูตรนี้ไม่เหมาะกับสินค้าราคานี้"})
            drop = 1 - cur["unit_selling_price"] / prev["unit_selling_price"]
            if drop > 0.25:
                warns.append({"level": "warn", "message":
                    f"ราคาตกลง {round(drop * 100)}% ระหว่าง {prev['quantity']} กับ {cur['quantity']} ชุด — "
                    f"ควรเสนอขั้นนี้เมื่อลูกค้าถาม ไม่ใช่พิมพ์ไว้ข้าง ๆ กัน"})

        floored = [r for r in rows if r["price_driven_by"] == "floor"]
        if floored:
            detail = ", ".join(f"{r['quantity']} ชุด (ให้ถึง {fmt(r['min_profit_floor'])} บาท)"
                               for r in floored)
            warns.append({"level": "warn", "message": f"พื้นกำไรดันราคาขึ้นที่ {detail}"})

        modes = {r["shipping_mode"] for r in rows}
        if len(modes) > 1:
            sea_qtys = ", ".join(str(r["quantity"]) for r in rows if r["shipping_mode"] == "sea")
            warns.append({"level": "warn", "message":
                f"วิธีส่งไม่เหมือนกันทุกขั้น — {sea_qtys} ชุดไปทางเรือ ถูกกว่าแต่ช้ากว่า "
                f"ต้องเช็ค lead time กับลูกค้า"})

        premium = [r for r in rows if r["small_order_factor"] > 1]
        if premium:
            detail = ", ".join(f"{r['quantity']} ชุด (x{r['small_order_factor']})" for r in premium)
            warns.append({"level": "warn", "message":
                f"โรงงานคิดราคาสูงขึ้นสำหรับออเดอร์เล็กที่ {detail} — "
                f"แคตตาล็อกบอกแค่ช่วง 1.1-1.5 เท่า ไม่ได้ระบุว่าจำนวนไหนได้เท่าไร ควรยืนยันกับโรงงาน"})

        if logo_method == "none":
            warns.append({"level": "warn", "message":
                "ยังไม่ได้เลือกวิธีสกรีน จึงไม่มีค่าสกรีนในต้นทุน — "
                "ใบราคาที่ส่งลูกค้าระบุว่ารวมสกรีนโลโก้ทุกชิ้นพร้อมกล่องและถุง"})
        elif logo_method == "uv" and not logo_uv_rate:
            warns.append({"level": "warn", "message":
                "UV print ไม่มีเรทประกาศ แคตตาล็อกให้สอบถามฝ่ายขาย — "
                "ตอนนี้คิดเป็นศูนย์ ทำให้ราคาต่ำกว่าความจริง"})

        if not kg:
            flip_kg = round(cbm * DENSITY_SWITCH, 2)
            warns.append({"level": "info", "message":
                f"ไม่ได้ระบุน้ำหนักกล่อง จึงคิดค่าขนส่งตามปริมาตร "
                f"จะเปลี่ยนไปคิดตามน้ำหนักเมื่อกล่องหนักเกิน {flip_kg} กก."})

        if custom_ucost == 0 and order_cost == 0:
            warns.append({"level": "info", "message":
                "ยังไม่ได้ใส่ค่ากล่องของขวัญ ถุง หรือค่าส่งในไทยนอกเหนือจากค่าสกรีน — "
                "กำไรที่เห็นจึงสูงกว่าความจริง"})

        return warns


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
