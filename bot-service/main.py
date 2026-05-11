from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages_router)
app.include_router(rooms_router)
app.include_router(bots_router)
app.include_router(presence_router)
app.include_router(scheduler_router)


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


@app.get("/", include_in_schema=False)
async def serve_ui() -> FileResponse:
    ui_path = Path(__file__).resolve().parents[1] / "test-ui.html"
    return FileResponse(str(ui_path), media_type="text/html")
