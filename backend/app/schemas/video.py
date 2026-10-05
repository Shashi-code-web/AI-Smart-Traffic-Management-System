from pydantic import BaseModel, Field


class VideoStatus(BaseModel):
    path: str
    exists: bool
    readable: bool
    fps: float = Field(ge=0)
    frame_count: int = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    duration_seconds: float = Field(ge=0)
    error: str | None = None
