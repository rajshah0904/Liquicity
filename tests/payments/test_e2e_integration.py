import os
import pytest

from app.payments.services.orchestrator import transfer_cross_border

pytestmark = pytest.mark.integration

@pytest.fixture(scope='module', autouse=True)
def check_e2e_env():
    """
    Skip the e2e integration test if required sandbox env vars are missing.
    """
    required = [
        "MODERN_TREASURY_API_KEY",
        "MODERN_TREASURY_ORG_ID",
        "RAPYD_ACCESS_KEY",
        "RAPYD_SECRET_KEY",
        "CIRCLE_API_KEY",
        "TEST_US_ACCOUNT",
        "TEST_US_ROUTING",
        "TEST_CA_ACCOUNT",
        "TEST_CA_ROUTING",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        pytest.skip(f"Skipping e2e integration test; missing env vars: {missing}")

@pytest.mark.asyncio
async def test_full_cross_border_flow():
    """
    End-to-end cross-border transfer from US -> CA via stablecoin in sandbox.
    """
    result = await transfer_cross_border(
        user_id="e2e_user",
        amount=0.05,
        src_cc="US",
        dst_cc="CA",
        currency="USD",
        chain="polygon",
        metadata={"integration": True},
    )
    assert result["status"] == "completed", f"Transfer failed: {result}"
    assert hasattr(result["debit"], "id"), "Debit step did not return an id"
    assert hasattr(result["mint"], "tx_id"), "Mint step did not return tx_id"
    assert hasattr(result["redeem"], "tx_id"), "Redeem step did not return tx_id"
    assert hasattr(result["payout"], "id"), "Payout step did not return an id" 