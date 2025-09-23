# -----------------------------
# Imports
# -----------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi import HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
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
app = FastAPI(
    title="AutoGuru — Service Price Prediction API",
    description=(
        "Predict prices for capped, logbook, prescribed and repair services. "
        "Interactive docs (Swagger) are customized and available at /docs."
    ),
    version="1.0.0",
    docs_url=None,    # disable builtin swagger docs, refer to custom /docs below
    redoc_url=None
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "details": {
                "path": str(request.url),
                "method": request.method
            }
        }
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Input validation error",
            "details": exc.errors()
        }
    )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AutoGuru — Service Price Prediction API",
        version="1.0.0",
        description="Predict prices for capped, logbook, prescribed and repair services. Interactive docs (Swagger) are available at /docs.",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# -----------------------------
# Serve static assets (CSS/logo) from ./static
# -----------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

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



def build_price_summary(df, price_col="AdjustedPrice"):
    # Make sure the column exists
    if price_col not in df.columns:
        return {"min": 0.0, "q1": 0.0, "median": 0.0, "q3": 0.0, "max": 0.0}

    # Drop missing values
    price_series = df[price_col].dropna()

    # If no valid data, return default zeros
    if price_series.empty:
        return {"min": 0.0, "iqr_low": 0.0, "median": 0.0, "iqr_high": 0.0, "max": 0.0}

    # Compute summary
    return {
        "min": float(price_series.min()),
        "iqr_low": float(price_series.quantile(0.25)),
        "median": float(price_series.median()),
        "iqr_high": float(price_series.quantile(0.75)),
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





# Standardized error responses for reuse
ERROR_RESPONSES = {
    400: {
        "description": "Invalid request or unknown model",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "code": 400,
                    "message": "Unknown model: FooBar",
                    "details": {"model_name": "FooBar"}
                }
            }
        }
    },
    422: {
        "description": "Validation error in input data",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "code": 422,
                    "message": "Input validation error",
                    "details": [
                        {
                            "loc": ["body", "features", "Months"],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                }
            }
        }
    },
    500: {
        "description": "Internal server error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "code": 500,
                    "message": "An unexpected error occurred",
                    "details": {"trace_id": "123e4567-e89b-12d3-a456-426614174000"}
                }
            }
        }
    }
}

# -----------------------------
# Preprocessing 
# -----------------------------

# -----------------------------
# Logging functions
# -----------------------------

import pandas as pd
import numpy as np

def filter_df_by_features(df: pd.DataFrame, raw_data):
    """
    Filters the dataframe based on Make and Model (required) and any other non-null attributes (optional).
    Only columns that exist in df are considered.
    """
    data_dict = raw_data.model_dump()  # or raw_data.model_dump() if using Pydantic
    
    # Make sure Make and Model exist in raw_data and df
    required_keys = ["Make", "Model"]
    for key in required_keys:
        if key not in df.columns or data_dict.get(key) is None:
            raise ValueError(f"{key} is required for filtering but is missing")
    
    # Start with required filters
    conditions = [df["Make"] == data_dict["Make"], df["Model"] == data_dict["Model"]]
    
    # Add optional filters for all other fields
    for key, value in data_dict.items():
        if key not in required_keys and value is not None and key in df.columns:
            conditions.append(df[key] == value)
    
    # Apply all conditions
    filtered_df = df[np.logical_and.reduce(conditions)]
    
    return filtered_df


def compare_price(predicted_price, summary, historical_prices):
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

    sorted_prices = np.sort(historical_prices)
    percentile = np.searchsorted(sorted_prices, predicted_price) / len(sorted_prices)

    # Confidence based on percentile
    if 0.25 <= percentile <= 0.75:
        confidence = "high"
    elif 0.05 <= percentile <= 0.95:
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
        "confidence": confidence,
        "percentile": percentile
    }


def generate_shap_plot(model, processed, feature_names):
    # Dynamically identify categorical features
    categorical_set = {"TaskName", "DriveType", "Make", "Model", "FuelType", "Transmission"}
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
    if "Months" in filtered_df.columns and "AdjustedPrice" in filtered_df.columns:
        fig1, ax1 = plt.subplots(figsize=(6,4))
        ax1.scatter(filtered_df["Months"], filtered_df["AdjustedPrice"], alpha=0.6, label="Historical")
        if month_value is not None:
            ax1.scatter([month_value], [predicted_price], color="red", s=100, label="Predicted", zorder=5)
        ax1.set_xlabel("Months")
        ax1.set_ylabel("Price")
        ax1.set_title("Price vs Months")
        ax1.legend()
        plots["month_vs_price_png"] = fig_to_base64(fig1)
        plt.close(fig1)
    
    # ----- Scatter: Distance vs Price -----
    if "Distance" in filtered_df.columns and "AdjustedPrice" in filtered_df.columns:
        fig2, ax2 = plt.subplots(figsize=(6,4))
        ax2.scatter(filtered_df["Distance"], filtered_df["AdjustedPrice"], alpha=0.6, label="Historical")
        if distance_value is not None:
            ax2.scatter([distance_value], [predicted_price], color="red", s=100, label="Predicted", zorder=5)
        ax2.set_xlabel("Distance")
        ax2.set_ylabel("Price")
        ax2.set_title("Price vs Distance")
        ax2.legend()
        plots["distance_vs_price_png"] = fig_to_base64(fig2)
        plt.close(fig2)

    return plots

# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Predict a service price",
    tags=["Prediction"],
    responses={200: {"description": "Prediction successful", "model": PredictResponse}, **ERROR_RESPONSES}
)
def predict(req: PredictRequest):
    if req.model_name not in models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                code=400,
                message=f"Unknown model: {req.model_name}",
                details={"model_name": req.model_name}
            ).model_dump()
        )

    try:
        model = models[req.model_name]
        processed = preprocess(req.features, req.model_name)
        prediction = float(model.predict(processed)[0])
        shap_b64 = generate_shap_plot(model, processed, MODEL_FEATURES[req.model_name])

        return {
            "model": req.model_name,
            "features": req.features.model_dump(),
            "prediction": prediction,
            "plots": {"shap_png": shap_b64},
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                code=400,
                message=f"Bad input: {str(e)}",
                details={"model_name": req.model_name, "features": req.features.model_dump()}
            ).model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                code=500,
                message=f"Unexpected server error: {str(e)}",
                details={"error_type": type(e).__name__}
            ).model_dump()
        )

# -----------------------------
# Historical summary endpoint   
# -----------------------------
@app.post(
    "/historical_summary",
    response_model=HistoricalResponse,
    tags=["Historical"],
    responses={400: ERROR_RESPONSES[400], 500: ERROR_RESPONSES[500]},
    summary="Get historical data"
)
def get_historical_data(req: HistoricalRequest):
    try:
        hist_df = historical_sets.get(req.model_name)
        if hist_df is None:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    code=404,
                    message=f"No dataset found for model '{req.model_name}'",
                    details={"model_name": req.model_name}
                ).model_dump()
            )

        filtered = filter_df_by_features(hist_df, req.features)

        # Generate scatter plots even if no rows found
        month_distance_plots = {}
        if req.model_name in ["Capped", "Logbook"]:
            month_distance_plots = plot_distance_month_comparison(
                filtered,
                predicted_price=req.prediction,
                month_value=req.months,
                distance_value=req.distance
            )

        if filtered.empty:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    code=404,
                    message="No historical rows match these features",
                    details={"model": req.model_name, "features": req.features.model_dump()}
                ).model_dump()
            )

        # Build summary + plots
        summary = build_price_summary(filtered, price_col="AdjustedPrice")
        comparison = compare_price(req.prediction, summary, filtered["AdjustedPrice"].values)
        box_b64, hist_b64 = plot_price_comparison_base64(filtered, req.prediction, price_col="AdjustedPrice")

        return {
            "summary": summary,
            "comparison": comparison,
            "plots": {
                "boxplot_png": box_b64,
                "histogram_png": hist_b64,
                **month_distance_plots,
            },
        }

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                code=400,
                message=f"Invalid feature key: {str(e)}",
                details={"invalid_key": str(e)}
            ).model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                code=500,
                message=f"Unexpected server error: {str(e)}",
                details={"error_type": type(e).__name__}
            ).model_dump()
        )
    
# -----------------------------
# Registration Lookup endpoint   
# -----------------------------
@app.get(
        "/registration_lookup",
        response_model = RegistrationResponse,
        responses={400: ERROR_RESPONSES[400], 500: ERROR_RESPONSES[500]},
        summary="Get registration data"
)
def get_rego_data(Registration: str = Query(..., description="Vehicle registration number")):
    reg = Registration.upper()
    record = rego_data[rego_data["Registration  "] == reg]
    
    if record.empty:
        raise HTTPException(status_code=400, detail="Registration not found")
    
    return RegistrationResponse(**record.iloc[0].to_dict())

# -----------------------------
# Custom docs endpoints
# -----------------------------
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Serve a customized Swagger UI:
    - uses our custom CSS at /static/custom-swagger.css
    - uses the swagger UI bundle via CDN
    - favicon/logo delivered from /static/logo.png
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="AutoGuru API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="/static/custom-swagger.css",
        swagger_favicon_url="/static/logo.png"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="AutoGuru API (ReDoc)",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(app.openapi())