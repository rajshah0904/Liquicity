"""Configuration for the event bus system."""

import os
from typing import Any, Dict


class EventBusConfig:
    """Configuration for the event bus system."""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
        
        # Event bus settings
        self.enable_redis = os.getenv("EVENT_BUS_ENABLE_REDIS", "true").lower() == "true"
        self.enable_local_events = os.getenv("EVENT_BUS_ENABLE_LOCAL", "true").lower() == "true"
        self.max_retries = int(os.getenv("EVENT_BUS_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("EVENT_BUS_RETRY_DELAY", "1.0"))
        
        # Event topics
        self.topics = {
            "order": {
                "completed": "order.completed",
                "status_changed": "order.status_changed",
                "failed": "order.failed",
                "processing": "order.processing"
            },
            "security": {
                "suspicious_activity": "security.suspicious_activity",
                "fraud_detected": "security.fraud_detected",
                "kyc_required": "security.kyc_required"
            },
            "payment": {
                "initiated": "payment.initiated",
                "completed": "payment.completed",
                "failed": "payment.failed",
                "refunded": "payment.refunded"
            },
            "wallet": {
                "created": "wallet.created",
                "linked": "wallet.linked",
                "balance_changed": "wallet.balance_changed"
            },
            "bridge": {
                "transfer_initiated": "bridge.transfer_initiated",
                "transfer_completed": "bridge.transfer_completed",
                "transfer_failed": "bridge.transfer_failed"
            }
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        config = {
            "url": self.redis_url,
            "db": self.redis_db,
            "max_connections": self.redis_max_connections
        }
        
        if self.redis_password:
            config["password"] = self.redis_password
        
        return config
    
    def get_topic(self, category: str, event: str) -> str:
        """Get topic name for a category and event."""
        return self.topics.get(category, {}).get(event, f"{category}.{event}")
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

# Global configuration instance
config = EventBusConfig() 