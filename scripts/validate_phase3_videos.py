from __future__ import annotations

import argparse
from pathlib import Path

import cv2


def inspect_video(path: Path) -> dict[str, object]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open: {path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    decoded = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame is None or frame.size == 0:
                raise RuntimeError(f"Empty frame at index {decoded} in {path}")
            decoded += 1
    finally:
        cap.release()

    if decoded != frame_count:
        raise RuntimeError(
            f"Frame decode mismatch for {path}: metadata={frame_count}, decoded={decoded}"
        )

    duration = decoded / fps if fps > 0 else 0.0
    return {
        "file": str(path),
        "fps": round(fps, 3),
        "frames": decoded,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fully decode local traffic videos for Phase 3 validation."
    )
    parser.add_argument("videos", nargs="+", type=Path)
    args = parser.parse_args()

    failures = 0
    for raw_path in args.videos:
        path = raw_path.expanduser().resolve()
        try:
            if not path.exists():
                raise FileNotFoundError(path)
            result = inspect_video(path)
            print(f"PASS: {result}")
        except Exception as exc:
            failures += 1
            print(f"FAIL: {path}: {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
