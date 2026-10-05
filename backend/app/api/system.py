from pathlib import Path

from fastapi import APIRouter

from ..config import settings
from ..schemas.system import SystemStatus

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def status():
    return SystemStatus(
        mode="demo" if settings.demo_mode else "live",
        ai_ready=Path(settings.model_path).exists(),
        database_ready=True,
        video_ready=Path(settings.demo_video_path).exists() or Path("data/videos/demo.mp4").exists(),
    )
