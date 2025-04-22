from typing import Protocol
from datetime import datetime

class BankAccount(Protocol):
    routing_number: str
    account_number: str
    country_code: str

class TransactionResult(Protocol):
    id: str
    status: str
    settled_at: datetime

class PaymentProvider(Protocol):
    async def pull(self, amount: float, currency: str, account: BankAccount) -> TransactionResult: ...
    async def push(self, amount: float, currency: str, account: BankAccount) -> TransactionResult: ... 