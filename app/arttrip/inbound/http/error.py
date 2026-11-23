from typing import Final

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse, Response

from arttrip.application.util.exception import DomainException, ErrorCode

STATUS_BY_ERROR_CODE: Final = {
    ErrorCode.INVALID_ARGUMENT: 400,
    ErrorCode.UNAUTHENTICATED: 401,
    ErrorCode.PERMISSION_DENIED: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.ALREADY_EXISTS: 409,
    ErrorCode.UNAVAILABLE: 503,
}
EXPOSED_VALIDATION_KEYS: Final = ("type", "loc", "msg")


async def handle_domain_exception(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, DomainException):
        raise exc
    http_error = HTTPException(
        status_code=STATUS_BY_ERROR_CODE[exc.error_code], detail=str(exc)
    )
    return await http_exception_handler(request, http_error)


async def handle_request_validation(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, RequestValidationError):
        raise exc
    errors = [
        {key: error[key] for key in EXPOSED_VALIDATION_KEYS if key in error}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})
