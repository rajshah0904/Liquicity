import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List
from clean_backend.models import Transaction
from clean_backend.services.walletconnect_service import WalletConnectV2Service

logger = logging.getLogger(__name__)

class TransactionMonitorService:
    """Background service for monitoring transaction statuses and updating them"""
    
    def __init__(self, db: Session, walletconnect_service: WalletConnectV2Service):
        self.db = db
        self.walletconnect_service = walletconnect_service
        self.is_running = False
        self.monitor_task = None
    
    async def start_monitoring(self):
        """Start the background monitoring task"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Transaction monitoring started")
    
    async def stop_monitoring(self):
        """Stop the background monitoring task"""
        self.is_running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Transaction monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                await self._check_pending_transactions()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in transaction monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_pending_transactions(self):
        """Check and update status of pending transactions"""
        # Get all pending transactions
        pending_transactions = self.db.query(Transaction).filter(
            Transaction.status == "pending"
        ).all()
        
        for transaction in pending_transactions:
            try:
                # Skip transactions without hash
                if not transaction.tx_hash:
                    continue
                
                # Check if transaction is confirmed
                confirmed = await self.walletconnect_service.check_transaction_confirmation(
                    transaction.tx_hash, 
                    transaction.chain_type
                )
                
                if confirmed:
                    transaction.status = "confirmed"
                    transaction.confirmed_at = datetime.utcnow()
                    self.db.commit()
                    logger.info(f"Transaction {transaction.id} confirmed")
                
                # Check for timeout (1 hour)
                time_diff = datetime.utcnow() - transaction.created_at
                if time_diff.total_seconds() > 3600 and transaction.status == "pending":
                    transaction.status = "failed"
                    self.db.commit()
                    logger.warning(f"Transaction {transaction.id} marked as failed due to timeout")
                    
            except Exception as e:
                logger.error(f"Error checking transaction {transaction.id}: {e}")
    
    async def update_single_transaction(self, transaction_id: str) -> bool:
        """Update a single transaction status"""
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction or not transaction.tx_hash:
            return False
        
        try:
            confirmed = await self.walletconnect_service.check_transaction_confirmation(
                transaction.tx_hash, 
                transaction.chain_type
            )
            
            if confirmed and transaction.status == "pending":
                transaction.status = "confirmed"
                transaction.confirmed_at = datetime.utcnow()
                self.db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating transaction {transaction_id}: {e}")
        
        return False

# Global monitor instance
transaction_monitor = None

async def start_transaction_monitor(db: Session, walletconnect_service: WalletConnectV2Service):
    """Start the global transaction monitor"""
    global transaction_monitor
    if transaction_monitor is None:
        transaction_monitor = TransactionMonitorService(db, walletconnect_service)
        await transaction_monitor.start_monitoring()

async def stop_transaction_monitor():
    """Stop the global transaction monitor"""
    global transaction_monitor
    if transaction_monitor:
        await transaction_monitor.stop_monitoring()
        transaction_monitor = None 