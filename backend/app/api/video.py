from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..schemas.video import VideoSession, VideoSource, VideoStartRequest, VideoStatus
from ..services.video_runtime import video_runtime
from ..services.video_validator import ALLOWED_SUFFIXES, VIDEO_ROOT, inspect_video

router = APIRouter(prefix="/api/video", tags=["video"])



@router.get("/sources", response_model=list[VideoSource])
def video_sources():
    sources: list[VideoSource] = []
    VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
    for path in sorted(VIDEO_ROOT.iterdir()):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        info = inspect_video(str(path))
        sources.append(
            VideoSource(
                path=info["path"],
                name=path.name,
                exists=info["exists"],
                readable=info["readable"],
                fps=info["fps"],
                frame_count=info["frame_count"],
                width=info["width"],
                height=info["height"],
                duration_seconds=info["duration_seconds"],
                error=info["error"],
            )
        )
    return sources

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
