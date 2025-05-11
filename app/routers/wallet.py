from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.bridge import BridgeClient
from typing import List, Dict, Any

router = APIRouter()

# --- Helpers ---

def _local_currency_for_country(country_code: str | None) -> str:
    if not country_code:
        return "usd"
    cc = country_code.upper()
    if cc == "US":
        return "usd"
    if cc in {"AT","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB","GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK"}:
        return "eur"
    if cc == "MX":
        return "mxn"
    return "usd"

# --- Endpoints ---

@router.get("/overview", tags=["wallet"])
async def wallet_overview(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Return current balances in local currency plus recent wallet transactions (card spends, withdrawals, etc.)."""
    # Look up user row
    row = db.execute(text("SELECT id, bridge_customer_id, country FROM users WHERE email = :id OR auth0_id = :id"), {"id": current_user}).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    _, cust_id, country = row
    if not cust_id:
        return {"wallets": [], "transactions": []}

    client = BridgeClient()

    # 1. Wallet balances
    wallets_raw: List[Dict[str, Any]] = await client.list_wallets(cust_id)
    local_curr = _local_currency_for_country(country)
    wallets: List[Dict[str, Any]] = []
    for w in wallets_raw:
        rate_data = await client.get_exchange_rate(w.get("currency"), local_curr)
        rate = float(rate_data.get("rate", 1)) if rate_data else 1.0
        balance = float(w.get("balance", 0))
        wallets.append({
            "wallet_id": w.get("id"),
            "currency": w.get("currency"),
            "balance": balance,
            "local_currency": local_curr,
            "local_balance": balance * rate,
        })

    # 2. Recent transactions (last 100 across all wallets)
    txns: List[Dict[str, Any]] = []
    for w in wallets_raw:
        history = await client.wallet_history(w.get("id"))
        for tx in history.get("resources", []):
            txns.append({
                "wallet_id": w.get("id"),
                "transaction_id": tx.get("id"),
                "amount": tx.get("amount"),
                "currency": tx.get("currency_code"),
                "description": tx.get("clean_description"),
                "date": tx.get("date"),
            })
    # Sort transactions by date desc
    txns.sort(key=lambda t: t.get("date"), reverse=True)

    return {"wallets": wallets, "transactions": txns[:100]}

@router.get("/{user_id}", tags=["wallet"], include_in_schema=False)
async def wallet_overview_by_id(user_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # For now this is just an alias to /wallet/overview ignoring the param.
    return await wallet_overview(db, current_user)

@router.get("/transactions", tags=["wallet"])
async def wallet_transactions(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    row = db.execute(text("SELECT id, bridge_customer_id FROM users WHERE email = :id OR auth0_id = :id"),{"id":current_user}).first()
    if not row or not row[1]:
        raise HTTPException(status_code=404, detail="User not found or no Bridge customer")
    cust_id = row[1]
    client = BridgeClient()
    wallets_raw = await client.list_wallets(cust_id)
    txns: List[Dict[str, Any]] = []
    for w in wallets_raw:
        history = await client.wallet_history(w.get("id"))
        for tx in history.get("resources", []):
            txns.append({
                "wallet_id": w.get("id"),
                "transaction_id": tx.get("id"),
                "amount": tx.get("amount"),
                "currency": tx.get("currency_code"),
                "description": tx.get("clean_description"),
                "date": tx.get("date"),
            })
    txns.sort(key=lambda t: t.get("date"), reverse=True)
    return {"transactions": txns[:500]} 