from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from models.schemas import MemoryEntry


class GoogleSheetsMemoryStore:
    def __init__(self) -> None:
        self.enabled = os.getenv("GOOGLE_SHEETS_MEMORY_ENABLED", "false").lower() == "true"
        self.sheet_id = os.getenv("GOOGLE_SHEETS_MEMORY_SHEET_ID", "")
        self.credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "")
        self._client: Any | None = None
        self._lock = asyncio.Lock()
        self._initialized = False
        self._init_error: str | None = None

    async def initialize(self) -> None:
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            if not self.enabled:
                self._initialized = True
                return

            if not self.sheet_id or not self.credentials_path:
                self._init_error = "Google Sheets memory enabled but missing sheet id or credentials path."
                self._initialized = True
                return

            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            credentials = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
            self._client = build("sheets", "v4", credentials=credentials, cache_discovery=False)
            await self._ensure_headers()
            self._initialized = True

    async def is_available(self) -> bool:
        await self.initialize()
        return self.enabled and self._client is not None and self._init_error is None

    async def append_memory(self, scope: str, memory_key: str, text: str, importance: float = 0.5) -> None:
        if not await self.is_available():
            return

        now = datetime.now(timezone.utc).isoformat()
        row = [[now, scope, memory_key, text, str(importance)]]
        await asyncio.to_thread(
            self._client.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.sheet_id,
                range="memories!A:E",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": row},
            )
            .execute
        )

    async def recent_memories(self, memory_key: str, limit: int = 6) -> list[MemoryEntry]:
        if not await self.is_available():
            return []

        values = await asyncio.to_thread(
            self._client.spreadsheets()
            .values()
            .get(spreadsheetId=self.sheet_id, range="memories!A:E")
            .execute
        )
        rows = values.get("values", [])
        if len(rows) <= 1:
            return []

        matched: list[MemoryEntry] = []
        for row in rows[1:]:
            if len(row) < 5:
                continue
            timestamp, scope, key, text, importance = row[:5]
            if key != memory_key:
                continue
            try:
                created_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                importance_f = float(importance)
            except ValueError:
                continue
            matched.append(
                MemoryEntry(
                    scope=scope,
                    key=key,
                    text=text,
                    importance=importance_f,
                    created_at=created_at,
                )
            )

        return matched[-limit:]

    async def _ensure_headers(self) -> None:
        assert self._client is not None
        await asyncio.to_thread(
            self._client.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.sheet_id,
                range="memories!A1:E1",
                valueInputOption="RAW",
                body={"values": [["timestamp", "scope", "memory_key", "text", "importance"]]},
            )
            .execute
        )


google_sheets_memory_store = GoogleSheetsMemoryStore()
