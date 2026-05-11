from __future__ import annotations

import random

from services.state_store import state_store


class PresenceEngine:
    async def simulate(self, room_id: str | None = None) -> list[dict]:
        events: list[dict] = []
        rooms = [await state_store.get_room(room_id)] if room_id else await state_store.all_rooms()
        bots = await state_store.list_bots()
        for room in rooms:
            for bot in random.sample(bots, k=min(len(bots), random.randint(1, 3))):
                event_type = random.choice(["join", "leave", "idle", "typing", "reaction"])
                events.append({"room_id": room.room_id, "bot": bot.id, "event": event_type})
        return events


presence_engine = PresenceEngine()
