import asyncio
import json
import uuid
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import qrcode
import base64
from io import BytesIO
from sqlalchemy.orm import Session as DBSession
from clean_backend.models import Transaction, BlacklistedAddress, WalletConnectSession as DBWalletConnectSession
import requests
import json as pyjson
from fastapi import HTTPException, Request

# TODO: Adapt these imports for clean_backend
# from config.settings import settings, ERROR_CODES
# from core.security import security_validator

logger = logging.getLogger(__name__)

class WalletConnectError(Exception):
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
class TransactionRequest:
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

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
ETH_RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/your-alchemy-key"  # Replace with your key

class WalletConnectV2Service:
    def __init__(self, settings, security_validator, error_codes, db: DBSession):
        self.project_id = settings.walletconnect_project_id
        self.relay_url = settings.walletconnect_relay_url
        self.metadata = getattr(settings, 'walletconnect_metadata', {})
        self.error_codes = error_codes
        self.security_validator = security_validator
        self.supported_chains = {
            ChainType.EVM: {
                "ethereum": {"chain_id": 1, "name": "Ethereum"},
                "polygon": {"chain_id": 137, "name": "Polygon"},
                "base": {"chain_id": 8453, "name": "Base"}
            },
            ChainType.SOLANA: {
                "solana": {"chain_id": "solana:mainnet", "name": "Solana"}
            }
        }
        self.db = db
        self.websocket = None
        self.websocket_task = None

    async def create_session(self, user_id: str, wallet_address: str, chain_type: ChainType, chain_id: str, request: Request = None) -> DBWalletConnectSession:
        import secrets
        # Rate limiting: allow max 5 sessions per user per hour
        recent_sessions = self.db.query(DBWalletConnectSession).filter(
            DBWalletConnectSession.user_id == user_id,
            DBWalletConnectSession.created_at > datetime.utcnow() - timedelta(hours=1)
        ).count()
        if recent_sessions >= 5:
            raise WalletConnectError(
                error_code=self.error_codes["RATE_LIMIT"],
                message="Too many session requests. Please wait before trying again."
            )
        # Strict input validation
        if not isinstance(wallet_address, str) or len(wallet_address) < 32 or len(wallet_address) > 128:
            raise WalletConnectError(
                error_code=self.error_codes["INVALID_WALLET_ADDRESS"],
                message="Invalid wallet address format."
            )
        if not self.security_validator.validate_wallet_address(wallet_address, chain_id):
            raise WalletConnectError(
                error_code=self.error_codes["INVALID_WALLET_ADDRESS"],
                message="Invalid wallet address for the specified chain"
            )
        if chain_id not in self.supported_chains[chain_type]:
            raise WalletConnectError(
                error_code=self.error_codes["INVALID_NETWORK"],
                message=f"Unsupported chain: {chain_id}"
            )
        session_id = str(uuid.uuid4())
        topic = secrets.token_hex(32)
        sym_key = secrets.token_hex(32)
        relay_protocol = "irn"
        version = "2"
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=getattr(self, 'session_expiry_hours', 24))
        db_session = DBWalletConnectSession(
            id=session_id,
            user_id=user_id,
            wallet_address=wallet_address,
            chain_type=chain_type.value,
            chain_id=chain_id,
            status=SessionStatus.PENDING.value,
            topic=topic,
            sym_key=sym_key,
            relay_protocol=relay_protocol,
            version=version,
            peer_metadata=pyjson.dumps(self.metadata),
            created_at=now,
            expires_at=expires_at
        )
        self.db.add(db_session)
        self.db.commit()
        # Audit log
        logger.info(f"[AUDIT] WalletConnect session created: user_id={user_id}, session_id={session_id}, chain_type={chain_type.value}, chain_id={chain_id}")
        return db_session

    async def generate_qr_code(self, session_id: str) -> str:
        db_session = self.db.query(DBWalletConnectSession).filter_by(id=session_id).first()
        if not db_session:
            raise WalletConnectError(
                error_code=self.error_codes["SESSION_EXPIRED"],
                message="Session not found"
            )
        uri = self._create_walletconnect_uri(db_session)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_base64}"

    async def get_wallet_balance(self, wallet_address: str, chain_type: str) -> float:
        if chain_type == "solana":
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
            try:
                resp = requests.post(SOLANA_RPC_URL, json=payload, timeout=10)
                resp.raise_for_status()
                lamports = resp.json().get("result", {}).get("value", 0)
                return lamports / 1_000_000_000  # SOL
            except Exception:
                return 0.0
        elif chain_type == "evm":
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_getBalance",
                "params": [wallet_address, "latest"]
            }
            try:
                resp = requests.post(ETH_RPC_URL, json=payload, timeout=10)
                resp.raise_for_status()
                wei = int(resp.json().get("result", "0x0"), 16)
                return wei / 1e18  # ETH
            except Exception:
                return 0.0
        return 0.0

    async def create_transaction_request(self, session_id: str, to_address: str, amount: str, currency: str = "usdc", gas_estimate: Optional[Dict[str, Any]] = None, db: DBSession = None, user_id: str = None, from_wallet: str = None, chain_type: str = None) -> TransactionRequest:
        # Blacklist check
        if db is not None:
            bl = db.query(BlacklistedAddress).filter_by(address=to_address, chain_type=chain_type or "solana", active=True).first()
            if bl:
                raise WalletConnectError(
                    error_code=self.error_codes["INVALID_WALLET_ADDRESS"],
                    message="Destination address is blacklisted."
                )
        
        # On-chain balance check
        if from_wallet and chain_type:
            balance = await self.get_wallet_balance(from_wallet, chain_type)
            if balance < float(amount):
                raise WalletConnectError(
                    error_code=self.error_codes["INTERNAL_ERROR"],
                    message=f"Insufficient balance: {balance} < {amount}"
                )
        
        # Risk assessment and compliance checks
        risk_assessment = None
        if db is not None and from_wallet and to_address:
            risk_assessment = await self.assess_transaction_risk(
                from_wallet, to_address, float(amount), currency, chain_type or "solana", db
            )
            
            # Create compliance report for high-risk transactions
            if risk_assessment["flagged"]:
                await self.create_compliance_report(
                    db=db,
                    report_type="SAR" if risk_assessment["risk_score"] >= 80 else "CTR",
                    details=f"High-risk transaction: {risk_assessment['flags']}",
                    user_id=user_id,
                    transaction_id=None  # Will be set after transaction creation
                )
        
        # Log transaction attempt with risk assessment
        tx_obj = None
        if db is not None and user_id and from_wallet:
            tx_obj = Transaction(
                user_id=user_id,
                from_wallet=from_wallet,
                to_wallet=to_address,
                amount=amount,
                currency=currency,
                chain_type=chain_type or "solana",
                status="pending",
                risk_score=risk_assessment["risk_score"] if risk_assessment else 0.0,
                flagged=risk_assessment["flagged"] if risk_assessment else False,
                notes=f"Risk flags: {', '.join(risk_assessment['flags'])}" if risk_assessment and risk_assessment['flags'] else None
            )
            db.add(tx_obj)
            db.commit()
            
            # Update compliance report with transaction ID if it was created
            if risk_assessment and risk_assessment["flagged"]:
                # Assuming ComplianceReport model is available and imported
                # from clean_backend.models import ComplianceReport
                # latest_report = db.query(ComplianceReport).filter(
                #     ComplianceReport.user_id == user_id,
                #     ComplianceReport.transaction_id.is_(None)
                # ).order_by(ComplianceReport.created_at.desc()).first()
                # if latest_report:
                #     latest_report.transaction_id = str(tx_obj.id)
                #     db.commit()
                pass # Placeholder for compliance report update
        
        # Create the WalletConnect transaction request
        request_id = str(uuid.uuid4())
        request = TransactionRequest(
            id=request_id,
            session_id=session_id,
            chain_type=ChainType(chain_type or "solana"),
            chain_id=chain_type or "solana",
            to_address=to_address,
            amount=amount,
            currency=currency,
            gas_estimate=gas_estimate,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        
        # Store request
        # self.transaction_requests[request_id] = request # Removed in-memory dict
        
        # Send transaction request to wallet via WebSocket
        await self._send_transaction_request(request)
        
        logger.info(f"Created transaction request {request_id} for session {session_id}")
        return request

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        db_session = self.db.query(DBWalletConnectSession).filter_by(id=session_id).first()
        if not db_session:
            return None
        return {
            "session_id": db_session.id,
            "user_id": db_session.user_id,
            "wallet_address": db_session.wallet_address,
            "chain_type": db_session.chain_type,
            "chain_id": db_session.chain_id,
            "status": db_session.status,
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "expires_at": db_session.expires_at.isoformat() if db_session.expires_at else None,
            "approved_at": db_session.approved_at.isoformat() if db_session.approved_at else None,
            "disconnected_at": db_session.disconnected_at.isoformat() if db_session.disconnected_at else None
        }

    async def get_transaction_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        # This method needs to be refactored to use the DB directly
        # For now, it will return None as the in-memory dict is removed
        return None

    async def disconnect_session(self, session_id: str) -> bool:
        db_session = self.db.query(DBWalletConnectSession).filter_by(id=session_id).first()
        if not db_session:
            return False
        db_session.status = SessionStatus.DISCONNECTED.value
        db_session.disconnected_at = datetime.utcnow()
        self.db.commit()
        await self._close_websocket_connection(session_id)
        # Audit log
        logger.info(f"[AUDIT] WalletConnect session disconnected: session_id={session_id}")
        return True

    def _create_walletconnect_uri(self, session: DBWalletConnectSession) -> str:
        # WalletConnect v2 URI format
        # wc:{topic}@{version}?relay-protocol={relay_protocol}&symKey={sym_key}
        return (
            f"wc:{session.topic}@{session.version}"
            f"?relay-protocol={session.relay_protocol}"
            f"&symKey={session.sym_key}"
        )

    async def _start_websocket_connection(self, session_id: str):
        """Start WebSocket connection for real-time events"""
        import websockets
        db_session = self.db.query(DBWalletConnectSession).filter_by(id=session_id).first()
        if not db_session:
            return
        try:
            websocket_url = f"wss://{self.relay_url}/wc/{db_session.topic}"
            self.websocket = await websockets.connect(websocket_url)
            self.websocket_task = asyncio.create_task(
                self._handle_websocket_events(session_id)
            )
            logger.info(f"Started WebSocket connection for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to start WebSocket connection for session {session_id}: {e}")
            raise WalletConnectError(
                error_code=self.error_codes["WEBSOCKET_ERROR"],
                message=f"Failed to establish WebSocket connection: {str(e)}"
            )

    async def _handle_websocket_events(self, session_id: str):
        """Handle WebSocket events from wallet"""
        if not self.websocket:
            return
        try:
            async for message in self.websocket:
                data = pyjson.loads(message)
                if data.get("method") == "wc_sessionRequest":
                    await self._handle_session_request(session_id, data)
                elif data.get("method") == "wc_sessionEvent":
                    await self._handle_session_event(session_id, data)
                elif data.get("method") == "wc_sessionDelete":
                    await self._handle_session_delete(session_id, data)
                elif data.get("method") == "wc_sessionPayload":
                    await self._handle_session_payload(session_id, data)
        except Exception as e:
            logger.error(f"Error handling WebSocket events for session {session_id}: {e}")

    async def _handle_session_request(self, session_id: str, data: Dict[str, Any]):
        """Handle session approval/rejection"""
        db_session = self.db.query(DBWalletConnectSession).filter_by(id=session_id).first()
        if not db_session:
            return
        if data.get("result", {}).get("approved"):
            db_session.status = SessionStatus.APPROVED.value
            db_session.approved_at = datetime.utcnow()
            db_session.wallet_address = data.get("result", {}).get("accounts", [""])[0]
            self.db.commit()
            logger.info(f"Session {session_id} approved by wallet")
        else:
            db_session.status = SessionStatus.REJECTED.value
            self.db.commit()
            logger.info(f"Session {session_id} rejected by wallet")

    async def _handle_session_event(self, session_id: str, data: Dict[str, Any]):
        logger.info(f"Session event for {session_id}: {data.get('name')}")

    async def _handle_session_delete(self, session_id: str, data: Dict[str, Any]):
        await self.disconnect_session(session_id)

    async def _handle_session_payload(self, session_id: str, data: Dict[str, Any]):
        request_id = data.get("id")
        # This method needs to be refactored to use the DB directly
        # For now, it will not update the transaction request status
        if request_id:
            # request = self.transaction_requests[request_id] # Removed in-memory dict
            # if data.get("result"):
            #     request.signed_transaction = data.get("result", {}).get("signedTransaction")
            #     request.transaction_hash = data.get("result", {}).get("hash")
            #     request.status = "signed"
            #     logger.info(f"Transaction {request_id} signed by wallet")
            # else:
            #     request.status = "rejected"
            #     logger.info(f"Transaction {request_id} rejected by wallet")
            pass # Placeholder for transaction request update

    async def _close_websocket_connection(self, session_id: str):
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
        if not self.websocket:
            return
        try:
            db_session = self.db.query(DBWalletConnectSession).filter_by(id=request.session_id).first()
            if not db_session:
                raise WalletConnectError(
                    error_code=self.error_codes["SESSION_EXPIRED"],
                    message="Session not found for transaction request"
                )

            transaction_data = {
                "id": request.id,
                "jsonrpc": "2.0",
                "method": "eth_sendTransaction",
                "params": [{
                    "from": db_session.wallet_address,
                    "to": request.to_address,
                    "value": request.amount,
                    "gas": request.gas_estimate.get("gas_limit") if request.gas_estimate else None,
                    "gasPrice": request.gas_estimate.get("gas_price") if request.gas_estimate else None
                }]
            }
            await self.websocket.send(pyjson.dumps(transaction_data))
            logger.info(f"Sent transaction request {request.id} to wallet")
        except Exception as e:
            logger.error(f"Failed to send transaction request {request.id}: {e}")
            raise WalletConnectError(
                error_code=self.error_codes["TRANSACTION_ERROR"],
                message=f"Failed to send transaction request: {str(e)}"
            )

    async def cleanup_expired_sessions(self):
        now = datetime.utcnow()
        expired_sessions = self.db.query(DBWalletConnectSession).filter(DBWalletConnectSession.expires_at < now, DBWalletConnectSession.status != SessionStatus.EXPIRED.value).all()
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED.value
            await self._close_websocket_connection(session.id)
            logger.info(f"[AUDIT] WalletConnect session expired: session_id={session.id}")
        self.db.commit()

    async def check_transaction_confirmation(self, tx_hash: str, chain_type: str) -> bool:
        """Check if a transaction is confirmed on the blockchain"""
        if chain_type == "solana":
            return await self._check_solana_transaction(tx_hash)
        elif chain_type == "evm":
            return await self._check_evm_transaction(tx_hash)
        return False

    async def _check_solana_transaction(self, tx_hash: str) -> bool:
        """Check Solana transaction confirmation"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignatureStatuses",
            "params": [[tx_hash], {"searchTransactionHistory": True}]
        }
        try:
            resp = requests.post(SOLANA_RPC_URL, json=payload, timeout=10)
            resp.raise_for_status()
            result = resp.json().get("result", {}).get("value", [None])[0]
            if result:
                # Check if transaction is confirmed (confirmationStatus: "confirmed" or "finalized")
                confirmation_status = result.get("confirmationStatus")
                return confirmation_status in ["confirmed", "finalized"]
        except Exception as e:
            logger.error(f"Error checking Solana transaction {tx_hash}: {e}")
        return False

    async def _check_evm_transaction(self, tx_hash: str) -> bool:
        """Check EVM transaction confirmation"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash]
        }
        try:
            resp = requests.post(ETH_RPC_URL, json=payload, timeout=10)
            resp.raise_for_status()
            result = resp.json().get("result")
            if result:
                # Check if transaction is confirmed (blockNumber exists and status is 1)
                block_number = result.get("blockNumber")
                status = result.get("status")
                return block_number is not None and status == "0x1"
        except Exception as e:
            logger.error(f"Error checking EVM transaction {tx_hash}: {e}")
        return False

    async def update_transaction_status(self, db: DBSession, transaction_id: str) -> bool:
        """Update transaction status in database based on blockchain confirmation"""
        from clean_backend.models import Transaction
        
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction or not transaction.tx_hash:
            return False
        
        try:
            confirmed = await self.check_transaction_confirmation(transaction.tx_hash, transaction.chain_type)
            if confirmed and transaction.status == "pending":
                transaction.status = "confirmed"
                transaction.confirmed_at = datetime.utcnow()
                db.commit()
                logger.info(f"Transaction {transaction_id} confirmed on blockchain")
                return True
            elif not confirmed and transaction.status == "pending":
                # Check if transaction has been pending too long (e.g., 1 hour)
                time_diff = datetime.utcnow() - transaction.created_at
                if time_diff.total_seconds() > 3600:  # 1 hour
                    transaction.status = "failed"
                    db.commit()
                    logger.warning(f"Transaction {transaction_id} marked as failed due to timeout")
                    return True
        except Exception as e:
            logger.error(f"Error updating transaction status for {transaction_id}: {e}")
        
        return False

    async def create_compliance_report(self, db: DBSession, report_type: str, details: str, 
                                     transaction_id: str = None, user_id: str = None) -> None:
        """Create a compliance report for suspicious activity"""
        from clean_backend.models import ComplianceReport
        
        report = ComplianceReport(
            transaction_id=transaction_id,
            user_id=user_id,
            report_type=report_type,
            details=details,
            reviewed=False
        )
        
        db.add(report)
        db.commit()
        logger.info(f"Created compliance report {report.id} for {report_type}")

    async def assess_transaction_risk(self, from_wallet: str, to_wallet: str, amount: float, 
                                    currency: str, chain_type: str, db: DBSession) -> dict:
        """Assess transaction risk and return risk score and flags"""
        risk_score = 0.0
        flags = []
        
        # Check if destination is blacklisted
        blacklisted = db.query(BlacklistedAddress).filter_by(
            address=to_wallet, 
            chain_type=chain_type, 
            active=True
        ).first()
        
        if blacklisted:
            risk_score += 100.0
            flags.append("destination_blacklisted")
        
        # Check for high-value transactions (SAR threshold)
        if amount > 10000:  # $10k threshold
            risk_score += 50.0
            flags.append("high_value")
        
        # Check for frequent transactions (CTR threshold)
        recent_transactions = db.query(Transaction).filter(
            Transaction.from_wallet == from_wallet,
            Transaction.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count()
        
        if recent_transactions > 10:
            risk_score += 30.0
            flags.append("high_frequency")
        
        # Check for new wallet (first transaction)
        wallet_transactions = db.query(Transaction).filter(
            Transaction.from_wallet == from_wallet
        ).count()
        
        if wallet_transactions == 0:
            risk_score += 20.0
            flags.append("new_wallet")
        
        return {
            "risk_score": min(risk_score, 100.0),
            "flags": flags,
            "flagged": risk_score >= 50.0
        } 