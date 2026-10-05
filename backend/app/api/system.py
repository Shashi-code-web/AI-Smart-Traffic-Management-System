from fastapi import APIRouter
from ..config import settings
from ..schemas.system import SystemStatus

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/status", response_model=SystemStatus)
def status():
    return SystemStatus(
        mode="demo" if settings.demo_mode else "live",
        ai_ready=False,
        database_ready=True,
        video_ready=False,
    )