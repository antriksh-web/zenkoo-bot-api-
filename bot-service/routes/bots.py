from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter

from services.state_store import state_store


router = APIRouter(tags=["bots"])


@router.get("/active-bots")
async def active_bots() -> dict:
    bots = await state_store.list_bots()
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    active = [b.id for b in bots if b.last_active_at and b.last_active_at > cutoff]
    lurking = [b.id for b in bots if b.id not in active]
    return {"active": active, "lurking": lurking, "count": len(active)}
