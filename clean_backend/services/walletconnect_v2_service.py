"""
WalletConnect v2 Service
Production-level service for crypto wallet linking and transaction signing
"""

import asyncio
import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed
import qrcode
import base64
from io import BytesIO
import secrets  # local import to avoid top of file clutter
import urllib.parse # Added for URL encoding

from clean_backend.config.settings import settings, ERROR_CODES
from .security import SecurityException, security_validator

logger = logging.getLogger(__name__)

class WalletConnectError(Exception):
    """Custom WalletConnect exception"""
    
    def __init__(self, error_code: str, message: str, details: Optional[str] = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(self.message)

class SessionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DISCONNECTED = "disconnected"

class ChainType(str, Enum):
    EVM = "evm"
    SOLANA = "solana"

@dataclass
class WalletConnectSession:
    """WalletConnect v2 session model"""
    id: str
    user_id: str
    wallet_address: str
    chain_type: ChainType
    chain_id: str
    status: SessionStatus
    topic: str
    peer_metadata: Dict[str, Any]
    sym_key: str
    created_at: datetime
    expires_at: datetime
    approved_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None

@dataclass
class TransactionRequest:
    """Transaction request for user approval"""
    id: str
    session_id: str
    chain_type: ChainType
    chain_id: str
    to_address: str
    amount: str
    currency: str
    gas_estimate: Optional[Dict[str, Any]] = None
    status: str = "pending"
    created_at: datetime = None
    expires_at: datetime = None
    signed_transaction: Optional[str] = None
    transaction_hash: Optional[str] = None

class WalletConnectV2Service:
    """
    Production WalletConnect v2 service
    Handles session management, QR codes, and transaction signing
    """
    
    def __init__(self):
        self.project_id = settings.walletconnect_project_id
        self.relay_url = settings.walletconnect_relay_url
        self.metadata = settings.walletconnect_metadata
        
        # Session storage (in production, use Redis/DB)
        self.sessions: Dict[str, WalletConnectSession] = {}
        self.transaction_requests: Dict[str, TransactionRequest] = {}
        
        # WebSocket connection for real-time events
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.websocket_task: Optional[asyncio.Task] = None
        
        # Supported chains configuration
        self.supported_chains = {
            ChainType.EVM: {
                "ethereum": {"chain_id": 1, "name": "Ethereum"},
                "polygon": {"chain_id": 137, "name": "Polygon"},
                "base": {"chain_id": 8453, "name": "Base"},
                "arbitrum": {"chain_id": 42161, "name": "Arbitrum"},
                "optimism": {"chain_id": 10, "name": "Optimism"}
            },
            ChainType.SOLANA: {
                "solana": {"chain_id": "solana:mainnet", "name": "Solana"}
            }
        }
    
    async def create_session(
        self, 
        user_id: str, 
        wallet_address: str, 
        chain_type: ChainType,
        chain_id: str
    ) -> WalletConnectSession:
        """Create a new WalletConnect v2 session"""
        
        # ------------------------------------------------------------------
        # Input validation
        # ------------------------------------------------------------------

        # If caller passed chain_type as plain string (e.g. "evm" from REST),
        # coerce it to the ChainType enum.
        if isinstance(chain_type, str):
            try:
                chain_type = ChainType(chain_type.lower())  # type: ignore[assignment]
            except ValueError:
                raise WalletConnectError(
                    error_code=ERROR_CODES["INVALID_NETWORK"],
                    message=f"Unsupported chain type: {chain_type}"
                )

        # Validate wallet address *only if provided*. During initial pairing the
        # caller may not yet know the address.
        if wallet_address:
            if not security_validator.validate_wallet_address(wallet_address, chain_id):
                raise WalletConnectError(
                    error_code=ERROR_CODES["INVALID_WALLET_ADDRESS"],
                    message="Invalid wallet address for the specified chain"
                )

        # Validate network id
        if chain_id not in self.supported_chains[chain_type]:
            raise WalletConnectError(
                error_code=ERROR_CODES["INVALID_NETWORK"],
                message=f"Unsupported chain: {chain_id}"
            )
        
        # Generate ids
        session_id = str(uuid.uuid4())
        # WalletConnect topics are random 32-byte hex strings (64 chars)
        topic = secrets.token_hex(32)
        sym_key = secrets.token_hex(32)
        
        # Create session
        session = WalletConnectSession(
            id=session_id,
            user_id=user_id,
            wallet_address=wallet_address,
            chain_type=chain_type,
            chain_id=chain_id,
            status=SessionStatus.PENDING,
            topic=topic,
            peer_metadata=self.metadata,
            sym_key=sym_key,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=settings.session_expiry_hours)
        )
        
        # Store session
        self.sessions[session_id] = session

        # Attempt to open WebSocket for real-time updates.  In development
        # environments this may fail due to firewall / DNS; we treat that as
        # non-fatal so that the user can still obtain the pairing URI & QR.
        try:
            await self._start_websocket_connection(session_id)
        except WalletConnectError as _ws_err:
            # Log and continue – frontend can poll REST endpoint instead.
            logger.warning("WebSocket connection failed during session creation: %s", _ws_err.message)
            # Keep session in PENDING state; QR flow still works.
            # Do not raise – allow caller to proceed.
 
        logger.info(f"Created WalletConnect session {session_id} for user {user_id}")
        return session
    
    async def generate_qr_code(self, session_id: str) -> str:
        """Generate QR code for WalletConnect connection"""
        
        if session_id not in self.sessions:
            raise WalletConnectError(
                error_code=ERROR_CODES["SESSION_EXPIRED"],
                message="Session not found"
            )
        
        session = self.sessions[session_id]
        
        # Create WalletConnect URI
        uri = self._create_walletconnect_uri(session)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_base64}"
    
    async def create_transaction_request(
        self,
        session_id: str,
        to_address: str,
        amount: str,
        currency: str = "usdc",
        gas_estimate: Optional[Dict[str, Any]] = None
    ) -> TransactionRequest:
        """Create a transaction request for user approval"""
        
        if session_id not in self.sessions:
            raise WalletConnectError(
                error_code=ERROR_CODES["SESSION_EXPIRED"],
                message="Session not found"
            )
        
        session = self.sessions[session_id]
        
        # Validate recipient address
        if not security_validator.validate_wallet_address(to_address, session.chain_id):
            raise WalletConnectError(
                error_code=ERROR_CODES["INVALID_WALLET_ADDRESS"],
                message="Invalid recipient address"
            )
        
        # Create transaction request
        request_id = str(uuid.uuid4())
        request = TransactionRequest(
            id=request_id,
            session_id=session_id,
            chain_type=session.chain_type,
            chain_id=session.chain_id,
            to_address=to_address,
            amount=amount,
            currency=currency,
            gas_estimate=gas_estimate,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # Store request
        self.transaction_requests[request_id] = request
        
        # Send transaction request to wallet
        await self._send_transaction_request(request)
        
        logger.info(f"Created transaction request {request_id} for session {session_id}")
        return request
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session status"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "wallet_address": session.wallet_address,
            "chain_type": session.chain_type.value,
            "chain_id": session.chain_id,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "approved_at": session.approved_at.isoformat() if session.approved_at else None,
            "disconnected_at": session.disconnected_at.isoformat() if session.disconnected_at else None
        }
    
    async def get_transaction_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction request status"""
        if request_id not in self.transaction_requests:
            return None
        
        request = self.transaction_requests[request_id]
        
        return {
            "request_id": request.id,
            "session_id": request.session_id,
            "chain_type": request.chain_type.value,
            "chain_id": request.chain_id,
            "to_address": request.to_address,
            "amount": request.amount,
            "currency": request.currency,
            "status": request.status,
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "expires_at": request.expires_at.isoformat() if request.expires_at else None,
            "signed_transaction": request.signed_transaction,
            "transaction_hash": request.transaction_hash
        }
    
    async def disconnect_session(self, session_id: str) -> bool:
        """Disconnect a WalletConnect session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.status = SessionStatus.DISCONNECTED
        session.disconnected_at = datetime.utcnow()
        
        # Close WebSocket connection
        await self._close_websocket_connection(session_id)
        
        logger.info(f"Disconnected session {session_id}")
        return True
    
    def _create_walletconnect_uri(self, session: WalletConnectSession) -> str:
        """Create WalletConnect v2 URI"""
        # WalletConnect v2 URI format:
        # wc:{topic}@2?relay-protocol=irn&symKey={symKey}&projectId={projectId}

        # WalletConnect v2 pairing URI including projectId (relay-data)
        # WalletConnect v2 spec additionally requires a `methods` parameter that declares
        # the JSON-RPC methods this pairing supports. For simple pairing we can advertise
        # just the mandatory `wc_sessionPropose` method. Note that the value must be URI
        # encoded because of the brackets / commas.
        methods_param = urllib.parse.quote("[wc_sessionPropose]")

        return (
            f"wc:{session.topic}@2?relay-protocol=irn"
            f"&symKey={session.sym_key}"
            f"&relay-data={self.project_id}"
            f"&methods={methods_param}"
        )
    
    async def _start_websocket_connection(self, session_id: str):
        """Start WebSocket connection for real-time events"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        try:
            # Build WalletConnect Cloud relay WebSocket URL
            if self.relay_url.startswith("ws://") or self.relay_url.startswith("wss://"):
                base_url = self.relay_url.rstrip('/')
            else:
                base_url = f"wss://{self.relay_url.rstrip('/') }"

            # Relay server expects root path '/' then query ?projectId=... only.
            websocket_url = f"{base_url}/?projectId={self.project_id}"

            self.websocket = await websockets.connect(websocket_url)
            
            # Start event handling
            self.websocket_task = asyncio.create_task(
                self._handle_websocket_events(session_id)
            )
            
            logger.info(f"Started WebSocket connection for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket connection for session {session_id}: {e}")
            raise WalletConnectError(
                error_code=ERROR_CODES["WEBSOCKET_ERROR"],
                message=f"Failed to establish WebSocket connection: {str(e)}"
            )
    
    async def _handle_websocket_events(self, session_id: str):
        """Handle WebSocket events from wallet"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Handle different event types
                if data.get("method") == "wc_sessionRequest":
                    await self._handle_session_request(session_id, data)
                elif data.get("method") == "wc_sessionEvent":
                    await self._handle_session_event(session_id, data)
                elif data.get("method") == "wc_sessionDelete":
                    await self._handle_session_delete(session_id, data)
                elif data.get("method") == "wc_sessionPayload":
                    await self._handle_session_payload(session_id, data)
                
        except ConnectionClosed:
            logger.info(f"WebSocket connection closed for session {session_id}")
        except Exception as e:
            logger.error(f"Error handling WebSocket events for session {session_id}: {e}")
    
    async def _handle_session_request(self, session_id: str, data: Dict[str, Any]):
        """Handle session approval/rejection"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        if data.get("result", {}).get("approved"):
            session.status = SessionStatus.APPROVED
            session.approved_at = datetime.utcnow()
            session.wallet_address = data.get("result", {}).get("accounts", [""])[0]
            logger.info(f"Session {session_id} approved by wallet")
        else:
            session.status = SessionStatus.REJECTED
            logger.info(f"Session {session_id} rejected by wallet")
    
    async def _handle_session_event(self, session_id: str, data: Dict[str, Any]):
        """Handle session events"""
        logger.info(f"Session event for {session_id}: {data.get('name')}")
    
    async def _handle_session_delete(self, session_id: str, data: Dict[str, Any]):
        """Handle session deletion"""
        await self.disconnect_session(session_id)
    
    async def _handle_session_payload(self, session_id: str, data: Dict[str, Any]):
        """Handle transaction responses"""
        request_id = data.get("id")
        if request_id and request_id in self.transaction_requests:
            request = self.transaction_requests[request_id]
            
            if data.get("result"):
                # Transaction approved
                request.signed_transaction = data.get("result", {}).get("signedTransaction")
                request.transaction_hash = data.get("result", {}).get("hash")
                request.status = "signed"
                logger.info(f"Transaction {request_id} signed by wallet")
            else:
                # Transaction rejected
                request.status = "rejected"
                logger.info(f"Transaction {request_id} rejected by wallet")
    
    async def _close_websocket_connection(self, session_id: str):
        """Close WebSocket connection"""
        if self.websocket_task:
            self.websocket_task.cancel()
            try:
                await self.websocket_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        logger.info(f"Closed WebSocket connection for session {session_id}")
    
    async def _send_transaction_request(self, request: TransactionRequest):
        """Send transaction request to wallet via WebSocket"""
        if not self.websocket:
            return
        
        try:
            # Build transaction request
            transaction_data = {
                "id": request.id,
                "jsonrpc": "2.0",
                "method": "eth_sendTransaction",
                "params": [{
                    "from": self.sessions[request.session_id].wallet_address,
                    "to": request.to_address,
                    "value": request.amount,
                    "gas": request.gas_estimate.get("gas_limit") if request.gas_estimate else None,
                    "gasPrice": request.gas_estimate.get("gas_price") if request.gas_estimate else None
                }]
            }
            
            # Send via WebSocket
            await self.websocket.send(json.dumps(transaction_data))
            logger.info(f"Sent transaction request {request.id} to wallet")
            
        except Exception as e:
            logger.error(f"Failed to send transaction request {request.id}: {e}")
            raise WalletConnectError(
                error_code=ERROR_CODES["TRANSACTION_ERROR"],
                message=f"Failed to send transaction request: {str(e)}"
            )
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.expires_at < current_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.disconnect_session(session_id)
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

# Global service instance
walletconnect_service = WalletConnectV2Service() 