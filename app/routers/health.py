from fastapi import APIRouter
from ..config import get_settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "mode": settings.sm_mode}