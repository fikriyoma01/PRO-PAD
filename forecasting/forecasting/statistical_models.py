from __future__ import annotations
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from typing import Dict, Any, Optional

TAXES = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]

def statistical_forecast(
    target_year: int,
    params: dict,
    overrides: dict | None = None,
    hist_data: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Performs a statistical forecast for each tax type using an ETS model.
    """
    results = []
    total_forecast = 0
    model_meta = {}

    if hist_data is None or hist_data.empty:
        # Return zero forecast if no historical data is available
        for tax_type in TAXES:
            results.append({
                "jenis_pajak": tax_type, "nilai": 0,
                "p10": 0, "p50": 0, "p90": 0
            })
        return {"total": 0, "components": results, "meta": {"model_name": "Statistical-ETS-v1", "details": "No history"}}

    # Ensure 'tahun' is the index for time series operations
    if 'tahun' in hist_data.columns:
        hist_data = hist_data.set_index('tahun')

    for tax_type in TAXES:
        # Filter series for the specific tax type and sort by year
        series = hist_data[hist_data['jenis_pajak'] == tax_type]['nilai'].sort_index()

        # Ensure we have enough data points to fit a model
        if len(series) < 3:
            # Fallback to a simple average if series is too short
            forecast_value = series.mean() if not series.empty else 0
            model_type = "SimpleMean_ShortHistory"
        else:
            # Fit an ETS(A,A,N) model - Additive error, Additive trend, No seasonality.
            try:
                model = ETSModel(series, error="add", trend="add", seasonal=None)
                fit = model.fit(disp=False)

                # Get forecast and prediction intervals
                forecast_horizon = 1
                pred = fit.get_prediction(end=fit.nobs + forecast_horizon - 1)
                pred_summary = pred.summary_frame(alpha=0.2) # alpha=0.2 for 80% interval (P10/P90)

                forecast_value = float(pred_summary.loc[fit.nobs, 'mean'])
                p10 = float(pred_summary.loc[fit.nobs, 'pi_lower'])
                p90 = float(pred_summary.loc[fit.nobs, 'pi_upper'])
                p50 = forecast_value # P50 is the mean forecast

                model_type = fit.model.components_shortlabel
            except Exception:
                # Fallback if model fails to converge
                forecast_value = series.mean() if not series.empty else 0
                p10, p50, p90 = None, None, None
                model_type = "ConvergenceFail_Mean"

        results.append({
            "jenis_pajak": tax_type,
            "nilai": forecast_value,
            "p10": p10,
            "p50": p50,
            "p90": p90,
        })
        total_forecast += forecast_value
        model_meta[tax_type] = {"model": model_type, "history_len": len(series)}

    return {
        "total": total_forecast,
        "components": results,
        "meta": {
            "model_name": "Statistical-ETS-v1",
            "details": model_meta,
        }
    }
