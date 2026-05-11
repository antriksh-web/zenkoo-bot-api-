from __future__ import annotations

from fastapi import APIRouter

from models.schemas import PresenceRequest
from services.presence_engine import presence_engine


router = APIRouter(tags=["presence"])


@router.post("/simulate-presence")
async def simulate_presence(payload: PresenceRequest) -> dict:
    events = await presence_engine.simulate(payload.room_id)
    return {"events": events}
