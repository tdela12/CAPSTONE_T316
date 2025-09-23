# config.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
MODEL_PATHS = {
    "Capped": BASE_DIR / "models_files" / "capped_model.cbm",
    "Logbook": BASE_DIR / "models_files" / "logbook_model.cbm",
    "Prescribed": BASE_DIR / "models_files" / "prescribed_model.cbm",
    "Repair": BASE_DIR / "models_files" / "repair_model.cbm",
}

DATA_PATHS = {
    "Capped": BASE_DIR / "data" / "preprocessed_capped_data.csv",
    "Logbook": BASE_DIR / "data" / "preprocessed_log_data.csv",
    "Prescribed": BASE_DIR / "data" / "preprocessed_prescribed_data.csv",
    "Repair": BASE_DIR / "data" / "preprocessed_repair_data.csv",
    "Rego": BASE_DIR / "data" / "rego_data.csv",
}

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
# Use '*' only for local dev; override via env in production:
ALLOW_ALL_CORS_DEV = os.getenv("ALLOW_ALL_CORS_DEV", "true").lower() == "true"
