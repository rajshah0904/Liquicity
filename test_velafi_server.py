#!/usr/bin/env python3
"""
Simple test server for VelaFi KYC system only
Bypasses all other dependencies to focus on VelaFi testing
"""

import asyncio
import json
import os
import sys
import time

# Enable test mode for the security service so that extreme stress tests do
# not get blocked by rate-limiting or size restrictions.  This only affects
# the lightweight test server and has no impact on the production backend.
os.environ.setdefault("TEST_MODE", "true")
from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv

from clean_backend.services.security import security_service
from VelaFi.services.regional_kyc_service import RegionalKycService
from VelaFi.services.velafi_kyc_service import VelafiKycService
from VelaFi.velafi_client import VelafiClient

load_dotenv()

app = FastAPI(title="VelaFi KYC Test Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
velafi_client = VelafiClient()
velafi_kyc_service = VelafiKycService(velafi_client)
regional_kyc_service = RegionalKycService(velafi_client)

# Pydantic models
class CustomerCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    country: str
    phone: str = None
    address: str = None
    city: str = None
    state: str = None
    postal_code: str = None

class DocumentUploadRequest(BaseModel):
    document_type: str
    filename: str
    mime_type: str
    file_size: int

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "velafi-kyc-test"}

# Regional KYC endpoints
@app.get("/kyc/requirements/{country_code}")
async def get_kyc_requirements(country_code: str):
    """Get KYC requirements for a specific country."""
    try:
        requirements = regional_kyc_service.get_kyc_requirements(country_code)
        return {
            "success": True,
            "country_code": country_code,
            "requirements": requirements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kyc/system/{country_code}")
async def get_kyc_system(country_code: str):
    """Get the KYC system for a specific country."""
    try:
        kyc_system = regional_kyc_service.get_kyc_system_for_country(country_code)
        return {
            "success": True,
            "country_code": country_code,
            "kyc_system": kyc_system
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kyc/supported-countries")
async def get_supported_countries():
    """Get list of supported countries and their KYC systems."""
    try:
        countries = regional_kyc_service.get_supported_countries()
        return {
            "success": True,
            "countries": countries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# VelaFi KYC endpoints
@app.post("/velafi/kyc/customer")
async def create_customer(customer_data: CustomerCreateRequest, request: Request):
    """Create a VelaFi customer for KYC with security validation."""
    try:
        # Get client ID for rate limiting
        client_id = security_service.get_client_id(request)
        
        # Check rate limiting
        rate_limit_ok, rate_limit_info = security_service.check_rate_limit(client_id, "kyc")
        if not rate_limit_ok:
            security_service.log_security_event("RATE_LIMIT_EXCEEDED", rate_limit_info, client_id)
            raise HTTPException(status_code=429, detail=rate_limit_info)
        
        # Validate customer data
        customer_dict = customer_data.dict()
        is_valid, validation_errors = security_service.validate_customer_data(customer_dict)
        if not is_valid:
            security_service.log_security_event("VALIDATION_FAILURE", {"errors": validation_errors}, client_id)
            raise HTTPException(status_code=422, detail={"errors": validation_errors})
        
        # Simulate customer creation (without database)
        customer_dict["velafi_customer_id"] = f"velafi_cust_{hash(customer_data.email) % 1000000}"
        customer_dict["kyc_status"] = "pending"
        customer_dict["created_at"] = "2024-07-29T19:30:00Z"
        
        return {
            "success": True,
            "customer": customer_dict,
            "message": "Customer created successfully (simulated)"
        }
    except HTTPException:
        raise
    except Exception as e:
        security_service.log_security_event("SYSTEM_ERROR", {"error": str(e)}, client_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/velafi/kyc/customer")
async def get_customer():
    """Get customer details (simulated)."""
    try:
        # Return mock customer data
        customer = {
            "id": "test-customer-123",
            "velafi_customer_id": "velafi_cust_123456",
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "juan.perez@test.com",
            "country": "MX",
            "kyc_status": "pending",
            "created_at": "2024-07-29T19:30:00Z"
        }
        
        return {
            "success": True,
            "customer": customer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/velafi/kyc/documents")
async def upload_document(document_data: DocumentUploadRequest, request: Request):
    """Upload a document for KYC verification with security validation."""
    try:
        # Get client ID for rate limiting
        client_id = security_service.get_client_id(request)
        
        # Check rate limiting
        rate_limit_ok, rate_limit_info = security_service.check_rate_limit(client_id, "kyc")
        if not rate_limit_ok:
            security_service.log_security_event("RATE_LIMIT_EXCEEDED", rate_limit_info, client_id)
            raise HTTPException(status_code=429, detail=rate_limit_info)
        
        # Validate document data
        document_dict = document_data.dict()
        is_valid, validation_errors = security_service.validate_document_data(document_dict)
        if not is_valid:
            security_service.log_security_event("VALIDATION_FAILURE", {"errors": validation_errors}, client_id)
            raise HTTPException(status_code=422, detail={"errors": validation_errors})
        
        # Simulate document upload
        document = {
            "id": f"doc_{hash(document_data.filename) % 1000000}",
            "velafi_document_id": f"velafi_doc_{hash(document_data.filename) % 1000000}",
            "document_type": document_data.document_type,
            "filename": document_data.filename,
            "mime_type": document_data.mime_type,
            "file_size": document_data.file_size,
            "status": "uploaded",
            "uploaded_at": "2024-07-29T19:30:00Z"
        }
        
        return {
            "success": True,
            "document": document,
            "message": "Document uploaded successfully (simulated)"
        }
    except HTTPException:
        raise
    except Exception as e:
        security_service.log_security_event("SYSTEM_ERROR", {"error": str(e)}, client_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/velafi/kyc/approved")
async def check_kyc_approved():
    """Check if KYC is approved."""
    try:
        # Simulate KYC status check
        return {
            "success": True,
            "kyc_approved": False,
            "kyc_status": "pending",
            "message": "KYC is pending approval"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Security endpoints
@app.post("/security/risk-assessment")
async def assess_transaction_risk():
    """Assess transaction risk."""
    try:
        # Simulate risk assessment
        risk_assessment = {
            "risk_score": 0.3,
            "risk_factors": ["new_user", "medium_amount"],
            "recommended_action": "allow_transaction",
            "requires_manual_review": False,
            "fraud_probability": 0.1,
            "compliance_issues": []
        }
        
        return {
            "success": True,
            "assessment": risk_assessment,
            "message": "Risk assessment completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Risk assessment failed"
        }

@app.post("/security/audit-log")
async def log_security_event():
    """Log security event."""
    try:
        # Simulate audit logging
        audit_event = {
            "event_id": f"audit_{int(time.time())}",
            "event_type": "security_check",
            "user_id": "test-user-123",
            "timestamp": datetime.utcnow().isoformat(),
            "risk_score": 0.3,
            "action_taken": "transaction_allowed"
        }
        
        return {
            "success": True,
            "event": audit_event,
            "message": "Security event logged"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to log security event"
        }

@app.get("/security/compliance-status")
async def get_compliance_status():
    """Get compliance status."""
    try:
        compliance_status = {
            "kyc_verified": True,
            "aml_screened": True,
            "compliance_level": "full",
            "last_screening": "2024-07-29T08:00:00Z",
            "next_screening": "2024-10-29T08:00:00Z"
        }
        
        return {
            "success": True,
            "compliance": compliance_status,
            "message": "Compliance status retrieved"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get compliance status"
        }

# VelaFi API test endpoints
@app.get("/velafi/test/account")
async def test_velafi_account():
    """Test VelaFi API connection."""
    try:
        account = await velafi_client.get_account()
        return {
            "success": True,
            "account": account,
            "message": "VelaFi API connection successful"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "VelaFi API connection failed"
        }

@app.get("/velafi/test/countries")
async def test_velafi_countries():
    """Test VelaFi countries endpoint."""
    try:
        countries = await velafi_client.get_countries()
        return {
            "success": True,
            "countries_count": len(countries),
            "countries": list(countries)[:5] if countries else [],  # Return first 5 for brevity
            "message": "VelaFi countries retrieved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "VelaFi countries request failed"
        }

@app.post("/velafi/test/quote")
async def test_velafi_quote():
    """Test VelaFi quote generation."""
    try:
        quote = await velafi_client.get_quote(
            fiat_amount=100,
            fiat_currency="USD",
            country="MX"
        )
        return {
            "success": True,
            "quote": quote,
            "message": "VelaFi quote generated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "VelaFi quote generation failed"
        }

# ---------------------------------------------------------------------------
# In-memory stores for simulated payment methods & orders
# ---------------------------------------------------------------------------

PAYMENT_METHODS: dict[str, dict] = {}
ORDERS: dict[str, dict] = {}

# simple helpers

def _gen_id(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{len(PAYMENT_METHODS) + len(ORDERS)}"

# ---------------------------------------------------------------------------
# Payment-method endpoints (Phase-2)
# ---------------------------------------------------------------------------


class PaymentMethodRequest(BaseModel):
    plaid_token: str


@app.post("/velafi/payment_method", status_code=201)
async def create_payment_method(body: PaymentMethodRequest):
    """Simulate creation of a VelaFi payment method from a Plaid public token."""

    pm_id = _gen_id("pm")
    pm = {
        "id": pm_id,
        "fiat_rail": "ach",
        "country": "US",
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "plaid_token": body.plaid_token,
    }
    PAYMENT_METHODS[pm_id] = pm
    return pm


@app.get("/velafi/payment_method/{pm_id}")
async def get_payment_method(pm_id: str):
    pm = PAYMENT_METHODS.get(pm_id)
    if not pm:
        raise HTTPException(status_code=404, detail="payment method not found")
    return pm


@app.delete("/velafi/payment_method/{pm_id}", status_code=204)
async def delete_payment_method(pm_id: str):
    PAYMENT_METHODS.pop(pm_id, None)

# ---------------------------------------------------------------------------
# On-ramp order endpoints (Phase-3)
# ---------------------------------------------------------------------------


class OrderRequest(BaseModel):
    payment_method_id: str
    fiat_amount: float


@app.post("/velafi/order", status_code=201)
async def create_order(body: OrderRequest):
    if body.payment_method_id not in PAYMENT_METHODS:
        raise HTTPException(status_code=404, detail="payment method not found")

    order_id = _gen_id("ord")
    order = {
        "id": order_id,
        "status": "processing",
        "fiat_amount": str(body.fiat_amount),
        "fiat_currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
    }
    ORDERS[order_id] = order

    # simulate async settlement after 200 ms
    async def _settle():
        await asyncio.sleep(0.2)
        order["status"] = "completed"
        order["usdc_amount"] = str(round(body.fiat_amount / 1.01, 2))

    asyncio.create_task(_settle())

    return order


@app.get("/velafi/order/{order_id}")
async def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    return order

if __name__ == "__main__":
    import uvicorn
    print("�� Starting VelaFi KYC Test Server...")
    print("📡 Available endpoints:")
    print("  GET  /health")
    print("  GET  /kyc/requirements/{country_code}")
    print("  GET  /kyc/system/{country_code}")
    print("  GET  /kyc/supported-countries")
    print("  POST /velafi/kyc/customer")
    print("  GET  /velafi/kyc/customer")
    print("  POST /velafi/kyc/documents")
    print("  GET  /velafi/kyc/approved")
    print("  GET  /velafi/test/account")
    print("  GET  /velafi/test/countries")
    print("  POST /velafi/test/quote")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8002) 