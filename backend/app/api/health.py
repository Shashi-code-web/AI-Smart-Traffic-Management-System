from fastapi import APIRouter
from ..schemas.system import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="traffic-backend", version="0.6.0")
