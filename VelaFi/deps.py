"""FastAPI dependency helpers for VelaFi package."""

from functools import lru_cache

from VelaFi.velafi_client import VelafiClient
from clean_backend.config.settings import settings


@lru_cache(maxsize=1)
def _get_client() -> VelafiClient:
    """Return a singleton VelafiClient instance (cached)."""
    return VelafiClient(
        api_key=settings.velafi_api_key.get_secret_value(),
        base_url=settings.velafi_base_url,
        timeout=settings.api_timeout,
    )


async def velafi_client_dep() -> VelafiClient:  # noqa: D401
    """FastAPI dependency that provides a VelafiClient instance."""
    return _get_client() 