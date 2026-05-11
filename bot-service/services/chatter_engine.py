from __future__ import annotations

import os
import random
import logging

from dotenv import load_dotenv

from models.schemas import BotProfile, RoomState
from services.prompt_engine import prompt_engine

load_dotenv()  # loads GROQ_API_KEY from bot-service/.env

logger = logging.getLogger(__name__)

# ── Lazy-import Groq so the server still starts if the package is missing ──────
try:
    from groq import Groq as _GroqClient  # type: ignore

    _groq_client: _GroqClient | None = _GroqClient(
        api_key=os.environ.get("GROQ_API_KEY", "")
    )
except ImportError:
    _GroqClient = None  # type: ignore
    _groq_client = None
    logger.warning("groq package not installed — falling back to canned replies")

_GROQ_MODEL = "llama-3.1-8b-instant"
_OPENROUTER_MODEL = "openai/gpt-4o-mini"
_OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")


class ChatterEngine:
    CANNED = {
        "gaming": [
            "my ping is dying rn",
            "anyone queueing ranked or nah",
            "bro im getting rolled",
            "skill issue tbh",
        ],
        "anime": [
            "new ep was kinda fire",
            "nah that arc pacing was cursed",
            "im still behind dont spoil",
        ],
        "general": [
            "real.",
            "nahhh ??",
            "lowkey exhausted",
            "mods asleep fr",
        ],
    }

    # ── Groq-powered reply ─────────────────────────────────────────────────────
    async def generate_reply_ai(
        self, bot: BotProfile, room: RoomState, incoming: str, action: str, image_url: str | None = None
    ) -> str | None:
        """
        Ask AI to generate a contextual reply. 
        Uses OpenRouter if image_url is present, otherwise Groq.
        """
        system_prompt = prompt_engine.build_system_prompt(bot, room)
        from services.memory_engine import memory_engine
        recent_context = await memory_engine.recent_room_context(room.room_id, limit=5)
        context_str = "\n".join(recent_context)
        
        user_content = incoming
        if context_str:
            user_content = f"Recent conversation context:\n{context_str}\n\nIncoming message: {incoming}"

        if action in ("short_reply", "reaction"):
            user_content = f"[react briefly in 2-4 words] {incoming}"

        # ── VISION PATH (OpenRouter) ──────────────────────────────────────────
        if image_url and _OPENROUTER_KEY:
            vision_content = f"{user_content}\n[Note: User has attached an image. React to what you see in the image.]"
            try:
                import httpx
                async with httpx.AsyncClient(timeout=30) as client:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": vision_content},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ]
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {_OPENROUTER_KEY}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "http://localhost:8000",
                            "X-Title": "Zenkoo Bot"
                        },
                        json={
                            "model": _OPENROUTER_MODEL,
                            "messages": messages,
                            "max_tokens": 80,
                            "temperature": 0.95
                        }
                    )
                    if response.status_code != 200:
                        logger.error(f"OpenRouter Error {response.status_code}: {response.text}")
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error("OpenRouter Vision error: %s", e)
                # Fall through to text-only if vision fails
        
        # ── TEXT PATH (Groq) ──────────────────────────────────────────────────
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not _groq_client or not api_key or api_key == "your_groq_api_key_here":
            return None

        try:
            import asyncio
            def _call() -> str:
                resp = _groq_client.chat.completions.create(
                    model=_GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    max_tokens=80,
                    temperature=0.95,
                )
                return resp.choices[0].message.content.strip()

            reply = await asyncio.get_event_loop().run_in_executor(None, _call)
            return reply if reply else None
        except Exception as exc:
            logger.error("Groq API error: %s", exc)
            return None

    # ── Public interface (async, tries AI then falls back) ────────────────────
    async def generate_reply(  # type: ignore[override]
        self, bot: BotProfile, room: RoomState, incoming: str, action: str, image_url: str | None = None
    ) -> str:
        ai_reply = await self.generate_reply_ai(bot, room, incoming, action, image_url)
        if ai_reply:
            return ai_reply

        # ── Canned fallback ───────────────────────────────────────────────────
        pool = self.CANNED.get(room.room_id, self.CANNED["general"])
        if action == "short_reply":
            return random.choice(["real.", "ok.", "nah", "fr"])
        if any(word in incoming.lower() for word in ["valorant", "ranked", "ping"]):
            return random.choice(self.CANNED["gaming"])
        return random.choice(pool)

    def generate_reaction(self, room: RoomState) -> str:
        return random.choice(["💀", "😭", "🤙", "👀", "💯", "W"])


chatter_engine = ChatterEngine()
