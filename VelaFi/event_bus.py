"""Simple event bus abstraction.

In production replace `publish` with real message broker integration (e.g. Redis
Pub/Sub, NATS, Kafka). Modules call `publish(topic, payload)` without worrying
about transport details.
"""

import json
import logging
from typing import Any, Dict

_log = logging.getLogger(__name__)


def publish(topic: str, payload: Dict[str, Any]) -> None:  # noqa: D401
    """Publish an event to internal subscribers (stub).

    Currently logs the message so that integrators can verify flow. Replace
    with actual broker call when ready.
    """
    _log.info("EVENT %s: %s", topic, json.dumps(payload, default=str)) 