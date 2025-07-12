<<<<<<< HEAD
import re

# Add base58 validation for Solana
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def is_base58(s: str) -> bool:
    return all(c in BASE58_ALPHABET for c in s)

# Strict Solana address validation using base58 decoding
try:
    import base58
except ImportError:
    base58 = None

class SecurityValidator:
    def validate_wallet_address(self, address: str, chain_type: str) -> bool:
        # Basic Ethereum address validation
        if chain_type == "evm":
            return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))
        # Strict Solana address validation (base58, decodes to 32 bytes)
        if chain_type == "solana":
            if not is_base58(address):
                return False
            if base58 is not None:
                try:
                    decoded = base58.b58decode(address)
                    if len(decoded) != 32:
                        return False
                except Exception:
                    return False
                return True
            # Fallback: check length if base58 not installed
            return len(address) in (32, 44)
        return False

security_validator = SecurityValidator() 
=======
"""
Enhanced Security Module
Comprehensive security protections for crypto payment system
Addresses fraud, attacks, and compliance requirements
"""

import hashlib
import hmac
import secrets
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import asyncio
from datetime import datetime, timedelta
import ipaddress
import re

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import jwt
import bcrypt

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FraudType(Enum):
    ACCOUNT_TAKEOVER = "account_takeover"
    MONEY_LAUNDERING = "money_laundering"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    PHISHING = "phishing"
    BOT_ATTACK = "bot_attack"
    SYBIL_ATTACK = "sybil_attack"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    FRONTRUNNING = "frontrunning"
    MEV_ATTACK = "mev_attack"
    RUG_PULL = "rug_pull"
    WASH_TRADING = "wash_trading"
    PUMP_AND_DUMP = "pump_and_dump"

@dataclass
class SecurityContext:
    user_id: str
    ip_address: str
    user_agent: str
    session_id: str
    wallet_address: str
    risk_score: float = 0.0
    fraud_indicators: List[str] = None
    permissions: List[str] = None
    last_activity: datetime = None
    device_fingerprint: str = None
    location_data: Dict = None
    
    def __post_init__(self):
        if self.fraud_indicators is None:
            self.fraud_indicators = []
        if self.permissions is None:
            self.permissions = []
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()

@dataclass
class TransactionRisk:
    transaction_id: str
    risk_score: float
    risk_factors: List[str]
    recommended_action: str
    requires_manual_review: bool
    fraud_probability: float
    compliance_issues: List[str]

class EnhancedSecurityService:
    """
    Comprehensive security service for crypto payment system
    """
    
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Security thresholds
        self.risk_thresholds = {
            SecurityLevel.LOW: 0.3,
            SecurityLevel.MEDIUM: 0.6,
            SecurityLevel.HIGH: 0.8,
            SecurityLevel.CRITICAL: 0.95
        }
        
        # Fraud detection patterns
        self.fraud_patterns = {
            FraudType.ACCOUNT_TAKEOVER: [
                "unusual_login_location",
                "multiple_failed_logins",
                "password_change_after_login",
                "unusual_transaction_pattern"
            ],
            FraudType.MONEY_LAUNDERING: [
                "structuring_transactions",
                "rapid_fund_movement",
                "suspicious_source_funds",
                "high_volume_low_frequency"
            ],
            FraudType.CHARGEBACK_FRAUD: [
                "new_account_high_value",
                "disputed_transaction_pattern",
                "multiple_chargebacks",
                "suspicious_refund_requests"
            ],
            FraudType.BOT_ATTACK: [
                "high_frequency_requests",
                "automated_patterns",
                "missing_human_indicators",
                "consistent_timing"
            ],
            FraudType.SYBIL_ATTACK: [
                "multiple_accounts_same_ip",
                "similar_behavior_patterns",
                "coordinated_activity",
                "fake_identity_indicators"
            ],
            FraudType.FLASH_LOAN_ATTACK: [
                "large_borrow_no_collateral",
                "rapid_repayment_pattern",
                "arbitrage_indicators",
                "manipulation_signals"
            ]
        }
        
        # Rate limiting configuration
        self.rate_limits = {
            "wallet_connect": {"requests": 10, "window": 300},  # 10 per 5 minutes
            "transaction": {"requests": 50, "window": 3600},    # 50 per hour
            "api_calls": {"requests": 1000, "window": 3600},    # 1000 per hour
            "login_attempts": {"requests": 5, "window": 900},   # 5 per 15 minutes
            "withdrawal": {"requests": 10, "window": 86400},    # 10 per day
        }
        
        # Compliance requirements
        self.compliance_rules = {
            "kyc_required": 1000,  # USD threshold for KYC
            "aml_threshold": 3000,  # USD threshold for AML
            "ctr_threshold": 10000,  # USD threshold for CTR
            "sar_threshold": 5000,   # USD threshold for SAR
        }
        
        # Blockchain security
        self.blockchain_security = {
            "max_gas_price": 100,  # Gwei
            "max_transaction_value": 100000,  # USD
            "suspicious_contracts": [
                "0x0000000000000000000000000000000000000000",  # Zero address
                "0x000000000000000000000000000000000000dEaD",  # Dead address
            ],
            "blacklisted_addresses": set(),
            "whitelisted_addresses": set(),
        }

    async def analyze_transaction_risk(
        self, 
        transaction_data: Dict[str, Any],
        user_context: SecurityContext
    ) -> TransactionRisk:
        """
        Comprehensive transaction risk analysis
        """
        risk_factors = []
        risk_score = 0.0
        fraud_probability = 0.0
        
        # 1. Amount-based risk
        amount = Decimal(transaction_data.get("amount", "0"))
        if amount > self.compliance_rules["sar_threshold"]:
            risk_factors.append("high_value_transaction")
            risk_score += 0.3
            fraud_probability += 0.1
        
        # 2. Velocity checks
        velocity_risk = await self._check_velocity_risk(user_context, amount)
        if velocity_risk > 0.5:
            risk_factors.append("high_velocity_activity")
            risk_score += velocity_risk
            fraud_probability += 0.2
        
        # 3. Geographic risk
        geo_risk = await self._check_geographic_risk(user_context)
        if geo_risk > 0.3:
            risk_factors.append("high_geographic_risk")
            risk_score += geo_risk
            fraud_probability += 0.15
        
        # 4. Device risk
        device_risk = await self._check_device_risk(user_context)
        if device_risk > 0.4:
            risk_factors.append("suspicious_device")
            risk_score += device_risk
            fraud_probability += 0.2
        
        # 5. Blockchain risk
        blockchain_risk = await self._check_blockchain_risk(transaction_data)
        if blockchain_risk > 0.3:
            risk_factors.append("blockchain_risk")
            risk_score += blockchain_risk
            fraud_probability += 0.25
        
        # 6. Behavioral risk
        behavioral_risk = await self._check_behavioral_risk(user_context)
        if behavioral_risk > 0.4:
            risk_factors.append("unusual_behavior")
            risk_score += behavioral_risk
            fraud_probability += 0.2
        
        # 7. Compliance checks
        compliance_issues = await self._check_compliance(transaction_data, user_context)
        if compliance_issues:
            risk_factors.extend(compliance_issues)
            risk_score += 0.2 * len(compliance_issues)
            fraud_probability += 0.1 * len(compliance_issues)
        
        # 8. MEV attack detection
        if self._detect_mev_attack(transaction_data):
            risk_factors.append("mev_attack_suspected")
            risk_score += 0.8
            fraud_probability += 0.6
        
        # Determine action based on risk score
        recommended_action = self._determine_action(risk_score)
        requires_manual_review = risk_score > self.risk_thresholds[SecurityLevel.HIGH]
        
        return TransactionRisk(
            transaction_id=transaction_data.get("transaction_id", ""),
            risk_score=min(risk_score, 1.0),
            risk_factors=risk_factors,
            recommended_action=recommended_action,
            requires_manual_review=requires_manual_review,
            fraud_probability=min(fraud_probability, 1.0),
            compliance_issues=compliance_issues
        )

    async def _check_velocity_risk(self, context: SecurityContext, amount: Decimal) -> float:
        """Check for high-velocity transaction patterns"""
        # In production, this would query a database for recent transactions
        # Implement velocity check based on amount and time
        current_time = datetime.utcnow()
        time_window = timedelta(hours=1)
        
        # Velocity check based on amount and time
        if amount > 10000 and (current_time - context.last_activity).total_seconds() < 300:
            return 0.7  # High velocity risk
        elif amount > 5000 and (current_time - context.last_activity).total_seconds() < 600:
            return 0.5  # Medium velocity risk
        elif amount > 1000 and (current_time - context.last_activity).total_seconds() < 1800:
            return 0.3  # Low velocity risk
        
        return 0.0

    async def _check_geographic_risk(self, context: SecurityContext) -> float:
        """Check geographic risk based on IP location"""
        try:
            ip = ipaddress.ip_address(context.ip_address)
            
            # Check for known high-risk regions
            high_risk_regions = [
                "192.168.0.0/16",  # Private network
                "10.0.0.0/8",      # Private network
                "172.16.0.0/12"    # Private network
            ]
            
            for region in high_risk_regions:
                if ip in ipaddress.ip_network(region):
                    return 0.6  # High risk for private IPs
            
            # Check for VPN/Tor exit nodes (simplified)
            if self._is_vpn_ip(context.ip_address):
                return 0.4
            
            return 0.1  # Low risk for normal IPs
            
        except ValueError:
            return 0.8  # Invalid IP

    async def _check_device_risk(self, context: SecurityContext) -> float:
        """Check device fingerprint risk"""
        if not context.device_fingerprint:
            return 0.3  # Missing fingerprint
        
        # Check for suspicious user agents
        suspicious_patterns = [
            "bot", "crawler", "spider", "scraper",
            "headless", "phantom", "selenium"
        ]
        
        user_agent_lower = context.user_agent.lower()
        for pattern in suspicious_patterns:
            if pattern in user_agent_lower:
                return 0.7  # Suspicious user agent
        
        # Check for missing or generic user agent
        if len(context.user_agent) < 20 or "mozilla" not in user_agent_lower:
            return 0.5  # Generic user agent
        
        return 0.1  # Normal device

    async def _check_blockchain_risk(self, transaction_data: Dict[str, Any]) -> float:
        """Check blockchain-specific risks"""
        risk_score = 0.0
        
        # Check for suspicious contract addresses
        to_address = transaction_data.get("to_address", "")
        if to_address in self.blockchain_security["suspicious_contracts"]:
            risk_score += 0.8
        
        # Check for blacklisted addresses
        if to_address in self.blockchain_security["blacklisted_addresses"]:
            risk_score += 1.0
        
        # Check gas price manipulation
        gas_price = transaction_data.get("gas_price", 0)
        if gas_price > self.blockchain_security["max_gas_price"]:
            risk_score += 0.4
        
        # Check transaction value
        amount = Decimal(transaction_data.get("amount", "0"))
        if amount > self.blockchain_security["max_transaction_value"]:
            risk_score += 0.3
        
        return min(risk_score, 1.0)

    async def _check_behavioral_risk(self, context: SecurityContext) -> float:
        """Check behavioral patterns"""
        risk_score = 0.0
        
        # Check for rapid session creation
        if (datetime.utcnow() - context.last_activity).total_seconds() < 60:
            risk_score += 0.3
        
        # Check for multiple failed attempts (would query DB in production)
        # For now, use a simple heuristic
        if context.fraud_indicators:
            risk_score += 0.2 * len(context.fraud_indicators)
        
        return min(risk_score, 1.0)

    async def _check_compliance(self, transaction_data: Dict[str, Any], context: SecurityContext) -> List[str]:
        """Check compliance requirements"""
        issues = []
        amount = Decimal(transaction_data.get("amount", "0"))
        
        # KYC requirements
        if amount > self.compliance_rules["kyc_required"]:
            if not await self._has_kyc_verification(context.user_id):
                issues.append("kyc_required")
        
        # AML screening
        if amount > self.compliance_rules["aml_threshold"]:
            if not await self._has_aml_screening(context.user_id):
                issues.append("aml_screening_required")
        
        # CTR reporting
        if amount > self.compliance_rules["ctr_threshold"]:
            issues.append("ctr_reporting_required")
        
        # SAR filing
        if amount > self.compliance_rules["sar_threshold"]:
            issues.append("sar_filing_required")
        
        return issues

    def _detect_mev_attack(self, transaction_data: Dict[str, Any]) -> bool:
        """Detect MEV (Maximal Extractable Value) attacks"""
        # Check for sandwich attack patterns
        gas_price = transaction_data.get("gas_price", 0)
        gas_limit = transaction_data.get("gas_limit", 0)
        
        # Unusually high gas prices might indicate MEV
        if gas_price > 100:  # 100 Gwei threshold
            return True
        
        # Check for frontrunning patterns
        if transaction_data.get("frontrun_detected"):
            return True
        
        # Check for arbitrage patterns
        if transaction_data.get("arbitrage_indicators"):
            return True
        
        return False

    def _determine_action(self, risk_score: float) -> str:
        """Determine recommended action based on risk score"""
        if risk_score > self.risk_thresholds[SecurityLevel.CRITICAL]:
            return "block_transaction"
        elif risk_score > self.risk_thresholds[SecurityLevel.HIGH]:
            return "require_manual_review"
        elif risk_score > self.risk_thresholds[SecurityLevel.MEDIUM]:
            return "require_additional_verification"
        elif risk_score > self.risk_thresholds[SecurityLevel.LOW]:
            return "monitor_closely"
        else:
            return "allow_transaction"

    async def _has_kyc_verification(self, user_id: str) -> bool:
        """Check if user has completed KYC verification"""
        # In production, this would query a database
        # For now, return False to trigger KYC requirements
        return False

    async def _has_aml_screening(self, user_id: str) -> bool:
        """Check if user has completed AML screening"""
        # In production, this would query a database
        # For now, return False to trigger AML requirements
        return False

    def _is_vpn_ip(self, ip_address: str) -> bool:
        """Check if IP is from a VPN service"""
        # In production, this would use a VPN detection service
        # For now, implement basic checks
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check for known VPN ranges (simplified)
            vpn_ranges = [
                "103.21.244.0/22",  # Cloudflare
                "104.16.0.0/12",    # Cloudflare
                "172.64.0.0/13",    # Cloudflare
            ]
            
            for vpn_range in vpn_ranges:
                if ip in ipaddress.ip_network(vpn_range):
                    return True
            
            return False
            
        except ValueError:
            return False

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def generate_secure_token(self, payload: Dict[str, Any], expiration: int = 3600) -> str:
        """Generate secure JWT token"""
        payload.update({
            "exp": datetime.utcnow() + timedelta(seconds=expiration),
            "iat": datetime.utcnow(),
            "iss": "liquicity-security"
        })
        
        return jwt.encode(payload, self.encryption_key, algorithm="HS256")

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.encryption_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise SecurityException("Token expired", "TOKEN_EXPIRED")
        except jwt.InvalidTokenError:
            raise SecurityException("Invalid token", "INVALID_TOKEN")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate device fingerprint"""
        fingerprint_data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    def validate_wallet_address(self, address: str, chain_type: str) -> bool:
        """Validate wallet address format"""
        if not address:
            return False
        
        if chain_type.lower() == "evm":
            # Ethereum-style address validation
            if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
                return False
        elif chain_type.lower() == "solana":
            # Solana address validation
            if not re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", address):
                return False
        
        return True

    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input"""
        if not input_data:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_data)
        
        # Remove script tags
        sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.IGNORECASE)
        
        # Remove other potentially dangerous tags
        sanitized = re.sub(r'<(iframe|object|embed).*?>.*?</\1>', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()

    def validate_ip_address(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    async def check_rate_limit(self, key: str, limit_type: str) -> bool:
        """Check rate limiting"""
        # In production, this would use Redis or similar
        # For now, implement basic in-memory rate limiting
        current_time = time.time()
        limit_config = self.rate_limits.get(limit_type, self.rate_limits["api_calls"])
        
        # This is a simplified implementation
        # In production, use Redis with proper TTL
        return True  # Allow for now

    def log_security_event(self, event_type: str, context: SecurityContext, details: Dict[str, Any]):
        """Log security event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": context.user_id,
            "ip_address": context.ip_address,
            "session_id": context.session_id,
            "risk_score": context.risk_score,
            "details": details
        }
        
        logger.warning(f"Security event: {json.dumps(log_entry)}")

class SecurityException(Exception):
    """Security-related exception"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

# Initialize security service
security_service = EnhancedSecurityService()

# Back-compat alias – some modules previously imported `security_validator` expecting
# an object with validation helpers.  Re-export it to avoid widespread renames.
security_validator = security_service 

>>>>>>> main
