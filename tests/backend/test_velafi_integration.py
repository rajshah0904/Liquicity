"""Integration tests for VelaFi LATAM on/off-ramp flow."""
import hashlib
import hmac
import json
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from clean_backend.main import app
from clean_backend.models import User, UserProfile
from clean_backend.models.velafi_order import VelafiDirection, VelafiOrder, VelafiStatus
from clean_backend.services.velafi_service import VelaFiService

# Test data
TEST_USER_ID = "test_user_id"
TEST_USER_EMAIL = "test@example.com"
TEST_CUSTOMER_ID = "test_customer_id"
TEST_ORDER_ID = "test_order_id"
TEST_WEBHOOK_SECRET = "test_webhook_secret"

@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def mock_auth(monkeypatch):
    """Mock authentication to return test user."""
    def mock_get_current_user():
        return {"sub": TEST_USER_ID, "email": TEST_USER_EMAIL}
    monkeypatch.setattr(
        "clean_backend.auth.get_current_user",
        mock_get_current_user
    )

@pytest.fixture
def mock_velafi_api(monkeypatch):
    """Mock VelaFi API responses."""
    class MockVelaFiAPI:
        def __init__(self):
            self.customer_id = TEST_CUSTOMER_ID
            self.order_id = TEST_ORDER_ID
        
        async def create_customer(self, *args, **kwargs):
            return {
                "customer_id": self.customer_id,
                "status": "pending",
                "requirements": {}
            }
        
        async def get_quote(self, *args, **kwargs):
            return {
                "fiat_amount": "1000.00",
                "fiat_currency": "BRL",
                "usdc_amount": "200.00",
                "fx_rate": "5.00",
                "fee_usd": "2.00"
            }
        
        async def create_order(self, *args, **kwargs):
            return {
                "order_id": self.order_id,
                "status": "pending",
                "rail": {
                    "type": "pix",
                    "key": "test-pix-key"
                }
            }
        
        async def get_order(self, order_id):
            return {
                "order_id": order_id,
                "status": "completed",
                "tx_hash": "0x1234..."
            }
    
    monkeypatch.setattr(
        "clean_backend.services.velafi_service.VelaFiService",
        lambda: MockVelaFiAPI()
    )

@pytest.fixture
def test_user(db: Session):
    """Create test user in database."""
    user = User(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        profile=UserProfile(
            country="BR",
            velafi_customer_id=TEST_CUSTOMER_ID,
            latam_kyc_status="approved"
        )
    )
    db.add(user)
    db.commit()
    return user

def test_create_latam_deposit(client, mock_auth, mock_velafi_api, test_user, db: Session):
    """Test complete LATAM deposit flow."""
    # Get quote
    quote_response = client.post(
        "/velafi/quote",
        json={
            "fiat_amount": 1000.00,
            "fiat_currency": "BRL",
            "direction": "BUY",
            "country_code": "BR"
        }
    )
    assert quote_response.status_code == 200
    quote_data = quote_response.json()
    assert quote_data["fiat_amount"] == "1000.00"
    assert quote_data["fiat_currency"] == "BRL"
    assert quote_data["usdc_amount"] == "200.00"
    
    # Create order
    order_response = client.post(
        "/velafi/orders",
        json={
            "direction": "BUY",
            "fiat_amount": 1000.00,
            "fiat_currency": "BRL",
            "wallet_address": "0x1234...",
            "country_code": "BR"
        }
    )
    assert order_response.status_code == 200
    order_data = order_response.json()
    assert order_data["order_id"] == TEST_ORDER_ID
    assert order_data["status"] == "pending"
    assert order_data["rail"]["type"] == "pix"
    
    # Verify order in database
    order = db.query(VelafiOrder).filter_by(order_id=TEST_ORDER_ID).first()
    assert order is not None
    assert order.user_id == TEST_USER_ID
    assert order.direction == VelafiDirection.BUY
    assert order.fiat_amount == Decimal("1000.00")
    assert order.fiat_currency == "BRL"
    assert order.status == VelafiStatus.PENDING
    
    # Simulate webhook for order completion
    webhook_data = {
        "event_type": "order.completed",
        "data": {
            "order_id": TEST_ORDER_ID,
            "status": "completed",
            "tx_hash": "0x1234..."
        }
    }
    webhook_body = json.dumps(webhook_data).encode()
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signature = hmac.new(
        TEST_WEBHOOK_SECRET.encode(),
        f"{timestamp}.{webhook_body.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    webhook_response = client.post(
        "/webhooks/velafi",
        data=webhook_body,
        headers={
            "X-VelaFi-Signature": signature,
            "X-VelaFi-Timestamp": timestamp
        }
    )
    assert webhook_response.status_code == 200
    
    # Verify order status updated
    db.refresh(order)
    assert order.status == VelafiStatus.COMPLETED
    assert order.tx_hash == "0x1234..."

def test_create_latam_withdrawal(client, mock_auth, mock_velafi_api, test_user, db: Session):
    """Test complete LATAM withdrawal flow."""
    # Get quote
    quote_response = client.post(
        "/velafi/quote",
        json={
            "fiat_amount": 1000.00,
            "fiat_currency": "BRL",
            "direction": "SELL",
            "country_code": "BR"
        }
    )
    assert quote_response.status_code == 200
    quote_data = quote_response.json()
    assert quote_data["fiat_amount"] == "1000.00"
    assert quote_data["fiat_currency"] == "BRL"
    assert quote_data["usdc_amount"] == "200.00"
    
    # Create order
    order_response = client.post(
        "/velafi/orders",
        json={
            "direction": "SELL",
            "fiat_amount": 1000.00,
            "fiat_currency": "BRL",
            "wallet_address": "0x1234...",
            "country_code": "BR",
            "bank_details": {
                "bank_code": "341",
                "branch": "1234",
                "account": "123456",
                "account_type": "checking",
                "cpf": "123.456.789-00"
            }
        }
    )
    assert order_response.status_code == 200
    order_data = order_response.json()
    assert order_data["order_id"] == TEST_ORDER_ID
    assert order_data["status"] == "pending"
    
    # Verify order in database
    order = db.query(VelafiOrder).filter_by(order_id=TEST_ORDER_ID).first()
    assert order is not None
    assert order.user_id == TEST_USER_ID
    assert order.direction == VelafiDirection.SELL
    assert order.fiat_amount == Decimal("1000.00")
    assert order.fiat_currency == "BRL"
    assert order.status == VelafiStatus.PENDING
    
    # Simulate webhook for order completion
    webhook_data = {
        "event_type": "order.completed",
        "data": {
            "order_id": TEST_ORDER_ID,
            "status": "completed",
            "tx_hash": "0x1234..."
        }
    }
    webhook_body = json.dumps(webhook_data).encode()
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signature = hmac.new(
        TEST_WEBHOOK_SECRET.encode(),
        f"{timestamp}.{webhook_body.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    webhook_response = client.post(
        "/webhooks/velafi",
        data=webhook_body,
        headers={
            "X-VelaFi-Signature": signature,
            "X-VelaFi-Timestamp": timestamp
        }
    )
    assert webhook_response.status_code == 200
    
    # Verify order status updated
    db.refresh(order)
    assert order.status == VelafiStatus.COMPLETED
    assert order.tx_hash == "0x1234..."

def test_latam_kyc_flow(client, mock_auth, mock_velafi_api, test_user, db: Session):
    """Test LATAM KYC flow."""
    # Create customer
    customer_response = client.post(
        "/velafi/customers",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": TEST_USER_EMAIL,
            "country_code": "BR",
            "phone": "+5511999999999"
        }
    )
    assert customer_response.status_code == 200
    customer_data = customer_response.json()
    assert customer_data["customer_id"] == TEST_CUSTOMER_ID
    assert customer_data["status"] == "pending"
    
    # Verify user profile updated
    db.refresh(test_user)
    assert test_user.profile.velafi_customer_id == TEST_CUSTOMER_ID
    assert test_user.profile.latam_kyc_status == "pending"
    
    # Simulate webhook for KYC approval
    webhook_data = {
        "event_type": "kyc.status.changed",
        "data": {
            "customer_id": TEST_CUSTOMER_ID,
            "status": "approved"
        }
    }
    webhook_body = json.dumps(webhook_data).encode()
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signature = hmac.new(
        TEST_WEBHOOK_SECRET.encode(),
        f"{timestamp}.{webhook_body.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    webhook_response = client.post(
        "/webhooks/velafi",
        data=webhook_body,
        headers={
            "X-VelaFi-Signature": signature,
            "X-VelaFi-Timestamp": timestamp
        }
    )
    assert webhook_response.status_code == 200
    
    # Verify KYC status updated
    db.refresh(test_user)
    assert test_user.profile.latam_kyc_status == "approved"