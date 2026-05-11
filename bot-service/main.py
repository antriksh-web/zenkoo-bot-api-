from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for required environment variables
if not os.getenv("GROQ_API_KEY"):
    logger.warning("GROQ_API_KEY not found - bot responses may be limited")
if not os.getenv("OPENROUTER_API_KEY"):
    logger.warning("OPENROUTER_API_KEY not found - bot responses may be limited")

from routes.messages import router as messages_router
from routes.rooms import router as rooms_router
from routes.bots import router as bots_router
from routes.presence import router as presence_router
from routes.scheduler import router as scheduler_router
from services.google_sheets_memory import google_sheets_memory_store
from services.state_store import state_store
from services.scheduler_engine import scheduler_engine


app = FastAPI(title="Zenkoo Bot Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(messages_router, prefix="/messages")
app.include_router(rooms_router, prefix="/rooms")
app.include_router(bots_router, prefix="/bots")
app.include_router(presence_router, prefix="/presence")
app.include_router(scheduler_router, prefix="/scheduler")


@app.on_event("startup")
async def startup_event() -> None:
    await state_store.bootstrap()
    # await google_sheets_memory_store.initialize()  # Legacy service removed
    await scheduler_engine.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await scheduler_engine.stop()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/debug")
async def debug() -> dict:
    bots = await state_store.list_bots()
    rooms = await state_store.all_rooms()
    return {
        "bots_loaded": len(bots),
        "bot_ids": [bot.id for bot in bots],
        "rooms_loaded": len(rooms),
        "room_ids": [room.room_id for room in rooms]
    }



