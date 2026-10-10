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
    """Local YOLO detector with persistent ByteTrack IDs and emergency-class support."""

    VEHICLE_CLASSES = {
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }

    EMERGENCY_LABELS = {
        "ambulance",
        "firetruck",
        "fire_truck",
        "fire engine",
        "fire_engine",
        "police",
        "policecar",
        "police_car",
        "police vehicle",
        "police_vehicle",
        "emergency",
        "emergencyvehicle",
        "emergency_vehicle",
        "emergency vehicle",
        "rescue",
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

    @classmethod
    def _label_for_class(cls, class_id: int, names: Any) -> str | None:
        if isinstance(names, dict):
            value = names.get(class_id)
        elif isinstance(names, (list, tuple)) and 0 <= class_id < len(names):
            value = names[class_id]
        else:
            value = None
        if value is None:
            value = cls.VEHICLE_CLASSES.get(class_id)
        return str(value).strip().lower() if value is not None else None

    @classmethod
    def _is_supported_label(cls, class_id: int, label: str | None) -> bool:
        # Prefer the model's label when present. Custom-trained YOLO models may
        # assign different class IDs, so an ID alone must not turn a person or
        # another non-vehicle into a traffic vehicle.
        if label is None or not label.strip():
            return class_id in cls.VEHICLE_CLASSES

        def normalize(value: str) -> str:
            return " ".join(
                value.strip().lower().replace("_", " ").replace("-", " ").split()
            )

        supported_labels = {
            normalize(value)
            for value in set(cls.VEHICLE_CLASSES.values()) | cls.EMERGENCY_LABELS
        }
        return normalize(label) in supported_labels

    @classmethod
    def _from_result(cls, result: Any) -> list[Detection]:
        detections: list[Detection] = []
        if result.boxes is None:
            return detections

        ids = getattr(result.boxes, "id", None)
        names = getattr(result, "names", None)

        for index, box in enumerate(result.boxes):
            class_id = int(box.cls.item())
            label = cls._label_for_class(class_id, names)
            if not cls._is_supported_label(class_id, label):
                continue

            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            track_id = int(ids[index].item()) if ids is not None else None
            detections.append(
                Detection(
                    class_id=class_id,
                    label=label or cls.VEHICLE_CLASSES[class_id],
                    confidence=float(box.conf.item()),
                    bbox=(x1, y1, x2, y2),
                    track_id=track_id,
                )
            )
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
