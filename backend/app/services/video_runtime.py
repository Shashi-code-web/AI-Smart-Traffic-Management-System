from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import threading
import time

import cv2

from ai.pipeline.traffic_pipeline import PipelineSnapshot, TrafficPipeline
from .demo_traffic import DemoTrafficSource
from .video_validator import PROJECT_ROOT, inspect_video, resolve_video_path
from ..config import settings


@dataclass(frozen=True)
class VideoSessionStatus:
    running: bool
    mode: str
    source: str | None
    error: str | None
    frames_processed: int
    started_at: str | None


class VideoRuntime:
    """Local video worker with optional YOLO+ByteTrack processing and MJPEG output."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._running = False
        self._mode = "IDLE"
        self._source: str | None = None
        self._error: str | None = None
        self._frames = 0
        self._started_at: str | None = None
        self._latest_jpeg: bytes | None = None
        self._pipeline: TrafficPipeline | None = None
        self._demo = DemoTrafficSource()

    def status(self) -> VideoSessionStatus:
        with self._lock:
            return VideoSessionStatus(
                running=self._running,
                mode=self._mode,
                source=self._source,
                error=self._error,
                frames_processed=self._frames,
                started_at=self._started_at,
            )

    def snapshot(self) -> PipelineSnapshot | None:
        with self._lock:
            pipeline = self._pipeline
        return pipeline.snapshot if pipeline else None

    @property
    def demo_source(self) -> DemoTrafficSource:
        return self._demo

    def start(self, path: str | None = None, use_ai: bool = True) -> VideoSessionStatus:
        with self._lock:
            if self._running:
                return VideoSessionStatus(
                    running=True,
                    mode=self._mode,
                    source=self._source,
                    error=self._error,
                    frames_processed=self._frames,
                    started_at=self._started_at,
                )

        info = inspect_video(path)
        if not info["readable"]:
            raise ValueError(info["error"] or "Video is not readable")
        if use_ai and not Path(settings.model_path).exists():
            raise RuntimeError(
                "Local YOLO model is unavailable. Add the configured .pt weight under models/yolo or run the video in simulation mode."
            )

        video_path = resolve_video_path(path)
        pipeline = (
            TrafficPipeline(
                settings.model_path,
                confidence=settings.model_confidence,
                signal_config=None,
            )
            if use_ai
            else None
        )

        with self._lock:
            self._stop.clear()
            self._running = True
            self._mode = "AI_VIDEO" if use_ai else "SIMULATION_VIDEO"
            self._source = str(video_path.relative_to(PROJECT_ROOT))
            self._error = None
            self._frames = 0
            self._started_at = datetime.now(timezone.utc).isoformat()
            self._latest_jpeg = None
            self._pipeline = pipeline
            self._thread = threading.Thread(
                target=self._worker,
                args=(video_path,),
                daemon=True,
            )
            self._thread.start()
            return VideoSessionStatus(
                True,
                self._mode,
                self._source,
                None,
                0,
                self._started_at,
            )

    def stop(self) -> VideoSessionStatus:
        self._stop.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
        with self._lock:
            self._running = False
            self._mode = "IDLE"
            self._thread = None
        return self.status()

    def _worker(self, video_path: Path) -> None:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            with self._lock:
                self._error = "OpenCV could not open the video after validation"
                self._running = False
                self._mode = "ERROR"
            return

        interval = 1.0 / max(1, settings.target_fps)
        try:
            while not self._stop.is_set():
                started = time.perf_counter()
                ok, frame = cap.read()
                if not ok:
                    break

                with self._lock:
                    pipeline = self._pipeline
                    mode = self._mode

                if pipeline is not None:
                    pipeline.process_frame(frame)
                    annotated = self._annotate(frame, pipeline)
                else:
                    annotated = frame

                cv2.putText(
                    annotated,
                    "AI VIDEO" if mode == "AI_VIDEO" else "SIMULATION VIDEO",
                    (18, 32),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (80, 220, 180),
                    2,
                    cv2.LINE_AA,
                )

                encoded, buffer = cv2.imencode(
                    ".jpg",
                    annotated,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 80],
                )
                if encoded:
                    with self._lock:
                        self._latest_jpeg = buffer.tobytes()
                        self._frames += 1

                elapsed = time.perf_counter() - started
                time.sleep(max(0.0, interval - elapsed))
        except Exception as exc:
            with self._lock:
                self._error = str(exc)
                self._mode = "ERROR"
        finally:
            cap.release()
            with self._lock:
                self._running = False
                if self._mode != "ERROR":
                    self._mode = "IDLE"

    def _annotate(self, frame, pipeline: TrafficPipeline):
        annotated = frame.copy()
        for detection in pipeline.last_detections:
            x1, y1, x2, y2 = detection.bbox
            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (80, 220, 180),
                2,
            )
            track_text = f"#{detection.track_id} " if detection.track_id is not None else ""
            label = f"{track_text}{detection.label} {detection.confidence:.2f}"
            cv2.putText(
                annotated,
                label,
                (x1, max(18, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (80, 220, 180),
                2,
                cv2.LINE_AA,
            )
        return annotated

    def mjpeg_stream(self):
        while True:
            with self._lock:
                jpeg = self._latest_jpeg
                running = self._running
            if jpeg:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Cache-Control: no-cache\r\n\r\n"
                    + jpeg
                    + b"\r\n"
                )
            if not running:
                return
            time.sleep(0.08)


video_runtime = VideoRuntime()
