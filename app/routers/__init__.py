from .user import router as user
from .wallet import router as wallet
from .bridge import router as bridge
from .transfer import router as transfer
from .notifications import router as notifications
from .requests import router as requests
from .demo import router as demo

__all__ = [
    "bridge",
    "user",
    "wallet",
    "transfer",
    "notifications",
    "requests",
    "demo",
]
