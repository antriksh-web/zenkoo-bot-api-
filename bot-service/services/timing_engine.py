from __future__ import annotations

import random

from models.schemas import BotProfile, RoomState
from utils.delays import reading_delay_ms, thinking_delay_ms, typing_delay_ms


class TimingEngine:
    def compose_delay(self, bot: BotProfile, room: RoomState, incoming_message: str, reply: str) -> int:
        read = reading_delay_ms(len(incoming_message), bot.activity_level)
        think = thinking_delay_ms(bot.confidence, room.tension)
        typing = typing_delay_ms(len(reply), bot.typing_style)
        distraction = random.randint(0, 1800) if random.random() < (1 - bot.patience) * 0.45 else 0
        return read + think + typing + distraction


timing_engine = TimingEngine()
