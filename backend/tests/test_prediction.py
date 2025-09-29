import pytest
import pandas as pd
from types import SimpleNamespace
from fastapi import HTTPException

from services.prediction import run_prediction
from schemas.requests import PredictRequest, CarFeatures

@pytest.fixture
def fake_app():
    """Fake FastAPI app with a models dictionary in state"""
    class App:
        state = SimpleNamespace()
    return App()

@pytest.fixture
def fake_req():
    """Fake PredictionRequest with valid CarFeatures"""
    car_features = CarFeatures(
        TaskName="Brake service",
        Make="TOYOTA",
        Model="TOYOTA COROLLA",
        Year=2015,
        FuelType="Petrol",
        Transmission="Auto",
        EngineSize=1.8,
        DriveType="FWD",
        Distance=50000,
        Months=12,
        AdjustedPrice=None
    )
    return PredictRequest(
        model_name="test_model",
        features=car_features
    )

@pytest.fixture(autouse=True)
def patch_prediction_dependencies(monkeypatch):
    """Patch preprocessing, SHAP plotting, and MODEL_FEATURES to isolate tests"""
    monkeypatch.setattr(
        "services.prediction.preprocess",
        lambda features, model_name: pd.DataFrame([features.model_dump()])
    )

    monkeypatch.setattr(
        "services.prediction.generate_shap_plot",
        lambda *a, **kw: "fake_shap"
    )

    from services import prediction
    monkeypatch.setitem(
        prediction.MODEL_FEATURES,
        "test_model",
        ["Feature1"]
    )

# Test handling of unknown models: ensures proper error response when model is not loaded
def test_unknown_model(fake_app, fake_req):
    """Should raise 400 if model is not loaded in app.state"""
    fake_app.state.models = {}
    with pytest.raises(HTTPException) as exc:
        run_prediction(fake_app, fake_req)
    assert exc.value.status_code == 400
    assert "Unknown model" in exc.value.detail

# Test successful prediction: ensures prediction runs correctly and SHAP plot is returned
def test_successful_prediction(fake_app, fake_req):
    """Should return correct prediction and SHAP plot"""
    class FakeModel:
        def predict(self, df):
            return [123.45]

    fake_app.state.models = {"test_model": FakeModel()}

    result = run_prediction(fake_app, fake_req)
    assert result["model"] == "test_model"
    assert result["prediction"] == 123.45
    assert result["plots"]["shap_png"] == "fake_shap"
    assert result["features"] == fake_req.features.model_dump()

# Test SHAP plot failure: ensures prediction still succeeds if plotting fails
def test_shap_fails(fake_app, fake_req, monkeypatch):
    """SHAP plot fails -> returns None but prediction succeeds"""
    class FakeModel:
        def predict(self, df):
            return [123.45]

    fake_app.state.models = {"test_model": FakeModel()}

    monkeypatch.setattr(
        "services.prediction.generate_shap_plot",
        lambda *a, **kw: (_ for _ in ()).throw(Exception("fail"))
    )

    result = run_prediction(fake_app, fake_req)
    assert result["plots"]["shap_png"] is None
    assert result["prediction"] == 123.45

# Test model prediction failure: ensures proper HTTP 500 is raised if model.predict throws
def test_model_predict_fails(fake_app, fake_req):
    """Model.predict raises exception -> HTTP 500"""
    class BrokenModel:
        def predict(self, df):
            raise ValueError("prediction failed")

    fake_app.state.models = {"test_model": BrokenModel()}

    with pytest.raises(HTTPException) as exc:
        run_prediction(fake_app, fake_req)
    assert exc.value.status_code == 500
    assert "Model prediction failed" in exc.value.detail
