import json
import time
import uuid

from fastapi import APIRouter, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.analytics import AnalyticsService
from app.api.routes import (
    chats,
    documents,
    execute,
    files,
    items,
    llm,
    login,
    messages,
    projects,
    settings,
    suggestions,
    teams,
    users,
    utils,
    votes,
)
from app.core.logger import get_logger

# Initialize analytics service and generate instance ID
analytics_service = AnalyticsService()
INSTANCE_ID = str(uuid.uuid4())  # Generate once at startup

# Setup logger using custom logger
logger = get_logger(__name__)

api_router = APIRouter()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Single request identifier
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()

        # Capture query parameters and sanitize sensitive data
        query_params = dict(request.query_params)
        if "password" in query_params:
            query_params["password"] = "[REDACTED]"

        # Get request body and attempt to decode it
        body = await request.body()
        try:
            body_decoded = json.loads(body.decode("utf-8"))
            if isinstance(body_decoded, dict):
                # Redact sensitive fields
                for sensitive_field in ["password", "token", "secret"]:
                    if sensitive_field in body_decoded:
                        body_decoded[sensitive_field] = "[REDACTED]"
        except (ValueError, json.JSONDecodeError):
            body_decoded = body.decode("utf-8") if body else None

        logger.info(
            "Incoming request",
            extra={
                "extra_fields": {
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client": request.client.host if request.client else "unknown",
                    "path": request.url.path,
                    "query_params": query_params,
                    "content_length": request.headers.get("content-length"),
                    "user_agent": request.headers.get("user-agent"),
                    "referer": request.headers.get("referer"),
                    "headers": {
                        k: v
                        for k, v in request.headers.items()
                        if k.lower() not in ["authorization", "cookie", "x-api-key"]
                    },
                    "body": body_decoded,
                }
            },
        )

        try:
            # Process the request
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"

            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Reset the response body
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

            # Decode response body if possible
            try:
                response_decoded = json.loads(response_body.decode("utf-8"))
                # Redact sensitive data in response
                if isinstance(response_decoded, dict):
                    for sensitive_field in ["password", "token", "secret"]:
                        if sensitive_field in response_decoded:
                            response_decoded[sensitive_field] = "[REDACTED]"
            except (ValueError, json.JSONDecodeError):
                response_decoded = (
                    response_body.decode("utf-8") if response_body else None
                )

            duration_ms = int((time.time() - start_time) * 1000)

            # Log response details
            logger.info(
                "Request completed",
                extra={
                    "extra_fields": {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "path": request.url.path,
                        "response_body": response_decoded,
                        "response_size": len(response_body),
                        "response_headers": {
                            k: v
                            for k, v in response.headers.items()
                            if k.lower() not in ["set-cookie"]
                        },
                        "duration_ms": duration_ms,
                        "slow_request": duration_ms
                        > 1000,  # Flag requests over 1 second
                    }
                },
            )

            # Log warning for slow requests
            if duration_ms > 1000:
                logger.warning(
                    f"Slow request detected: {duration_ms}ms",
                    extra={
                        "extra_fields": {
                            "request_id": request_id,
                            "path": request.url.path,
                            "method": request.method,
                            "duration_ms": duration_ms,
                        }
                    },
                )

            # Track analytics with instance ID instead of request ID
            analytics_service.track_api_event(
                request=request,
                response_status=response.status_code,
                duration_ms=duration_ms,
                user_id=INSTANCE_ID,  # Use the instance ID instead of generating new UUID
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "Unhandled exception during request processing",
                extra={
                    "extra_fields": {
                        "request_id": request_id,
                        "method": request.method,
                        "url": str(request.url),
                        "path": request.url.path,
                        "query_params": query_params,
                        "error_type": type(e).__name__,
                        "error": str(e),
                        "stack_trace": repr(e),
                        "duration_ms": duration_ms,
                    }
                },
            )
            raise

        return response


# Include all routers
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(
    suggestions.router, prefix="/suggestions", tags=["suggestions"]
)
api_router.include_router(votes.router, prefix="/votes", tags=["votes"])
api_router.include_router(execute.router, prefix="/execute", tags=["execute"])
