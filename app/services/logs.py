from __future__ import annotations
from typing import List, Literal, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

Action = Literal["toggle", "create", "delete"]

class LogEntry(BaseModel):
    id: int
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    device_id: int
    action: Action
    note: str | None = None

_LOGS: list[LogEntry] = []
_SEQ = 0

def _next_id() -> int:
    global _SEQ
    _SEQ += 1
    return _SEQ

def append_log(*, device_id: int, action: Action, note: str | None = None) -> LogEntry:
    entry = LogEntry(id=_next_id(), device_id=device_id, action=action, note=note)
    _LOGS.append(entry)
    return entry

def query_logs(limit: int = 50, device_id: Optional[int] = None, action: Optional[Action] = None) -> List[LogEntry]:
    items = _LOGS
    if device_id is not None:
        items = [x for x in items if x.device_id == device_id]
    if action is not None:
        items = [x for x in items if x.action == action]
    # 최신순
    items = sorted(items, key=lambda x: x.ts, reverse=True)
    return items[: max(1, min(limit, 200))]