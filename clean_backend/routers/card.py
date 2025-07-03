from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..bridge import BridgeClient

router = APIRouter(prefix="/card", tags=["card"])

@router.post("/provision")
async def provision_card_account(
    db: Session = Depends(get_db),
    jwt=Depends(get_current_user),
):
    """Provision a card account for the logged-in user.

    The card account will be funded by the user's existing Bridge wallet. The
    wallet's *public crypto address* (not the Bridge wallet id) will be used
    as the funding source, as required by Bridge.
    """
    # 1. Ensure the user exists and has Bridge identifiers stored.
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id or not user.bridge_wallet_id:
        raise HTTPException(status_code=404, detail="Bridge wallet not found for user")

    bridge = BridgeClient()

    # 2. Retrieve wallet details to extract the public address.
    try:
        wallet = bridge.get_wallet(user.bridge_customer_id, user.bridge_wallet_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Unable to fetch Bridge wallet") from e

    # Bridge solana wallet responses typically include either "address" or
    # nested under "crypto_account". Try common patterns before failing.
    wallet_address = (
        wallet.get("address")
        or (wallet.get("crypto_account", {}).get("address") if isinstance(wallet.get("crypto_account"), dict) else None)
    )
    if not wallet_address:
        raise HTTPException(status_code=500, detail="Bridge wallet address missing in response")

    # 3. Create / provision the card account.
    try:
        card = bridge.create_card_account(
            user.bridge_customer_id,
            wallet_address=wallet_address,
            chain="solana",
            currency="usdc",
            client_reference_id=str(user.id),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge card provisioning failed") from e

    # Optional: you might persist card["id"] or other metadata here in DB.

    return card 