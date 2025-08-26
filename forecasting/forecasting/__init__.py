from __future__ import annotations
import pandas as pd
from typing import Dict, Any, Optional

from .deterministic import driver_based_forecast
from .statistical_models import statistical_forecast
from .model_evaluation import backtest_mape

TAXES = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]

def generate_forecast(
    target_year: int,
    params: dict,
    overrides: Optional[dict],
    hist_data: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Orchestrates the model averaging forecast.
    1. Backtests models to get MAPE scores.
    2. Calculates weights based on inverse MAPE.
    3. Runs models for the target year.
    4. Combines results using weighted averaging.
    5. Performs hierarchical reconciliation.
    6. Returns the final forecast with a detailed meta payload.
    """
    # 1. Backtest models
    mape_driver = backtest_mape(driver_based_forecast, params, overrides, hist_data)
    mape_stat = backtest_mape(statistical_forecast, params, overrides, hist_data)

    # 2. Calculate weights (inverse MAPE, with epsilon for stability)
    epsilon = 0.01
    weight_driver = 1 / (mape_driver + epsilon)
    weight_stat = 1 / (mape_stat + epsilon)
    total_weight = weight_driver + weight_stat

    norm_weight_driver = weight_driver / total_weight
    norm_weight_stat = weight_stat / total_weight

    # 3. Run models for the target year
    driver_result = driver_based_forecast(target_year, params, overrides, hist_data)
    stat_result = statistical_forecast(target_year, params, overrides, hist_data)

    # 4. Combine results (weighted average)
    driver_map = {comp['jenis_pajak']: comp for comp in driver_result['components']}
    stat_map = {comp['jenis_pajak']: comp for comp in stat_result['components']}

    combined_components = []
    unrec_total = 0
    for tax_type in TAXES:
        d_comp = driver_map.get(tax_type, {'nilai': 0, 'p10': 0, 'p50': 0, 'p90': 0})
        s_comp = stat_map.get(tax_type, {'nilai': 0, 'p10': 0, 'p50': 0, 'p90': 0})

        # Safely get values, falling back to the point forecast ('nilai') if interval is None
        d_p10 = d_comp.get('p10') or d_comp.get('nilai', 0)
        d_p50 = d_comp.get('p50') or d_comp.get('nilai', 0)
        d_p90 = d_comp.get('p90') or d_comp.get('nilai', 0)
        s_p10 = s_comp.get('p10') or s_comp.get('nilai', 0)
        s_p50 = s_comp.get('p50') or s_comp.get('nilai', 0)
        s_p90 = s_comp.get('p90') or s_comp.get('nilai', 0)

        # Weighted average for all values
        w_avg_val = (d_comp['nilai'] * norm_weight_driver) + (s_comp['nilai'] * norm_weight_stat)
        w_avg_p10 = (d_p10 * norm_weight_driver) + (s_p10 * norm_weight_stat)
        w_avg_p50 = (d_p50 * norm_weight_driver) + (s_p50 * norm_weight_stat)
        w_avg_p90 = (d_p90 * norm_weight_driver) + (s_p90 * norm_weight_stat)

        combined_components.append({
            'jenis_pajak': tax_type,
            'nilai': w_avg_val,
            'p10': w_avg_p10,
            'p50': w_avg_p50,
            'p90': w_avg_p90,
        })
        unrec_total += w_avg_val

    # Also combine the total forecast from each model
    combined_total = (driver_result['total'] * norm_weight_driver) + \
                     (stat_result['total'] * norm_weight_stat)

    # 5. Hierarchical Reconciliation (top-down, proportional)
    reconciled_components = []
    if unrec_total > 0:
        ratio = combined_total / unrec_total
        for comp in combined_components:
            comp['nilai'] *= ratio
            comp['p10'] *= ratio
            comp['p50'] *= ratio
            comp['p90'] *= ratio
            reconciled_components.append(comp)
    else: # If un-reconciled total is zero, just distribute the total equally
        val_per_comp = combined_total / len(TAXES) if len(TAXES) > 0 else 0
        for tax_type in TAXES:
            reconciled_components.append({
                'jenis_pajak': tax_type, 'nilai': val_per_comp,
                'p10': val_per_comp, 'p50': val_per_comp, 'p90': val_per_comp
            })

    # 6. Construct final response
    final_annual_points = []
    total_p10 = 0
    total_p90 = 0
    for comp in reconciled_components:
        final_annual_points.append({
            "periode": f"{target_year}-12-31",
            "jenis_pajak": comp['jenis_pajak'],
            "nilai": comp['nilai'],
            "p10": comp['p10'],
            "p50": comp['p50'],
            "p90": comp['p90'],
            "model": "ModelAverage-v1",
        })
        total_p10 += comp['p10']
        total_p90 += comp['p90']

    meta_payload = {
        "assumptions": driver_result['meta']['assumptions'], # Use driver-based assumptions as primary
        "model_weights": {
            "driver_based": round(norm_weight_driver, 4),
            "statistical_ets": round(norm_weight_stat, 4),
        },
        "backtest": {
            "driver_mape": round(mape_driver, 4),
            "stat_mape": round(mape_stat, 4),
            "window_years": 3, # As configured in backtest_mape
        },
        "interval": {
            "p10_total": total_p10,
            "p50_total": combined_total,
            "p90_total": total_p90,
        },
        "reconciliation": {
            "method": "TopDownProportional",
            "pre_total": unrec_total,
            "post_total": combined_total
        }
    }

    return {
        "annual": final_annual_points,
        "meta": meta_payload
    }

# Make the main function available for import
__all__ = ["generate_forecast"]
