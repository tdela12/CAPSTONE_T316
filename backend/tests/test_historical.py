import pytest
from fastapi import HTTPException
from types import SimpleNamespace
import pandas as pd
from services.historical import run_historical_summary
from schemas.requests import HistoricalRequest

@pytest.fixture
def fake_app():
    """Fake app with state for testing"""
    class App:
        state = SimpleNamespace()
    return App()

@pytest.fixture
def fake_req():
    """Fake request object"""
    req = HistoricalRequest(
        model_name="test_model",
        features={
            "TaskName": "Brake service",
            "Make": "TOYOTA",
            "Model": "TOYOTA COROLLA",
            "Year": 2015,
            "FuelType": "Petrol",
            "Transmission": "Auto",
            "EngineSize": 1.8,
            "DriveType": "FWD",
            "Distance": 50000,
            "Months": 12,
            "AdjustedPrice": None
        },
        prediction=250.0,
        months=12,
        distance=50000
    )
    return req

@pytest.fixture(autouse=True)
def patch_historical_services(monkeypatch):
    # Patch all external dependencies used in run_historical_summary
    monkeypatch.setattr("services.historical.filter_df_by_features", lambda df, f: df)
    monkeypatch.setattr("services.historical.build_price_summary", lambda df: {"mean": 200})
    monkeypatch.setattr("services.historical.compare_price", lambda pred, summary, prices: {"diff": 0})
    monkeypatch.setattr(
        "services.historical.get_all_price_plots", 
        lambda df, pred, m, d: {"boxplot_png": "data", "histogram_png": "data", "month_vs_price_png": "data", "distance_vs_price_png": "data"}
    )

# Test handling of invalid model names: ensures proper error response when the model does not exist
def test_invalid_model(fake_app, fake_req):
    fake_app.state.historical_sets = {}
    with pytest.raises(HTTPException) as exc:
        run_historical_summary(fake_app, fake_req)
    assert exc.value.status_code == 400

# Test behavior when the historical dataframe is empty: ensures function handles lack of data gracefully
def test_empty_dataframe(fake_app, fake_req, monkeypatch):
    fake_app.state.historical_sets = {"test_model": pd.DataFrame()}

    result = run_historical_summary(fake_app, fake_req)

    assert result["summary"] is None
    assert result["message"] == "No matching historical data available"

# Test behavior when filtered dataframe is empty: ensures filtering logic correctly identifies no matching records
def test_empty_filtered(fake_app, fake_req, monkeypatch):
    df = pd.DataFrame({"AdjustedPrice": [10, 20, 30]})
    fake_app.state.historical_sets = {"test_model": df}

    # Return empty DataFrame after filtering
    monkeypatch.setattr("services.historical.filter_df_by_features", lambda df, f: pd.DataFrame())
    result = run_historical_summary(fake_app, fake_req)

    assert result["summary"] is None
    assert result["message"] == "No matching historical records"

# Test valid case: ensures proper computation of summary, comparison, and plot generation
def test_valid_case(fake_app, fake_req, monkeypatch):
    df = pd.DataFrame({"AdjustedPrice": [100, 200, 300]})
    fake_app.state.historical_sets = {"test_model": df}

    result = run_historical_summary(fake_app, fake_req)

    assert result["summary"] == {"mean": 200}
    assert result["comparison"] == {"diff": 0}
    assert "boxplot_png" in result["plots"]
    assert result["message"] == "Historical summary computed successfully"

# Test exception handling during plotting: ensures function continues gracefully if plot generation fails
def test_plotting_exception(fake_app, fake_req, monkeypatch):
    df = pd.DataFrame({"AdjustedPrice": [100, 200, 300]})
    fake_app.state.historical_sets = {"test_model": df}

    # Throw exception when generating plots
    monkeypatch.setattr("services.historical.get_all_price_plots", lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))

    result = run_historical_summary(fake_app, fake_req)

    assert result["plots"]["boxplot_png"] is None
    assert result["message"] == "Historical summary computed successfully"
