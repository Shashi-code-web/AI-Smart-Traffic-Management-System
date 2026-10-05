from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class SystemStatus(BaseModel):
    mode: str
    ai_ready: bool
    database_ready: bool
    video_ready: bool