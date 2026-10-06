from pathlib import Path

from fastapi import APIRouter

from ..config import settings
from ..database.session import SessionLocal
from ..schemas.diagnostics import DiagnosticCheck, SystemDiagnostics
from ..schemas.system import SystemStatus
from ..services.video_validator import ALLOWED_SUFFIXES, VIDEO_ROOT, inspect_video

router = APIRouter(prefix="/api/system", tags=["system"])


def _database_check() -> DiagnosticCheck:
    try:
        from sqlalchemy import text

        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return DiagnosticCheck(name="database", ok=True, detail="SQLite database is reachable")
    except Exception as exc:
        return DiagnosticCheck(name="database", ok=False, detail=f"Database check failed: {exc}")


def _video_directory_check() -> DiagnosticCheck:
    try:
        VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
        readable = 0
        for path in VIDEO_ROOT.iterdir():
            if path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES:
                if inspect_video(str(path))["readable"]:
                    readable += 1
        return DiagnosticCheck(
            name="video_directory",
            ok=True,
            detail=f"Video directory ready; {readable} readable local video(s)",
        )
    except Exception as exc:
        return DiagnosticCheck(name="video_directory", ok=False, detail=f"Video check failed: {exc}")


def _model_check() -> DiagnosticCheck:
    path = Path(settings.model_path)
    return DiagnosticCheck(
        name="local_model",
        ok=path.exists(),
        detail=f"Configured model: {settings.model_name}" if path.exists() else "Local YOLO model is not installed; simulation mode remains available",
    )


def diagnostics() -> SystemDiagnostics:
    checks = [_database_check(), _video_directory_check(), _model_check()]
    return SystemDiagnostics(
        healthy=all(check.ok for check in checks),
        checks=checks,
    )


@router.get("/diagnostics", response_model=SystemDiagnostics)
def system_diagnostics():
    return diagnostics()


@router.get("/status", response_model=SystemStatus)
def status():
    VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
    video_ready = any(
        path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES
        for path in VIDEO_ROOT.iterdir()
    )
    database_ready = _database_check().ok
    return SystemStatus(
        mode="demo" if settings.demo_mode else "live",
        ai_ready=Path(settings.model_path).exists(),
        database_ready=database_ready,
        video_ready=video_ready,
    )
