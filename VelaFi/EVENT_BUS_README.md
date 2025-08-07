# VelaFi Event Bus System

## Overview

The VelaFi Event Bus is a production-ready event-driven architecture that enables loose coupling between different components of the crypto payment system. It supports both local in-process events and distributed Redis Pub/Sub for scalable event handling.

## Key Features

### 🚀 **Production Ready**
- **Redis Pub/Sub Integration**: Distributed event handling across multiple services
- **Graceful Fallback**: Falls back to local events if Redis is unavailable
- **Async Support**: Full async/await support for high-performance event processing
- **Error Handling**: Comprehensive error handling and retry mechanisms

### 🔧 **Developer Friendly**
- **Simple API**: Easy-to-use `publish()` and `subscribe()` functions
- **Type Safety**: Full type hints and structured event messages
- **Configuration**: Environment-based configuration
- **Logging**: Detailed logging for debugging and monitoring

### 📊 **Observability**
- **Structured Logging**: JSON-formatted logs with metadata
- **Event Tracing**: Message IDs and timestamps for event tracking
- **Metrics**: Built-in metrics collection (coming soon)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Webhook       │    │   Order         │    │   Security      │
│   Handlers      │    │   Service       │    │   Service       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Event Bus            │
                    │  ┌─────────────────────┐  │
                    │  │   Local Events      │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │   Redis Pub/Sub     │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Event Handlers          │
                    │  ┌─────────────────────┐  │
                    │  │   Order Handler     │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │  Security Handler   │  │
                    │  └─────────────────────┘  │
                    │  ┌─────────────────────┐  │
                    │  │  Notification       │  │
                    │  │  Handler            │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Quick Start

### 1. Basic Usage

```python
from VelaFi.event_bus import publish, subscribe, EventMessage

# Subscribe to events
def handle_order_completed(event: EventMessage):
    print(f"Order {event.payload['order_id']} completed!")

subscribe("order.completed", handle_order_completed)

# Publish events
publish("order.completed", {
    "order_id": "ord_123",
    "user_id": "user_456",
    "usdc_amount": 100.50
})
```

### 2. Async Handlers

```python
async def handle_order_completed_async(event: EventMessage):
    # Process order asynchronously
    await process_order(event.payload)
    await send_notification(event.payload)

subscribe("order.completed", handle_order_completed_async)
```

### 3. Redis Integration

```python
from VelaFi.event_bus import initialize_event_bus, subscribe_redis

# Initialize with Redis
await initialize_event_bus("redis://localhost:6379")

# Subscribe to Redis events
await subscribe_redis("order.completed", handle_order_completed)
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_password
REDIS_DB=0
REDIS_MAX_CONNECTIONS=10

# Event Bus Settings
EVENT_BUS_ENABLE_REDIS=true
EVENT_BUS_ENABLE_LOCAL=true
EVENT_BUS_MAX_RETRIES=3
EVENT_BUS_RETRY_DELAY=1.0

# Environment
ENVIRONMENT=production
```

### Using Configuration

```python
from VelaFi.event_bus_config import config

# Get Redis config
redis_config = config.get_redis_config()

# Get topic names
topic = config.get_topic("order", "completed")  # "order.completed"

# Check environment
if config.is_production():
    # Production-specific logic
    pass
```

## Event Topics

### Order Events
- `order.completed` - Order successfully completed
- `order.status_changed` - Order status updated
- `order.failed` - Order failed
- `order.processing` - Order is being processed

### Security Events
- `security.suspicious_activity` - Suspicious activity detected
- `security.fraud_detected` - Fraud detected
- `security.kyc_required` - KYC verification required

### Payment Events
- `payment.initiated` - Payment initiated
- `payment.completed` - Payment completed
- `payment.failed` - Payment failed
- `payment.refunded` - Payment refunded

### Wallet Events
- `wallet.created` - New wallet created
- `wallet.linked` - Wallet linked to account
- `wallet.balance_changed` - Wallet balance updated

### Bridge Events
- `bridge.transfer_initiated` - Bridge transfer started
- `bridge.transfer_completed` - Bridge transfer completed
- `bridge.transfer_failed` - Bridge transfer failed

## Event Handlers

### Order Event Handler

```python
from VelaFi.event_handlers import OrderEventHandler

# Register handlers
order_handler = OrderEventHandler(db_session)
subscribe("order.completed", order_handler.handle_order_completed)
subscribe("order.status_changed", order_handler.handle_order_status_changed)
```

### Security Event Handler

```python
from VelaFi.event_handlers import SecurityEventHandler

# Register handlers
security_handler = SecurityEventHandler(db_session)
subscribe("security.suspicious_activity", security_handler.handle_suspicious_activity)
```

## Best Practices

### 1. **Event Design**
- Use descriptive topic names (e.g., `order.completed` not `order_done`)
- Include all necessary data in the payload
- Use consistent data structures across events

### 2. **Handler Design**
- Keep handlers focused and single-purpose
- Handle errors gracefully
- Use async handlers for I/O operations
- Log important events and errors

### 3. **Performance**
- Use Redis for high-throughput scenarios
- Implement proper error handling and retries
- Monitor event processing performance

### 4. **Testing**
- Test handlers in isolation
- Mock external dependencies
- Use event replay for testing

## Monitoring and Debugging

### Logging

Events are automatically logged with structured data:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "EVENT order.completed: {\"order_id\": \"ord_123\", \"user_id\": \"user_456\"}",
  "topic": "order.completed",
  "message_id": "order.completed_1705312200.123456"
}
```

### Metrics (Coming Soon)

- Event publish rate
- Event processing latency
- Error rates
- Redis connection health

## Migration from Old Event Bus

The new event bus is backward compatible. Your existing code will continue to work:

```python
# Old way (still works)
from VelaFi.event_bus import publish
publish("order.completed", {"order_id": "123"})

# New way (recommended)
from VelaFi.event_bus import publish_async
await publish_async("order.completed", {"order_id": "123"})
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check Redis server is running
   - Verify connection URL and credentials
   - Event bus will fall back to local events

2. **Events Not Being Processed**
   - Check handler registration
   - Verify topic names match
   - Check logs for errors

3. **Performance Issues**
   - Monitor Redis connection pool
   - Check handler processing time
   - Consider using async handlers

## Future Enhancements

- [ ] **Message Persistence**: Store events in database for replay
- [ ] **Event Schema Validation**: JSON schema validation for events
- [ ] **Dead Letter Queue**: Handle failed event processing
- [ ] **Event Replay**: Replay events for testing and recovery
- [ ] **Metrics Dashboard**: Real-time event metrics
- [ ] **Multi-Broker Support**: Kafka, NATS, RabbitMQ support 