from fastapi import APIRouter

from app.api.routes import dev_mock, exports, health, logs, meetings, notes, settings, transcription

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(settings.router, tags=["settings"])
api_router.include_router(meetings.router, tags=["meetings"])
api_router.include_router(transcription.router, tags=["transcription"])
api_router.include_router(notes.router, tags=["notes"])
api_router.include_router(exports.router, tags=["exports"])
api_router.include_router(logs.router, tags=["logs"])
api_router.include_router(dev_mock.router, prefix="/dev/mock", tags=["development"])
