from pathlib import Path

from fastapi import APIRouter
from sqlalchemy import text

from ..config import settings
from ..database.session import SessionLocal
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

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        database_ready = True
    except Exception:
        database_ready = False

    return SystemStatus(
        mode="demo" if settings.demo_mode else "live",
        ai_ready=Path(settings.model_path).exists(),
        database_ready=database_ready,
        video_ready=has_readable_video,
    )
