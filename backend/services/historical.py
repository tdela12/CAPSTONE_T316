from fastapi import HTTPException, status
from utils.plotting import get_all_price_plots
from utils.historical_summary import filter_df_by_features, build_price_summary, compare_price
import numpy as np
import scipy.stats as stats

def run_historical_summary(app, req):
    """
    Finds historical data matching the features,
    computes statistics, comparison metrics, and generates multiple plots.
    """

    if req.model_name not in app.state.historical_sets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model: {req.model_name}"
        )

    df = app.state.historical_sets.get(req.model_name)
    filtered = filter_df_by_features(df, req.features)

    if df.empty:
        return {
            "summary": None,
            "comparison": None,
            "plots": {
                "boxplot_png": None,
                "histogram_png": None,
                "month_vs_price_png": None,
                "distance_vs_price_png": None
            },
            "message": "No matching historical data available"
        }

    # --- filtering ---
    
    if filtered.empty:
        return {
            "summary": None,
            "comparison": None,
            "plots": {
                "boxplot_png": None,
                "histogram_png": None,
                "month_vs_price_png": None,
                "distance_vs_price_png": None
            },
            "message": "No matching historical records"
        }

   

    # --- summary statistics ---
    summary = build_price_summary(filtered)

    # --- comparison metrics ---
    predicted_price = req.prediction
    comparison = compare_price(predicted_price, summary, filtered["AdjustedPrice"])

    # --- plots ---
    
    try:
        plots = get_all_price_plots(filtered, predicted_price, req.months, req.distance)
    except Exception:
        plots = {
            "boxplot_png": None,
            "histogram_png": None,
            "month_vs_price_png": None,
            "distance_vs_price_png": None
        }

    return {
        "summary": summary,
        "comparison": comparison,
        "plots": plots,
        "message": "Historical summary computed successfully"
    }
