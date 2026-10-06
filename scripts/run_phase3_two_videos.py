from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from ai.pipeline.traffic_pipeline import TrafficPipeline
from backend.app.config import settings


def resize_frame(frame):
    max_width = max(320, settings.max_inference_width)
    height, width = frame.shape[:2]
    if width <= max_width:
        return frame
    scale = max_width / width
    size = (max_width, max(1, int(round(height * scale))))
    return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)


def run_video(video_path: Path, output_dir: Path) -> dict:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    pipeline = TrafficPipeline(
        settings.model_path,
        confidence=settings.model_confidence,
    )

    fps = max(1.0, float(cap.get(cv2.CAP_PROP_FPS)))
    writer = None
    frames = 0
    resized_frames = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            original_width = frame.shape[1]
            frame = resize_frame(frame)
            resized_frames += int(frame.shape[1] != original_width)

            snapshot = pipeline.process_frame(frame)
            annotated = frame.copy()

            for detection in pipeline.last_detections:
                x1, y1, x2, y2 = detection.bbox
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (80, 220, 180), 2)
                track = f"#{detection.track_id} " if detection.track_id is not None else ""
                cv2.putText(
                    annotated,
                    f"{track}{detection.label} {detection.confidence:.2f}",
                    (x1, max(18, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (80, 220, 180),
                    2,
                    cv2.LINE_AA,
                )

            cv2.putText(
                annotated,
                f"Signal: {snapshot.active_direction} | Green: {snapshot.green_seconds}s",
                (16, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            if writer is None:
                output_path = output_dir / f"{video_path.stem}_phase3_annotated.mp4"
                writer = cv2.VideoWriter(
                    str(output_path),
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    fps,
                    (annotated.shape[1], annotated.shape[0]),
                )
                if not writer.isOpened():
                    raise RuntimeError(f"Could not create output video: {output_path}")

            writer.write(annotated)
            frames += 1

    finally:
        cap.release()
        if writer is not None:
            writer.release()

    return {
        "video": str(video_path),
        "frames_processed": frames,
        "unique_vehicles": pipeline.snapshot.total_tracked,
        "vehicle_type_counts": pipeline.snapshot.vehicle_type_counts,
        "last_frame_lane_counts": pipeline.snapshot.lane_counts,
        "last_frame_density": pipeline.snapshot.lane_densities,
        "active_direction": pipeline.snapshot.active_direction,
        "green_seconds": pipeline.snapshot.green_seconds,
        "resized_frames": resized_frames,
        "output_video": str(output_dir / f"{video_path.stem}_phase3_annotated.mp4"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the real Phase 3 YOLO + ByteTrack pipeline on local traffic videos."
    )
    parser.add_argument("videos", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/records/phase3"))
    args = parser.parse_args()

    model_path = Path(settings.model_path).resolve()
    if not model_path.exists():
        raise SystemExit(
            f"YOLO model not found: {model_path}. "
            "Install backend requirements and place yolo26n.pt there first."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for raw_path in args.videos:
        path = raw_path.expanduser().resolve()
        if not path.exists():
            raise SystemExit(f"Video not found: {path}")
        results.append(run_video(path, args.output_dir))

    report = args.output_dir / "phase3_two_video_report.json"
    report.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
