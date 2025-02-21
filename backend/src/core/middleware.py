from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Union, Dict, Any
from .logging_config import get_logger
from datetime import datetime, UTC
import uuid

logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = datetime.now(UTC)

        response = await call_next(request)

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str((datetime.now(UTC) - start_time).total_seconds())

        return response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            logger.warning(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail}
            )
        except Exception as exc:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )

class APIKeyValidationError(HTTPException):
    def __init__(self, detail: str = "Invalid API Key"):
        super().__init__(status_code=403, detail=detail)

class ValidationError(HTTPException):
    def __init__(self, detail: Union[str, Dict[str, Any]]):
        super().__init__(status_code=422, detail=detail)

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)