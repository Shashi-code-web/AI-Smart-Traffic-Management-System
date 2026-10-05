from pathlib import Path

from fastapi import APIRouter

from ..config import settings
from ..schemas.system import SystemStatus
from ..services.video_validator import inspect_video

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def status():
    video = inspect_video()
    return SystemStatus(
        mode="demo" if settings.demo_mode else "live",
        ai_ready=Path(settings.model_path).exists(),
        database_ready=True,
        video_ready=bool(video["readable"]),
    )
