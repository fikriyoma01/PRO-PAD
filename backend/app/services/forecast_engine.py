# backend/app/services/forecast_engine.py
from __future__ import annotations
from datetime import date

TAXES = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]

def _p(params: dict, overrides: dict | None, key: str, default=None):
    """Ambil parameter: prioritas overrides (dari scenario), lalu params (registry)."""
    if overrides and key in overrides:
        return overrides[key]
    return params.get(key, default)

def _collect_dict(params: dict, overrides: dict | None, prefix: str, defaults: dict[str, float]):
    out = {}
    for k in TAXES:
        out[k] = float(_p(params, overrides, f"{prefix}.{k}", defaults.get(k, 1.0)) or 0.0)
    return out

def run_forecast(target_year: int, params: dict, overrides: dict | None = None):
    """
    Model transparan:
      1) Total dasar: base_total * (1 + gdp_growth)
      2) Bagi ke jenis pajak: share.<JENIS>  (dinormalisasi jika tak tepat 1.0)
      3) Respons growth: (1 + elas.<JENIS> * gdp_growth)
      4) Kebijakan/multiplier: policy.<JENIS>
      Nilai akhir per jenis = total * share * respons * policy
    """
    base_total = float(_p(params, overrides, "base_total", 3_200_000_000_000) or 0.0)
    g = float(_p(params, overrides, "gdp_growth", 0.05) or 0.0)

    shares = _collect_dict(params, overrides, "share",
                           {"PKB":0.34,"BBNKB":0.27,"PBBKB":0.22,"PAP":0.07,"ROKOK":0.10})
    elas   = _collect_dict(params, overrides, "elas",
                           {"PKB":1.10,"BBNKB":0.95,"PBBKB":0.85,"PAP":0.70,"ROKOK":0.60})
    policy = _collect_dict(params, overrides, "policy",
                           {k:1.00 for k in TAXES})

    # normalisasi share jika tidak pas = 1
    ssum = sum(shares.values()) or 1.0
    shares = {k: v/ssum for k, v in shares.items()}

    # total annual one-step-ahead
    total = base_total * (1.0 + g)

    # hitung nilai per jenis
    rows = []
    model_name = "Transparent-Elasticity-v1"
    for k in TAXES:
        respons = (1.0 + elas[k]*g)
        nilai = total * shares[k] * respons * policy[k]
        rows.append({
            "periode": date(target_year, 12, 31),
            "jenis_pajak": k,
            "nilai": float(round(nilai, 2)),
            "model": model_name
        })

    return rows
