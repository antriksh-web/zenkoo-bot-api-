#!/usr/bin/env python3
"""
Simple test to debug bot response issue
"""
import asyncio
import json
from pathlib import Path

# Add the bot-service directory to Python path
import sys
sys.path.append(str(Path(__file__).parent / "bot-service"))

from models.schemas import BotProfile, RoomState, ReplyRequest, ReplyResponse

async def test_bot_logic():
    """Test the core bot logic without external dependencies"""
    
    # Create a test bot
    test_bot = BotProfile(
        id="test_bot",
        username="TestBot",
        personality="test",
        confidence=0.8,
        humor=0.7,
        aggression=0.3,
        patience=0.6,
        emoji_usage=0.5,
        grammar_quality=0.7,
        activity_level=0.8,
        typing_style="normal",
        favorite_topics=["anime", "gaming"],
        favorite_rooms=["anime", "general"],
        sleep_schedule={"start": 3, "end": 10},
        current_mood="chill"
    )
    
    # Create test room
    test_room = RoomState(
        room_id="anime",
        activity_level=0.5,
        current_topic="anime"
    )
    
    # Test request
    test_request = ReplyRequest(
        room_id="anime",
        username="testuser",
        message="What anime do you recommend?"
    )
    
    print("🤖 Bot Profile:")
    print(f"  ID: {test_bot.id}")
    print(f"  Username: {test_bot.username}")
    print(f"  Favorite Rooms: {test_bot.favorite_rooms}")
    print(f"  Favorite Topics: {test_bot.favorite_topics}")
    
    print("\n🏠 Room State:")
    print(f"  Room ID: {test_room.room_id}")
    print(f"  Activity Level: {test_room.activity_level}")
    
    print("\n💬 Test Request:")
    print(f"  Room: {test_request.room_id}")
    print(f"  Username: {test_request.username}")
    print(f"  Message: {test_request.message}")
    
    # Check if bot should respond
    if test_request.room_id in test_bot.favorite_rooms:
        print("\n✅ Bot should respond (room in favorite_rooms)")
        
        # Check topic interest
        topic_interest = any(topic in test_request.message.lower() for topic in test_bot.favorite_topics)
        print(f"   Topic Interest: {topic_interest}")
        
        if topic_interest:
            print("   🎯 Bot is interested in this topic!")
        else:
            print("   🤔 Bot might not be very interested")
    else:
        print("\n❌ Bot will not respond (room not in favorite_rooms)")

if __name__ == "__main__":
    asyncio.run(test_bot_logic())
