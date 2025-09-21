from fastapi import FastAPI
from .config import settings
from .routers import devices, logs
from .routers import logs as logs_router

app = FastAPI(title="SmartHome Web Dashboard", version="0.2.0")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": settings.mode}

app.include_router(devices.router)
app.include_router(logs.router)
app.include_router(logs_router.router)