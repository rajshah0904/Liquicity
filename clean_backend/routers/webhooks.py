from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.encumbrance_service import EncumbranceService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/bridge", status_code=202)
async def bridge_webhook(req: Request, db: Session = Depends(get_db)):
    """Generic webhook endpoint for Bridge events.

    We only care about transfer settlement events to either clear or recover
    outstanding encumbrances. Payload example:
    {
      "type": "transfer.succeeded",
      "data": { "id": "tr_123", ... }
    }
    """
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    evt_type = body.get("type")
    data = body.get("data") or {}
    transfer_id = data.get("id")
    if not evt_type or not transfer_id:
        raise HTTPException(status_code=400, detail="Missing fields in webhook")

    svc = EncumbranceService(db)

    if evt_type in {"transfer.succeeded", "transfer.settled"}:
        svc.clear_encumbrance(transfer_id)
    elif evt_type in {"transfer.failed", "transfer.returned"}:
        svc.recover_encumbrance(transfer_id)
    # else ignore

    return {"received": True} 