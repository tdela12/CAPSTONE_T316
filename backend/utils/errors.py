from fastapi import HTTPException
from schemas.responses import ErrorResponse


class AppException(HTTPException):
    """Base exception with a consistent JSON response"""

    def __init__(self, status_code: int, detail: str, code: str = "ERROR"):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, code="NOT_FOUND")


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail, code="BAD_REQUEST")


class InternalErrorException(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail, code="INTERNAL_ERROR")


def error_response(exc: AppException) -> dict:
    """Format error response consistently"""
    return ErrorResponse(
        code=exc.code,        # string like "INTERNAL_ERROR"
        message=exc.detail,   # must use 'message', not 'detail'
        details=getattr(exc, "details", None)
    ).model_dump()           # Pydantic v2 requires model_dump()
