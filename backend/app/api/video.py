from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..schemas.video import VideoSession, VideoStartRequest, VideoStatus
from ..services.video_runtime import video_runtime
from ..services.video_validator import inspect_video

router = APIRouter(prefix="/api/video", tags=["video"])


@router.get("/status", response_model=VideoStatus)
def video_status(path: str | None = None):
    return inspect_video(path)


@router.get("/session", response_model=VideoSession)
def session_status():
    return VideoSession(**video_runtime.status().__dict__)


@router.post("/start", response_model=VideoSession)
def start_video(request: VideoStartRequest):
    try:
        return VideoSession(**video_runtime.start(request.path, request.use_ai).__dict__)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/stop", response_model=VideoSession)
def stop_video():
    return VideoSession(**video_runtime.stop().__dict__)


@router.get("/stream")
def video_stream():
    return StreamingResponse(video_runtime.mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
