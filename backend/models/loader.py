from catboost import CatBoostRegressor, Pool
import pandas as pd
from config import MODEL_PATHS, DATA_PATHS
from typing import Dict

def load_catboost_model(path: str) -> CatBoostRegressor:
    model = CatBoostRegressor()
    model.load_model(str(path))
    return model

def load_all_models() -> Dict[str, CatBoostRegressor]:
    models = {}
    for name, p in MODEL_PATHS.items():
        try:
            models[name] = load_catboost_model(p)
        except Exception as e:
            # log but don't crash the server — you can decide to raise instead
            raise RuntimeError(f"Failed to load {name} model from {p}: {e}")
    return models

def load_csv(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return pd.DataFrame(columns=["AdjustedPrice"])

def load_historical_sets():
    return {name: load_csv(path) for name, path in DATA_PATHS.items() if name != "Rego"}

def load_rego_data():
    return load_csv(DATA_PATHS["Rego"])
