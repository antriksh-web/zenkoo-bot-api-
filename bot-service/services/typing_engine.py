from __future__ import annotations

import random


class TypingEngine:
    def typing_events(self, bot_id: str, room_id: str, typing_delay: int) -> list[dict]:
        events = [{"room_id": room_id, "bot": bot_id, "event": "typing_start"}]
        if random.random() < 0.22:
            events.append({"room_id": room_id, "bot": bot_id, "event": "typing_stop"})
            events.append({"room_id": room_id, "bot": bot_id, "event": "typing_resume"})
        events.append({"room_id": room_id, "bot": bot_id, "event": "typing_end", "after_ms": typing_delay})
        return events


typing_engine = TypingEngine()
