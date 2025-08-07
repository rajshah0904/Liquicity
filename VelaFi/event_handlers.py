"""Event handlers for VelaFi events.

This module contains handlers for various events in the VelaFi system.
Handlers can be registered with the event bus to process events asynchronously.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from clean_backend.database import get_db
from clean_backend.models import User

from .event_bus import EventMessage, publish, subscribe, subscribe_redis
from .models import OnRampOrder, OrderStatus

_log = logging.getLogger(__name__)

class OrderEventHandler:
    """Handles order-related events."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def handle_order_completed(self, event: EventMessage) -> None:
        """Handle order.completed events."""
        try:
            order_id = event.payload.get("order_id")
            user_id = event.payload.get("user_id")
            usdc_amount = event.payload.get("usdc_amount")
            
            _log.info(f"Processing completed order {order_id} for user {user_id}")
            
            # Update order status
            order = self.db.query(OnRampOrder).filter_by(velafi_order_id=order_id).first()
            if order:
                order.status = OrderStatus.completed
                order.updated_at = datetime.utcnow()
                self.db.commit()
                _log.info(f"Order {order_id} status updated to completed")
            
            # Trigger credit allocation
            await self._allocate_credit(user_id, usdc_amount)
            
            # Send notification
            await self._send_notification(user_id, "order_completed", {
                "order_id": order_id,
                "usdc_amount": usdc_amount
            })
            
        except Exception as e:
            _log.error(f"Error handling order.completed event: {e}")
    
    async def handle_order_status_changed(self, event: EventMessage) -> None:
        """Handle order.status_changed events."""
        try:
            order_id = event.payload.get("order_id")
            status = event.payload.get("status")
            
            _log.info(f"Order {order_id} status changed to {status}")
            
            # Update order status
            order = self.db.query(OnRampOrder).filter_by(velafi_order_id=order_id).first()
            if order:
                order.status = OrderStatus(status)
                order.updated_at = datetime.utcnow()
                self.db.commit()
            
            # Handle different status changes
            if status == "processing":
                await self._handle_order_processing(order_id)
            elif status == "failed":
                await self._handle_order_failed(order_id)
            
        except Exception as e:
            _log.error(f"Error handling order.status_changed event: {e}")
    
    async def _allocate_credit(self, user_id: str, usdc_amount: float) -> None:
        """Allocate credit to user's Bridge wallet."""
        try:
            # This would integrate with your Bridge credit system
            _log.info(f"Allocating {usdc_amount} USDC credit to user {user_id}")
            
            # Get user's Bridge wallet ID
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user or not user.bridge_wallet_id:
                _log.error(f"User {user_id} has no Bridge wallet configured")
                return
            
            # TODO: Implement actual Bridge API call
            # For now, log the allocation
            _log.info(f"Would allocate {usdc_amount} USDC to Bridge wallet {user.bridge_wallet_id}")
            
            # Update user's balance in database
            # This would be replaced with actual Bridge API integration
            _log.info(f"Credit allocation completed for user {user_id}")
            
        except Exception as e:
            _log.error(f"Error allocating credit: {e}")
            # Publish failure event
            await publish("credit.allocation_failed", {
                "user_id": user_id,
                "amount": usdc_amount,
                "error": str(e)
            })
    
    async def _send_notification(self, user_id: str, notification_type: str, data: Dict[str, Any]) -> None:
        """Send notification to user."""
        try:
            _log.info(f"Sending {notification_type} notification to user {user_id}")
            
            # Get user details
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                _log.error(f"User {user_id} not found for notification")
                return
            
            # Create notification payload
            notification_data = {
                "user_id": user_id,
                "user_email": user.email,
                "notification_type": notification_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish notification event
            await publish("notification.send", notification_data)
            
            # Log notification
            _log.info(f"Notification {notification_type} sent to user {user_id} ({user.email})")
            
        except Exception as e:
            _log.error(f"Error sending notification: {e}")
            # Publish notification failure event
            await publish("notification.failed", {
                "user_id": user_id,
                "notification_type": notification_type,
                "error": str(e)
            })
    
    async def _handle_order_processing(self, order_id: str) -> None:
        """Handle order processing status."""
        try:
            _log.info(f"Order {order_id} is now processing")
            
            # Get order details
            order = self.db.query(OnRampOrder).filter_by(velafi_order_id=order_id).first()
            if not order:
                _log.error(f"Order {order_id} not found in database")
                return
            
            # Update processing timestamp
            order.updated_at = datetime.utcnow()
            self.db.commit()
            
            # Send processing notification
            await self._send_notification(str(order.user_id), "order_processing", {
                "order_id": order_id,
                "fiat_amount": str(order.fiat_amount),
                "fiat_currency": order.fiat_currency
            })
            
            # Publish processing event
            await publish("order.processing", {
                "order_id": order_id,
                "user_id": str(order.user_id),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            _log.error(f"Error handling order processing: {e}")
    
    async def _handle_order_failed(self, order_id: str) -> None:
        """Handle order failure."""
        try:
            _log.info(f"Order {order_id} failed")
            
            # Get order details
            order = self.db.query(OnRampOrder).filter_by(velafi_order_id=order_id).first()
            if not order:
                _log.error(f"Order {order_id} not found in database")
                return
            
            # Update failure timestamp
            order.updated_at = datetime.utcnow()
            self.db.commit()
            
            # Send failure notification
            await self._send_notification(str(order.user_id), "order_failed", {
                "order_id": order_id,
                "fiat_amount": str(order.fiat_amount),
                "fiat_currency": order.fiat_currency,
                "failure_reason": "Payment processing failed"
            })
            
            # Publish failure event for refund processing
            await publish("order.failed", {
                "order_id": order_id,
                "user_id": str(order.user_id),
                "fiat_amount": str(order.fiat_amount),
                "fiat_currency": order.fiat_currency,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # TODO: Implement automatic refund processing
            _log.info(f"Order {order_id} failure handled - refund processing required")
            
        except Exception as e:
            _log.error(f"Error handling order failure: {e}")

class SecurityEventHandler:
    """Handles security-related events."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def handle_suspicious_activity(self, event: EventMessage) -> None:
        """Handle suspicious activity events."""
        try:
            user_id = event.payload.get("user_id")
            activity_type = event.payload.get("activity_type")
            risk_score = event.payload.get("risk_score")
            
            _log.warning(f"Suspicious activity detected for user {user_id}: {activity_type} (risk: {risk_score})")
            
            # Log security event
            await self._log_security_event(user_id, activity_type, risk_score)
            
            # Trigger additional verification if needed
            if risk_score > 0.8:
                await self._trigger_additional_verification(user_id)
            
        except Exception as e:
            _log.error(f"Error handling suspicious activity event: {e}")
    
    async def _send_notification(self, user_id: str, notification_type: str, data: Dict[str, Any]) -> None:
        """Send notification to user."""
        try:
            _log.info(f"Sending {notification_type} notification to user {user_id}")
            
            # Get user details
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                _log.error(f"User {user_id} not found for notification")
                return
            
            # Create notification payload
            notification_data = {
                "user_id": user_id,
                "user_email": user.email,
                "notification_type": notification_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish notification event
            await publish("notification.send", notification_data)
            
            # Log notification
            _log.info(f"Notification {notification_type} sent to user {user_id} ({user.email})")
            
        except Exception as e:
            _log.error(f"Error sending notification: {e}")
            # Publish notification failure event
            await publish("notification.failed", {
                "user_id": user_id,
                "notification_type": notification_type,
                "error": str(e)
            })
    
    async def _log_security_event(self, user_id: str, activity_type: str, risk_score: float) -> None:
        """Log security event for audit purposes."""
        try:
            # Create security event record
            security_event = {
                "user_id": user_id,
                "activity_type": activity_type,
                "risk_score": risk_score,
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": "unknown",  # Would come from context
                "user_agent": "unknown",  # Would come from context
                "session_id": "unknown"   # Would come from context
            }
            
            # Publish security event for logging
            await publish("security.event_logged", security_event)
            
            # Log to database (would create SecurityEvent model)
            _log.warning(f"Security event logged: {activity_type} for user {user_id} (risk: {risk_score})")
            
        except Exception as e:
            _log.error(f"Error logging security event: {e}")
    
    async def _trigger_additional_verification(self, user_id: str) -> None:
        """Trigger additional verification for high-risk users."""
        try:
            _log.warning(f"Triggering additional verification for high-risk user {user_id}")
            
            # Get user details
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                _log.error(f"User {user_id} not found for additional verification")
                return
            
            # Publish additional verification event
            await publish("security.additional_verification_required", {
                "user_id": user_id,
                "user_email": user.email,
                "verification_type": "enhanced_kyc",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Send notification to user
            await self._send_notification(user_id, "additional_verification_required", {
                "verification_type": "enhanced_kyc",
                "reason": "High-risk activity detected"
            })
            
            # Log the action
            _log.info(f"Additional verification triggered for user {user_id}")
            
        except Exception as e:
            _log.error(f"Error triggering additional verification: {e}")

def register_event_handlers() -> None:
    """Register all event handlers with the event bus."""
    
    # Get database session
    db = next(get_db())
    
    # Create handlers
    order_handler = OrderEventHandler(db)
    security_handler = SecurityEventHandler(db)
    
    # Register local handlers
    subscribe("order.completed", order_handler.handle_order_completed)
    subscribe("order.status_changed", order_handler.handle_order_status_changed)
    subscribe("security.suspicious_activity", security_handler.handle_suspicious_activity)
    
    _log.info("Event handlers registered successfully")

async def register_redis_handlers() -> None:
    """Register handlers for Redis events (distributed processing)."""
    
    # Get database session
    db = next(get_db())
    
    # Create handlers
    order_handler = OrderEventHandler(db)
    security_handler = SecurityEventHandler(db)
    
    # Register Redis handlers
    await subscribe_redis("order.completed", order_handler.handle_order_completed)
    await subscribe_redis("order.status_changed", order_handler.handle_order_status_changed)
    await subscribe_redis("security.suspicious_activity", security_handler.handle_suspicious_activity)
    
    _log.info("Redis event handlers registered successfully") 