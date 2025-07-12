"""Service wrappers for crypto wallet linking, USDC payments, and Bridge transfers.

These simply re-export the robust implementations that currently live in
`python_backend.core`.  Keeping them behind this facade means we can migrate
or swap out implementations later without touching router code.
"""

from .walletconnect_v2_service import (
    WalletConnectV2Service,
    walletconnect_service,
    WalletConnectError,
)

from .usdc_payment_service import (
    USDCPaymentService,
    usdc_payment_service,
    USDCError,
)

from .bridge_api_client import (
    BridgeAPIClient,
    BridgeError,
)

bridge_client = BridgeAPIClient()

__all__ = [
    # WalletConnect
    "WalletConnectV2Service",
    "walletconnect_service",
    "WalletConnectError",
    # USDC payments
    "USDCPaymentService",
    "usdc_payment_service",
    "USDCError",
    # Bridge
    "BridgeAPIClient",
    "bridge_client",
    "BridgeError",
] 