# Placeholder for WalletConnect router. Will add endpoints for session creation, status, and disconnect here. 

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from clean_backend.services.walletconnect_service import (
    WalletConnectV2Service, WalletConnectError, SessionStatus, ChainType
)
from clean_backend.database import get_settings, get_db  # Assume you have a settings loader
from clean_backend.auth import get_current_user  # Assume you have authentication
from clean_backend.services.security import security_validator  # Your real validator
from clean_backend.config.settings import ERROR_CODES
from clean_backend.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/walletconnect", tags=["WalletConnect"])

# Dependency to get the WalletConnect service with real settings
async def get_walletconnect_service():
    settings = get_settings()
    return WalletConnectV2Service(settings, security_validator, ERROR_CODES)

# Pydantic models
class WalletConnectRequest(BaseModel):
    user_id: str
    wallet_address: str
    chain_type: ChainType
    chain_id: str

class WalletConnectResponse(BaseModel):
    session_id: str
    qr_code: str
    uri: str
    status: str
    expires_at: str

class TransactionRequestModel(BaseModel):
    session_id: str
    to_address: str
    amount: str
    currency: Optional[str] = "usdc"
    gas_estimate: Optional[Dict[str, Any]] = None

class TransactionResponseModel(BaseModel):
    request_id: str
    status: str
    signed_transaction: Optional[str] = None
    transaction_hash: Optional[str] = None
    expires_at: Optional[str] = None

# Endpoint: Create WalletConnect session
@router.post("/session", response_model=WalletConnectResponse)
async def create_walletconnect_session(
    request: WalletConnectRequest,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    try:
        session = await service.create_session(
            user_id=request.user_id,
            wallet_address=request.wallet_address,
            chain_type=request.chain_type,
            chain_id=request.chain_id
        )
        qr_code = await service.generate_qr_code(session.id)
        uri = service._create_walletconnect_uri(session)
        return WalletConnectResponse(
            session_id=session.id,
            qr_code=qr_code,
            uri=uri,
            status=session.status.value,
            expires_at=session.expires_at.isoformat()
        )
    except WalletConnectError as e:
        logger.error(f"WalletConnect error: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get session status
@router.get("/session/{session_id}")
async def get_session_status(
    session_id: str,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    try:
        status = await service.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        return status
    except Exception as e:
        logger.error(f"Session status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Disconnect session
@router.delete("/session/{session_id}")
async def disconnect_session(
    session_id: str,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    try:
        success = await service.disconnect_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session disconnected successfully"}
    except Exception as e:
        logger.error(f"Session disconnect error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Create transaction request
@router.post("/transaction", response_model=TransactionResponseModel)
async def create_transaction(
    request: TransactionRequestModel,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get user object
        user_obj = db.query(User).filter(User.auth0_id == user.get("sub")).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get session to extract wallet info
        session_status = await service.get_session_status(request.session_id)
        if not session_status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        tx = await service.create_transaction_request(
            session_id=request.session_id,
            to_address=request.to_address,
            amount=request.amount,
            currency=request.currency,
            gas_estimate=request.gas_estimate,
            db=db,
            user_id=str(user_obj.id),
            from_wallet=session_status.get("wallet_address"),
            chain_type=session_status.get("chain_type")
        )
        return TransactionResponseModel(
            request_id=tx.id,
            status=tx.status,
            signed_transaction=tx.signed_transaction,
            transaction_hash=tx.transaction_hash,
            expires_at=tx.expires_at.isoformat() if tx.expires_at else None
        )
    except WalletConnectError as e:
        logger.error(f"Transaction error: {e}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get transaction status with real-time updates
@router.get("/transaction/{request_id}/status")
async def get_transaction_request_status(
    request_id: str,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    """Get real-time transaction request status"""
    try:
        status = await service.get_transaction_status(request_id)
        if not status:
            raise HTTPException(status_code=404, detail="Transaction request not found")
        return status
    except Exception as e:
        logger.error(f"Transaction status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get session events (for real-time updates)
@router.get("/session/{session_id}/events")
async def get_session_events(
    session_id: str,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    """Get recent session events for real-time updates"""
    try:
        # This would return recent events from the session
        # For now, return session status as events
        status = await service.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "events": [
                {
                    "type": "status_change",
                    "timestamp": status.get("created_at"),
                    "data": status
                }
            ]
        }
    except Exception as e:
        logger.error(f"Session events error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get WebSocket connection status
@router.get("/session/{session_id}/connection")
async def get_connection_status(
    session_id: str,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    """Get WebSocket connection status for a session"""
    try:
        # Check if session exists
        status = await service.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check WebSocket connection status
        is_connected = service.websocket is not None and not service.websocket.closed
        
        return {
            "session_id": session_id,
            "connected": is_connected,
            "websocket_status": "connected" if is_connected else "disconnected"
        }
    except Exception as e:
        logger.error(f"Connection status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Force refresh session connection
@router.post("/session/{session_id}/refresh")
async def refresh_session_connection(
    session_id: str,
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    """Force refresh the WebSocket connection for a session"""
    try:
        # Check if session exists
        status = await service.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Close existing connection and restart
        await service._close_websocket_connection(session_id)
        await service._start_websocket_connection(session_id)
        
        return {"success": True, "message": "Session connection refreshed"}
    except Exception as e:
        logger.error(f"Session refresh error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get all active sessions for user
@router.get("/sessions/active")
async def get_active_sessions(
    service: WalletConnectV2Service = Depends(get_walletconnect_service),
    user: dict = Depends(get_current_user)
):
    """Get all active sessions for the authenticated user"""
    try:
        # This would filter sessions by user_id
        # For now, return all sessions (in production, filter by user)
        active_sessions = []
        for session_id, session in service.sessions.items():
            if session.status in [SessionStatus.PENDING, SessionStatus.APPROVED]:
                session_data = await service.get_session_status(session_id)
                if session_data:
                    active_sessions.append(session_data)
        
        return {"sessions": active_sessions, "count": len(active_sessions)}
    except Exception as e:
        logger.error(f"Active sessions error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint: Get service health and statistics
@router.get("/health")
async def get_service_health(
    service: WalletConnectV2Service = Depends(get_walletconnect_service)
):
    """Get WalletConnect service health and statistics"""
    try:
        active_sessions = len([s for s in service.sessions.values() if s.status in [SessionStatus.PENDING, SessionStatus.APPROVED]])
        pending_transactions = len([t for t in service.transaction_requests.values() if t.status == "pending"])
        
        return {
            "status": "healthy",
            "active_sessions": active_sessions,
            "pending_transactions": pending_transactions,
            "total_sessions": len(service.sessions),
            "websocket_connected": service.websocket is not None and not service.websocket.closed
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 