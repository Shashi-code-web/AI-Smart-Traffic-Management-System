from pathlib import Path

from fastapi import APIRouter

from ..config import settings
from ..schemas.system import SystemStatus
from ..services.video_validator import ALLOWED_SUFFIXES, VIDEO_ROOT, inspect_video

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def status():
    VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
    has_readable_video = False
    for path in VIDEO_ROOT.iterdir():
        if path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES:
            if inspect_video(str(path))["readable"]:
                has_readable_video = True
                break

    return SystemStatus(
        mode="demo" if settings.demo_mode else "live",
        ai_ready=Path(settings.model_path).exists(),
        database_ready=True,
        video_ready=has_readable_video,
    )
