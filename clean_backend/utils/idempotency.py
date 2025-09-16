from __future__ import annotations

import functools
import json
from datetime import datetime, timedelta, timezone
from typing import Callable, Awaitable, Any, Dict

from fastapi import Request, Response
from starlette.responses import JSONResponse

from clean_backend.database import db_session
from clean_backend.models.velafi_idempotency import VelafiIdempotencyKey

DEFAULT_TTL_HOURS = 24


def idempotent_route(key_builder: Callable[[Request], str], ttl_hours: int = DEFAULT_TTL_HOURS):
    """Decorator for FastAPI routes to enforce idempotency and replay cached responses.

    Parameters
    ----------
    key_builder: Callable[[Request], str]
        Function that receives the incoming *Request* and returns a unique idempotency key.
    ttl_hours: int
        Expiration for cached responses; expired rows are ignored and overwritten.
    """

    def decorator(func: Callable[..., Awaitable[Response]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):  # pylint: disable=missing-docstring
            request: Request = kwargs.get("request")  # FastAPI injects request via dependency
            if request is None:
                # attempt positional search (rare)
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if request is None:
                # Should not happen; continue without idempotency.
                return await func(*args, **kwargs)

            key = key_builder(request)

            async with db_session() as session:
                record = await session.get(VelafiIdempotencyKey, {"key": key})  # type: ignore[arg-type]
                if record and (not record.expires_at or record.expires_at > datetime.now(timezone.utc)):
                    return JSONResponse(content=record.response_json, status_code=record.status_code)

            # first call – execute handler
            response: Response = await func(*args, **kwargs)

            # Persist response
            async with db_session() as session:
                rec = VelafiIdempotencyKey(
                    key=key,
                    response_json=json.loads(response.body.decode()) if hasattr(response, "body") else None,
                    status_code=response.status_code,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
                )
                session.add(rec)
                try:
                    await session.commit()
                except Exception:  # pragma: no cover – ignore unique failure race
                    pass

            return response

        return wrapper

    return decorator 