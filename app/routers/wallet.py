from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.bridge import BridgeClient
from typing import List, Dict, Any
from pydantic import BaseModel

# WalletUpdate model for updating wallet settings
class WalletUpdate(BaseModel):
    display_currency: str = None
    base_currency: str = None
    country_code: str = None
    currency_settings: Dict[str, Any] = None

router = APIRouter()

# --- Helpers ---

def _local_currency_for_country(country_code: str | None) -> str:
    if not country_code:
        return "usd"
    cc = country_code.upper()
    if cc == "US":
        return "usd"
    if cc == "EU" or cc in {"AT","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB","GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK"}:
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

@router.put("/update/{user_id}", tags=["wallet"])
async def update_wallet(
    user_id: str, 
    wallet_data: WalletUpdate, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Update wallet settings for a user.
    """
    # Check if user exists
    user_row = db.execute(
        text("SELECT id FROM users WHERE (email = :id OR auth0_id = :id)"),
        {"id": current_user}
    ).first()
    
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Make sure user is updating their own wallet
    current_user_id = user_row[0]
    if str(current_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this wallet")
    
    # Check if wallet exists
    wallet_row = db.execute(
        text("SELECT id FROM wallets WHERE user_id = :user_id"),
        {"user_id": current_user_id}
    ).first()
    
    update_fields = []
    params = {"user_id": current_user_id}
    
    if wallet_data.display_currency:
        update_fields.append("display_currency = :display_currency")
        params["display_currency"] = wallet_data.display_currency.upper()
    
    if wallet_data.base_currency:
        update_fields.append("base_currency = :base_currency")
        params["base_currency"] = wallet_data.base_currency.upper()
    
    if wallet_data.country_code:
        update_fields.append("country_code = :country_code")
        params["country_code"] = wallet_data.country_code
    
    if wallet_data.currency_settings:
        import json
        update_fields.append("currency_settings = :currency_settings::json")
        params["currency_settings"] = json.dumps(wallet_data.currency_settings)
    
    if not update_fields:
        return {"message": "No changes to make"}
    
    if wallet_row:
        # Update existing wallet
        db.execute(
            text(f"UPDATE wallets SET {', '.join(update_fields)} WHERE user_id = :user_id"),
            params
        )
    else:
        # Create new wallet
        fields = ["user_id"]
        values = [":user_id"]
        
        if wallet_data.display_currency:
            fields.append("display_currency")
            values.append(":display_currency")
        
        if wallet_data.base_currency:
            fields.append("base_currency")
            values.append(":base_currency")
        
        if wallet_data.country_code:
            fields.append("country_code")
            values.append(":country_code")
        
        if wallet_data.currency_settings:
            fields.append("currency_settings")
            values.append(":currency_settings::json")
        
        db.execute(
            text(f"INSERT INTO wallets ({', '.join(fields)}) VALUES ({', '.join(values)})"),
            params
        )
    
    db.commit()
    
    # Update user's country if we're setting a display currency
    if wallet_data.display_currency:
        if wallet_data.display_currency.upper() == "EUR":
            db.execute(
                text("UPDATE users SET country = 'EU' WHERE id = :user_id"),
                {"user_id": current_user_id}
            )
            db.commit()
    
    return {"success": True, "message": "Wallet settings updated"} 