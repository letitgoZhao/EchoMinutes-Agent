from fastapi import APIRouter

from app.api.routes import dev_mock, health, meetings, settings

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(settings.router, tags=["settings"])
api_router.include_router(meetings.router, tags=["meetings"])
api_router.include_router(dev_mock.router, prefix="/dev/mock", tags=["development"])
