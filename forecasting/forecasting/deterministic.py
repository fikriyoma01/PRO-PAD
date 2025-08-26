from __future__ import annotations
from datetime import date
from typing import Dict, Any, List, Optional

TAXES = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]

def _p(params: dict, overrides: dict | None, key: str, default=None):
    """Helper to get a parameter, prioritizing scenario overrides."""
    if overrides and key in overrides:
        return overrides[key]
    return params.get(key, default)

def _collect_dict(params: dict, overrides: dict | None, prefix: str, defaults: dict[str, float]):
    """Helper to collect a dictionary of parameters for all tax types."""
    out = {}
    for k in TAXES:
        out[k] = float(_p(params, overrides, f"{prefix}.{k}", defaults.get(k, 1.0)) or 0.0)
    return out

def driver_based_forecast(
    target_year: int,
    params: dict,
    overrides: dict | None = None,
    hist_data: Any = None, # Pandas DataFrame, unused in this model but needed for consistent signature
) -> Dict[str, Any]:
    """
    Transparent driver-based model as described in the main prompt.
    Formula: Final_Value = Total_Base * Share * (1 + Elasticity * GDP_Growth) * Policy_Multiplier
    """
    base_total = float(_p(params, overrides, "base_total", 3.2e12) or 0.0)
    g = float(_p(params, overrides, "gdp_growth", 0.05) or 0.0)

    # Default values are illustrative
    shares = _collect_dict(params, overrides, "share", {"PKB": 0.34, "BBNKB": 0.27, "PBBKB": 0.22, "PAP": 0.07, "ROKOK": 0.10})
    elas = _collect_dict(params, overrides, "elas", {"PKB": 1.10, "BBNKB": 0.95, "PBBKB": 0.85, "PAP": 0.70, "ROKOK": 0.60})
    policy = _collect_dict(params, overrides, "policy", {k: 1.0 for k in TAXES})

    # Normalize shares to sum to 1
    share_sum = sum(shares.values()) or 1.0
    normalized_shares = {k: v / share_sum for k, v in shares.items()}

    # Project total PAD first
    projected_total = base_total * (1.0 + g)

    # Calculate value for each tax component
    components = []
    final_total = 0
    for tax_type in TAXES:
        responsiveness = (1.0 + elas[tax_type] * g)
        value = projected_total * normalized_shares[tax_type] * responsiveness * policy[tax_type]
        # For this model, p10, p50, p90 are the same as the point forecast
        components.append({
            "jenis_pajak": tax_type,
            "nilai": value,
            "p10": value,
            "p50": value,
            "p90": value,
        })
        final_total += value

    # Structure the output
    return {
        "total": final_total,
        "components": components,
        "meta": {
            "model_name": "DriverBased-v1",
            "assumptions": {
                "base_total": base_total,
                "gdp_growth": g,
                "shares": normalized_shares,
                "elasticities": elas,
                "policies": policy,
            }
        }
    }
