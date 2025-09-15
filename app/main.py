from fastapi import FastAPI
from .config import settings
from .routers import devices

app = FastAPI(title="SmartHome Web Dashboard", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": settings.mode}

app.include_router(devices.router)
