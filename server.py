# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from catboost import CatBoostRegressor, Pool
import numpy as np
import shap
import matplotlib
matplotlib.use("Agg")  # non-GUI backend for server-side plotting
import matplotlib.pyplot as plt
import io
import base64
import json
import pandas as pd


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
# Open processed data
# -----------------------------

try:
    historical_df = pd.read_csv("models/training_context.csv")
except FileNotFoundError:
    historical_df = pd.DataFrame(columns=["AdjustedPrice"])

price_series = historical_df["AdjustedPrice"]
price_summary = {
    "min": price_series.min(),
    "q1": price_series.quantile(0.25),
    "median": price_series.median(),
    "q3": price_series.quantile(0.75),
    "max": price_series.max()
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
def preprocess(raw_data: CarFeatures, model_name: str):
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

def filter_df_by_features(df: pd.DataFrame, raw_data: CarFeatures):

    data_dict = raw_data.model_dump()

    make = data_dict.get("Make")
    model = data_dict.get("Model")
    year = data_dict.get("Year")

    filtered_df = df[
        (df["Make"] == make) &
        (df["Model"] == model) &
        (df["Year"] == year)
    ]
    return filtered_df

def build_summary(df, price_col="AdjustedPrice"):
    prices = df[price_col].dropna()
    if prices.empty:
        return {"mean": 0, "median": 0, "iqr_low": 0, "iqr_high": 0}

    q1 = prices.quantile(0.25)
    q3 = prices.quantile(0.75)
    return {
        "mean": prices.mean(),
        "median": prices.median(),
        "iqr_low": q1,
        "iqr_high": q3
    }

def compare_price(predicted_price, summary):
    iqr_low = summary.get("iqr_low", 0)
    iqr_high = summary.get("iqr_high", 0)
    mean = summary.get("mean", 0)
    median = summary.get("median", 0)

    in_iqr = iqr_low <= predicted_price <= iqr_high
    z = (predicted_price - mean) / ((iqr_high - iqr_low) / 1.349) if (iqr_high - iqr_low) != 0 else 0

    return {
        "predicted_price": predicted_price,
        "mean": mean,
        "median": median,
        "iqr_low": iqr_low,
        "iqr_high": iqr_high,
        "within_iqr": in_iqr,
        "z_from_mean": z
    }


def generate_shap_plot(model, processed, feature_names):
    # Dynamically identify categorical features
    categorical_set = {"TaskName", "DriveType", "Make", "Model", "FuelType"}
    cat_features = [f for f in feature_names if f in categorical_set]
    # Calculate SHAP values
    shap_values = model.get_feature_importance(
        Pool(processed, feature_names=feature_names,  cat_features=cat_features),
        type="ShapValues"
    )
    
    # shap_values includes an extra column for expected_value
    shap_values_matrix = shap_values[:, :-1]  
    expected_value = shap_values[:, -1][0]

    # Use SHAP’s waterfall plot for the first sample
    explainer = shap.Explanation(
        values=shap_values_matrix[0],
        base_values=expected_value,
        data=processed[0],
        feature_names=feature_names,
    )
    
    plt.figure()
    shap.plots.waterfall(explainer, show=False)

    # Save plot to base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return img_base64

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def plot_price_comparison_base64(filtered_df, predicted_price, price_col="AdjustedPrice"):
    # ----- Boxplot -----
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.boxplot(filtered_df[price_col].dropna(), vert=False, patch_artist=True,
                boxprops=dict(facecolor='lightblue'))
    ax1.axvline(predicted_price, color='red', linestyle='--', label='Predicted')
    ax1.set_title("Historical Price Distribution (Boxplot)")
    ax1.set_xlabel("Price")
    ax1.legend()
    box_b64 = fig_to_base64(fig1)
    plt.close(fig1)

    # ----- Histogram -----
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.hist(filtered_df[price_col].dropna(), bins=20, edgecolor='black', alpha=0.7)
    ax2.axvline(predicted_price, color='red', linestyle='--', label='Predicted')
    ax2.set_title("Historical Price Distribution (Histogram)")
    ax2.set_xlabel("Price")
    ax2.set_ylabel("Frequency")
    ax2.legend()
    hist_b64 = fig_to_base64(fig2)
    plt.close(fig2)

    return box_b64, hist_b64



# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post("/predict")
def predict(req: PredictRequest):
    if req.model_name not in models:
        return {"error": f"Unknown model {req.model_name}"}
    
    model = models[req.model_name]

    # Preprocess features
    processed = preprocess(req.features, req.model_name)

    # Make prediction
    prediction = model.predict(processed)
    prediction = float(prediction[0])

    shap_plot = generate_shap_plot(model, processed, MODEL_FEATURES[req.model_name])

    filtered = filter_df_by_features(historical_df, req.features)

    if filtered.empty:
        return {
            "model": req.model_name,
            "prediction": prediction,
            "shap_plot": shap_plot,
            "message": "No historical rows match these features"
        }
    summary = build_summary(filtered, price_col="AdjustedPrice")
    comparison = compare_price(prediction, summary)

    box_b64, hist_b64 = plot_price_comparison_base64(filtered, prediction, price_col="AdjustedPrice")

    return {
        "model": req.model_name,
        "prediction": prediction,
        "shap_plot": shap_plot,          
        "historical_summary": summary,   
        "comparison": comparison,        
        "plots": {
            "boxplot_png": box_b64,
            "histogram_png": hist_b64
        }
    }