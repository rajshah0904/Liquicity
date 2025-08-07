"""Production-ready event bus abstraction.

Supports Redis Pub/Sub for distributed event handling with fallback to logging.
Modules call `publish(topic, payload)` without worrying about transport details.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import redis.asyncio as redis

_log = logging.getLogger(__name__)

@dataclass
class EventMessage:
    """Structured event message with metadata."""
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime
    message_id: str
    source: str = "velafi"
    version: str = "1.0"

class EventBus:
    """Production event bus with Redis Pub/Sub support."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379"
        self.redis_client: Optional[redis.Redis] = None
        self.local_subscribers: Dict[str, List[Callable]] = {}
        self._connection_healthy = False
        
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            self._connection_healthy = True
            _log.info("EventBus: Redis connection established")
        except Exception as e:
            _log.warning(f"EventBus: Redis connection failed, falling back to local events: {e}")
            self._connection_healthy = False
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self._connection_healthy = False
            _log.info("EventBus: Redis connection closed")
    
    async def publish(self, topic: str, payload: Dict[str, Any], 
                     message_id: Optional[str] = None) -> None:
        """Publish event to Redis and local subscribers."""
        event = EventMessage(
            topic=topic,
            payload=payload,
            timestamp=datetime.utcnow(),
            message_id=message_id or f"{topic}_{datetime.utcnow().timestamp()}"
        )
        
        # Always log for debugging
        _log.info("EVENT %s: %s", topic, json.dumps(payload, default=str))
        
        # Publish to Redis if available
        if self._connection_healthy and self.redis_client:
            try:
                message = json.dumps({
                    "topic": event.topic,
                    "payload": event.payload,
                    "timestamp": event.timestamp.isoformat(),
                    "message_id": event.message_id,
                    "source": event.source,
                    "version": event.version
                })
                await self.redis_client.publish(topic, message)
                _log.debug(f"EventBus: Published to Redis topic '{topic}'")
            except Exception as e:
                _log.error(f"EventBus: Redis publish failed: {e}")
                self._connection_healthy = False
        
        # Notify local subscribers
        await self._notify_local_subscribers(event)
    
    def subscribe(self, topic: str, handler: Callable[[EventMessage], None]) -> None:
        """Subscribe to local events (for in-process handlers)."""
        if topic not in self.local_subscribers:
            self.local_subscribers[topic] = []
        self.local_subscribers[topic].append(handler)
        _log.info(f"EventBus: Local subscriber added for topic '{topic}'")
    
    async def _notify_local_subscribers(self, event: EventMessage) -> None:
        """Notify local subscribers of an event."""
        if event.topic in self.local_subscribers:
            for handler in self.local_subscribers[event.topic]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    _log.error(f"EventBus: Local subscriber error for topic '{event.topic}': {e}")




        
    
    async def subscribe_redis(self, topic: str, handler: Callable[[EventMessage], None]) -> None:
        """Subscribe to Redis events (for distributed handlers)."""
        if not self._connection_healthy or not self.redis_client:
            _log.warning(f"EventBus: Cannot subscribe to Redis topic '{topic}' - no connection")
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(topic)
            
            async def listen():
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            event = EventMessage(
                                topic=data["topic"],
                                payload=data["payload"],
                                timestamp=datetime.fromisoformat(data["timestamp"]),
                                message_id=data["message_id"],
                                source=data.get("source", "unknown"),
                                version=data.get("version", "1.0")
                            )
                            if asyncio.iscoroutinefunction(handler):
                                await handler(event)
                            else:
                                handler(event)
                        except Exception as e:
                            _log.error(f"EventBus: Redis subscriber error for topic '{topic}': {e}")
            
            asyncio.create_task(listen())
            _log.info(f"EventBus: Redis subscriber added for topic '{topic}'")
            
        except Exception as e:
            _log.error(f"EventBus: Failed to subscribe to Redis topic '{topic}': {e}")

# Global event bus instance
_event_bus = EventBus()

async def initialize_event_bus(redis_url: Optional[str] = None) -> None:
    """Initialize the global event bus."""
    global _event_bus
    _event_bus = EventBus(redis_url)
    await _event_bus.connect()

async def shutdown_event_bus() -> None:
    """Shutdown the global event bus."""
    await _event_bus.disconnect()

def publish(topic: str, payload: Dict[str, Any], message_id: Optional[str] = None) -> None:
    """Publish an event (synchronous wrapper for async publish)."""
    asyncio.create_task(_event_bus.publish(topic, payload, message_id))

async def publish_async(topic: str, payload: Dict[str, Any], message_id: Optional[str] = None) -> None:
    """Publish an event asynchronously."""
    await _event_bus.publish(topic, payload, message_id)

def subscribe(topic: str, handler: Callable[[EventMessage], None]) -> None:
    """Subscribe to local events."""
    _event_bus.subscribe(topic, handler)

async def subscribe_redis(topic: str, handler: Callable[[EventMessage], None]) -> None:
    """Subscribe to Redis events."""
    await _event_bus.subscribe_redis(topic, handler)

@asynccontextmanager
async def event_bus_context(redis_url: Optional[str] = None):
    """Context manager for event bus lifecycle."""
    await initialize_event_bus(redis_url)
    try:
        yield _event_bus
    finally:
        await shutdown_event_bus() 

    