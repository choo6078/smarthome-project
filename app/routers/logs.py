from fastapi import APIRouter, Query
from typing import Optional, Literal, List
from ..services.logs import query_logs, LogEntry

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("", response_model=List[LogEntry])
async def list_logs(
    limit: int = Query(50, ge=1, le=200),
    device_id: Optional[int] = None,
    action: Optional[Literal["toggle", "create", "update", "delete"]] = None,
):
    return query_logs(limit=limit, device_id=device_id, action=action)

