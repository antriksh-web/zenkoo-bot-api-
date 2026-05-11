from __future__ import annotations

import random
from datetime import datetime

from services.state_store import state_store
from services.chatter_engine import chatter_engine
from services.timing_engine import timing_engine
from services.scheduler_engine import scheduler_engine
from utils.formatting import stylize_text


class ActivityEngine:
    async def generate_room_activity(self, room_id: str) -> list[dict]:
        room = await state_store.get_room(room_id)
        bots = [b for b in await state_store.list_bots() if room_id in b.favorite_rooms]
        if not bots or random.random() < (0.45 - room.activity_level * 0.3):
            return [{"room_id": room_id, "event": "silence"}]

        sample_size = min(len(bots), random.randint(1, 2))
        picked = random.sample(bots, k=sample_size)
        out = []
        for bot in picked:
            reply = chatter_engine.generate_reply(bot, room, room.current_topic, "reply")
            reply = stylize_text(reply, bot.typing_style, bot.grammar_quality, bot.emoji_usage)
            delay = timing_engine.compose_delay(bot, room, room.current_topic, reply)
            scheduled = await scheduler_engine.schedule_message(room_id, bot.username, reply, delay)
            out.append({"room_id": room_id, "bot": bot.username, "reply": reply, "typing_delay": delay, "due_at": scheduled.due_at})
            bot.last_active_at = datetime.utcnow()
            await state_store.save_bot(bot)
        return out


activity_engine = ActivityEngine()
