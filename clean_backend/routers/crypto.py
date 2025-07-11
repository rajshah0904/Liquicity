"""Crypto wallet and payment endpoints (WalletConnect + USDC + Bridge).

NOTE: For now we expose just /wallet/connect as a proof-of-concept.  Additional
endpoints from python_backend will be ported next.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field

from ..auth import get_current_user  # example dependency
from ..database import get_db
from ..models.crypto import WalletSession
from ..services.wallet_services import (
    walletconnect_service,
    WalletConnectError,
    usdc_payment_service,
    USDCError,
    bridge_client,
    BridgeError,
)

from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/crypto", tags=["crypto"])


class WalletConnectRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    wallet_address: str = Field(..., description="User wallet address (optional placeholder)")
    chain_type: str = Field(..., description="evm or solana")
    chain_id: str = Field(..., description="chain/network id")


@router.post("/wallet/connect")
async def connect_wallet(request: WalletConnectRequest, current_user=Depends(get_current_user)):
    """Begin a WalletConnect v2 session and return QR / URI."""

    try:
        session = await walletconnect_service.create_session(
            user_id=request.user_id,
            wallet_address=request.wallet_address,
            chain_type=request.chain_type,
            chain_id=request.chain_id,
        )
        qr_code_url = await walletconnect_service.generate_qr_code(session.id)
        uri = walletconnect_service._create_walletconnect_uri(session)

        return {
            "success": True,
            "data": {
                "session_id": session.id,
                "qr_code_url": qr_code_url,
                "uri": uri,
                "status": session.status.value,
                "expires_at": session.expires_at.isoformat(),
            },
        }

    except WalletConnectError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": e.message})


# --- Models ---

class WalletConnectStatusResponse(BaseModel):
    session_id: str
    status: str
    wallet_address: Optional[str]
    expires_at: datetime


class USDCPaymentRequest(BaseModel):
    session_id: str
    to_address: str
    amount: str
    chain_id: str = "ethereum"
    currency: str = "usdc"


class USDCSignedTxRequest(BaseModel):
    transfer_id: str
    signed_transaction: str


class BridgeTransferRequest(BaseModel):
    session_id: str
    amount: str
    source_network: str
    destination_network: str
    destination_address: str
    currency: str = "usdc"


# --- Routes ---

@router.get("/wallet/session/{session_id}", response_model=WalletConnectStatusResponse)
async def get_session_status(session_id: str):
    """Return status of an existing WalletConnect session."""
    status = await walletconnect_service.get_session_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail={"success": False, "error": "Session not found"})
    return status


@router.get("/wallet/sessions")
async def list_wallet_sessions(user_id: str, db: Session = Depends(get_db)):
    sessions = db.query(WalletSession).filter(WalletSession.user_id == user_id).all()
    return {"success": True, "data": [
        {
            "session_id": s.id,
            "wallet_address": s.wallet_address,
            "status": s.status,
            "chain_type": s.chain_type,
            "chain_id": s.chain_id,
        } for s in sessions
    ]}


@router.post("/payments/usdc/transfer")
async def create_usdc_transfer(payload: USDCPaymentRequest, current_user=Depends(get_current_user)):
    try:
        transfer = await usdc_payment_service.create_usdc_transfer(
            session_id=payload.session_id,
            to_address=payload.to_address,
            amount=payload.amount,
            chain_id=payload.chain_id,
            currency=payload.currency,
        )
        return {"success": True, "data": transfer.__dict__}
    except USDCError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": e.message})


@router.post("/payments/usdc/sign")
async def sign_usdc_transaction(payload: USDCSignedTxRequest, current_user=Depends(get_current_user)):
    try:
        result = await usdc_payment_service.process_signed_transaction(
            transfer_id=payload.transfer_id,
            signed_transaction=payload.signed_transaction,
        )
        return {"success": True, "data": result}
    except USDCError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": e.message})


@router.post("/bridge/transfer")
async def create_bridge_transfer(req: BridgeTransferRequest, current_user=Depends(get_current_user)):
    """Kick off Bridge transfer after crypto deposit."""
    try:
        bridge_req = bridge_client.create_usdc_transfer_request(
            amount=req.amount,
            user_id=current_user["id"],
            source_network=req.source_network,
            source_address="",  # could be pulled from session
            destination_network=req.destination_network,
            destination_address=req.destination_address,
            currency=req.currency,
        )
        transfer = await bridge_client.create_transfer(bridge_req)
        return {"success": True, "data": transfer.__dict__}
    except BridgeError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": e.message}) 