
import pytest
from models.preprocess import preprocess
from schemas.requests import CarFeatures
from config import MODEL_FEATURES

@pytest.fixture
def car_features():
    """Return a valid CarFeatures object for testing"""
    return CarFeatures(
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
        AdjustedPrice=250.0
    )

# Test basic preprocessing: ensures output is in correct format and values match input
def test_preprocess_basic(monkeypatch, car_features):
    """Test basic preprocessing output"""
    # patch MODEL_FEATURES to ensure consistent ordering
    monkeypatch.setitem(MODEL_FEATURES, "test_model", [
        "TaskName", "Make", "Model", "Year", "FuelType", "Transmission",
        "EngineSize", "DriveType", "Distance", "Months"
    ])

    result = preprocess(car_features, "test_model")
    assert isinstance(result, list)
    assert isinstance(result[0], list)

    data_dict = car_features.model_dump()
    assert "AdjustedPrice" in data_dict
    assert len(result[0]) == len(MODEL_FEATURES["test_model"])

    assert result[0][0] == "Brake service"  # TaskName
    assert result[0][1] == "TOYOTA"         # Make

# Test handling of missing categorical features: ensures missing values are replaced with 'missing'
def test_preprocess_missing_categoricals(monkeypatch):
    """Categorical fields missing -> should fill with 'missing'"""
    features = CarFeatures(
        TaskName=None,
        Make="TOYOTA",
        Model="TOYOTA COROLLA",
        Year=2015,
        FuelType=None,
        Transmission=None,
        EngineSize=1.8,
        DriveType=None,
        Distance=50000,
        Months=12,
        AdjustedPrice=100
    )

    monkeypatch.setitem(MODEL_FEATURES, "test_model", [
        "TaskName", "Make", "Model", "Year", "FuelType", "Transmission",
        "EngineSize", "DriveType", "Distance", "Months"
    ])

    result = preprocess(features, "test_model")
    # categorical fields with None should be 'missing'
    assert result[0][0] == "missing"  # TaskName
    assert result[0][4] == "missing"  # FuelType
    assert result[0][5] == "missing"  # Transmission
    assert result[0][7] == "missing"  # DriveType

# Test that feature order in output matches MODEL_FEATURES: ensures consistent mapping
def test_preprocess_feature_order(monkeypatch, car_features):
    """Test that output respects MODEL_FEATURES order"""
    monkeypatch.setitem(MODEL_FEATURES, "test_model", [
        "Distance", "Year", "EngineSize", "TaskName"
    ])
    result = preprocess(car_features, "test_model")
    # output length matches feature_order
    assert len(result[0]) == 4
    # first element corresponds to Distance
    assert result[0][0] == 50000
    # last element corresponds to TaskName
    assert result[0][3] == "Brake service"

# Test behavior with unknown model name: ensures proper error is raised for invalid models
def test_preprocess_unknown_model(car_features):
    """Should raise ValueError if model_name not in MODEL_FEATURES"""
    with pytest.raises(ValueError) as exc:
        preprocess(car_features, "unknown_model")
    assert "No feature mapping found for model" in str(exc.value)
