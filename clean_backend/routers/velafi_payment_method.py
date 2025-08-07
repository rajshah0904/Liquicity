"""VelaFi payment-method CRUD passthrough routes (Phase-2)."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from clean_backend.config.settings import settings
from clean_backend.database import get_db
from VelaFi.velafi_client import VelafiClient, VelafiError

router = APIRouter(prefix="/velafi/payment_method", tags=["velafi"])


def _client() -> VelafiClient:
    return VelafiClient(
        api_key=settings.velafi_api_key.get_secret_value(),
        base_url=settings.velafi_base_url,
        timeout=settings.api_timeout,
    )


# dependency helper
def _svc(db: Session = Depends(get_db)):
    from VelaFi.services.payment_method_service import PaymentMethodService
    return PaymentMethodService(db)


@router.get("/templates")
async def list_templates(cli: VelafiClient = Depends(_client)):
    try:
        return await cli.list_payment_templates()
    except VelafiError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.get("/{pm_id}")
async def get_pm(pm_id: str = Path(..., description="payment_method_id in VelaFi"), cli: VelafiClient = Depends(_client)):
    try:
        return await cli.get_payment_method(pm_id)
    except VelafiError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.delete("/{pm_id}", status_code=204)
async def delete_pm(pm_id: str, svc=Depends(_svc)):
    try:
        await svc.delete_payment_method(pm_id)
    except VelafiError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.patch("/{pm_id}/refund_account")
async def set_refund_account(pm_id: str, body: Dict[str, Any], cli: VelafiClient = Depends(_client)):
    try:
        return await cli.set_refund_account(pm_id, body["refund_account_id"])
    except VelafiError as e:
        raise HTTPException(status_code=e.status, detail=e.message) 