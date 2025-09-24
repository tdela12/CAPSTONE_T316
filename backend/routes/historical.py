from fastapi import APIRouter, Request
from schemas.requests import HistoricalRequest
from schemas.responses import HistoricalResponse, ErrorResponse
from services.historical import run_historical_summary

router = APIRouter(prefix="/historical", tags=["Historical"])


@router.post(
    "/summary",
    response_model=HistoricalResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Get historical data summary",
)
def historical_summary(req: HistoricalRequest, request: Request):
    return run_historical_summary(request.app, req)
