from __future__ import annotations

from utils.randomness import clamp
from services.state_store import state_store


class RelationshipEngine:
    async def affinity(self, source_bot: str, target: str) -> float:
        rel = await state_store.get_relationship(source_bot, target)
        return clamp((rel.friendship + rel.trust + rel.respect) / 3.0, -1.0, 1.0)

    async def update_after_interaction(self, source_bot: str, target: str, sentiment: float) -> None:
        rel = await state_store.get_relationship(source_bot, target)
        rel.friendship = clamp(rel.friendship + sentiment * 0.08, -1.0, 1.0)
        rel.trust = clamp(rel.trust + sentiment * 0.04, 0.0, 1.0)
        rel.respect = clamp(rel.respect + sentiment * 0.03, 0.0, 1.0)
        rel.interaction_frequency += 1
        await state_store.upsert_relationship(rel)
        
        # Persist to Google Sheets
        from services.apps_script_memory import apps_script_memory_store
        await apps_script_memory_store.upsert_relationship(rel)


relationship_engine = RelationshipEngine()
