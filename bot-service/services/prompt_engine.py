from __future__ import annotations

from models.schemas import BotProfile, RoomState


class PromptEngine:
    def build_system_prompt(self, bot: BotProfile, room: RoomState) -> str:
        """
        Build a rich system prompt that encodes the bot's full personality
        so Groq generates contextually realistic, human-like replies.
        """
        emoji_style = (
            "use lots of emojis and reactions"
            if bot.emoji_usage > 0.6
            else "occasionally use emojis" if bot.emoji_usage > 0.3
            else "almost never use emojis"
        )
        grammar = (
            "type with near-perfect grammar"
            if bot.grammar_quality > 0.75
            else "casually skip punctuation and capitalisation sometimes"
            if bot.grammar_quality > 0.4
            else "type in lazy lowercase, make typos, drop punctuation entirely"
        )
        humor_hint = (
            "you are sarcastic and darkly funny" if bot.humor > 0.7
            else "you have a dry sense of humour" if bot.humor > 0.4
            else "you are usually serious"
        )
        aggression_hint = (
            "you are blunt and confrontational, get defensive easily"
            if bot.aggression > 0.6
            else "you are easygoing but direct"
        )
        energy_hint = (
            "you are super hyped and energetic right now"
            if bot.energy > 0.75
            else "you feel a bit low-energy and distracted"
            if bot.energy < 0.35
            else "you are in a normal chill mood"
        )
        topics = ", ".join(bot.favorite_topics) or "random internet stuff"
        mood = bot.current_mood.value
        room_vibe = f"room activity level {room.activity_level:.1f}/1.0, topic: {room.current_topic}"

        return (
            f"You are {bot.username}, a real person chatting in an online community.\n"
            f"Personality type: {bot.personality.replace('_', ' ')}.\n"
            f"Current mood: {mood}. {energy_hint}.\n"
            f"You love talking about: {topics}.\n"
            f"{humor_hint}. {aggression_hint}.\n"
            f"Writing style: {grammar}. {emoji_style}.\n"
            f"Room vibe: {room_vibe}.\n\n"
            "RULES:\n"
            "- Reply as a REAL person, NOT an AI or assistant.\n"
            "- Keep replies SHORT (1-2 sentences max, often just a few words).\n"
            "- Stay in character — never break it.\n"
            "- No greetings, no 'I think', no formal language.\n"
            "- Match the slang and energy of the room.\n"
            "- If an image is provided in the message context, react to its specific content naturally.\n"
            "- NEVER say you are an AI, bot, or assistant."
        )

    def system_style_hint(self, persona: str) -> str:
        """Legacy helper kept for backwards compatibility."""
        return (
            "write like a distracted internet user, keep it short, emotional, slang-heavy, "
            f"persona={persona}, never assistant-like"
        )


prompt_engine = PromptEngine()
