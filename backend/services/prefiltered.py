from fastapi import HTTPException, status
from utils.historical_summary import filter_df_by_features
import numpy as np

def run_prefiltered(app, req):
  df = app.state.historical_sets.get(req.model_name)

  if df.empty:
        return {
            "Make": [],
            "Model": [],
            "Year": [],
            "EngineSize": [],
            "Distance":[],
            "Months": []
        }
  
  filtered = filter_df_by_features(df, req.features)
  if filtered.empty:
        return {
            "Make": [],
            "Model": [],
            "Year": [],
            "EngineSize": [],
            "Distance":[],
            "Months": []
        }
  
  unique_vals = {}
  for column in filtered.columns:
      vals = filtered[column].dropna().unique().tolist()
      unique_vals[column] = [v.item() if isinstance(v, (np.generic,)) else v for v in vals]
    
  return {col: unique_vals.get(col, []) for col in ["Make", "Model", "Year", "EngineSize", "Distance", "Months"]}
