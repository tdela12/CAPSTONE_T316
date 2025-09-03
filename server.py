# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from catboost import CatBoostRegressor
import numpy as np

app = FastAPI()

# -----------------------------
# Enable CORS
# -----------------------------
origins = [
    "http://localhost:3000",   # React dev server (CRA)
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*"  # allow all # (care in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],          
)

# -----------------------------
# Load multiple CatBoost models
# -----------------------------
models = {
    "Capped": CatBoostRegressor().load_model("models/capped_model.cbm"),
    "Logbook": CatBoostRegressor().load_model("models/logbook_model.cbm"),
    "Prescribed": CatBoostRegressor().load_model("models/prescribed_model.cbm"),
    "Repair": CatBoostRegressor().load_model("models/repair_model.cbm"),
}

MODEL_FEATURES ={
    "Capped": ["Make", "Model", "Year", "FuelType", "EngineSize", "DriveType", "Distance", "Months"],
    "Logbook": ["Make", "Model", "Year", "FuelType", "EngineSize", "Distance", "Months"],
    "Prescribed": ["Make", "Model", "Year", "FuelType", "EngineSize", "Transmission", "DriveType", "Distance"],
    "Repair": ["Make", "Model", "FuelType", "EngineSize", "Odometer", "Distance", "Months"],
}

# -----------------------------
# Pydantic models for input
# -----------------------------
class CarFeatures(BaseModel):
    TaskName: str
    Odometer: Optional[float] = None
    Make: str
    Model: str
    Year: Optional[int] = None
    FuelType: Optional[str] = None
    Transmission: Optional[str] = None
    EngineSize: Optional[float] = None
    DriveType: Optional[str] = None 
    Distance: Optional[float] = None
    Months: Optional[float] = None
    AdjustedPrice: float

class PredictRequest(BaseModel):
    model_name: str
    features: CarFeatures

# -----------------------------
# Preprocessing
# -----------------------------
def preprosses(raw_data: CarFeatures, model_name: str):
    data_dict = raw_data.model_dump()
    
    # Drop unwanted features
    drop_features = ["AdjustedPrice", "Odometer"]
    cleaned_data = {k: v for k, v in data_dict.items() if k not in drop_features}
    
    for cat in ["TaskName", "DriveType", "Make", "Model", "FuelType"]:
        value = cleaned_data.get(cat)
        if value is None:        
            cleaned_data[cat] = "missing"
        else:
            cleaned_data[cat] = str(value)
            
    
    # Get the correct feature order for the model
    feature_order = MODEL_FEATURES.get(model_name)
    if not feature_order:
        raise ValueError(f"No feature mapping found for model: {model_name}")
    
    # Build ordered feature list
    feature_list = [cleaned_data.get(k, 0) for k in feature_order]  # default 0 if missing
    
    return [feature_list]



# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post("/predict")
def predict(req: PredictRequest):
    if req.model_name not in models:
        return {"error": f"Unknown model {req.model_name}"}
    
    model = models[req.model_name]

    # Preprocess features
    processed = preprosses(req.features, req.model_name)

    # Make prediction
    prediction = model.predict(processed)

    return {"model": req.model_name, "prediction": prediction.tolist()}
