# -----------------------------
# Imports
# -----------------------------
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

# -----------------------------
# FastAPI app initialization
# -----------------------------
app = FastAPI()

# -----------------------------
# CORS (Cross-Origin Resource Sharing) Setup
# -----------------------------
# Allow frontend (React/Vite dev servers) to communicate with this backend
origins = [
    "http://localhost:3000",   # React dev server (CRA)
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*"  # allow all (dev purposes only, do not use in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],          
)


# -----------------------------
# Load pretrained CatBoost models
# -----------------------------
# Dictionary holds models by task type
models = {
    "Capped": CatBoostRegressor().load_model("models/capped_model.cbm"),
    "Logbook": CatBoostRegressor().load_model("models/logbook_model.cbm"),
    "Prescribed": CatBoostRegressor().load_model("models/prescribed_model.cbm"),
    "Repair": CatBoostRegressor().load_model("models/repair_model.cbm"),
}

# Define required feature order for each model
MODEL_FEATURES ={
    "Capped": ["Make", "Model", "Year", "FuelType", "Transmission", "EngineSize", "DriveType", "Distance",],
    "Logbook": ["Make", "Model", "Year", "FuelType", "Transmission", "EngineSize", "DriveType", "Distance", "Months"],
    "Prescribed": ["Make", "Model", "Year", "FuelType", "Transmission", "EngineSize", "DriveType", "Distance",],
    "Repair": ["TaskName", "Make", "Model", "Year", "FuelType", "Transmission", "EngineSize", "DriveType", "Distance",],
}

# -----------------------------
# Load historical training context data
# -----------------------------
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=["AdjustedPrice"])

historical_sets = {
    "Capped": load_csv("data/preprocessed_capped_data.csv"),
    "Logbook": load_csv("data/preprocessed_log_data.csv"),
    "Prescribed": load_csv("data/preprocessed_prescribed_data.csv"),
    "Repair": load_csv("data/preprocessed_repair_data.csv"),
}

def build_price_summary(df, price_col="AdjustedPrice"):
    # Make sure the column exists
    if price_col not in df.columns:
        return {"min": 0.0, "q1": 0.0, "median": 0.0, "q3": 0.0, "max": 0.0}

    # Drop missing values
    price_series = df[price_col].dropna()

    # If no valid data, return default zeros
    if price_series.empty:
        return {"min": 0.0, "q1": 0.0, "median": 0.0, "q3": 0.0, "max": 0.0}

    # Compute summary
    return {
        "min": float(price_series.min()),
        "q1": float(price_series.quantile(0.25)),
        "median": float(price_series.median()),
        "q3": float(price_series.quantile(0.75)),
        "max": float(price_series.max()),
    }


# Extract overall price summary (used for global stats)
price_summaries = {
    name: build_price_summary(df)
    for name, df in historical_sets.items()
}

# -----------------------------
# Pydantic request models (input validation)
# -----------------------------
class CarFeatures(BaseModel):
    TaskName: str
    Make: str
    Model: str
    Year: Optional[int] = None
    FuelType: Optional[str] = None
    Transmission: Optional[str] = None
    EngineSize: Optional[float] = None
    DriveType: Optional[str] = None 
    Distance: Optional[float] = None
    Months: Optional[float] = None
    AdjustedPrice: Optional[float] = None

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

# -----------------------------
# Logging functions
# -----------------------------

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

<<<<<<< HEAD
def build_summary(df, price_col="AdjustedPrice"):
    prices = pd.to_numeric(df[price_col], errors="coerce").dropna()
    if prices.empty:
        return {"mean": 0, "median": 0, "iqr_low": 0, "iqr_high": 0}

    q1 = prices.quantile(0.25)
    q3 = prices.quantile(0.75)
    return {
        "mean": float(prices.mean()),
        "median": float(prices.median()),
        "iqr_low": float(q1),
        "iqr_high": float(q3)
    }
=======
>>>>>>> c15e57bfd5f11d8ab447972a41577118d30e18b4

def compare_price(predicted_price, summary):
    iqr_low = summary.get("q1", 0)
    iqr_high = summary.get("q3", 0)
    mean = summary.get("mean", 0)
    median = summary.get("median", 0)

    # Check if prediction falls inside IQR
    in_iqr = iqr_low <= predicted_price <= iqr_high

    # Robust z-score (centered at median, scaled by IQR)
    z_from_median = (
        (predicted_price - median) / ((iqr_high - iqr_low) / 1.349)
        if (iqr_high - iqr_low) != 0 else 0
    )

    # Confidence classification
    if in_iqr:
        confidence = "high"
    elif summary.get("min", 0) <= predicted_price <= summary.get("max", 0):
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "predicted_price": predicted_price,
        "mean": mean,
        "median": median,
        "iqr_low": iqr_low,
        "iqr_high": iqr_high,
        "within_iqr": in_iqr,
        "z_from_median": z_from_median,
        "confidence": confidence
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

def plot_distance_month_comparison(filtered_df, predicted_price, month_value, distance_value):
    plots = {}

    # ----- Scatter: Months vs Price -----
    fig1, ax1 = plt.subplots(figsize=(6,4))
    ax1.scatter(filtered_df["Months"], filtered_df["AdjustedPrice"], alpha=0.6, label="Historical")
    ax1.scatter([month_value], [predicted_price], color="red", s=100, label="Predicted", zorder=5)
    ax1.set_xlabel("Months")
    ax1.set_ylabel("Price")
    ax1.set_title("Price vs Months")
    ax1.legend()
    plots["month_vs_price"] = fig_to_base64(fig1)
    plt.close(fig1)

    # ----- Scatter: Distance vs Price -----
    fig2, ax2 = plt.subplots(figsize=(6,4))
    ax2.scatter(filtered_df["Distance"], filtered_df["AdjustedPrice"], alpha=0.6, label="Historical")
    ax2.scatter([distance_value], [predicted_price], color="red", s=100, label="Predicted", zorder=5)
    ax2.set_xlabel("Distance")
    ax2.set_ylabel("Price")
    ax2.set_title("Price vs Distance")
    ax2.legend()
    plots["distance_vs_price"] = fig_to_base64(fig2)
    plt.close(fig2)

    return plots

# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post("/predict")
def predict(req: PredictRequest):
    if req.model_name not in models:
        return {"error": f"Unknown model {req.model_name}"}
    
    model = models[req.model_name]
    processed = preprocess(req.features, req.model_name)
    prediction = float(model.predict(processed)[0])
    shap_b64 = generate_shap_plot(model, processed, MODEL_FEATURES[req.model_name])

    hist_df = historical_sets.get(req.model_name, pd.DataFrame(columns=["AdjustedPrice"]))
    filtered = filter_df_by_features(hist_df, req.features)

    month_distance_plots = {}
    if req.model_name in ["Capped", "Logbook"]:
        month_distance_plots = plot_distance_month_comparison(
            filtered,
            predicted_price=prediction,
            month_value=req.features.Months,
            distance_value=req.features.Distance
        )

    if filtered.empty:
        return {
            "model": req.model_name,
            "prediction": prediction,
            "plots": {
                "shap_png": shap_b64,
                **month_distance_plots
            },
            "message": "No historical rows match these features"
        }

    summary = build_price_summary(filtered, price_col="AdjustedPrice")
    comparison = compare_price(prediction, summary)
    box_b64, hist_b64 = plot_price_comparison_base64(filtered, prediction, price_col="AdjustedPrice")

    return {
        "model": req.model_name,
        "prediction": prediction,
        "historical_summary": summary,   
        "comparison": comparison,        
        "plots": {
            "boxplot_png": box_b64,
            "histogram_png": hist_b64,
            "shap_png": shap_b64,
            **month_distance_plots
        }
    }
