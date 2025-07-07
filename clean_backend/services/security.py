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