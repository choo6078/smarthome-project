from fastapi import APIRouter, Query
from typing import Annotated, Literal
from app.services.logs import list_logs as _list_logs

router = APIRouter(prefix="/api", tags=["logs"])

@router.get("/logs")
async def get_logs(
    action: Annotated[Literal["create", "toggle", "delete", "update"] | None, Query()] = None,
    device_id: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int | None, Query(ge=0)] = None,
):
    return _list_logs(action=action, device_id=device_id, limit=limit)

