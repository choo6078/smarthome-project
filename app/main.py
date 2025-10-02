from fastapi import FastAPI
from .config import get_settings 
from .routers import devices, logs, health
from .routers import logs as logs_router
from .routers.health import router as health_router
from .routers.devices import router as devices_router
from .routers.logs import router as logs_router
from .routers import devices
from .state import seed_devices, _SIM_DB
from .services.logs import reset_logs, _LOGS
from .db import Base, engine, reset_db
import os

def _ensure_seed_once() -> None:
    if not _SIM_DB:
        seed_devices()
    if _LOGS is None or len(_LOGS) == 0:
        reset_logs()

app = FastAPI(title="SmartHome Web Dashboard", version="0.2.0")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": settings.mode}

app.include_router(devices_router)
app.include_router(logs_router)
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
def startup():
    # 1) 테스트(또는 원하는 환경)에서는 drop_all → create_all
    if os.getenv("RESET_DB_ON_STARTUP") == "1":
        reset_db()
    else:
        Base.metadata.create_all(bind=engine)

    # 2) 이후에만 시드/로그 초기화 수행
    from .state import seed_devices
    from .services.logs import reset_logs
    seed_devices()   # 내부에서 '비어있을 때만' 시드라면 그대로 OK
    reset_logs()