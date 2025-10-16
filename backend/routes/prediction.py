from fastapi import APIRouter, Request
from schemas.requests import PredictRequest
from schemas.responses import PredictResponse, ErrorResponse
from services.prediction import run_prediction
import logging


router = APIRouter(prefix="/predict", tags=["Prediction"])
logger = logging.getLogger("prediction_routes")


@router.post(
    "",
    response_model=PredictResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Predict a service price",
)
def predict(req: PredictRequest, request: Request):
    trace_id = request.state.trace_id
    logger.info("Received prediction request")
    
    try:
        result = run_prediction(request.app, req, trace_id)
        logger.info("Prediction completed successfully")
        return {"trace_id": trace_id, **result}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise
    return run_prediction(request.app, req)

