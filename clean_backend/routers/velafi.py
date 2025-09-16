"""VelaFi API routers for LATAM fiat on/off-ramp integration."""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    Response,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, constr
from sqlalchemy.orm import Session

from clean_backend.auth import get_current_user
from clean_backend.database import get_db
from clean_backend.models import User, UserProfile
from clean_backend.models.velafi_order import VelafiDirection, VelafiOrder, VelafiStatus
from clean_backend.services.velafi_service import VelaFiError, VelaFiService
from clean_backend.utils.idempotency import idempotent_route
from clean_backend.utils.ratelimit import limiter
from clean_backend.bridge import BridgeClient

logger = logging.getLogger(__name__)

# Initialize routers
router = APIRouter(prefix="/velafi", tags=["velafi"])
webhook_router = APIRouter(tags=["velafi-webhooks"])

# Initialize service
_service = VelaFiService()

# ---------------------------- Schemas ----------------------------

class CustomerCreateRequest(BaseModel):
    """Request schema for creating a VelaFi customer."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    country_code: str = Field(..., min_length=2, max_length=2)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    metadata: Optional[Dict[str, Any]] = None

class CustomerResponse(BaseModel):
    """Response schema for VelaFi customer operations."""
    customer_id: str
    status: str
    requirements: Dict[str, Any]

class DocumentUploadRequest(BaseModel):
    """Request schema for uploading KYC documents."""
    document_type: str = Field(..., pattern='^(passport|id_card|drivers_license)$')
    file_name: str = Field(..., min_length=1, max_length=255)

class QuoteRequest(BaseModel):
    """Request schema for getting a fiat ↔ USDC quote."""
    fiat_amount: Decimal = Field(..., gt=0, description="Amount in fiat currency")
    fiat_currency: str = Field(..., min_length=3, max_length=3)
    direction: VelafiDirection
    country_code: str = Field(..., min_length=2, max_length=2)

class OrderCreateRequest(BaseModel):
    """Request schema for creating a fiat ↔ USDC order."""
    direction: VelafiDirection
    fiat_amount: Decimal = Field(..., gt=0)
    fiat_currency: str = Field(..., min_length=3, max_length=3)
    wallet_address: str = Field(..., min_length=42, max_length=42)
    country_code: str = Field(..., min_length=2, max_length=2)
    metadata: Optional[Dict[str, Any]] = None

class OrderResponse(BaseModel):
    """Response schema for order operations."""
    order_id: str
    status: str
    fiat_amount: Decimal
    fiat_currency: str
    usdc_amount: Optional[Decimal]
    fx_rate: Optional[Decimal]
    fee_usd: Optional[Decimal]
    rail: Optional[str]
    rail_instructions: Optional[Dict[str, Any]] = None
    tx_hash: Optional[str]
    created_at: str

class WebhookEvent(BaseModel):
    """Schema for incoming webhook events."""
    event_type: str
    data: Dict[str, Any]

# ---------------------------- Routes ----------------------------

async def _order_key_builder(req):
    body = await req.json()
    return (
        f"order_{body.get('idempotency_key') or body.get('client_intent_id') or body.get('direction')}" \
        f"_{body.get('fiat_amount')}"
    )


@router.post("/customers", response_model=CustomerResponse)
async def create_customer(
    request: CustomerCreateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new VelaFi customer for KYC."""
    try:
        response = await _service.create_customer(
            user_id=current_user,
            email=request.email,
            country_code=request.country_code,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            metadata=request.metadata
        )
        return response
    except VelaFiError as e:
        logger.error(f"VelaFi customer creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/customers/{customer_id}/documents")
async def upload_document(
    customer_id: str,
    document_type: str = Form(...),
    file: bytes = File(...),
    file_name: str = Form(...),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Upload KYC verification documents for a customer."""
    try:
        response = await _service.upload_documents(
            customer_id=customer_id,
            document_type=document_type,
            file_data=file,
            file_name=file_name
        )
        return response
    except VelaFiError as e:
        logger.error(f"VelaFi document upload failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/quote", response_model=Dict[str, Any])
@limiter.limit("5/minute")
async def get_quote(
    request: QuoteRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a quote for a fiat ↔ USDC conversion."""
    try:
        return await _service.get_quote(
            fiat_amount=request.fiat_amount,
            fiat_currency=request.fiat_currency,
            direction=request.direction,
            country_code=request.country_code
        )
    except VelaFiError as e:
        logger.error(f"VelaFi quote failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def _order_key_builder(req):
    body = await req.json()
    return f"order_{body.get('idempotency_key') or body.get('client_intent_id') or body.get('direction')}_{body.get('fiat_amount')}"


@router.post("/orders", response_model=OrderResponse)
@limiter.limit("5/minute")
@idempotent_route(_order_key_builder)
async def create_order(
    request: OrderCreateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new fiat ↔ USDC conversion order."""
    try:
        # Get customer ID from user profile
        user = await db.query(User).filter(User.id == current_user).first()
        if not user or not user.profile.velafi_customer_id:
            raise HTTPException(status_code=400, detail="Complete KYC first")

        if request.direction == VelafiDirection.SELL:
            bridge = BridgeClient()

            # 1. Fetch current USDC balance
            try:
                balances_resp = bridge.get_wallet_balances(
                    user.profile.bridge_customer_id,
                    user.profile.bridge_wallet_id,
                )
                usdc_available = Decimal(
                    next(
                        (
                            b["amount"]
                            for b in balances_resp["balances"]
                            if b["currency"].upper() == "USDC"
                        ),
                        "0",
                    )
                )
            except Exception as exc:
                logger.error("Bridge balance lookup failed: %s", exc)
                raise HTTPException(status_code=502, detail="Bridge balance lookup failed")

            # 2. Ensure user has enough balance
            if usdc_available < request.fiat_amount:
                raise HTTPException(status_code=400, detail="Insufficient USDC balance")

            # 3. Debit immediately (places a hold)
            try:
                debit_payload = {
                    "wallet_id": user.profile.bridge_wallet_id,
                    "amount": str(request.fiat_amount),
                    "currency": "usdc",
                    "kind": "debit",
                    "memo": f"VelaFi withdraw {request.fiat_currency}",
                }
                bridge.create_transfer_sync(debit_payload)
            except Exception as exc:
                logger.error("Bridge debit failed: %s", exc)
                raise HTTPException(status_code=502, detail="Bridge debit failed")

        order = await _service.create_order(
            user_id=current_user,
            customer_id=user.profile.velafi_customer_id,
            direction=request.direction,
            fiat_amount=request.fiat_amount,
            fiat_currency=request.fiat_currency,
            wallet_address=request.wallet_address,
            country_code=request.country_code,
            metadata=request.metadata
        )
        
        return {
            "order_id": order.order_id,
            "status": order.status.value,
            "fiat_amount": order.fiat_amount,
            "fiat_currency": order.fiat_currency,
            "usdc_amount": order.usdc_amount,
            "fx_rate": order.fx_rate,
            "fee_usd": order.fee_usd,
            "rail": order.rail,
            "rail_instructions": getattr(order, "rail_instructions", None),
            "tx_hash": order.tx_hash,
            "created_at": order.created_at.isoformat()
        }
    except VelaFiError as e:
        logger.error(f"VelaFi order creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the current status of an order."""
    # First check local DB
    order = await db.query(VelafiOrder).filter(
        VelafiOrder.order_id == order_id,
        VelafiOrder.user_id == current_user
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # If order is pending/processing, get latest status from VelaFi
    if order.status in [VelafiStatus.PENDING, VelafiStatus.PROCESSING]:
        try:
            status = await _service.get_order(order_id)
            if status["status"] != order.status.value:
                order.status = VelafiStatus(status["status"])
                if status.get("tx_hash"):
                    order.tx_hash = status["tx_hash"]
                await db.commit()
        except VelaFiError as e:
            logger.error(f"VelaFi order status check failed: {e}")
            # Don't fail the request, just return last known status
    
    return {
        "order_id": order.order_id,
        "status": order.status.value,
        "fiat_amount": order.fiat_amount,
        "fiat_currency": order.fiat_currency,
        "usdc_amount": order.usdc_amount,
        "fx_rate": order.fx_rate,
        "fee_usd": order.fee_usd,
        "rail": order.rail,
        "tx_hash": order.tx_hash,
        "created_at": order.created_at.isoformat()
    }

# ---------------------------- Webhooks ----------------------------

async def _webhook_key_builder(req):
    body = await req.body()
    return f"webhook_{hash(body)}"


@webhook_router.post("/webhooks/velafi")
@idempotent_route(_webhook_key_builder)
async def velafi_webhook(
    request: Request,
    response: Response,
    x_velafi_signature: str = Header(None),
    x_velafi_timestamp: str = Header(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Handle VelaFi webhook events."""
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify webhook signature
    if not _service.verify_webhook_signature(x_velafi_signature, x_velafi_timestamp, body):
        logger.error("Invalid webhook signature")
        return Response(status_code=401)
    
    # Parse event
    try:
        event = WebhookEvent.parse_raw(body)
    except Exception as e:
        logger.error(f"Failed to parse webhook: {e}")
        return Response(status_code=400)
    
    # Handle different event types
    try:
        if event.event_type == "kyc.status.changed":
            # Update user profile KYC status
            customer_id = event.data["customer_id"]
            status = event.data["status"]
            
            user = await db.query(User).join(UserProfile).filter(
                UserProfile.velafi_customer_id == customer_id
            ).first()
            
            if user:
                user.profile.latam_kyc_status = status
                await db.commit()
                
        elif event.event_type == "order.completed":
            # Update order status and trigger balance update
            order_id = event.data["order_id"]
            tx_hash = event.data.get("tx_hash")
            
            order = await db.query(VelafiOrder).filter(
                VelafiOrder.order_id == order_id
            ).first()
            
            if order:
                order.status = VelafiStatus.COMPLETED
                order.tx_hash = tx_hash
                await db.commit()
                
                # TODO: Trigger balance update via event bus
                
        elif event.event_type == "order.failed":
            # Update order status
            order_id = event.data["order_id"]
            reason = event.data.get("reason")
            
            order = await db.query(VelafiOrder).filter(
                VelafiOrder.order_id == order_id
            ).first()
            
            if order:
                order.status = VelafiStatus.FAILED
                await db.commit()
                
                logger.error(f"Order {order_id} failed: {reason}")
        
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return Response(status_code=500)