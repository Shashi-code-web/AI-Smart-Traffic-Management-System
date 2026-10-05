from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database.session import Base, engine
from .models.system_event import SystemEvent  # noqa: F401
from .api.health import router as health_router
from .api.system import router as system_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(system_router)

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running", "phase": 1}