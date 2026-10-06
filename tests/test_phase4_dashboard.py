from datetime import datetime, timezone

import numpy as np

from ai.pipeline.traffic_pipeline import PipelineSnapshot
from backend.app.services.video_runtime import VideoRuntime


def test_phase4_resize_keeps_small_frames_unchanged():
    frame = np.zeros((720, 1000, 3), dtype=np.uint8)
    resized = VideoRuntime._resize_for_inference(frame)

    assert resized.shape == frame.shape


def test_phase4_resize_caps_large_frame_width(monkeypatch):
    frame = np.zeros((3840, 2160, 3), dtype=np.uint8)
    monkeypatch.setattr(
        "backend.app.services.video_runtime.settings.max_inference_width",
        1280,
    )

    resized = VideoRuntime._resize_for_inference(frame)

    assert resized.shape[1] == 1280
    assert resized.shape[0] == 2276
    assert resized.shape[0] < frame.shape[0]


def test_phase4_completed_ai_session_keeps_final_snapshot():
    runtime = VideoRuntime()
    snapshot = PipelineSnapshot(
        total_tracked=4,
        current_vehicle_count=2,
        vehicle_type_counts={"car": 2},
        lane_counts={"NORTH": 2, "EAST": 0, "SOUTH": 0, "WEST": 0},
        lane_densities={"NORTH": "LOW", "EAST": "LOW", "SOUTH": "LOW", "WEST": "LOW"},
        active_direction="NORTH",
        next_direction="NORTH",
        signal_state="GREEN",
        remaining_seconds=19,
        green_seconds=19,
        model_ready=True,
        signal_reason="test",
        processed_at=datetime.now(timezone.utc).isoformat(),
    )
    runtime._mode = "AI_VIDEO"
    runtime._running = False
    runtime._latest_snapshot = snapshot

    assert runtime.status().mode == "AI_VIDEO"
    assert runtime.snapshot() == snapshot
