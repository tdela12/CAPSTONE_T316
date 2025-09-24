from fastapi import APIRouter, Request, Query
from schemas.responses import RegistrationResponse, ErrorResponse
from services.registration import lookup_registration

router = APIRouter(prefix="/registration", tags=["Registration"])


@router.get(
    "/lookup",
    response_model=RegistrationResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Lookup registration data",
)
def registration_lookup(
    request: Request,
    registration: str = Query(..., description="Vehicle registration number"),
):
    return lookup_registration(request.app, registration.upper())
