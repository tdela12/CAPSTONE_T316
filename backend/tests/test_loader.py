from models.loader import load_all_models, load_historical_sets, load_rego_data
from catboost import CatBoostRegressor

# Test that all models are loaded correctly: ensures load_all_models returns a dict of CatBoost models
def test_load_all_models():
    models = load_all_models()
    assert isinstance(models, dict)
    assert all(isinstance(model, CatBoostRegressor) for model in models.values())

# Test that historical datasets are loaded: ensures load_historical_sets returns a dictionary
def test_load_historical_sets():
    historical_sets = load_historical_sets()
    assert isinstance(historical_sets, dict)
    
# Test that registration data is loaded: ensures load_rego_data returns a non-empty DataFrame
def test_load_rego_data():
    rego_data = load_rego_data()
    assert not rego_data.empty
