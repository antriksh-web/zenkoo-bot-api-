from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from models.schemas import MemoryEntry, RelationshipEdge, RoomState

logger = logging.getLogger(__name__)

class AppsScriptMemoryStore:
    def __init__(self) -> None:
        self.enabled = os.getenv("APPS_SCRIPT_MEMORY_ENABLED", "false").lower() == "true"
        self.web_app_url = os.getenv("APPS_SCRIPT_MEMORY_URL", "").strip()
        self.timeout_seconds = float(os.getenv("APPS_SCRIPT_MEMORY_TIMEOUT_SECONDS", "10.0"))

    async def is_available(self) -> bool:
        if not self.enabled or not self.web_app_url or "YOUR_DEPLOYED_WEB_APP_URL" in self.web_app_url:
            return False
        return True

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not await self.is_available():
            return None
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                response = await client.post(self.web_app_url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Apps Script error: {e}")
            return None

    # ── Memories ──────────────────────────────────────────────────────────
    async def append_memory(self, scope: str, memory_key: str, text: str, importance: float = 0.5) -> None:
        payload = {
            "action": "appendMemory",
            "scope": scope,
            "memory_key": memory_key,
            "text": text,
            "importance": importance,
        }
        await self._post(payload)

    async def recent_memories(self, memory_key: str, limit: int = 6) -> list[MemoryEntry]:
        payload = {
            "action": "recentMemories",
            "memory_key": memory_key,
            "limit": limit,
        }
        body = await self._post(payload)
        if not body or not body.get("ok"):
            return []

        memories = body.get("memories", [])
        out: list[MemoryEntry] = []
        for item in memories:
            try:
                raw_ts = str(item.get("timestamp", ""))
                created_at = datetime.now(timezone.utc)
                if raw_ts:
                    # Simple date parsing for Sheets ISO format
                    created_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                out.append(
                    MemoryEntry(
                        scope=str(item.get("scope", "room")),
                        key=str(item.get("memory_key", memory_key)),
                        text=str(item.get("text", "")),
                        importance=float(item.get("importance", 0.5)),
                        created_at=created_at,
                    )
                )
            except Exception:
                continue
        return out

    # ── Relationships ─────────────────────────────────────────────────────
    async def upsert_relationship(self, rel: RelationshipEdge) -> None:
        payload = {
            "action": "upsertRelationship",
            "source_bot": rel.source_bot,
            "target_bot": rel.target_bot,
            "friendship": rel.friendship,
            "trust": rel.trust,
            "respect": rel.respect,
            "interaction_count": rel.interaction_frequency
        }
        await self._post(payload)

    async def get_relationships(self, source_bot: str) -> list[RelationshipEdge]:
        payload = {
            "action": "getRelationships",
            "source_bot": source_bot
        }
        body = await self._post(payload)
        if not body or not body.get("ok"):
            return []

        rels = body.get("relationships", [])
        out = []
        for r in rels:
            out.append(RelationshipEdge(
                source_bot=r["source_bot"],
                target_bot=r["target_bot"],
                friendship=r["friendship"],
                trust=r["trust"],
                respect=r["respect"],
                interaction_frequency=r["interaction_count"]
            ))
        return out

    # ── Rooms ─────────────────────────────────────────────────────────────
    async def snapshot_room(self, room: RoomState) -> None:
        payload = {
            "action": "snapshotRoom",
            "room_id": room.room_id,
            "activity_level": room.activity_level,
            "current_topic": room.current_topic,
            "tension": room.tension
        }
        await self._post(payload)

    async def get_room_snapshot(self, room_id: str) -> dict[str, Any] | None:
        payload = {
            "action": "getRoom",
            "room_id": room_id
        }
        body = await self._post(payload)
        if not body or not body.get("ok"):
            return None
        return body.get("room")

apps_script_memory_store = AppsScriptMemoryStore()
