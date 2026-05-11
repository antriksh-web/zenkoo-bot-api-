from __future__ import annotations

import random
from datetime import datetime

from models.schemas import BotProfile, RoomState
from services.relationship_engine import relationship_engine


class DecisionEngine:
    async def should_engage(self, bot: BotProfile, room: RoomState, sender: str, message: str) -> tuple[bool, float]:
        hour = datetime.utcnow().hour
        asleep = self._is_sleeping(bot, hour)
        if asleep and random.random() < 0.85:
            return False, 0.0

        topic_interest = 1.0 if any(topic in message.lower() for topic in bot.favorite_topics) else 0.4
        relationship = await relationship_engine.affinity(bot.id, sender)
        room_pull = max(0.3, room.activity_level * bot.activity_level)
        boredom_drive = max(0.0, 1.0 - room.activity_level) * 0.5
        energy = bot.energy
        randomness = random.uniform(0.2, 1.0)  # always at least 0.2

        score = (
            0.28 * topic_interest
            + 0.15 * ((relationship + 1) / 2)
            + 0.18 * room_pull
            + 0.12 * boredom_drive
            + 0.12 * energy
            + 0.15 * randomness
        )
        threshold = 0.18 + room.tension * 0.05  # much lower threshold
        return score > threshold, score

    def pick_action(self, score: float) -> str:
        if score < 0.35:
            return random.choice(["reaction", "short_reply"])
        if score < 0.55:
            return random.choice(["short_reply", "reply", "reply"])
        return random.choice(["reply", "reply", "reply", "reaction"])

    @staticmethod
    def _is_sleeping(bot: BotProfile, hour: int) -> bool:
        start = bot.sleep_schedule.start
        end = bot.sleep_schedule.end
        if start < end:
            return start <= hour < end
        return hour >= start or hour < end


decision_engine = DecisionEngine()
