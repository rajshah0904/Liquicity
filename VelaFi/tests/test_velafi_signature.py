import time, hmac, hashlib
from VelaFi.webhooks import _verify_signature, _WEBHOOK_SECRET_PLACEHOLDER


def test_verify_signature_valid():
    secret = _WEBHOOK_SECRET_PLACEHOLDER or "test-secret"
    payload = b"{\"hello\": \"world\"}"
    ts = int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.{payload.decode()}".encode(), hashlib.sha256).hexdigest()
    header = f"t={ts},v1={sig}"
    assert _verify_signature(payload, header) is True


def test_verify_signature_invalid():
    payload = b"{}"
    header = "t=0,v1=badsignature"
    assert _verify_signature(payload, header) is False 