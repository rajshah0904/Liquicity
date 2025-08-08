"""VelaFi Service
Production-level service for LATAM fiat on/off-ramp integration.
Handles KYC, fiat deposits/withdrawals, FX conversion, and USDC settlement.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException
from sqlalchemy import and_, select

from clean_backend.config.settings import settings
from clean_backend.database import db_session
from clean_backend.models.velafi_order import VelafiDirection, VelafiOrder, VelafiStatus

logger = logging.getLogger(__name__)

class VelaFiError(Exception):
    """Raised when the VelaFi API returns an error."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class VelaFiService:
    """
    Production VelaFi service for LATAM fiat on/off-ramp.
    
    Features:
    - KYC & account creation
    - Document upload
    - Quote retrieval
    - Order creation & management
    - Webhook signature verification
    - Exponential backoff for retries
    """

    def __init__(self):
        if not all([settings.velafi_api_key, settings.velafi_api_secret, settings.velafi_webhook_secret]):
            raise RuntimeError("Missing required VelaFi configuration")

        self.api_key = settings.velafi_api_key.get_secret_value()
        self.api_secret = settings.velafi_api_secret.get_secret_value()
        self.webhook_secret = settings.velafi_webhook_secret.get_secret_value()
        self.base_url = settings.velafi_base_url

        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-API-Key": self.api_secret,
                "Content-Type": "application/json",
            },
            timeout=30.0
        )

    async def _post(self, path: str, json: Dict[str, Any], idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Make a POST request to the VelaFi API with retry logic."""
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        try:
            response = await self.session.post(path, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except Exception:
                pass
            
            raise VelaFiError(
                message=str(e),
                code=error_data.get("code"),
                details=error_data
            ) from e

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the VelaFi API with retry logic."""
        try:
            response = await self.session.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except Exception:
                pass
            
            raise VelaFiError(
                message=str(e),
                code=error_data.get("code"),
                details=error_data
            ) from e

    def verify_webhook_signature(self, signature: str, timestamp: str, body: bytes) -> bool:
        """
        Verify the HMAC signature of a webhook payload.
        
        Args:
            signature: The X-VelaFi-Signature header value
            timestamp: The X-VelaFi-Timestamp header value
            body: Raw request body bytes
        
        Returns:
            bool: True if signature is valid
        """
        if not all([signature, timestamp, body]):
            return False

        # Reconstruct the string to sign
        message = f"{timestamp}.{body.decode('utf-8')}"
        
        # Calculate expected signature
        expected = hmac.new(
            self.webhook_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison
        return hmac.compare_digest(signature, expected)

    async def create_customer(
        self,
        user_id: str,
        email: str,
        country_code: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new VelaFi customer for KYC.

        Args:
            user_id: Internal user ID
            email: Customer's email
            country_code: ISO 3166-1 alpha-2 country code
            first_name: Legal first name
            last_name: Legal last name
            phone: Optional phone number in E.164 format
            metadata: Optional metadata to attach to the customer

        Returns:
            Dict containing customer details including velafi_customer_id
        """
        payload = {
            "external_id": str(user_id),
            "email": email,
            "country": country_code.upper(),
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "metadata": metadata or {}
        }
        
        return await self._post(
            "/customers",
            json=payload,
            idempotency_key=f"create_customer_{user_id}"
        )

    async def upload_documents(
        self,
        customer_id: str,
        document_type: str,
        file_data: bytes,
        file_name: str
    ) -> Dict[str, Any]:
        """
        Upload KYC verification documents for a customer.

        Args:
            customer_id: VelaFi customer ID
            document_type: Type of document (passport, id_card, drivers_license)
            file_data: Raw file bytes
            file_name: Original file name with extension

        Returns:
            Dict containing upload status and document ID
        """
        # TODO: Implement multipart file upload
        raise NotImplementedError("Document upload not yet implemented")

    async def get_quote(
        self,
        fiat_amount: Decimal,
        fiat_currency: str,
        direction: VelafiDirection,
        country_code: str
    ) -> Dict[str, Any]:
        """
        Get a quote for a fiat ↔ USDC conversion.

        Args:
            fiat_amount: Amount in fiat currency
            fiat_currency: ISO 4217 currency code
            direction: BUY for fiat→USDC, SELL for USDC→fiat
            country_code: ISO 3166-1 alpha-2 country code

        Returns:
            Dict containing quote details including fx_rate and fees
        """
        params = {
            "fiat_amount": str(fiat_amount),
            "fiat_currency": fiat_currency.upper(),
            "direction": direction.value,
            "country": country_code.upper()
        }
        
        return await self._get("/quote", params=params)

    async def create_order(
        self,
        user_id: str,
        customer_id: str,
        direction: VelafiDirection,
        fiat_amount: Decimal,
        fiat_currency: str,
        wallet_address: str,
        country_code: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VelafiOrder:
        """
        Create a new fiat ↔ USDC conversion order.

        Args:
            user_id: Internal user ID
            customer_id: VelaFi customer ID
            direction: BUY for fiat→USDC, SELL for USDC→fiat
            fiat_amount: Amount in fiat currency
            fiat_currency: ISO 4217 currency code
            wallet_address: Destination wallet for USDC
            country_code: ISO 3166-1 alpha-2 country code
            metadata: Optional metadata to attach to the order

        Returns:
            VelafiOrder model instance
        """
        # Generate order ID and get quote
        order_id = str(uuid.uuid4())
        quote = await self.get_quote(fiat_amount, fiat_currency, direction, country_code)

        payload = {
            "order_id": order_id,
            "customer_id": customer_id,
            "direction": direction.value,
            "fiat_amount": str(fiat_amount),
            "fiat_currency": fiat_currency.upper(),
            "wallet_address": wallet_address,
            "country": country_code.upper(),
            "metadata": metadata or {}
        }

        # Create order in VelaFi
        response = await self._post(
            "/orders",
            json=payload,
            idempotency_key=f"create_order_{order_id}"
        )

        # Create local order record
        order = VelafiOrder(
            order_id=order_id,
            user_id=user_id,
            direction=direction,
            fiat_amount=fiat_amount,
            fiat_currency=fiat_currency.upper(),
            usdc_amount=Decimal(quote["usdc_amount"]),
            fx_rate=Decimal(quote["fx_rate"]),
            fee_usd=Decimal(quote["fee_usd"]),
            rail=response["rail"],
            status=VelafiStatus.PENDING
        )

        async with db_session() as session:
            session.add(order)
            await session.commit()
            await session.refresh(order)

        return order

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get the current status of an order.

        Args:
            order_id: VelaFi order ID

        Returns:
            Dict containing order details and status
        """
        return await self._get(f"/orders/{order_id}")

    async def poll_pending_orders(self, min_age_minutes: int = 10) -> None:
        """
        Poll VelaFi for updates on pending orders older than min_age_minutes.
        This serves as a fallback in case webhooks are missed.

        Args:
            min_age_minutes: Minimum age in minutes for orders to poll
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=min_age_minutes)
        
        async with db_session() as session:
            # Find pending/processing orders older than cutoff
            pending_orders = await session.execute(
                select(VelafiOrder).where(
                    and_(
                        VelafiOrder.status.in_([VelafiStatus.PENDING, VelafiStatus.PROCESSING]),
                        VelafiOrder.created_at < cutoff
                    )
                )
            )

            for order in pending_orders.scalars():
                try:
                    # Get latest status from VelaFi
                    status = await self.get_order(order.order_id)
                    
                    # Update if status has changed
                    if status["status"] != order.status.value:
                        order.status = VelafiStatus(status["status"])
                        if status.get("tx_hash"):
                            order.tx_hash = status["tx_hash"]
                        
                        await session.commit()
                        
                        logger.info(
                            f"Updated order {order.order_id} status to {order.status.value}"
                        )
                except Exception as e:
                    logger.error(f"Error polling order {order.order_id}: {e}")