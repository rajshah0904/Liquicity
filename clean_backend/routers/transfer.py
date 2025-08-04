from decimal import Decimal
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from sqlalchemy.orm import Session

from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from ..database import get_db
from ..models import User, BridgeCustomer, BridgeWallet
from ..bridge import BridgeClient
from ..services.encumbrance_service import EncumbranceService, CORPORATE_WALLET_ID, CORPORATE_CUSTOMER_ID
from ..models import PlaidItem

router = APIRouter(prefix="/transfers", tags=["transfers"])

# Separate router with no prefix to expose legacy /deposits endpoint at root
public_router = APIRouter(tags=["transfers"], include_in_schema=False)


# ---------------------------- Schemas ----------------------------
class DepositIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str


class DepositOut(BaseModel):
    fiat_transfer_id: str
    advance_transfer_id: str
    encumbrance_id: str
    state: str


class WithdrawalIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str


# ---------------------------- Helpers ----------------------------

def _get_user_by_sub(db: Session, sub: str) -> Optional[User]:
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
    1. Create bridge transfer: external_account_id ➜ corporate account treasury wallet (fiat rails).
    2. Advance USDB from treasury wallet ➜ user's bridge wallet.
    3. Persist encumbrance so funds can be clawed back if fiat leg fails.
    """

    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer and wallet from related tables
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=400, detail="Bridge wallet not found")

    if not CORPORATE_WALLET_ID or not CORPORATE_CUSTOMER_ID:
        raise HTTPException(status_code=500, detail="Treasury configuration missing on server")

    client = BridgeClient()
    # Fetch the external account to determine currency and appropriate on-ramp rail
    try:
        ext_acct = client.get_external_account(body.external_account_id, bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid external account: {e}")

    # ------------------------------------------------------------------
    # Plaid balance guardrail – ensure sufficient funds before pushing ACH
    # ------------------------------------------------------------------

    from ..services.plaid_client import PlaidClient  # local import to avoid cycles

    plaid_item = db.query(PlaidItem).filter(PlaidItem.external_account_id == body.external_account_id).first()
    if plaid_item:
        try:
            bal_resp = PlaidClient(force_production=True).get_balance(plaid_item.access_token)
            # Sum available balance across matching accounts
            available_sum = 0
            for acct in bal_resp.get("accounts", []):
                avail = acct.get("balances", {}).get("available")
                if avail is not None:
                    available_sum += float(avail)

            if available_sum < float(body.amount):
                raise HTTPException(status_code=400, detail="Insufficient bank balance to cover deposit amount")
        except HTTPException:
            raise
        except Exception as e:
            # Non-fatal – log warning but continue; Bridge will still attempt ACH
            import logging
            logging.getLogger(__name__).warning("Plaid balance check failed: %s", e)

    currency = (ext_acct.get("currency") or "usd").lower()
    rail_by_cur = {"usd": "ach_push", "eur": "sepa", "mxn": "spei"}
    if currency not in rail_by_cur:
        raise HTTPException(status_code=400, detail=f"Unsupported external account currency: {currency}")

    payment_rail = rail_by_cur[currency]

    # ------------------------------------------------------------------
    # Generate Plaid processor token & initiate ACH debit via Seamless Chex
    # ------------------------------------------------------------------
    processor_token = None
    if plaid_item:
        from ..services.seamless_chex_client import SeamlessChexClient, SeamlessChexError  # local import
        try:
            auth_resp = PlaidClient(force_production=True).get_auth(plaid_item.access_token)
            # Pick first account (or first checking/savings) for processor token
            accounts = auth_resp.get("accounts", [])
            if not accounts:
                raise ValueError("No accounts returned by Plaid Auth")
            preferred = next((a for a in accounts if a.get("subtype") in ("checking", "savings")), accounts[0])
            account_id_for_token = preferred["account_id"]

            proc_resp = PlaidClient(force_production=True).create_processor_token(
                plaid_item.access_token,
                account_id=account_id_for_token,
                processor="seamless_chex",
            )
            processor_token = proc_resp.get("processor_token")
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Failed to create processor token for Seamless Chex: %s", e)

    # Initiate debit via Seamless Chex if we have a processor token
    if processor_token:
        try:
            dest_acct_id = os.getenv("SEAMLESSCHEX_DESTINATION_ACCOUNT_ID")
            chex = SeamlessChexClient()
            chex_resp = chex.initiate_debit(
                processor_token=processor_token,
                amount=Decimal(str(body.amount)),
                currency=currency.upper(),
                description="Liquicity fiat deposit",
                destination_account_id=dest_acct_id,
            )
            # Optionally persist chex_resp somewhere or include in response
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("Seamless Chex debit failed: %s", e)
            # Non-fatal for now – continue with Bridge on-ramp so deposit isn't blocked

    # Fetch current exchange rate currency -> USDB so we can credit user immediately
    try:
        if currency == "usd":
            # USDB is 1:1 pegged to USD – no conversion needed
            usdb_amount_dec = Decimal(str(body.amount))
        else:
            # Bridge only provides USD→EUR and USD→MXN rates. Invert to get EUR/MXN → USD.
            rate_data = client.get_exchange_rate("usd", currency)
            rate_usd_to_cur = Decimal(str(rate_data.get("rate") or rate_data.get("exchange_rate") or 0))
            if rate_usd_to_cur == 0:
                raise ValueError("Rate missing in response")
            # amount (currency) × (USD / currency) = USD equivalent
            usdb_amount_dec = (Decimal(str(body.amount)) / rate_usd_to_cur).quantize(Decimal("0.000001"))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch exchange rate: {e}")

    # ---------------- Treasury liquidity check ----------------
    try:
        treas_wallet = client.get_wallet(CORPORATE_CUSTOMER_ID, CORPORATE_WALLET_ID)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Treasury wallet not found or unreachable: {e}")

    bal_list = treas_wallet.get("balances", [])
    treas_usdb = Decimal("0")
    for b in bal_list:
        if b.get("currency", "").lower() == "usdb":
            treas_usdb = Decimal(str(b.get("available_balance") or b.get("balance") or 0))
            break

    if treas_usdb < usdb_amount_dec:
        raise HTTPException(status_code=400, detail="Treasury liquidity insufficient to cover instant credit. Please try again later.")

    fiat_payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": bridge_customer.id,
        "source": {
            "payment_rail": payment_rail,
            "currency": currency,
            "external_account_id": body.external_account_id,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": CORPORATE_WALLET_ID,
        },
        "convert_to_currency": "usdb",
    }
    try:
        fiat_tx = client.create_transfer_sync(fiat_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to initiate fiat transfer: {e}")

    # Guardrail: proceed with instant credit only if Bridge immediately returned state=='pending'
    fiat_state = fiat_tx.get("state")
    if fiat_state != "pending":
        # Do not advance funds; let normal settlement complete first
        return DepositOut(
            fiat_transfer_id=fiat_tx["id"],
            advance_transfer_id="",
            encumbrance_id="",
            state=fiat_state,
        )

    # 2. Advance USDB to user using the rate-based amount
    usdb_amount = str(usdb_amount_dec)
    advance_payload: Dict[str, Any] = {
        "amount": usdb_amount,
        "on_behalf_of": CORPORATE_CUSTOMER_ID,  # treasury sends on its own behalf
        "source": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": CORPORATE_WALLET_ID,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": bridge_wallet.id,
        },
    }

    try:
        advance_tx = client.create_transfer_sync(advance_payload)
    except Exception as e:
        # Cancel the fiat on-ramp since treasury couldn't advance funds
        try:
            client.delete_transfer(fiat_tx["id"])
        except Exception as cancel_err:
            # Log but surface original error
            import logging
            logging.getLogger(__name__).error("Failed to cancel fiat transfer %s after advance failure: %s", fiat_tx["id"], cancel_err)

        raise HTTPException(status_code=502, detail=f"Advance payout failed; deposit cancelled: {e}")

    # 3. Record encumbrance
    svc = EncumbranceService(db)
    enc = svc.create_encumbrance(
        fiat_transfer_id=fiat_tx["id"],
        user_wallet_id=bridge_wallet.id,
        amount=usdb_amount_dec,
    )

    return DepositOut(
        fiat_transfer_id=fiat_tx["id"],
        advance_transfer_id=advance_tx["id"],
        encumbrance_id=str(enc.id),
        state=fiat_tx.get("state", "pending"),
    )


@router.post("/deposits", response_model=DepositOut, include_in_schema=False)
async def deposit_alias_transfers(
    body: DepositIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Alias for legacy frontend which calls /deposits under /transfers/deposits."""
    return await deposit_fiat_to_wallet(body, db, auth_user)


# Root-level alias
# This route has no /transfers prefix because it belongs to `public_router`.
@public_router.post("/deposits", response_model=DepositOut)
async def deposit_alias_root(
    body: DepositIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Root-level /deposits alias for frontend convenience."""
    return await deposit_fiat_to_wallet(body, db, auth_user)


@router.post("/withdraw", response_model=Dict[str, Any])
async def withdraw_fiat_from_wallet(
    body: WithdrawalIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Initiate a fiat withdrawal: Bridge wallet ➜ external bank account.

    We pick the appropriate fiat rail (ACH, SEPA, etc.) based on the external
    account's currency.
    """
    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer and wallet from related tables
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=400, detail="Bridge wallet not found")

    client = BridgeClient()

    # Fetch external account to validate ownership & get currency
    try:
        ext_acct = client.get_external_account(body.external_account_id, bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid external account: {e}")

    currency = (ext_acct.get("currency") or "usd").lower()
    rail_by_cur = {"usd": "ach_push", "eur": "sepa"}
    if currency not in rail_by_cur:
        raise HTTPException(status_code=400, detail=f"Unsupported withdrawal currency: {currency}")

    payment_rail = rail_by_cur[currency]

    payload = {
        "amount": str(body.amount),
        "on_behalf_of": bridge_customer.id,
        "source": {
            "payment_rail": "solana",
            "currency": "usdb",
            "wallet_id": bridge_wallet.id,
        },
        "destination": {
            "payment_rail": payment_rail,
            "currency": currency,
            "external_account_id": body.external_account_id,
        },
    }

    try:
        transfer = client.create_transfer_sync(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge withdrawal failed: {e}")

    # TODO: optionally persist withdrawal record / encumbrance if needed
    return transfer 