from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from fastapi import FastAPI

# Default: in-memory storage; for prod, override with Redis limiter using settings.REDIS_URL
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


def init_app(app: FastAPI) -> None:  # pragma: no cover
    """Attach rate-limit middleware and exception handler to FastAPI *app*."""
    app.state.limiter = limiter  # accessed by decorators
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):  # noqa: D401
    """Return JSON 429 with Retry-After header."""
    headers = {"Retry-After": str(int(exc.detail))} if exc.detail else {}
    return app_json_response({"detail": "Too Many Requests"}, 429, headers)


from fastapi.responses import JSONResponse  # placed here to avoid circular import

def app_json_response(payload: dict, status: int, headers: dict | None = None):
    return JSONResponse(content=payload, status_code=status, headers=headers or {}) 