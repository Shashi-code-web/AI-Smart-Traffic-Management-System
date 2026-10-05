from backend.app.services.video_validator import inspect_video, resolve_video_path


def test_missing_demo_video_is_reported_cleanly():
    result = inspect_video("data/videos/does-not-exist.mp4")

    assert result["exists"] is False
    assert result["readable"] is False
    assert "not found" in result["error"].lower()


def test_unsupported_video_format_is_rejected():
    result = inspect_video("data/videos/demo.txt")

    assert result["readable"] is False
    assert "unsupported video format" in result["error"].lower()


def test_video_path_must_stay_inside_video_directory():
    try:
        resolve_video_path("../README.md")
    except ValueError as exc:
        assert "data/videos" in str(exc)
    else:
        raise AssertionError("Path traversal was not rejected")
