import pandas as pd
import numpy as np

def filter_df_by_features(df: pd.DataFrame, raw_data):
    """
    Filters dataframe by required fields Make & Model, and any optional fields present.
    Handles type mismatches and NaNs gracefully.
    """
    data_dict = raw_data.model_dump()
    required_keys = ["Make", "Model"]

    for key in required_keys:
        if key not in df.columns or data_dict.get(key) is None:
            raise ValueError(f"{key} is required for filtering but is missing")
    
    # Start with required filters
    mask = (df["Make"] == data_dict["Make"]) & (df["Model"] == data_dict["Model"])
    
    # Optional filters
    for key, value in data_dict.items():
        if key in required_keys or value is None or key not in df.columns:
            continue
        try:
            col_type = df[key].dtype
            if np.issubdtype(col_type, np.floating):
                mask &= np.isclose(df[key], float(value))
            else:
                mask &= df[key] == value
        except Exception as e:
            print(f"Warning: Could not apply filter for {key}={value}: {e}")
    
    filtered_df = df[mask]
    if filtered_df.empty:
        print("No matching rows found. Filters applied:", data_dict)
    
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

def build_price_summary(df, price_col="AdjustedPrice"):
    # Make sure the column exists
    if price_col not in df.columns:
        return {"min": 0.0, "q1": 0.0, "median": 0.0, "q3": 0.0, "max": 0.0}

    # Drop missing values
    price_series = df[price_col].dropna()

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
