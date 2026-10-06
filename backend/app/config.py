from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Smart Traffic Management System"
    environment: str = "development"
    database_url: str = f"sqlite:///{BASE_DIR / 'traffic.db'}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    demo_mode: bool = True
    model_path: str = str(BASE_DIR / "models" / "yolo" / "yolo26n.pt")
    model_name: str = "yolo26n.pt"
    model_confidence: float = 0.35
    target_fps: int = 15
    max_inference_width: int = 1280
    min_green_seconds: int = 15
    max_green_seconds: int = 60
    yellow_seconds: int = 3
    all_red_seconds: int = 1
    demo_video_path: str = "data/videos/demo.mp4"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
