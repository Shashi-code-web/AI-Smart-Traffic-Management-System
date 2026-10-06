# Phase 3 Traffic Video Validation

Two local traffic videos were selected for Phase 3 validation. The binary video files are intentionally kept outside GitHub so the repository stays lightweight.

## Test assets

| Asset | Duration | Resolution | FPS | Frames | Decode |
|---|---:|---:|---:|---:|---|
| Traffic Video 1 | 23.991 s | 1920x1080 | 29.97 | 719 | PASS |
| Traffic Video 3 | 13.033 s | 2160x3840 | 30.00 | 391 | PASS |

Both files were fully decoded frame-by-frame with OpenCV with zero bad or empty frames.

Recommended local filenames:

`data/videos/traffic_video_1.mp4`
`data/videos/traffic_video_3.mp4`

## Repeatable validation

From the repository root:

```bash
python scripts/validate_phase3_videos.py \
  data/videos/traffic_video_1.mp4 \
  data/videos/traffic_video_3.mp4
```

Expected result: a `PASS` line for each video and exit code 0.

## AI inference verification

The runtime already accepts a video path inside `data/videos` through `VideoStartRequest.path`, so the two videos can be processed independently by the same YOLO + ByteTrack pipeline.

Actual YOLO inference requires the local Ultralytics package and the configured weight file at:

`models/yolo/yolo26n.pt`

The repository does not commit that model weight. A full AI-inference pass therefore must be performed on the development laptop after the model is present.
