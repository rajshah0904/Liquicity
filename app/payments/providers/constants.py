from enum import Enum, auto

class TransactionType(str, Enum):
    """Enum for transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    """Enum for transaction statuses"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    PROCESSING = "processing" 

class TransactionType(str, Enum):
    """Enum for transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    """Enum for transaction statuses"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    PROCESSING = "processing" 