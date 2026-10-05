from fastapi import APIRouter, Query

from ..schemas.video import VideoStatus
from ..services.video_validator import inspect_video

router = APIRouter(prefix="/api/video", tags=["video"])


@router.get("/status", response_model=VideoStatus)
def video_status(path: str | None = Query(default=None)):
    return inspect_video(path)
