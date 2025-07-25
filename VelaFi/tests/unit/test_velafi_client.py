import asyncio
from typing import Dict, Any

import pytest

from VelaFi.velafi_client import VelafiClient, PaymentMethod, OnRampOrder, VelafiError


@pytest.mark.asyncio
async def test_add_payment_method_success(monkeypatch):
    """VelafiClient.add_payment_method returns parsed PaymentMethod object."""

    async def fake_request(self, method: str, path: str, *, payload: Dict[str, Any] | None = None, headers=None):
        assert method == "POST"
        assert path == "/v1/payment_methods"
        assert payload == {"plaid_token": "public-sandbox-123", "customer_reference": "user-1"}
        return {
            "id": "pm_abc",
            "payment_rail": "ach",
            "country": "US",
            "currency": "USD",
        }

    monkeypatch.setattr(VelafiClient, "_request", fake_request, raising=True)

    client = VelafiClient(api_key="test-key", base_url="https://example.com")
    pm = await client.add_payment_method("public-sandbox-123", user_id="user-1")
    assert isinstance(pm, PaymentMethod)
    assert pm.id == "pm_abc"
    assert pm.fiat_rail == "ach"
    assert pm.country == "US"
    assert pm.currency == "USD"


@pytest.mark.asyncio
async def test_create_order_success(monkeypatch):
    async def fake_request(self, method, path, *, payload=None, headers=None):
        assert method == "POST"
        assert path == "/v1/orders/fiat_to_crypto"
        return {
            "id": "ord_123",
            "status": "pending",
            "amount": "100",
            "fiat_currency": "USD",
            "usdc_amount": "99",
            "quote_rate": "1",
            "fee_usd": "1",
        }

    monkeypatch.setattr(VelafiClient, "_request", fake_request, raising=True)

    client = VelafiClient(api_key="test-key", base_url="https://example.com")
    order = await client.create_order(user_id="user-1", payment_method_id="pm_abc", fiat_amount="100")
    assert isinstance(order, OnRampOrder)
    assert order.id == "ord_123"
    assert order.status == "pending"
    assert order.fiat_amount == "100"
    assert order.usdc_amount == "99"


@pytest.mark.asyncio
async def test_get_order_error(monkeypatch):
    async def fake_request(self, method, path, *, payload=None, headers=None):
        raise VelafiError(404, "Not Found")

    monkeypatch.setattr(VelafiClient, "_request", fake_request, raising=True)

    client = VelafiClient(api_key="test-key", base_url="https://example.com")
    with pytest.raises(VelafiError) as ctx:
        await client.get_order("ord_missing")
    assert ctx.value.status == 404 