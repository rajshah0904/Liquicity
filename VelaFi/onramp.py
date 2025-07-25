from __future__ import annotations

"""On-Ramp (VelaFi) endpoints.

These routes are consumed by the frontend Plaid flow and internal services to
kick-off fiat→crypto on-ramp orders.
"""

import logging
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field, PositiveInt, constr
from sqlalchemy.orm import Session

import hashlib

from VelaFi.models import OnRampPaymentMethod, OnRampOrder, OrderStatus

# NOTE: These imports reference the existing backend modules. Adjust paths if your
# project structure differs.
from clean_backend.auth import get_current_user  # Auth0 dependency
from clean_backend.database import get_db
from clean_backend.services.security import EnhancedSecurityService, SecurityContext

# VelaFi client wrapper
from VelaFi.velafi_client import VelafiError
from VelaFi.deps import velafi_client_dep

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/onramp", tags=["onramp"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class PaymentMethodReq(BaseModel):
    plaid_token: constr(strip_whitespace=True, min_length=10)


class PaymentMethodRes(BaseModel):
    id: str
    fiat_rail: str
    country: str
    currency: str


class OrderReq(BaseModel):
    payment_method_id: str = Field(..., examples=["pm_abc123"])
    fiat_amount: Decimal = Field(..., gt=Decimal("0"))


class OrderRes(BaseModel):
    id: str
    status: str
    fiat_amount: str
    fiat_currency: str
    usdc_amount: str | None = None
    quote_rate: str | None = None
    fee_usd: str | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/payment_method", response_model=PaymentMethodRes, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    body: PaymentMethodReq,
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    velafi_client=Depends(velafi_client_dep),
):
    """Add a new payment method in VelaFi based on Plaid public token."""

    user_id = jwt.get("sub")
    try:
        pm = await velafi_client.add_payment_method(body.plaid_token, user_id=user_id)
    except VelafiError as e:
        _log.error("VelaFi add_payment_method failed: %s", e)
        raise HTTPException(status_code=502, detail="VelaFi unreachable")

    # Persist record (upsert by payment_method_id)
    plaid_hash = hashlib.sha256(body.plaid_token.encode()).hexdigest()
    existing = db.query(OnRampPaymentMethod).filter_by(payment_method_id=pm.id).first()
    if existing:
        existing.raw_payload = pm.raw  # update in case of changes
        db.commit()
    else:
        rec = OnRampPaymentMethod(
            user_id=user_id,
            payment_method_id=pm.id,
            plaid_token_hash=plaid_hash,
            fiat_rail=pm.fiat_rail,
            country=pm.country,
            currency=pm.currency,
            raw_payload=pm.raw,
        )
        db.add(rec)
        db.commit()

    return PaymentMethodRes.model_validate(pm.model_dump())


@router.post("/order", response_model=OrderRes, status_code=status.HTTP_201_CREATED)
async def create_onramp_order(
    body: OrderReq,
    request: Request,
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    velafi_client=Depends(velafi_client_dep),
):
    """Create an on-ramp order after security & AML checks."""

    user_id = jwt.get("sub")

    # -------------------- Compliance / velocity checks -------------------
    # Determine caller IP – prefer X-Forwarded-For when behind a proxy
    forwarded = request.headers.get("x-forwarded-for")
    ip_addr = forwarded.split(",")[0].strip() if forwarded else request.client.host

    ctx = SecurityContext(
        user_id=user_id,
        ip_address=ip_addr,
        user_agent=request.headers.get("user-agent", "api/onramp"),
        last_activity=None,  # Not tracked yet; placeholder
    )
    sec_service = EnhancedSecurityService(db)
    if not await sec_service.is_deposit_allowed(ctx, body.fiat_amount):
        raise HTTPException(status_code=403, detail="Deposit flagged for review")

    # -------------------- Create VelaFi order ----------------------------
    try:
        order = await velafi_client.create_order(
            user_id=user_id,
            payment_method_id=body.payment_method_id,
            fiat_amount=str(body.fiat_amount),
        )
    except VelafiError as e:
        _log.error("VelaFi create_order failed: %s", e)
        raise HTTPException(status_code=502, detail="VelaFi unreachable")

    # Persist order
    rec = OnRampOrder(
        user_id=user_id,
        payment_method_id=db.query(OnRampPaymentMethod.id).filter_by(payment_method_id=body.payment_method_id).scalar(),
        velafi_order_id=order.id,
        fiat_amount=body.fiat_amount,
        fiat_currency=order.fiat_currency,
        fiat_rail="ach",  # currently only ACH; could derive from payment method
        status=OrderStatus(order.status),
        usdc_amount=order.usdc_amount or None,
        quote_rate=order.quote_rate or None,
        fee_usd=order.fee_usd or None,
        raw_payload=order.raw,
    )
    db.add(rec)
    db.commit()

    from VelaFi.event_bus import publish
    publish("order.status_changed", {"order_id": rec.velafi_order_id, "status": order.status})

    return OrderRes.model_validate(order.model_dump()) 