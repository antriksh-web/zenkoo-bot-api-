from __future__ import annotations

from fastapi import APIRouter

from models.schemas import RoomActivityRequest
from services.state_store import state_store
from services.activity_engine import activity_engine


router = APIRouter(tags=["rooms"])


@router.get("/room-state/{room_id}")
async def room_state(room_id: str) -> dict:
    room = await state_store.get_room(room_id)
    return room.model_dump()


@router.post("/generate-room-activity")
async def generate_room_activity(payload: RoomActivityRequest) -> dict:
    events = await activity_engine.generate_room_activity(payload.room_id)
    return {"events": events}
