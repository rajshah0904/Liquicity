"""Crypto wallet and payment endpoints (WalletConnect + USDC + Bridge).

NOTE: For now we expose just /wallet/connect as a proof-of-concept.  Additional
endpoints from python_backend will be ported next.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field

from ..auth import get_current_user  # example dependency
from ..database import get_db

from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Services
from ..services.walletconnect_v2_service import walletconnect_service, WalletConnectError
from ..services.usdc_payment_service import usdc_payment_service, USDCError

router = APIRouter(prefix="/api/crypto", tags=["crypto"])


class WalletConnectRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    wallet_address: str = Field("", description="User wallet address (optional placeholder)")
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
        # Generate a pairing URI
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
        raise HTTPException(status_code=400, detail={"success": False, "error": {"code": e.error_code, "message": e.message}})


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
    data = await walletconnect_service.get_session_status(session_id)
    if not data:
        raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "SESSION_NOT_FOUND", "message": "Session not found"}})
    return {
        "session_id": data["session_id"],
        "status": data["status"],
        "wallet_address": data.get("wallet_address"),
        "expires_at": datetime.fromisoformat(data["expires_at"]) if isinstance(data["expires_at"], str) else data["expires_at"],
    }


@router.get("/wallet/sessions")
async def list_wallet_sessions(user_id: str, db: Session = Depends(get_db)):
    # Placeholder list – sessions are kept in-memory in the service for now
    return {"success": True, "data": []}


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
        gas = transfer.gas_estimate
        return {
            "success": True,
            "data": {
                "transfer_id": transfer.id,
                "session_id": transfer.session_id,
                "amount": transfer.amount,
                "to_address": transfer.to_address,
                "chain_type": transfer.chain_type.value,
                "chain_id": transfer.chain_id,
                "gas_estimate": {
                    "gas_price": gas.gas_price if gas else None,
                    "gas_limit": gas.gas_limit if gas else None,
                    "total_cost": gas.total_cost if gas else None,
                    "estimated_time": gas.estimated_time if gas else None,
                },
                "status": transfer.status.value,
                "expires_at": (transfer.created_at + timedelta(minutes=30)).isoformat() if transfer.created_at else None,
            },
        }
    except USDCError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": {"code": e.error_code, "message": e.message}})


@router.post("/payments/usdc/sign")
async def sign_usdc_transaction(payload: USDCSignedTxRequest, current_user=Depends(get_current_user)):
    try:
        result = await usdc_payment_service.process_signed_transaction(
            transfer_id=payload.transfer_id,
            signed_transaction=payload.signed_transaction,
        )
        return {"success": True, "data": {**result}}
    except USDCError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": {"code": e.error_code, "message": e.message}})


@router.get("/payments/usdc/transfer/{transfer_id}")
async def get_usdc_transfer_status(transfer_id: str, current_user=Depends(get_current_user)):
    data = await usdc_payment_service.get_transfer_status(transfer_id)
    if not data:
        raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "TRANSFER_NOT_FOUND", "message": "Transfer not found"}})
    return {"success": True, "data": data}


@router.get("/payments/usdc/build/{transfer_id}")
async def build_usdc_transaction(transfer_id: str, current_user=Depends(get_current_user)):
    try:
        tx = await usdc_payment_service.build_transaction(transfer_id)
        return {"success": True, "data": tx}
    except USDCError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": {"code": e.error_code, "message": e.message}})


class TxRequestPayload(BaseModel):
    transfer_id: str = Field(..., description="Previously created transfer id")


@router.post("/wallet/txrequest")
async def create_wallet_tx_request(payload: TxRequestPayload, current_user=Depends(get_current_user)):
    """Send a transaction request to the user's wallet via WalletConnect."""
    # Lookup transfer to pull session, destination, amount, and gas
    transfer = await usdc_payment_service.get_transfer_status(payload.transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "TRANSFER_NOT_FOUND", "message": "Transfer not found"}})

    session_id = transfer["session_id"]
    to_address = transfer["to_address"]
    amount = transfer["amount"]
    currency = transfer.get("currency", "usdc")
    gas_estimate = transfer.get("gas_estimate")

    try:
        req = await walletconnect_service.create_transaction_request(
            session_id=session_id,
            to_address=to_address,
            amount=amount,
            currency=currency,
            gas_estimate=gas_estimate,
        )
        return {"success": True, "data": {"request_id": req.id, "status": req.status}}
    except WalletConnectError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": {"code": e.error_code, "message": e.message}})


@router.get("/wallet/txstatus/{request_id}")
async def get_wallet_tx_status(request_id: str, current_user=Depends(get_current_user)):
    data = await walletconnect_service.get_transaction_status(request_id)
    if not data:
        raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "TX_NOT_FOUND", "message": "Transaction request not found"}})
    return {"success": True, "data": data}


@router.post("/bridge/transfer")
async def create_bridge_transfer(req: BridgeTransferRequest, current_user=Depends(get_current_user)):
    """Kick off Bridge transfer after crypto deposit. Placeholder passthrough for now."""
    return {"success": True, "data": {"transfer_id": "placeholder-bridge-transfer-id"}} 