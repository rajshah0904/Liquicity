"""VelaFi reference-data & quote routes (Phase-1)."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query

from clean_backend.config.settings import settings
from VelaFi.velafi_client import VelafiClient, VelafiError

from ..services.cache import cache

router = APIRouter(prefix="/velafi", tags=["velafi"])


def _client() -> VelafiClient:
    return VelafiClient(
        api_key=settings.velafi_api_key.get_secret_value(),
        base_url=settings.velafi_base_url,
        timeout=settings.api_timeout,
    )

#Data pulls

@router.get("/countries")
async def list_countries(cli: VelafiClient = Depends(_client)):
    cache_key = "velafi:countries"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    data = await cli.list_countries()
    await cache.set(cache_key, data)
    return data


@router.get("/fiat_currencies")
async def list_fiat(cli: VelafiClient = Depends(_client)):
    key = "velafi:fiat_curr"
    if (val := await cache.get(key)):
        return val
    data = await cli.list_fiat_currencies()
    await cache.set(key, data)
    return data


@router.get("/crypto_currencies")
async def list_crypto(cli: VelafiClient = Depends(_client)):
    key = "velafi:crypto_curr"
    if (val := await cache.get(key)):
        return val
    data = await cli.list_crypto_currencies()
    await cache.set(key, data)
    return data


@router.get("/pairs")
async def list_pairs(
    pair_type: str = Query("fiat_crypto", pattern="^(fiat_crypto|crypto_fiat|fiat_fiat)$"),
    cli: VelafiClient = Depends(_client),
):
    key = f"velafi:pairs:{pair_type}"
    if (val := await cache.get(key)):
        return val
    data = await cli.list_pairs(pair_type)
    await cache.set(key, data)
    return data

#quotes

@router.post("/quote/crypto_to_fiat")
async def quote_crypto_to_fiat(body: Dict[str, Any], cli: VelafiClient = Depends(_client)):
    try:
        quote = await cli.get_quote_crypto_to_fiat(
            user_id=body["user_id"],
            crypto_symbol=body["crypto_symbol"],
            fiat_symbol=body["fiat_symbol"],
            crypto_amount=str(body["crypto_amount"]),
        )
        return quote
    except VelafiError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.post("/quote/fiat_to_fiat")
async def quote_fiat_to_fiat(body: Dict[str, Any], cli: VelafiClient = Depends(_client)):
    try:
        quote = await cli.get_quote_fiat_to_fiat(
            user_id=body["user_id"],
            from_currency=body["from_currency"],
            to_currency=body["to_currency"],
            fiat_amount=str(body["fiat_amount"]),
        )
        return quote
    except VelafiError as e:
        raise HTTPException(status_code=e.status, detail=e.message) 