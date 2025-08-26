from __future__ import annotations
from typing import Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session

# The new entrypoint from our forecasting package
from propad_forecasting import generate_forecast

from ..models import RealisasiTahunan

def run_forecast(
    target_year: int,
    params: dict,
    overrides: Optional[dict],
    db: Session, # Add db session to fetch historical data
) -> Dict[str, Any]:
    """
    New forecast engine service.
    This function acts as a bridge between the API layer and the forecasting package.
    It fetches necessary data from the database and calls the core forecasting logic.
    """

    # 1. Fetch historical data from the database
    # This query will be executed by the caller (the router)
    historical_query = db.query(
        RealisasiTahunan.tahun,
        RealisasiTahunan.jenis_pajak,
        RealisasiTahunan.nilai
    ).all()

    # Convert to pandas DataFrame
    if historical_query:
        hist_df = pd.DataFrame(historical_query, columns=['tahun', 'jenis_pajak', 'nilai'])
    else:
        hist_df = pd.DataFrame(columns=['tahun', 'jenis_pajak', 'nilai'])

    # 2. Call the forecasting package orchestrator
    # The orchestrator now handles everything: model execution, averaging, reconciliation.
    forecast_result = generate_forecast(
        target_year=target_year,
        params=params,
        overrides=overrides,
        hist_data=hist_df
    )

    # 3. Return the structured result
    # The format from generate_forecast should already match what the API router expects
    # (an object with 'annual' and 'meta' keys).
    return forecast_result
