"""
Tests for the security module
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import hashlib
import json

from core.security import (
    SecurityContext, 
    SecurityService, 
    BridgeTransferRequest,
    authenticate_user,
    authorize_action,
    calculate_risk_score,
    detect_fraud,
    generate_jwt_token,
    verify_jwt_token,
    hash_password,
    verify_password,
    generate_device_fingerprint,
    validate_transfer_request,
    rate_limit_check,
    audit_log
)

class TestSecurityContext:
    """Test SecurityContext class"""
    
    def test_security_context_creation(self):
        """Test creating a security context"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read", "write"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        assert context.user_id == "test_user"
        assert context.ip_address == "192.168.1.1"
        assert context.risk_score == 0.1
        assert "read" in context.permissions
        assert "write" in context.permissions
    
    def test_security_context_to_dict(self):
        """Test converting security context to dictionary"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        context_dict = context.to_dict()
        assert context_dict["user_id"] == "test_user"
        assert context_dict["ip_address"] == "192.168.1.1"
        assert context_dict["risk_score"] == 0.1

class TestBridgeTransferRequest:
    """Test BridgeTransferRequest class"""
    
    def test_transfer_request_creation(self):
        """Test creating a transfer request"""
        request = BridgeTransferRequest(
            amount="100.00",
            source_network="ethereum",
            source_address="0x1234567890abcdef",
            destination_network="polygon",
            destination_address="0xfedcba0987654321",
            currency="usdc",
            urgency="low",
            metadata={"user_id": "test_user"}
        )
        
        assert request.amount == "100.00"
        assert request.source_network == "ethereum"
        assert request.destination_network == "polygon"
        assert request.currency == "usdc"
        assert request.urgency == "low"
    
    def test_transfer_request_validation(self):
        """Test transfer request validation"""
        # Valid request
        request = BridgeTransferRequest(
            amount="100.00",
            source_network="ethereum",
            source_address="0x1234567890abcdef",
            destination_network="polygon",
            destination_address="0xfedcba0987654321",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        assert request.is_valid() is True
        
        # Invalid amount
        request.amount = "invalid"
        assert request.is_valid() is False
        
        # Invalid network
        request.amount = "100.00"
        request.source_network = "invalid_network"
        assert request.is_valid() is False

class TestAuthentication:
    """Test authentication functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
        assert hashed.startswith("$2b$")
    
    def test_verify_password(self):
        """Test password verification"""
        password = "test_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_generate_jwt_token(self):
        """Test JWT token generation"""
        payload = {"user_id": "test_user", "permissions": ["read"]}
        token = generate_jwt_token(payload)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = verify_jwt_token(token)
        assert decoded["user_id"] == "test_user"
        assert "read" in decoded["permissions"]
    
    def test_verify_jwt_token(self):
        """Test JWT token verification"""
        payload = {"user_id": "test_user"}
        token = generate_jwt_token(payload)
        
        # Valid token
        decoded = verify_jwt_token(token)
        assert decoded["user_id"] == "test_user"
        
        # Invalid token
        with pytest.raises(jwt.InvalidTokenError):
            verify_jwt_token("invalid_token")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Mock user data
        user_data = {
            "id": "test_user",
            "email": "test@example.com",
            "password_hash": hash_password("test_password"),
            "is_active": True,
            "permissions": ["read", "write"]
        }
        
        with patch('core.security.get_user_by_email', return_value=user_data):
            result = await authenticate_user("test@example.com", "test_password")
            
            assert result["success"] is True
            assert result["user_id"] == "test_user"
            assert "token" in result
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        with patch('core.security.get_user_by_email', return_value=None):
            result = await authenticate_user("test@example.com", "wrong_password")
            
            assert result["success"] is False
            assert "Invalid credentials" in result["error"]

class TestAuthorization:
    """Test authorization functions"""
    
    @pytest.mark.asyncio
    async def test_authorize_action_success(self):
        """Test successful action authorization"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read", "write", "transfer"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        result = await authorize_action(context, "transfer", {"amount": "100.00"})
        assert result["authorized"] is True
    
    @pytest.mark.asyncio
    async def test_authorize_action_insufficient_permissions(self):
        """Test authorization with insufficient permissions"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read"],  # No transfer permission
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        result = await authorize_action(context, "transfer", {"amount": "100.00"})
        assert result["authorized"] is False
        assert "Insufficient permissions" in result["reason"]

class TestRiskScoring:
    """Test risk scoring functions"""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        transfer_data = {
            "amount": "1000.00",
            "source_network": "ethereum",
            "destination_network": "polygon",
            "urgency": "high"
        }
        
        risk_score = calculate_risk_score(context, transfer_data)
        
        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0
    
    def test_detect_fraud(self):
        """Test fraud detection"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.8,  # High risk
            fraud_indicators=[],
            permissions=["read"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        transfer_data = {
            "amount": "50000.00",  # Large amount
            "source_network": "ethereum",
            "destination_network": "polygon",
            "urgency": "high"
        }
        
        fraud_result = detect_fraud(context, transfer_data)
        
        assert isinstance(fraud_result, dict)
        assert "is_fraudulent" in fraud_result
        assert "indicators" in fraud_result
        assert "risk_level" in fraud_result

class TestValidation:
    """Test validation functions"""
    
    def test_validate_transfer_request(self):
        """Test transfer request validation"""
        request = BridgeTransferRequest(
            amount="100.00",
            source_network="ethereum",
            source_address="0x1234567890abcdef",
            destination_network="polygon",
            destination_address="0xfedcba0987654321",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        result = validate_transfer_request(request)
        assert result["valid"] is True
    
    def test_validate_transfer_request_invalid_amount(self):
        """Test transfer request validation with invalid amount"""
        request = BridgeTransferRequest(
            amount="invalid_amount",
            source_network="ethereum",
            source_address="0x1234567890abcdef",
            destination_network="polygon",
            destination_address="0xfedcba0987654321",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        result = validate_transfer_request(request)
        assert result["valid"] is False
        assert "amount" in result["errors"]
    
    def test_rate_limit_check(self):
        """Test rate limiting"""
        context = SecurityContext(
            user_id="test_user",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session",
            wallet_address="0x1234567890abcdef",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        result = rate_limit_check(context, "transfer")
        assert isinstance(result, dict)
        assert "allowed" in result
        assert "remaining" in result

class TestSecurityService:
    """Test SecurityService class"""
    
    @pytest.mark.asyncio
    async def test_security_service_creation(self):
        """Test creating security service"""
        service = SecurityService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_security_service_audit_log(self):
        """Test audit logging"""
        service = SecurityService()
        
        log_entry = await service.audit_log(
            user_id="test_user",
            action="transfer",
            details={"amount": "100.00"},
            ip_address="192.168.1.1",
            success=True
        )
        
        assert log_entry["user_id"] == "test_user"
        assert log_entry["action"] == "transfer"
        assert log_entry["success"] is True
    
    @pytest.mark.asyncio
    async def test_security_service_validate_session(self):
        """Test session validation"""
        service = SecurityService()
        
        # Mock session data
        session_data = {
            "user_id": "test_user",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "is_active": True
        }
        
        with patch('core.security.get_session', return_value=session_data):
            result = await service.validate_session("test_session_id")
            assert result["valid"] is True
    
    @pytest.mark.asyncio
    async def test_security_service_validate_session_expired(self):
        """Test expired session validation"""
        service = SecurityService()
        
        # Mock expired session data
        session_data = {
            "user_id": "test_user",
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "is_active": True
        }
        
        with patch('core.security.get_session', return_value=session_data):
            result = await service.validate_session("test_session_id")
            assert result["valid"] is False
            assert "expired" in result["reason"]

class TestDeviceFingerprinting:
    """Test device fingerprinting"""
    
    def test_generate_device_fingerprint(self):
        """Test device fingerprint generation"""
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ip_address = "192.168.1.1"
        
        fingerprint = generate_device_fingerprint(user_agent, ip_address)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) > 0
        
        # Should be consistent for same inputs
        fingerprint2 = generate_device_fingerprint(user_agent, ip_address)
        assert fingerprint == fingerprint2
        
        # Should be different for different inputs
        fingerprint3 = generate_device_fingerprint(user_agent, "192.168.1.2")
        assert fingerprint != fingerprint3 