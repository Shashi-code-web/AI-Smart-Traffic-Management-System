from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class Detection:
    class_id: int
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
    track_id: int | None = None

class VehicleDetector:
    """Local YOLO detector with optional persistent ByteTrack IDs."""

    VEHICLE_CLASSES = {
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }

    def __init__(self, model_path: str | Path, confidence: float = 0.35):
        self.model_path = Path(model_path)
        self.confidence = confidence
        self._model: Any = None

    @property
    def available(self) -> bool:
        return self.model_path.exists()

    def load(self) -> None:
        if not self.available:
            raise FileNotFoundError(f"YOLO model not found: {self.model_path}")
        from ultralytics import YOLO
        self._model = YOLO(str(self.model_path), verbose=False)

    @staticmethod
    def _from_result(result: Any) -> list[Detection]:
        detections: list[Detection] = []
        if result.boxes is None:
            return detections
        ids = getattr(result.boxes, "id", None)
        for index, box in enumerate(result.boxes):
            class_id = int(box.cls.item())
            if class_id not in VehicleDetector.VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            track_id = int(ids[index].item()) if ids is not None else None
            detections.append(Detection(
                class_id=class_id,
                label=VehicleDetector.VEHICLE_CLASSES[class_id],
                confidence=float(box.conf.item()),
                bbox=(x1, y1, x2, y2),
                track_id=track_id,
            ))
        return detections

    def detect(self, frame: Any) -> list[Detection]:
        if self._model is None:
            self.load()
        results = self._model.predict(frame, conf=self.confidence, verbose=False)
        return self._from_result(results[0]) if results else []

    def track(self, frame: Any) -> list[Detection]:
        if self._model is None:
            self.load()
        results = self._model.track(
            frame,
            conf=self.confidence,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )
        return self._from_result(results[0]) if results else []
