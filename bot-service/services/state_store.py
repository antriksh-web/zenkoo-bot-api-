from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path

from models.schemas import BotProfile, MemoryEntry, RelationshipEdge, RoomState


class InMemoryStateStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.bots: dict[str, BotProfile] = {}
        self.rooms: dict[str, RoomState] = {}
        self.relationships: dict[tuple[str, str], RelationshipEdge] = {}
        self.memories: dict[str, list[MemoryEntry]] = {}

    async def bootstrap(self) -> None:
        personalities_dir = Path(__file__).resolve().parents[1] / "personalities"
        async with self._lock:
            for file in personalities_dir.glob("*.json"):
                data = json.loads(file.read_text(encoding="utf-8"))
                bot = BotProfile(**data)
                self.bots[bot.id] = bot

            for room_id in {"general", "gaming", "anime", "night"}:
                self.rooms.setdefault(room_id, RoomState(room_id=room_id))

        # Hydrate relationships from Google Sheets in parallel
        from services.apps_script_memory import apps_script_memory_store
        if await apps_script_memory_store.is_available():
            async def hydrate_bot(bot_id: str):
                rels = await apps_script_memory_store.get_relationships(bot_id)
                for r in rels:
                    self.relationships[(r.source_bot, r.target_bot)] = r
            
            try:
                await asyncio.wait_for(
                    asyncio.gather(*(hydrate_bot(bid) for bid in self.bots)),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                from services.apps_script_memory import logger
                logger.warning("Google Sheets relationship hydration timed out - starting with empty state")

    async def get_bot(self, bot_id: str) -> BotProfile | None:
        return self.bots.get(bot_id)

    async def list_bots(self) -> list[BotProfile]:
        return list(self.bots.values())

    async def save_bot(self, bot: BotProfile) -> None:
        async with self._lock:
            self.bots[bot.id] = bot

    async def get_room(self, room_id: str) -> RoomState:
        if room_id not in self.rooms:
            self.rooms[room_id] = RoomState(room_id=room_id)
        return self.rooms[room_id]

    async def save_room(self, room: RoomState) -> None:
        async with self._lock:
            self.rooms[room.room_id] = room

    async def all_rooms(self) -> list[RoomState]:
        return list(self.rooms.values())

    async def get_relationship(self, source: str, target: str) -> RelationshipEdge:
        key = (source, target)
        rel = self.relationships.get(key)
        if rel is None:
            rel = RelationshipEdge(source_bot=source, target_bot=target, friendship=0.0, trust=0.5, respect=0.5)
            self.relationships[key] = rel
        return rel

    async def upsert_relationship(self, rel: RelationshipEdge) -> None:
        async with self._lock:
            self.relationships[(rel.source_bot, rel.target_bot)] = rel

    async def append_memory(self, memory_key: str, text: str, importance: float = 0.5) -> None:
        entry = MemoryEntry(scope="social", key=memory_key, text=text, importance=importance, created_at=datetime.utcnow())
        self.memories.setdefault(memory_key, []).append(entry)
        self.memories[memory_key] = self.memories[memory_key][-40:]

    async def get_memories(self, memory_key: str) -> list[MemoryEntry]:
        return self.memories.get(memory_key, [])


state_store = InMemoryStateStore()
