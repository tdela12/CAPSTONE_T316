# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from catboost import CatBoostRegressor
import numpy as np

app = FastAPI()

# Load multiple models
models = {
    "Capped": CatBoostRegressor().load_model("Regression Models/CatBoostRegressionModels/capped_model.cbm"),
    "Logbook": CatBoostRegressor().load_model("Regression Models/CatBoostRegressionModels/logbook_model.cbm"),
    "Prescribed": CatBoostRegressor().load_model("Regression Models/CatBoostRegressionModels/prescribed_model.cbm"),
    "Repair": CatBoostRegressor().load_model("Regression Models/CatBoostRegressionModels/repair_model.cbm"),
}

# Request format
class PredictRequest(BaseModel):
    model_name: str
    features: list[float]

@app.post("/predict")
def predict(req: PredictRequest):
    if req.model_name not in models:
        return {"error": f"Unknown model {req.model_name}"}
    
    model = models[req.model_name]
    data = np.array(req.features).reshape(1, -1)
    processed = preprosses(req.features)
    prediction = model.predict(processed).tolist()
    return {"model": req.model_name, "prediction": prediction}

def preprosses(raw_data: dict):
    # TODO: Implement Preprocessing logic
    preprossesed_data = raw_data  # Placeholder
    return preprossesed_data