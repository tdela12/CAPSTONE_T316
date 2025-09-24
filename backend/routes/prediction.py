from fastapi import APIRouter, Request
from schemas.requests import PredictRequest
from schemas.responses import PredictResponse, ErrorResponse
from services.prediction import run_prediction

router = APIRouter(prefix="/predict", tags=["Prediction"])


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
    return run_prediction(request.app, req)
