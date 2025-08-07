"""Background task that polls VelaFi for order status updates.

Integrators can schedule `poll_pending_orders` with their preferred scheduler
(e.g. Celery beat, APScheduler, FastAPI lifespan tasks). It relies on the
`onramp_orders` table to locate orders still in *pending* or *processing*.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from clean_backend.database import SessionLocal  # adjust import to your DB helper
from VelaFi.velafi_client import VelafiError
from VelaFi.deps import _get_client
from VelaFi.models import OnRampOrder, OrderStatus

_log = logging.getLogger(__name__)


_POLL_INTERVAL_SEC = 60  # can be overridden by env/config


async def poll_pending_orders() -> None:
    """Poll VelaFi for pending orders & sync status to DB."""

    velafi = _get_client()

    while True:
        try:
            with SessionLocal() as db:
                await _process_cycle(db, velafi)
        except Exception as exc:  # pragma: no cover – guardrail
            _log.error("Order monitor cycle failed: %s", exc, exc_info=True)
        await asyncio.sleep(_POLL_INTERVAL_SEC)


async def _process_cycle(db: Session, velafi: VelafiClient) -> None:
    """One pass through orders still awaiting settlement."""

    pending = db.query(OnRampOrder).filter(OnRampOrder.status.in_([OrderStatus.pending, OrderStatus.processing])).all()
    for rec in pending:
        try:
            order = await velafi.get_order(rec.velafi_order_id)
        except VelafiError as e:
            _log.warning("Failed to fetch order %s: %s", rec.velafi_order_id, e)
            continue

        if order.status in {"completed", "failed"}:
            _log.info("Order %s transitioned to %s", rec.velafi_order_id, order.status)
            rec.status = OrderStatus(order.status)
            rec.usdc_amount = order.usdc_amount or rec.usdc_amount
            rec.updated_at = datetime.utcnow()
            db.commit()
            # Optionally, trigger other actions (event bus, etc.) 