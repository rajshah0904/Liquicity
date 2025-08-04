"""Crypto wallet and payment endpoints (WalletConnect + USDC + Bridge).

NOTE: For now we expose just /wallet/connect as a proof-of-concept.  Additional
endpoints from python_backend will be ported next.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field

from ..auth import get_current_user  # example dependency
from ..database import get_db

# Note: Crypto wallet services can be implemented using the main BridgeClient from ..bridge

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
    # Placeholder implementation
    return {
        "success": True,
        "data": {
            "session_id": "placeholder-session-id",
            "qr_code_url": "placeholder-qr-url",
            "uri": "placeholder-uri",
            "status": "pending",
            "expires_at": "2025-01-08T00:00:00Z",
        },
    }


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
    # Placeholder implementation
    return {
        "session_id": session_id,
        "status": "pending",
        "wallet_address": None,
        "expires_at": "2025-01-08T00:00:00Z",
    }


@router.get("/wallet/sessions")
async def list_wallet_sessions(user_id: str, db: Session = Depends(get_db)):
    # For now, return empty list since we removed WalletSession model
    # This can be enhanced later if needed with ExternalWallet or BridgeWallet
    return {"success": True, "data": []}


@router.post("/payments/usdc/transfer")
async def create_usdc_transfer(payload: USDCPaymentRequest, current_user=Depends(get_current_user)):
    # Placeholder implementation
    return {"success": True, "data": {"transfer_id": "placeholder-transfer-id"}}


@router.post("/payments/usdc/sign")
async def sign_usdc_transaction(payload: USDCSignedTxRequest, current_user=Depends(get_current_user)):
    # Placeholder implementation
    return {"success": True, "data": {"status": "signed"}}


@router.post("/bridge/transfer")
async def create_bridge_transfer(req: BridgeTransferRequest, current_user=Depends(get_current_user)):
    """Kick off Bridge transfer after crypto deposit."""
    # Placeholder implementation
    return {"success": True, "data": {"transfer_id": "placeholder-bridge-transfer-id"}} 