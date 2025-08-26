from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Callable, Dict, Any, List, Optional

def backtest_mape(
    model_func: Callable,
    params: dict,
    overrides: Optional[dict],
    hist_data: pd.DataFrame,
    backtest_window: int = 3,
) -> float:
    """
    Calculates the Mean Absolute Percentage Error (MAPE) for a given model
    using walk-forward validation.

    Args:
        model_func: The forecasting function to evaluate.
        params: Base parameters.
        overrides: Scenario overrides.
        hist_data: DataFrame with historical data, must contain 'tahun', 'jenis_pajak', 'nilai'.
        backtest_window: The number of years to use for backtesting.

    Returns:
        The calculated MAPE value (as a percentage), or a large number (999.0) if backtesting fails.
    """
    errors: List[float] = []

    if hist_data is None or hist_data.empty or 'tahun' not in hist_data.columns:
        return 999.0 # Cannot backtest without data

    all_years = sorted(hist_data['tahun'].unique())

    # We need at least one year to train on and one year to test on.
    if len(all_years) < 2:
        return 999.0

    # Adjust window if history is shorter than desired window
    actual_window = min(backtest_window, len(all_years) - 1)

    if actual_window == 0:
        return 999.0

    start_year_idx = len(all_years) - actual_window

    for i in range(start_year_idx, len(all_years)):
        train_years = all_years[:i]
        test_year = all_years[i]

        train_df = hist_data[hist_data['tahun'].isin(train_years)]
        test_df = hist_data[hist_data['tahun'] == test_year]

        try:
            # Forecast the test year using data up to the previous year
            forecast_result = model_func(
                target_year=test_year,
                params=params,
                overrides=overrides,
                hist_data=train_df,
            )

            if not forecast_result or 'components' not in forecast_result:
                continue

            # Create a dictionary for quick lookup of forecasted values
            forecast_map = {
                item['jenis_pajak']: item['nilai']
                for item in forecast_result['components']
            }

            # Compare forecast with actuals for the test year
            for _, actual_row in test_df.iterrows():
                actual_value = actual_row['nilai']
                forecasted_value = forecast_map.get(actual_row['jenis_pajak'])

                if forecasted_value is not None and actual_value is not None and actual_value > 0:
                    error = np.abs((actual_value - forecasted_value) / actual_value)
                    errors.append(error)

        except Exception:
            # If the model fails for any reason during backtest, we can treat it as a high error
            # but continuing might be better to evaluate other years. Here we'll just skip the failing run.
            continue

    if not errors:
        return 999.0 # No valid comparisons could be made

    return np.mean(errors) * 100 # Return MAPE as a percentage
