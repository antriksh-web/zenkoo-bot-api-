from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter

from models.schemas import ReplyRequest, ReplyResponse
from services.state_store import state_store
from services.room_engine import room_engine
from services.memory_engine import memory_engine
from services.decision_engine import decision_engine
from services.chatter_engine import chatter_engine
from services.timing_engine import timing_engine
from services.scheduler_engine import scheduler_engine
from services.relationship_engine import relationship_engine
from services.typing_engine import typing_engine
from utils.formatting import stylize_text


router = APIRouter(tags=["messages"])


@router.post("/generate-reply", response_model=ReplyResponse)
async def generate_reply(payload: ReplyRequest) -> ReplyResponse:
    room = await state_store.get_room(payload.room_id)
    await room_engine.update_from_message(payload.room_id, payload.message)
    
    # Always remember the incoming message
    await memory_engine.remember_interaction(payload.room_id, payload.username, payload.message, importance=0.4)

    bots = [b for b in await state_store.list_bots() if payload.room_id in b.favorite_rooms]
    if not bots:
        return ReplyResponse()

    best = None
    best_score = -1.0
    for bot in bots:
        engage, score = await decision_engine.should_engage(bot, room, payload.username, payload.message)
        if engage and score > best_score:
            best = bot
            best_score = score

    if best is None:
        return ReplyResponse(will_send=False)

    action = decision_engine.pick_action(best_score)
    if action == "ignore":
        return ReplyResponse(will_send=False)

    if action == "reaction":
        reaction = chatter_engine.generate_reaction(room)
        return ReplyResponse(bot=best.id, reply=reaction, typing_delay=0, will_send=True)

    draft = await chatter_engine.generate_reply(best, room, payload.message, action, image_url=payload.image_url)
    reply = stylize_text(draft, best.typing_style, best.grammar_quality, best.emoji_usage)
    typing_delay = timing_engine.compose_delay(best, room, payload.message, reply)
    scheduled = await scheduler_engine.schedule_message(payload.room_id, best.username, reply, typing_delay)

    if action == "typing_cancel":
        await scheduler_engine.cancel(scheduled.id)
        return ReplyResponse(will_send=False)

    await memory_engine.remember_interaction(payload.room_id, best.id, reply, importance=0.6)
    await relationship_engine.update_after_interaction(best.id, payload.username, sentiment=0.1)

    best.last_active_at = datetime.utcnow()
    await state_store.save_bot(best)

    _ = typing_engine.typing_events(best.id, payload.room_id, typing_delay)
    return ReplyResponse(bot=best.username, reply=reply, typing_delay=typing_delay, will_send=True)
