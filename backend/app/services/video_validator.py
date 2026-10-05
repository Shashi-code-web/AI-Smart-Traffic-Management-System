from pathlib import Path

import cv2

from ..config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VIDEO_ROOT = (PROJECT_ROOT / "data" / "videos").resolve()
ALLOWED_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".m4v"}


def resolve_video_path(path: str | None) -> Path:
    candidate = Path(path or settings.demo_video_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    candidate = candidate.resolve()
    if not candidate.is_relative_to(VIDEO_ROOT):
        raise ValueError("Video path must be inside data/videos")
    if candidate.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported video format: {candidate.suffix or 'none'}")
    return candidate


def inspect_video(path: str | None = None) -> dict:
    requested = path or settings.demo_video_path
    try:
        video_path = resolve_video_path(path)
    except ValueError as exc:
        return {
            "path": requested,
            "exists": False,
            "readable": False,
            "fps": 0,
            "frame_count": 0,
            "width": 0,
            "height": 0,
            "duration_seconds": 0,
            "error": str(exc),
        }

    if not video_path.exists():
        return {
            "path": str(video_path.relative_to(PROJECT_ROOT)),
            "exists": False,
            "readable": False,
            "fps": 0,
            "frame_count": 0,
            "width": 0,
            "height": 0,
            "duration_seconds": 0,
            "error": "Video file not found",
        }

    cap = cv2.VideoCapture(str(video_path))
    try:
        if not cap.isOpened():
            return {
                "path": str(video_path.relative_to(PROJECT_ROOT)),
                "exists": True,
                "readable": False,
                "fps": 0,
                "frame_count": 0,
                "width": 0,
                "height": 0,
                "duration_seconds": 0,
                "error": "OpenCV could not open the video",
            }
        fps = max(0.0, float(cap.get(cv2.CAP_PROP_FPS)))
        frame_count = max(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        width = max(0, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        height = max(0, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        duration = frame_count / fps if fps > 0 else 0.0
        return {
            "path": str(video_path.relative_to(PROJECT_ROOT)),
            "exists": True,
            "readable": True,
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration_seconds": duration,
            "error": None,
        }
    finally:
        cap.release()
