from typing import Any

class ByteTrackManager:
    """Thin adapter around Ultralytics' local ByteTrack implementation."""

    def __init__(self, model: Any):
        self.model = model

    def track(self, frame: Any, confidence: float = 0.35) -> Any:
        return self.model.track(
            frame,
            conf=confidence,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )
