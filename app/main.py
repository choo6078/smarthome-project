from fastapi import FastAPI
from .config import get_settings 
from .routers import devices, logs, health
from .routers import logs as logs_router
from .routers.health import router as health_router
from .routers.devices import router as devices_router
from .routers.logs import router as logs_router
from app.routers import devices
from .state import seed_devices, _SIM_DB
from .services.logs import reset_logs, _LOGS
from .db import Base, engine

def _ensure_seed_once() -> None:
    if not _SIM_DB:
        seed_devices()
    if _LOGS is None or len(_LOGS) == 0:
        reset_logs()

app = FastAPI(title="SmartHome Web Dashboard", version="0.2.0")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": settings.mode}

app.include_router(devices.router)
app.include_router(logs.router)
app.include_router(logs_router)

def create_app() -> FastAPI:
    app = FastAPI(title="SmartHome API")

    _ = get_settings()  # (필요 시 사용; 현재는 사이드이펙트 없음)

    _ensure_seed_once()

    @app.on_event("startup")
    def _init_state():
        seed_devices()
        reset_logs()

    app.include_router(health_router)
    app.include_router(devices_router)
    app.include_router(logs_router)
    return app
app = create_app()

@app.on_event("startup")
def _init_state():
    from .state import seed_devices
    from .services.logs import reset_logs
    Base.metadata.create_all(bind=engine)
    seed_devices()
    reset_logs()