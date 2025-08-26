import pytest
import pandas as pd
import numpy as np
from forecasting import generate_forecast

# Sample parameters for testing
@pytest.fixture
def sample_params():
    return {
        "base_total": 1000.0,
        "gdp_growth": 0.05,
        "share.PKB": 0.4,
        "share.BBNKB": 0.3,
        "share.PBBKB": 0.2,
        "share.PAP": 0.05,
        "share.ROKOK": 0.05,
        "elas.PKB": 1.1,
        "elas.BBNKB": 1.0,
        "elas.PBBKB": 0.9,
        "elas.PAP": 0.8,
        "elas.ROKOK": 0.7,
        "policy.PKB": 1.0,
        "policy.BBNKB": 1.0,
        "policy.PBBKB": 1.0,
        "policy.PAP": 1.0,
        "policy.ROKOK": 1.0,
    }

# Sample historical data for testing
@pytest.fixture
def sample_hist_data():
    years = range(2020, 2025)
    taxes = ["PKB", "BBNKB", "PBBKB", "PAP", "ROKOK"]
    data = []
    for year in years:
        for tax in taxes:
            # Create some synthetic data with a trend
            nilai = 100 + (year - 2020) * 20 + np.random.uniform(-5, 5)
            data.append({"tahun": year, "jenis_pajak": tax, "nilai": nilai})
    return pd.DataFrame(data)

def test_generate_forecast_output_structure(sample_params, sample_hist_data):
    """
    Tests that the main orchestrator returns the expected dictionary structure.
    """
    target_year = 2025
    overrides = None

    result = generate_forecast(target_year, sample_params, overrides, sample_hist_data)

    assert isinstance(result, dict)
    assert "annual" in result
    assert "meta" in result
    assert isinstance(result["annual"], list)
    assert len(result["annual"]) > 0
    assert isinstance(result["meta"], dict)

    # Check structure of a component
    component = result["annual"][0]
    assert "jenis_pajak" in component
    assert "nilai" in component
    assert "p10" in component
    assert "p50" in component
    assert "p90" in component

def test_generate_forecast_reconciliation(sample_params, sample_hist_data):
    """
    Tests that the sum of components equals the total forecast after reconciliation.
    """
    target_year = 2025
    overrides = None

    result = generate_forecast(target_year, sample_params, overrides, sample_hist_data)

    # Get the total from the meta payload (post-reconciliation total)
    reconciled_total = result["meta"]["reconciliation"]["post_total"]

    # Sum the individual components
    components_sum = sum(item["nilai"] for item in result["annual"])

    # They should be very close (allowing for float precision issues)
    assert np.isclose(reconciled_total, components_sum)

def test_generate_forecast_meta_payload(sample_params, sample_hist_data):
    """
    Tests that the meta payload contains the required information.
    """
    target_year = 2025
    overrides = None

    result = generate_forecast(target_year, sample_params, overrides, sample_hist_data)

    meta = result["meta"]
    assert "assumptions" in meta
    assert "model_weights" in meta
    assert "backtest" in meta
    assert "reconciliation" in meta
    assert "interval" in meta

    # Check weights
    weights = meta["model_weights"]
    assert "driver_based" in weights
    assert "statistical_ets" in weights
    assert np.isclose(weights["driver_based"] + weights["statistical_ets"], 1.0)

    # Check backtest MAPEs
    backtest = meta["backtest"]
    assert "driver_mape" in backtest
    assert "stat_mape" in backtest
    assert backtest["driver_mape"] >= 0
    assert backtest["stat_mape"] >= 0

def test_forecast_with_empty_history(sample_params):
    """
    Tests that the forecast runs without error even with no historical data.
    """
    target_year = 2025
    overrides = None
    empty_df = pd.DataFrame(columns=['tahun', 'jenis_pajak', 'nilai'])

    try:
        result = generate_forecast(target_year, sample_params, overrides, empty_df)
        # Backtesting should fail gracefully and models should produce some output
        assert result is not None
        assert result['meta']['backtest']['driver_mape'] == 999.0
        assert result['meta']['backtest']['stat_mape'] == 999.0
    except Exception as e:
        pytest.fail(f"Forecast with empty history failed unexpectedly: {e}")
