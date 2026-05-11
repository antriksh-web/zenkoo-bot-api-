from __future__ import annotations

import random

from services.state_store import state_store
from utils.randomness import clamp


class RoomEngine:
    async def update_from_message(self, room_id: str, message: str) -> None:
        room = await state_store.get_room(room_id)
        room.activity_level = clamp(room.activity_level + 0.08)
        if any(word in message.lower() for word in ["fight", "trash", "hate", "loser"]):
            room.tension = clamp(room.tension + 0.1)
            room.recent_arguments = (room.recent_arguments + [message])[-10:]
        elif any(word in message.lower() for word in ["lol", "lmao", "haha", "??"]):
            room.humor_level = clamp(room.humor_level + 0.08)

        tokens = [t for t in message.lower().split() if len(t) > 3]
        if tokens:
            room.current_topic = random.choice(tokens)

        await state_store.save_room(room)

    async def natural_decay(self) -> None:
        for room in await state_store.all_rooms():
            room.activity_level = clamp(room.activity_level - 0.03)
            room.tension = clamp(room.tension - 0.02)
            room.humor_level = clamp(room.humor_level - 0.01)
            await state_store.save_room(room)


room_engine = RoomEngine()
