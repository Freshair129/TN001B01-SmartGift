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

import copy
import hashlib
import json
import os
import re
try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_FX = 5.0
DEFAULT_INLAND_RMB = 2.0
DEFAULT_PRICE_STEP_THB = 10.0

# Rate tables for the logo methods. Every method except "flat" is quoted in USD and
# converted with usd_to_thb; the caller still supplies the flat and UV rates themselves.
LOGO_METHODS = {
    "flat": {"unit": "thb_per_position_per_piece", "default_rate_thb": 10.0},
    "hotstamp": {"setup_usd": 11.3, "per_piece_over_100_usd": [
        {"max_qty": 100, "usd": 0.0}, {"max_qty": 499, "usd": 0.081},
        {"max_qty": 999, "usd": 0.065}, {"max_qty": float("inf"), "usd": 0.048}]},
    "hotstamp_text": {"flat_usd": 4.84},
    "engrave": {"per_piece_usd": [
        {"max_qty": 9, "usd": 0.17}, {"max_qty": 99, "usd": 0.081},
        {"max_qty": 299, "usd": 0.05}, {"max_qty": 499, "usd": 0.035},
        {"max_qty": float("inf"), "usd": 0.02}]},
    "silk": {"flat_usd_up_to_qty": 350, "flat_usd": 13.0, "per_piece_usd_above": 0.04},
    "uv": {"per_piece_usd": None},
    "none": {"unit": "none"},
}

LOGO_POSITIONS_RULE = {"pieces_from_code_last_digit": True, "extra_positions": 2, "min_positions": 1}

LEAD_TIME_WORKING_DAYS = {
    "artwork_confirm": {"min": 2, "max": 2},
    "sample": {"min": 3, "max": 5},
    "production": [{"max_qty": 500, "min": 7, "max": 7},
                   {"max_qty": float("inf"), "min": 15, "max": 15}],
    "freight": {"truck": {"min": 7, "max": 10}, "sea": {"min": 21, "max": 30}},
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _tier_table(rows: Any, bound_key: str, value_key: str,
                out_key: str = "max_qty", out_value: str = None) -> Optional[List[Dict[str, float]]]:
    """Normalize a YAML list of {bound, value} rows, sorted by bound. None if unusable."""
    if not isinstance(rows, list) or not rows:
        return None
    out_value = out_value or value_key
    table = []
    for row in rows:
        if not isinstance(row, dict) or not _is_number(row.get(bound_key)) or not _is_number(row.get(value_key)):
            return None
        table.append({out_key: float(row[bound_key]), out_value: float(row[value_key])})
    table.sort(key=lambda r: r[out_key])
    return table


def _tier_value(rows: Any, qty: int, value_key: str, default: float) -> float:
    if not isinstance(rows, list):
        return default
    for row in rows:
        if isinstance(row, dict) and _is_number(row.get("max_qty")) and qty <= row["max_qty"]:
            return float(row.get(value_key) or 0.0)
    return default


class SmartGiftPricingCalculator:
    # config/pricing_rules_formula.yaml is the declared source of truth for the formula
    # lane (docs/DATA_PIPELINE_AND_VAULT_STRUCTURE.md). Until 2026-09-10 this class read
    # key names that file never had ("currency_fx", "shipping_rates"), so every constant
    # silently came from the module defaults below. The defaults are now the fallback for
    # when the config is missing or unreadable, not the normal path.
    CONFIG_CANDIDATES = (
        os.path.join(os.path.dirname(__file__), "..", "..", "config", "pricing_rules_formula.yaml"),
        "config/pricing_rules_formula.yaml",
    )

    def __init__(self, fx: Optional[float] = None, config_path: Optional[str] = None,
                 usd_to_thb: Optional[float] = None):
        # Precedence: explicit constructor argument > config file > module default.
        self.config_path = config_path
        self.fx = DEFAULT_FX
        self.usd_to_thb = None
        self.rates = copy.deepcopy(RATES)
        self.min_cbm = MIN_CBM
        self.sea_threshold = SEA_THRESHOLD
        self.density_switch = DENSITY_SWITCH
        self.season_months = list(SEASON_MONTHS)
        self.floors = copy.deepcopy(FLOORS)
        self.sof_table = copy.deepcopy(SMALL_ORDER_FACTORS)
        self.markup_bands = copy.deepcopy(MARKUP_BANDS_STANDARD)
        self.profiles = copy.deepcopy(PROFILES)
        self.logo_methods = copy.deepcopy(LOGO_METHODS)
        self.logo_positions_rule = dict(LOGO_POSITIONS_RULE)
        self.lead_times = copy.deepcopy(LEAD_TIME_WORKING_DAYS)
        self.default_inland_rmb = DEFAULT_INLAND_RMB
        self.price_step_thb = DEFAULT_PRICE_STEP_THB
        self.config_source = {"path": None, "version": None, "sha256": None, "applied": []}

        self._load_config()

        if fx is not None:
            self.fx = float(fx)
        if usd_to_thb is not None:
            self.usd_to_thb = float(usd_to_thb)
        if self.usd_to_thb is None:
            # Last-resort estimate when no explicit rate and no config: ~6.5 CNY per USD
            self.usd_to_thb = self.fx * 6.5

    def _load_config(self):
        for path in [self.config_path, *self.CONFIG_CANDIDATES]:
            if not path or not os.path.exists(path):
                continue
            try:
                with open(path, "rb") as f:
                    raw = f.read()
                text = raw.decode("utf-8-sig")
                if path.endswith((".yaml", ".yml")):
                    if yaml is None:
                        continue
                    data = yaml.safe_load(text)
                else:
                    data = json.loads(text)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            self.config_source = {
                "path": os.path.normpath(path),
                "version": data.get("version"),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "applied": self._apply_config(data),
            }
            return

    def _apply_config(self, data: Dict[str, Any]) -> List[str]:
        """Overlay a parsed pricing_rules_formula document. Returns the blocks applied."""
        applied: List[str] = []

        fx_block = data.get("currency_exchange_rates") or {}
        if _is_number(fx_block.get("cny_to_thb")):
            self.fx = float(fx_block["cny_to_thb"])
            applied.append("currency_exchange_rates.cny_to_thb")
        if _is_number(fx_block.get("usd_to_thb")):
            self.usd_to_thb = float(fx_block["usd_to_thb"])
            applied.append("currency_exchange_rates.usd_to_thb")

        log = data.get("logistics_density_and_freight") or {}
        if _is_number(log.get("density_threshold_kg_per_cbm")):
            self.density_switch = float(log["density_threshold_kg_per_cbm"])
        if _is_number(log.get("min_chargeable_cbm")):
            self.min_cbm = float(log["min_chargeable_cbm"])
        if _is_number(log.get("sea_threshold_cbm")):
            self.sea_threshold = float(log["sea_threshold_cbm"])
        if isinstance(log.get("seasonality_peak_months"), list) and log["seasonality_peak_months"]:
            self.season_months = [int(m) for m in log["seasonality_peak_months"]]
        if log:
            applied.append("logistics_density_and_freight")
        inland = log.get("inland_china_freight") or {}
        if _is_number(inland.get("default_rate_cny_per_set")):
            self.default_inland_rmb = float(inland["default_rate_cny_per_set"])
            applied.append("inland_china_freight.default_rate_cny_per_set")

        step = (data.get("price_rounding") or {}).get("ladder_price_step_thb")
        if _is_number(step) and float(step) > 0:
            self.price_step_thb = float(step)
            applied.append("price_rounding")

        floors = _tier_table(data.get("profit_floors"), "max_qty", "thb")
        if floors:
            self.floors = floors
            applied.append("profit_floors")
        else:
            legacy = data.get("profit_floors_thb") or {}
            if _is_number(legacy.get("small_order_floor")) and _is_number(legacy.get("standard_floor")):
                self.floors = [
                    {"max_qty": 20, "thb": float(legacy["small_order_floor"])},
                    {"max_qty": float("inf"), "thb": float(legacy["standard_floor"])},
                ]
                applied.append("profit_floors_thb")

        sof = _tier_table(data.get("small_order_factors"), "max_qty", "sof")
        if sof:
            self.sof_table = sof
            applied.append("small_order_factors")

        bands = _tier_table(data.get("markup_bands_standard"), "max_cost_thb", "markup_multiplier",
                            out_key="max_cost", out_value="markup")
        if bands:
            self.markup_bands = bands
            applied.append("markup_bands_standard")

        for key, block_name in (("standard", "standard_quote_profile"),
                                ("corporate", "corporate_quote_profile")):
            profile = self._read_profile(data.get(block_name))
            if profile:
                self.profiles[key] = profile
                applied.append(block_name)

        if isinstance(data.get("logo_methods"), dict) and data["logo_methods"]:
            self.logo_methods = copy.deepcopy(data["logo_methods"])
            applied.append("logo_methods")
        if isinstance(data.get("logo_positions_rule"), dict) and data["logo_positions_rule"]:
            self.logo_positions_rule = dict(data["logo_positions_rule"])
            applied.append("logo_positions_rule")
        if isinstance(data.get("lead_time_working_days"), dict) and data["lead_time_working_days"]:
            self.lead_times = copy.deepcopy(data["lead_time_working_days"])
            applied.append("lead_time_working_days")

        matrix = data.get("shipping_rate_matrix") or data.get("shipping_rates") or data.get("rates")
        if isinstance(matrix, dict) and matrix:
            self._merge_rates(matrix)
            applied.append("shipping_rate_matrix")

        return applied

    def _read_profile(self, block: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(block, dict):
            return None
        breaks, factors = block.get("breaks"), block.get("factors")
        anchor = block.get("anchor_qty", block.get("anchor"))
        if not (isinstance(breaks, list) and isinstance(factors, list)):
            return None
        if len(breaks) != len(factors) or anchor not in breaks:
            # A ladder whose factors do not line up with its breaks would price silently
            # wrong, so the block is rejected and the module default stays in place.
            return None
        profile: Dict[str, Any] = {
            "name": block.get("name", ""),
            "breaks": [int(b) for b in breaks],
            "factors": [float(f) for f in factors],
            "anchor": int(anchor),
            "basis": block.get("basis", "landed"),
        }
        if _is_number(block.get("flat_markup")):
            profile["flat_markup"] = float(block["flat_markup"])
        if block.get("reference_goods_type"):
            profile["ref_goods"] = block["reference_goods_type"]
        if block.get("markup_source") == "markup_bands_standard" or "flat_markup" not in profile:
            profile["markup_bands"] = None  # resolved against self.markup_bands at quote time
        return profile

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

    def describe_config(self) -> Dict[str, Any]:
        """Which config file is in effect and which blocks it supplied."""
        return dict(self.config_source)

    def positions_for_code(self, code: str) -> int:
        """Pieces in the set (last digit of the code) plus the gift box and the bag."""
        rule = self.logo_positions_rule
        pieces = 1
        if rule.get("pieces_from_code_last_digit", True):
            match = re.search(r"(\d)\s*$", code or "")
            if match:
                pieces = int(match.group(1)) or 1
        return max(int(rule.get("min_positions", 1)), pieces + int(rule.get("extra_positions", 0)))

    def get_small_order_factor(self, qty: int) -> float:
        for tier in self.sof_table:
            if qty <= tier["max_qty"]:
                return tier["sof"]
        return 1.0

    def get_floor_profit(self, qty: int) -> float:
        for f in self.floors:
            if qty <= f["max_qty"]:
                return f["thb"]
        return self.floors[-1]["thb"] if self.floors else 3000.0

    def resolve_shipping_mode(self, mode: str, month: int, volume_cbm: float) -> str:
        if mode != "auto":
            return mode
        if month in self.season_months:
            return "truck"
        if volume_cbm > self.sea_threshold:
            return "sea"
        return "truck"

    def calculate_freight(self, qty: int, upc: int, cbm: float, kg: Optional[float],
                          warehouse: str, mode: str, month: int, goods_type: str, tier: str) -> Dict[str, Any]:
        cartons = math.ceil(qty / max(upc, 1))
        volume_cbm = round(cartons * max(cbm, self.min_cbm), 2)
        weight_kg = round(cartons * kg, 2) if kg else None

        density = (kg / cbm) if (kg and cbm > 0) else 0.0
        charged_by = "weight" if density >= self.density_switch else "volume"
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
        # Rate tables come from logo_methods in the config; the flat and UV rates stay
        # caller-supplied because they are quoted per job, not published in the catalog.
        spec = self.logo_methods.get(method)
        if method == "none" or spec is None:
            return 0.0
        positions, colors = max(1, positions), max(1, colors)
        if method == "flat":
            return qty * positions * rate
        if method == "uv":
            return qty * positions * uv_rate * self.usd_to_thb

        if method == "hotstamp":
            per = _tier_value(spec.get("per_piece_over_100_usd"), qty, "usd", 0.0)
            usd = (float(spec.get("setup_usd") or 0.0) + max(0, qty - 100) * per) * positions
        elif method == "hotstamp_text":
            usd = float(spec.get("flat_usd") or 0.0) * positions
        elif method == "engrave":
            usd = qty * _tier_value(spec.get("per_piece_usd"), qty, "usd", 0.0) * positions
        elif method == "silk":
            cap = float(spec.get("flat_usd_up_to_qty") or 0)
            base = float(spec.get("flat_usd") or 0.0) if qty <= cap else qty * float(spec.get("per_piece_usd_above") or 0.0)
            usd = base * positions * colors
        else:
            return 0.0
        return usd * self.usd_to_thb

    def calculate_landed_cost(self, rmb: float, qty: int, upc: int, cbm: float, kg: Optional[float],
                              warehouse: str = "guangzhou_shenzhen", mode: str = "auto", month: int = 8,
                              goods_type: str = "general", tier: str = "gold",
                              inland_rmb: Optional[float] = None, custom_ucost: float = 0.0,
                              logo_method: str = "none", logo_positions: int = 1, logo_colors: int = 1,
                              logo_rate: float = 0.0, logo_uv_rate: float = 0.0) -> Dict[str, Any]:
        if inland_rmb is None:
            inland_rmb = self.default_inland_rmb
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
        prof = self.profiles.get(profile_key, self.profiles["corporate"])
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
            bands = prof.get("markup_bands") or self.markup_bands
            markup = bands[-1]["markup"]
            for band in bands:
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

            final_price = self.round_up_to_step(max(ladder_price, floor_price), self.price_step_thb)
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
