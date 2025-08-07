import pytest
from decimal import Decimal
from clean_backend.services.security import EnhancedSecurityService, SecurityContext

@pytest.mark.asyncio
async def test_deposit_allowed_low_risk(monkeypatch):
    svc = EnhancedSecurityService()

    # Monkeypatch internal checks to force low risk
    async def zero(*args, **kwargs):
        return 0.0
    async def no_flags(*args, **kwargs):
        return []

    monkeypatch.setattr(svc, "_check_velocity_risk", zero)
    monkeypatch.setattr(svc, "_check_geographic_risk", zero)
    monkeypatch.setattr(svc, "_check_compliance", no_flags)

    ctx = SecurityContext(
        user_id="u1",
        ip_address="1.2.3.4",
        user_agent="pytest",
        session_id="s1",
        wallet_address="",
    )
    allowed = await svc.is_deposit_allowed(ctx, Decimal("100"))
    assert allowed is True

@pytest.mark.asyncio
async def test_deposit_blocked_high_risk(monkeypatch):
    svc = EnhancedSecurityService()
    async def high(*args, **kwargs):
        return 0.8
    async def flags(*args, **kwargs):
        return ["kyc_required"]
    monkeypatch.setattr(svc, "_check_velocity_risk", high)
    monkeypatch.setattr(svc, "_check_geographic_risk", high)
    monkeypatch.setattr(svc, "_check_compliance", flags)

    ctx = SecurityContext(
        user_id="u1",
        ip_address="1.2.3.4",
        user_agent="pytest",
        session_id="s1",
        wallet_address="",
    )
    allowed = await svc.is_deposit_allowed(ctx, Decimal("5000"))
    assert allowed is False 