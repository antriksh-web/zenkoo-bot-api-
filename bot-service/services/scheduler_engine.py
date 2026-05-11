from __future__ import annotations

import asyncio
import heapq
import random
import uuid
from datetime import datetime, timedelta

from models.schemas import ScheduledMessage


class SchedulerEngine:
    def __init__(self) -> None:
        self._queue: list[tuple[float, ScheduledMessage]] = []
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self._running = False
        self.sent_messages: list[dict] = []
        self.typing_bots: dict[str, set[str]] = {} # room_id -> set(bot_names)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._dispatch_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def schedule_message(self, room_id: str, bot_name: str, text: str, delay_ms: int) -> ScheduledMessage:
        due = datetime.utcnow() + timedelta(milliseconds=delay_ms)
        msg = ScheduledMessage(id=str(uuid.uuid4()), room_id=room_id, bot_name=bot_name, text=text, due_at=due, typing_delay_ms=delay_ms)
        async with self._lock:
            heapq.heappush(self._queue, (due.timestamp(), msg))
            # Track as typing
            if room_id not in self.typing_bots:
                self.typing_bots[room_id] = set()
            self.typing_bots[room_id].add(bot_name)
        return msg

    async def cancel(self, message_id: str) -> bool:
        async with self._lock:
            for _, msg in self._queue:
                if msg.id == message_id:
                    msg.cancelled = True
                    # Remove from typing
                    if msg.room_id in self.typing_bots:
                        self.typing_bots[msg.room_id].discard(msg.bot_name)
                    return True
        return False

    async def pending(self) -> list[ScheduledMessage]:
        async with self._lock:
            return [m for _, m in self._queue if not m.cancelled]

    async def _dispatch_loop(self) -> None:
        while self._running:
            await asyncio.sleep(0.2)
            now = datetime.utcnow().timestamp()
            due_batch: list[ScheduledMessage] = []
            async with self._lock:
                while self._queue and self._queue[0][0] <= now:
                    _, msg = heapq.heappop(self._queue)
                    due_batch.append(msg)
                    # No longer typing once it's about to be sent
                    if msg.room_id in self.typing_bots:
                        self.typing_bots[msg.room_id].discard(msg.bot_name)

            for msg in due_batch:
                if msg.cancelled:
                    continue
                
                sent_msg = {
                    "id": msg.id,
                    "room_id": msg.room_id,
                    "bot": msg.bot_name,
                    "reply": msg.text,
                    "sent_at": datetime.utcnow().isoformat(),
                }
                self.sent_messages.append(sent_msg)
                self.sent_messages = self.sent_messages[-200:]

                # ── Trigger secondary bot response ──
                # This allows bots to talk to each other
                depth = getattr(msg, "depth", 0)
                # High chance for first bot-to-bot interaction (95%), then decay
                if random.random() < (0.95 / (depth + 1)):
                    asyncio.create_task(self._trigger_secondary_response(msg.room_id, msg.bot_name, msg.text, depth + 1))

    async def _trigger_secondary_response(self, room_id: str, sender_name: str, message: str, depth: int = 0) -> None:
        """Allow other bots to react to a bot that just spoke."""
        from services.state_store import state_store
        from services.decision_engine import decision_engine
        from services.chatter_engine import chatter_engine
        from services.timing_engine import timing_engine
        from utils.formatting import stylize_text

        # Natural delay
        await asyncio.sleep(random.uniform(2.5, 6.0))
        
        room = await state_store.get_room(room_id)
        # All bots except the one who just spoke
        bots = [b for b in await state_store.list_bots() if room_id in b.favorite_rooms and b.username != sender_name]
        
        # Shuffle so the same bot doesn't always hog the conversation
        random.shuffle(bots)

        for bot in bots:
            engage, score = await decision_engine.should_engage(bot, room, sender_name, message)
            
            # Use a more reasonable threshold for bot-to-bot (0.5 instead of 0.75)
            if engage and score > 0.5:
                action = decision_engine.pick_action(score)
                if action in ["reply", "question", "interjection", "reaction", "short_reply"]:
                    from services.memory_engine import memory_engine
                    from services.relationship_engine import relationship_engine

                    draft = await chatter_engine.generate_reply(bot, room, message, action)
                    reply = stylize_text(draft, bot.typing_style, bot.grammar_quality, bot.emoji_usage)
                    typing_delay = timing_engine.compose_delay(bot, room, message, reply)
                    
                    # Store in memory so other bots can see it
                    await memory_engine.remember_interaction(room_id, bot.id, reply, importance=0.6)
                    # Improve relationship between bots
                    await relationship_engine.update_after_interaction(bot.id, sender_name, sentiment=0.1)

                    # Schedule the message
                    scheduled = await self.schedule_message(room_id, bot.username, reply, typing_delay)
                    scheduled.depth = depth
                    break # Only one bot per "turn" to keep it orderly


scheduler_engine = SchedulerEngine()
