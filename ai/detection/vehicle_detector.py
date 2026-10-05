from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class Detection:
    class_id: int
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]

class VehicleDetector:
    """Local YOLO detector. Model loading is lazy so demo mode can run without weights."""

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
        self._model = YOLO(str(self.model_path))

    def detect(self, frame: Any) -> list[Detection]:
        if self._model is None:
            self.load()
        results = self._model.predict(frame, conf=self.confidence, verbose=False)
        detections: list[Detection] = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id = int(box.cls.item())
                if class_id not in self.VEHICLE_CLASSES:
                    continue
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                detections.append(Detection(
                    class_id=class_id,
                    label=self.VEHICLE_CLASSES[class_id],
                    confidence=float(box.conf.item()),
                    bbox=(x1, y1, x2, y2),
                ))
        return detections
