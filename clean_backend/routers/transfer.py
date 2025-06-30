from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from sqlalchemy.orm import Session

from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from ..database import get_db
from ..models import User
from ..bridge import BridgeClient
from ..services.encumbrance_service import EncumbranceService, CORP_WALLET_ID, CORPORATE_CUSTOMER_ID

router = APIRouter(prefix="/transfers", tags=["transfers"])


# ---------------------------- Schemas ----------------------------
class DepositIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str


class DepositOut(BaseModel):
    fiat_transfer_id: str
    advance_transfer_id: str
    encumbrance_id: str
    state: str


# ---------------------------- Helpers ----------------------------

def _get_user_by_sub(db: Session, sub: str) -> User | None:
    return db.query(User).filter((User.auth0_id == sub) | (User.email == sub)).first()


# ---------------------------- Routes ----------------------------

@router.post("/deposit", response_model=DepositOut)
async def deposit_fiat_to_wallet(
    body: DepositIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Start a fiat deposit (bank push) and immediately credit the user's on-chain wallet with USDB.

    Steps:
    1. Create bridge transfer: external_account_id ➜ corporate treasury wallet (fiat rails).
    2. Advance USDB from treasury wallet ➜ user's bridge wallet.
    3. Persist encumbrance so funds can be clawed back if fiat leg fails.
    """

    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.bridge_customer_id or not user.bridge_wallet_id:
        raise HTTPException(status_code=400, detail="User missing Bridge account")

    if not CORP_WALLET_ID or not CORPORATE_CUSTOMER_ID:
        raise HTTPException(status_code=500, detail="Treasury configuration missing on server")

    client = BridgeClient()
    # 1. Bank ➜ Treasury fiat transfer
    fiat_payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": user.bridge_customer_id,
        "source": {
            "payment_rail": "ach",  # TODO: infer rail by country / currency
            "currency": "usd",
            "external_account_id": body.external_account_id,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usd",
            "wallet_id": CORP_WALLET_ID,
        },
    }
    try:
        fiat_tx = client.create_transfer_sync(fiat_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to initiate fiat transfer: {e}")

    # 2. Advance USDB to user
    advance_payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": CORPORATE_CUSTOMER_ID,  # treasury sends on its own behalf
        "source": {
            "payment_rail": "solana",
            "currency": "usdb",
            "wallet_id": CORP_WALLET_ID,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usdb",
            "wallet_id": user.bridge_wallet_id,
        },
    }

    try:
        advance_tx = client.create_transfer_sync(advance_payload)
    except Exception as e:
        # TODO: optionally cancel fiat transfer
        raise HTTPException(status_code=502, detail=f"Advance payout failed: {e}")

    # 3. Record encumbrance
    svc = EncumbranceService(db)
    enc = svc.create_encumbrance(
        fiat_transfer_id=fiat_tx["id"],
        user_wallet_id=user.bridge_wallet_id,
        amount=Decimal(body.amount),
    )

    return DepositOut(
        fiat_transfer_id=fiat_tx["id"],
        advance_transfer_id=advance_tx["id"],
        encumbrance_id=str(enc.id),
        state=fiat_tx.get("state", "pending"),
    ) 