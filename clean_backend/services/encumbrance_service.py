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
from ..models import Encumbrance, EncPosition

logger = logging.getLogger(__name__)

# These vars should ideally live in settings.py / env.
CORP_WALLET_ID = os.getenv("TREASURY_WALLET_ID", "")
CORPORATE_CUSTOMER_ID = os.getenv("TREASURY_CUSTOMER_ID", "")

if not CORP_WALLET_ID or not CORPORATE_CUSTOMER_ID:
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
        fiat_transfer_id: str,
        user_wallet_id: str,
        amount: Decimal,
    ) -> Encumbrance:
        """Persist an encumbrance + initial position after advancing USDB."""
        enc = Encumbrance(
            fiat_transfer_id=fiat_transfer_id,
            original_amount=amount,
        )
        self.db.add(enc)
        self.db.flush()
        self.db.add(EncPosition(enc_id=enc.id, wallet_id=user_wallet_id, amount=amount))
        self.db.commit()
        return enc

    # ------------------------------------------------------------------
    # Movement when user sends encumbered tokens
    # ------------------------------------------------------------------
    def shift_position(
        self,
        enc_id: str,
        sender_wallet: str,
        receiver_wallet: str,
        amount: Decimal,
    ) -> None:
        """Atomic DB update: subtract from sender, add / create for receiver."""
        with self.db.begin():
            q = (
                self.db.query(EncPosition)
                .filter_by(enc_id=enc_id, wallet_id=sender_wallet)
                .with_for_update()
            )
            pos_sender = q.one()
            if pos_sender.amount < amount:
                raise ValueError("Sender lacks encumbered balance")
            pos_sender.amount -= amount
            if pos_sender.amount == 0:
                self.db.delete(pos_sender)

            # Upsert receiver
            pos_recv = (
                self.db.query(EncPosition)
                .filter_by(enc_id=enc_id, wallet_id=receiver_wallet)
                .one_or_none()
            )
            if pos_recv:
                pos_recv.amount += amount
            else:
                self.db.add(
                    EncPosition(enc_id=enc_id, wallet_id=receiver_wallet, amount=amount)
                )

    # ------------------------------------------------------------------
    # On settlement success / failure (called by webhooks)
    # ------------------------------------------------------------------
    def clear_encumbrance(self, fiat_transfer_id: str) -> None:
        enc = (
            self.db.query(Encumbrance)
            .filter_by(fiat_transfer_id=fiat_transfer_id)
            .one_or_none()
        )
        if not enc:
            return
        enc.status = "cleared"
        self.db.query(EncPosition).filter_by(enc_id=enc.id).delete()
        self.db.commit()

    def recover_encumbrance(self, fiat_transfer_id: str) -> None:
        enc = (
            self.db.query(Encumbrance)
            .filter_by(fiat_transfer_id=fiat_transfer_id)
            .with_for_update()
            .one_or_none()
        )
        if not enc or enc.status != "pending":
            return

        positions: List[EncPosition] = (
            self.db.query(EncPosition)
            .filter_by(enc_id=enc.id)
            .order_by(EncPosition.amount.desc())
            .all()
        )

        remaining = enc.original_amount - enc.recovered_amount
        for pos in positions:
            if remaining <= 0:
                break

            to_pull = min(remaining, pos.amount)
            try:
                self.bridge.create_transfer_sync(
                    {
                        "amount": str(to_pull),
                        "on_behalf_of": CORPORATE_CUSTOMER_ID,
                        "source": {
                            "payment_rail": "solana",
                            "currency": "usdb",
                            "wallet_id": pos.wallet_id,
                        },
                        "destination": {
                            "payment_rail": "solana",
                            "currency": "usdb",
                            "wallet_id": CORP_WALLET_ID,
                        },
                    }
                )
                remaining -= to_pull
                pos.amount -= to_pull
                if pos.amount == 0:
                    self.db.delete(pos)
            except Exception as e:
                logger.error("Recovery pull failed for wallet %s: %s", pos.wallet_id, e)

        enc.recovered_amount = enc.original_amount - remaining
        enc.status = "failed_recovered" if remaining == 0 else "failed_partial"
        self.db.commit() 