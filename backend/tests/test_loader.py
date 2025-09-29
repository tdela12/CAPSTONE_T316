from models.loader import  load_all_models, load_historical_sets, load_rego_data
from catboost import CatBoostRegressor

def test_load_all_models():
    models = load_all_models()
    assert isinstance(models, dict)
    assert all(isinstance(model, CatBoostRegressor) for model in models.values())

def test_load_historical_sets():
    historical_sets = load_historical_sets()
    assert isinstance(historical_sets, dict)
    
def test_load_rego_data():
    rego_data = load_rego_data()
    assert not rego_data.empty