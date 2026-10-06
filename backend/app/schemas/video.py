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


class VideoStartRequest(BaseModel):
    path: str | None = None
    use_ai: bool = True


class VideoSession(BaseModel):
    running: bool
    mode: str
    source: str | None = None
    error: str | None = None
    frames_processed: int = Field(ge=0)
    started_at: str | None = None


class VideoSource(BaseModel):
    path: str
    name: str
    exists: bool
    readable: bool
    fps: float = Field(ge=0)
    frame_count: int = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    duration_seconds: float = Field(ge=0)
    error: str | None = None
