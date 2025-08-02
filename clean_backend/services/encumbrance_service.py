from __future__ import annotations

"""Encumbrance tracking + recovery logic.

This module provides a small service class that keeps the *business rules* around
encumbrances in one place so routers / jobs can call simple methods.

It assumes:
• SQLAlchemy session management is handled by FastAPI deps (get_db).
• BridgeClient already exists and exposes synchronous create_transfer (simple wrapper around POST /transfers).
"""

import logging
from decimal import Decimal
from typing import List, Tuple
import os

from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete, update

from ..bridge import BridgeClient
from ..models import Encumbrance, Transfer

logger = logging.getLogger(__name__)

# These vars should ideally live in settings.py / env.
CORPORATE_WALLET_ID = os.getenv("TREASURY_WALLET_ID", "")
CORPORATE_CUSTOMER_ID = os.getenv("TREASURY_CUSTOMER_ID", "")

if not CORPORATE_WALLET_ID or not CORPORATE_CUSTOMER_ID:
    logging.getLogger(__name__).warning("TREASURY_WALLET_ID / TREASURY_CUSTOMER_ID not set; encumbrance operations may fail")


class EncumbranceService:
    """Main entry-point used by routers & webhooks to maintain encumbrance state."""

    def __init__(self, db: Session):
        self.db = db
        self.bridge = BridgeClient()

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------
    def create_encumbrance(
        self,
        transfer_id: str,
        amount: Decimal,
    ) -> Encumbrance:
        """Persist an encumbrance for a transfer."""
        enc = Encumbrance(
            transfer_id=transfer_id,
            original_amount=amount,
            remaining_amount=amount,
        )
        self.db.add(enc)
        self.db.commit()
        return enc

    # ------------------------------------------------------------------
    # On settlement success / failure (called by webhooks)
    # ------------------------------------------------------------------
    def clear_encumbrance(self, transfer_id: str) -> None:
        """Mark encumbrance as cleared when fiat transfer succeeds."""
        enc = self.db.query(Encumbrance).filter_by(transfer_id=transfer_id).first()
        if enc:
            enc.status = "cleared"
            enc.cleared_at = func.now()
            self.db.commit()

    def recover_encumbrance(self, transfer_id: str) -> None:
        """Mark encumbrance as failed when fiat transfer fails."""
        enc = self.db.query(Encumbrance).filter_by(transfer_id=transfer_id).first()
        if enc:
            enc.status = "failed"
            self.db.commit()

    def get_pending_encumbrances(self, user_id: str) -> List[Encumbrance]:
        """Get all pending encumbrances for a user."""
        return (
            self.db.query(Encumbrance)
            .join(Transfer, Encumbrance.transfer_id == Transfer.id)
            .filter(Transfer.user_id == user_id, Encumbrance.status == "pending")
            .all()
        )

    def get_total_encumbered_amount(self, user_id: str) -> Decimal:
        """Get total amount of encumbered funds for a user."""
        result = (
            self.db.query(func.sum(Encumbrance.remaining_amount))
            .join(Transfer, Encumbrance.transfer_id == Transfer.id)
            .filter(Transfer.user_id == user_id, Encumbrance.status == "pending")
            .scalar()
        )
        return result or Decimal('0') 