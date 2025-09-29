from fastapi import HTTPException, status
from utils.historical_summary import filter_df_by_features

def run_prefiltered(app, req):
  df = app.state.historical_sets.get(req.model_name)

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
  
  filtered = filter_df_by_features(df, req.features)
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
  
  unique_vals = {}
  for column in filtered.columns:
      unique_vals[column] = filtered[column].unique().tolist()
      print(column)
  
  return {col: unique_vals.get(col, []) for col in ["Make", "Model", "EngineSize", "Distance", "Months"]}
