from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Mood(str, Enum):
    bored = "bored"
    chill = "chill"
    hyped = "hyped"
    annoyed = "annoyed"
    sleepy = "sleepy"
    motivated = "motivated"
    suspicious = "suspicious"
    fabulous = "fabulous"
    depressed = "depressed"
    anxious = "anxious"


class SleepSchedule(BaseModel):
    start: int = Field(ge=0, le=23)
    end: int = Field(ge=0, le=23)


class BotProfile(BaseModel):
    id: str
    username: str
    personality: str
    confidence: float = Field(ge=0.0, le=1.0)
    humor: float = Field(ge=0.0, le=1.0)
    aggression: float = Field(ge=0.0, le=1.0)
    patience: float = Field(ge=0.0, le=1.0)
    emoji_usage: float = Field(ge=0.0, le=1.0)
    grammar_quality: float = Field(ge=0.0, le=1.0)
    activity_level: float = Field(ge=0.0, le=1.0)
    typing_style: str
    favorite_topics: list[str]
    favorite_rooms: list[str]
    sleep_schedule: SleepSchedule
    current_mood: Mood = Mood.bored
    social_preferences: dict[str, float] = Field(default_factory=dict)
    energy: float = Field(default=0.7, ge=0.0, le=1.0)
    last_active_at: datetime | None = None


class RelationshipEdge(BaseModel):
    source_bot: str
    target_bot: str
    friendship: float = Field(ge=-1.0, le=1.0)
    trust: float = Field(ge=0.0, le=1.0)
    respect: float = Field(ge=0.0, le=1.0)
    interaction_frequency: int = 0


class RoomState(BaseModel):
    room_id: str
    activity_level: float = Field(default=0.2, ge=0.0, le=1.0)
    current_topic: str = "general"
    humor_level: float = Field(default=0.5, ge=0.0, le=1.0)
    tension: float = Field(default=0.1, ge=0.0, le=1.0)
    recent_arguments: list[str] = Field(default_factory=list)
    active_bots: list[str] = Field(default_factory=list)
    lurking_bots: list[str] = Field(default_factory=list)


class MemoryEntry(BaseModel):
    scope: str
    key: str
    text: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime


class ReplyRequest(BaseModel):
    room_id: str
    username: str
    message: str
    image_url: str | None = None  # Optional image context


class ReplyResponse(BaseModel):
    bot: str | None = None
    reply: str | None = None
    typing_delay: int = 0
    will_send: bool = False


class RoomActivityRequest(BaseModel):
    room_id: str


class PresenceRequest(BaseModel):
    room_id: str | None = None


class ScheduledMessage(BaseModel):
    id: str
    room_id: str
    bot_name: str
    text: str
    due_at: datetime
    typing_delay_ms: int
    cancelled: bool = False
