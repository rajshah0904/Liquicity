from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
import json
import os

# Mock data storage location
MOCK_DATA_FILE = "mock_wallet_data.json"

# Initialize router
router = APIRouter(prefix="/mock/wallet", tags=["mock"])

# Models
class BalanceSchema(BaseModel):
    usd: float = 0.0
    eur: float = 0.0

class TransferSchema(BaseModel):
    sender_email: EmailStr
    recipient_email: EmailStr
    amount: float  # amount taken from sender wallet
    currency: str  # currency of sender wallet amount (usd / eur)
    bank_amount: Optional[float] = 0  # additional amount coming from external bank (same currency)
    description: Optional[str] = None

# Helper to load mock data
def load_mock_data():
    if os.path.exists(MOCK_DATA_FILE):
        with open(MOCK_DATA_FILE, "r") as f:
            return json.load(f)
    
    # Default data
    default_data = {
        "users": {
            "rajshah11@gmail.com": {"usd": 1000.0, "eur": 0.0},
            "hadeermotair@gmail.com": {"usd": 0.0, "eur": 0.0},
            "user@example.com": {"usd": 500.0, "eur": 0.0}
        },
        "transactions": []
    }
    
    # Save default data
    with open(MOCK_DATA_FILE, "w") as f:
        json.dump(default_data, f, indent=2)
    
    return default_data

# Helper to save mock data
def save_mock_data(data):
    with open(MOCK_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Get all balances
@router.get("/balances")
async def get_balances():
    data = load_mock_data()
    return data["users"]

# Get a specific user's balance
@router.get("/balances/{email}")
async def get_user_balance(email: str):
    data = load_mock_data()
    if email not in data["users"]:
        data["users"][email] = {"usd": 0.0, "eur": 0.0}
        save_mock_data(data)
    
    return data["users"][email]

# Update a user's balance
@router.post("/balances/{email}")
async def update_user_balance(email: str, balance: BalanceSchema):
    data = load_mock_data()
    data["users"][email] = balance.dict()
    save_mock_data(data)
    return data["users"][email]

# Process a transfer between users
@router.post("/transfer")
async def transfer_funds(transfer: TransferSchema):
    # Constants
    USD_TO_EUR_RATE = 0.9
    CURRENCY_CONVERSION_FEE = 0.02
    
    data = load_mock_data()
    
    # Validate sender and recipient
    if transfer.sender_email not in data["users"]:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    if transfer.recipient_email not in data["users"]:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    sender = data["users"][transfer.sender_email]
    recipient = data["users"][transfer.recipient_email]
    
    sender_currency = transfer.currency.lower()
    wallet_amount = transfer.amount
    bank_amount = transfer.bank_amount or 0
    total_send = wallet_amount + bank_amount

    # Check if sender has enough wallet balance
    if sender_currency not in sender or sender[sender_currency] < wallet_amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process transfer
    # Deduct wallet part from sender + wallet fee (0.5%)
    wallet_fee = wallet_amount * 0.005
    sender[sender_currency] -= (wallet_amount + wallet_fee)
    
    # Determine recipient currency (Hadeer -> eur else same as sender)
    if transfer.recipient_email == "hadeermotair@gmail.com":
        recipient_currency = "eur"
        
        # Helper to convert usd->eur as needed
        def convert_to_eur(amt_usd: float):
            conversion_fee = amt_usd * CURRENCY_CONVERSION_FEE
            return (amt_usd - conversion_fee) * USD_TO_EUR_RATE

        if sender_currency == "usd":
            recipient[recipient_currency] += convert_to_eur(wallet_amount)
        else:
            recipient[recipient_currency] += wallet_amount  # unlikely path

        # Add bank_amount if any
        if bank_amount > 0:
            if sender_currency == "usd":
              recipient[recipient_currency] += convert_to_eur(bank_amount)
            else:
              recipient[recipient_currency] += bank_amount
    else:
        recipient_currency = sender_currency
        recipient[recipient_currency] += wallet_amount + bank_amount
    
    # Record transaction
    transaction = {
        "sender": transfer.sender_email,
        "recipient": transfer.recipient_email,
        "amount": total_send,
        "sender_currency": sender_currency.upper(),
        "recipient_currency": recipient_currency.upper(),
        "description": transfer.description or f"Transfer from {transfer.sender_email} to {transfer.recipient_email}"
    }
    
    data["transactions"].append(transaction)
    
    # Save changes
    save_mock_data(data)
    
    return {
        "success": True,
        "transaction": transaction,
        "sender_balance": sender,
        "recipient_balance": recipient
    } 