from fastapi import APIRouter, Request
from schemas.requests import PrefilteredRequest
from schemas.responses import PrefilteredResponse, ErrorResponse
from services.prefiltered import run_prefiltered

router = APIRouter(prefix="/prefilter", tags=["Prefiltered"])


@router.post(
    "",
    response_model=PrefilteredResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Prefilter",
)
def Prefilter(req: PrefilteredRequest, request: Request):
    return run_prefiltered(request.app, req)
