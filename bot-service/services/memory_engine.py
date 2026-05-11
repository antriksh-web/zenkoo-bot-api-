from __future__ import annotations

from services.apps_script_memory import apps_script_memory_store
from services.google_sheets_memory import google_sheets_memory_store
from services.state_store import state_store


class MemoryEngine:
    async def remember_interaction(self, room_id: str, actor: str, text: str, importance: float = 0.5) -> None:
        room_key = f"room:{room_id}"
        bot_key = f"bot:{actor}"

        await state_store.append_memory(room_key, f"{actor}: {text}", importance=importance)
        await state_store.append_memory(bot_key, text, importance=importance)

        await apps_script_memory_store.append_memory(
            scope="room",
            memory_key=room_key,
            text=f"{actor}: {text}",
            importance=importance,
        )
        await apps_script_memory_store.append_memory(
            scope="bot",
            memory_key=bot_key,
            text=text,
            importance=importance,
        )

        await google_sheets_memory_store.append_memory(
            scope="room",
            memory_key=room_key,
            text=f"{actor}: {text}",
            importance=importance,
        )
        await google_sheets_memory_store.append_memory(
            scope="bot",
            memory_key=bot_key,
            text=text,
            importance=importance,
        )

    async def recent_room_context(self, room_id: str, limit: int = 6) -> list[str]:
        room_key = f"room:{room_id}"
        app_script_memories = await apps_script_memory_store.recent_memories(room_key, limit=limit)
        if app_script_memories:
            return [m.text for m in app_script_memories]

        sheet_memories = await google_sheets_memory_store.recent_memories(room_key, limit=limit)
        if sheet_memories:
            return [m.text for m in sheet_memories]

        memories = await state_store.get_memories(room_key)
        return [m.text for m in memories[-limit:]]


memory_engine = MemoryEngine()
