from fastapi import HTTPException, status
from models.preprocess import preprocess
from utils.plotting import generate_shap_plot
from config import MODEL_FEATURES
import logging

logger = logging.getLogger("prediction_service")

def run_prediction(app, req, trace_id):
    """
    Runs a prediction for a given model and features.
    Uses models loaded in app.state.
    """

    if req.model_name not in app.state.models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model: {req.model_name}"
        )

    model = app.state.models[req.model_name]
    processed = preprocess(req.features, req.model_name)
    logger.info("Preprocessing input data")

    try:
        prediction = float(model.predict(processed)[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model prediction failed: {str(e)}"
        )

    # Generate SHAP plot
    
    shap_b64 = generate_shap_plot(
            model,
            processed,
            MODEL_FEATURES[req.model_name]
        )
    

    logger.info(
        f"Model predicted price={prediction:.2f}",
        extra={"trace_id": trace_id},
    )


    return {
        "model": req.model_name,
        "features": req.features.model_dump(),
        "prediction": prediction,
        "plots": {"shap_png": shap_b64},
    }
