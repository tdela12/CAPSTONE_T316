from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.errors import AppException, error_response, InternalErrorException
from schemas.responses import ErrorResponse

def register_exception_handlers(app):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if isinstance(exc, AppException):
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response(exc),  # already returns dict
            )
        # Standard HTTPException
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code="HTTP_ERROR",
                message=str(exc.detail),
                details=None
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code="VALIDATION_ERROR",
                message="Validation error",
                details=exc.errors()  # include validation details
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=error_response(InternalErrorException()),
        )
