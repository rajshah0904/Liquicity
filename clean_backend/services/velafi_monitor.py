"""VelaFi monitor service.

This service polls VelaFi for updates on pending orders and reconciles their status.
It serves as a fallback in case webhooks are missed.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from clean_backend.config.settings import settings
from clean_backend.database import get_db
from clean_backend.models.velafi_order import VelafiOrder, VelafiStatus
from clean_backend.services.velafi_service import VelaFiError, VelaFiService

logger = logging.getLogger(__name__)

class VelaFiMonitor:
    """
    Monitor service for VelaFi orders.
    
    Features:
    - Polls pending/processing orders older than N minutes
    - Updates local order status based on VelaFi API
    - Handles missed webhooks
    - Retries with exponential backoff
    """

    def __init__(self, db: Session):
        self.db = db
        self.service = VelaFiService()
        
        # Configuration from settings
        self.min_age_minutes = settings.velafi_monitor_min_age
        self.max_retries = settings.velafi_monitor_max_retries
        self.base_delay = settings.velafi_monitor_base_delay

    async def _get_pending_orders(self, cutoff: datetime) -> List[VelafiOrder]:
        """Get pending/processing orders older than cutoff."""
        return (await self.db.execute(
            select(VelafiOrder).where(
                and_(
                    VelafiOrder.status.in_([VelafiStatus.PENDING, VelafiStatus.PROCESSING]),
                    VelafiOrder.created_at < cutoff
                )
            )
        )).scalars().all()

    async def _update_order_status(
        self,
        order: VelafiOrder,
        retry_count: int = 0
    ) -> Optional[VelafiStatus]:
        """
        Update order status from VelaFi API with retry logic.
        
        Args:
            order: The order to update
            retry_count: Current retry attempt number
            
        Returns:
            Optional[VelafiStatus]: New status if changed, None if unchanged or error
        """
        try:
            # Get latest status from VelaFi
            status = await self.service.get_order(order.order_id)
            
            # Update if status has changed
            if status["status"] != order.status.value:
                new_status = VelafiStatus(status["status"])
                order.status = new_status
                
                # Update tx_hash if available
                if status.get("tx_hash"):
                    order.tx_hash = status["tx_hash"]
                
                await self.db.commit()
                
                logger.info(
                    f"Updated order {order.order_id} status to {order.status.value}"
                )
                return new_status
            
            return None
            
        except VelaFiError as e:
            logger.error(f"Error polling order {order.order_id}: {e}")
            
            # Retry with exponential backoff
            if retry_count < self.max_retries:
                delay = self.base_delay * (2 ** retry_count)
                logger.info(
                    f"Retrying order {order.order_id} in {delay} seconds "
                    f"(attempt {retry_count + 1}/{self.max_retries})"
                )
                await asyncio.sleep(delay)
                return await self._update_order_status(order, retry_count + 1)
            
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error polling order {order.order_id}: {e}")
            return None

    async def poll_pending_orders(self) -> None:
        """
        Poll VelaFi for updates on pending orders.
        
        This method:
        1. Finds pending/processing orders older than min_age_minutes
        2. Polls VelaFi API for current status
        3. Updates local order status if changed
        4. Retries failed requests with exponential backoff
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.min_age_minutes)
        
        try:
            # Get pending orders
            orders = await self._get_pending_orders(cutoff)
            if not orders:
                logger.debug("No pending orders to poll")
                return
                
            logger.info(f"Polling {len(orders)} pending orders")
            
            # Update each order's status
            for order in orders:
                await self._update_order_status(order)
                
        except Exception as e:
            logger.error(f"Error in poll_pending_orders: {e}")

async def run_monitor(poll_interval: int = None) -> None:
    """
    Run the VelaFi monitor as a background task.
    
    Args:
        poll_interval: Seconds between polling runs (defaults to settings.velafi_monitor_interval)
    """
    interval = poll_interval or settings.velafi_monitor_interval
    
    while True:
        try:
            async with get_db() as db:
                monitor = VelaFiMonitor(db)
                await monitor.poll_pending_orders()
        except Exception as e:
            logger.error(f"Monitor run failed: {e}")
        
        await asyncio.sleep(interval)