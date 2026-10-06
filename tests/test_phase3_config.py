from pathlib import Path

from backend.app.config import settings


def test_model_path_stays_inside_project_models_directory():
    model_path = Path(settings.model_path).resolve()
    expected_root = (
        Path(__file__).resolve().parents[1] / "models" / "yolo"
    ).resolve()

    assert model_path.parent == expected_root
    assert model_path.name == settings.model_name
