from schemas.requests import CarFeatures
from config import MODEL_FEATURES

def preprocess(raw_data: CarFeatures, model_name: str):
    data_dict = raw_data.model_dump()
    drop_features = ["AdjustedPrice", "Odometer"]
    cleaned_data = {k: v for k, v in data_dict.items() if k not in drop_features}

    for cat in ["TaskName", "DriveType", "Make", "Model", "FuelType", "Transmission"]:
        value = cleaned_data.get(cat)
        cleaned_data[cat] = str(value) if value is not None else "missing"

    feature_order = MODEL_FEATURES.get(model_name)
    if not feature_order:
        raise ValueError(f"No feature mapping found for model: {model_name}")

    feature_list = [cleaned_data.get(k, 0) for k in feature_order]
    return [feature_list]
