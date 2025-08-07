"""Service layer for VelaFi payment-method operations.

This service keeps local DB in sync with VelaFi and emits internal events.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from clean_backend.config.settings import settings
from clean_backend.services.event_bus import publish  # reuse global event bus
from VelaFi.models import VelafiPaymentMethod
from VelaFi.velafi_client import VelafiClient, VelafiError

_logger = logging.getLogger(__name__)


class PaymentMethodService:
    def __init__(self, db: Session):
        self.db = db
        self.client = VelafiClient(
            api_key=settings.velafi_api_key.get_secret_value(),
            base_url=settings.velafi_base_url,
            timeout=settings.api_timeout,
        )

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    async def add_payment_method(self, plaid_token: str, *, user_id: str) -> Dict[str, Any]:
        """Create payment method via VelaFi and persist a local record."""
        remote = await self.client.add_payment_method(plaid_token, user_id=user_id)
        rec = self._upsert(remote, user_id)
        publish("payment_method.created", {"pm_id": rec.payment_method_id, "user_id": user_id})
        return remote.raw  # type: ignore[attr-defined]

    async def delete_payment_method(self, payment_method_id: str) -> None:
        try:
            await self.client.delete_payment_method(payment_method_id)
        except VelafiError as e:
            if e.status != 404:
                raise
        # Remove local row if exists
        self.db.query(VelafiPaymentMethod).filter_by(payment_method_id=payment_method_id).delete()
        self.db.commit()
        publish("payment_method.deleted", {"pm_id": payment_method_id})

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _upsert(self, remote_pm, user_id: str) -> VelafiPaymentMethod:  # noqa: ANN001 – remote_pm is Pydantic model
        stmt = select(VelafiPaymentMethod).where(VelafiPaymentMethod.payment_method_id == remote_pm.id)
        rec = self.db.execute(stmt).scalar_one_or_none()
        if rec:
            rec.raw_payload = remote_pm.raw  # type: ignore[attr-defined]
        else:
            rec = VelafiPaymentMethod(
                user_id=user_id,
                payment_method_id=remote_pm.id,
                fiat_rail=remote_pm.fiat_rail,
                country=remote_pm.country,
                currency=remote_pm.currency,
                raw_payload=remote_pm.raw,  # type: ignore[attr-defined]
            )
            self.db.add(rec)
        self.db.commit()
        return rec 