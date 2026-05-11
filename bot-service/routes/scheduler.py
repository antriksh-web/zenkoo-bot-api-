from __future__ import annotations

from fastapi import APIRouter

from services.scheduler_engine import scheduler_engine
from services.room_engine import room_engine


router = APIRouter(tags=["scheduler"])


@router.get("/scheduler/pending")
async def pending_messages() -> dict:
    pending = await scheduler_engine.pending()
    return {"pending": [p.model_dump() for p in pending]}


@router.get("/scheduler/sent")
async def sent_messages() -> dict:
    return {"sent": scheduler_engine.sent_messages[-100:]}


@router.get("/scheduler/typing/{room_id}")
async def typing_status(room_id: str) -> dict:
    typing = scheduler_engine.typing_bots.get(room_id, set())
    return {"typing": list(typing)}


@router.post("/scheduler/decay")
async def decay_rooms() -> dict:
    await room_engine.natural_decay()
    return {"status": "ok"}
