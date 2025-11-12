from fastapi.responses import JSONResponse
from fastapi.requests import Request
from openai import RateLimitError, APIError, ServiceUnavailableError
from qdrant_client.http.exceptions import UnexpectedResponse

from .exceptions import AppError

def register_exception_handlers(app):
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "detail": str(exc)},
        )

    @app.exception_handler(RateLimitError)
    async def handle_rate_limit_error(request: Request, exc: RateLimitError):
        return JSONResponse(
            status_code=429,
            content={"error": "RateLimitExceeded", "detail": "OpenAI rate limit reached."},
        )

    @app.exception_handler(APIError)
    @app.exception_handler(ServiceUnavailableError)
    @app.exception_handler(UnexpectedResponse)
    async def handle_external_errors(request: Request, exc: Exception):
        return JSONResponse(
            status_code=502,
            content={"error": "ExternalServiceError", "detail": str(exc)},
        )
