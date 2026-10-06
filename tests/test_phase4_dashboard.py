import numpy as np

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


def test_phase4_signal_display_can_use_final_ai_snapshot():
    runtime = VideoRuntime()
    runtime._mode = "AI_VIDEO"
    runtime._running = False

    snapshot = runtime.snapshot()

    assert snapshot is None
    assert runtime.status().mode == "AI_VIDEO"
