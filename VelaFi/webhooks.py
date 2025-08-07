"""Webhook listener for VelaFi events.

This router is **not yet wired into the main FastAPI app**. Integrators should
import `router` into their API and include it:

```python
from VelaFi.webhooks import router as velafi_webhook_router
app.include_router(velafi_webhook_router)
```

The implementation focuses on verifying VelaFi HMAC signatures and forwarding
completed orders to business logic (e.g., crediting USDC via Bridge).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Dict, Any

# Standard lib
import os
from decimal import Decimal

# Project imports
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from clean_backend.database import get_db
# Bridge-credit feature flag (set VELAFI_CREDIT_ENABLED=false to disable)
_CREDIT_ENABLED = os.getenv("VELAFI_CREDIT_ENABLED", "false").lower() == "true"  # default off now

from VelaFi.event_bus import publish
from VelaFi.models import OnRampOrder, OrderStatus

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/velafi", tags=["webhooks"])

# Secret should come from env or settings
_WEBHOOK_SECRET_PLACEHOLDER = os.getenv("VELAFI_WEBHOOK_SECRET", "changeme")

_ALLOWED_DRIFT_SEC = 300  # ±5 minutes


def _verify_signature(raw_body: bytes, signature_header: str) -> bool:
    """Return True if signature matches secret & timestamp within drift."""
    try:
        parts = {k: v for k, v in (kv.split("=", 1) for kv in signature_header.split(","))}
        ts = int(parts.get("t", 0))
        sig = parts.get("v1")
    except ValueError:
        return False
    if not sig:
        return False
    if abs(time.time() - ts) > _ALLOWED_DRIFT_SEC:
        return False
    message = f"{ts}.{raw_body.decode()}".encode()
    expected = hmac.new(_WEBHOOK_SECRET_PLACEHOLDER.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def velafi_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_velafi_signature: str | None = Header(None),
):
    """Accept webhook events from VelaFi.

    Expected payload:
    ```json
    {
      "type": "order.completed",
      "data": { "id": "ord_123", ... }
    }
    ```
    """

    raw = await request.body()
    if not x_velafi_signature or not _verify_signature(raw, x_velafi_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload: Dict[str, Any] = json.loads(raw)
    evt_type = payload.get("type")
    data = payload.get("data", {})
    if not evt_type or "id" not in data:
        raise HTTPException(status_code=400, detail="Missing fields")

    # Persist webhook receipt (basic logging for now)
    _log.debug("VelaFi webhook received: %s", payload)

    # Lookup order
    order_rec = db.query(OnRampOrder).filter_by(velafi_order_id=data["id"]).first()
    if not order_rec:
        _log.warning("Unknown velafi_order_id %s", data["id"])
        return {"received": True}

    if evt_type == "order.completed":
        order_rec.status = OrderStatus.completed
        order_rec.usdc_amount = Decimal(str(data.get("usdc_amount"))) if data.get("usdc_amount") else order_rec.usdc_amount
        order_rec.updated_at = datetime.utcnow()
        db.commit()

        # Emit event so a separate Bridge-credit consumer can act.
        publish("order.completed", {"order_id": order_rec.velafi_order_id, "user_id": order_rec.user_id, "usdc_amount": order_rec.usdc_amount})
    elif evt_type == "order.failed":
        order_rec.status = OrderStatus.failed
        order_rec.updated_at = datetime.utcnow()
        db.commit()
    else:
        _log.debug("Ignoring event %s", evt_type)

    return {"received": True} 