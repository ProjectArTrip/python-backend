from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import Lifespan

from arttrip.application.util.exception import DomainException
from arttrip.inbound.http.error import (
    handle_domain_exception,
    handle_request_validation,
)
from arttrip.inbound.http.routes import root_router


def create_app(
    lifespan: Lifespan[FastAPI] | None = None,
    *,
    docs_enabled: bool = False,
    allowed_origins: list[str] | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Artrip Swagger API",
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins or [],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.add_exception_handler(DomainException, handle_domain_exception)
    app.include_router(root_router)
    app.add_exception_handler(DomainException, handle_domain_exception)
    app.add_exception_handler(RequestValidationError, handle_request_validation)
    return app
