from __future__ import annotations
from typing import Literal, List, Dict, Any, Optional
from datetime import datetime, timezone

Action = Literal["create", "toggle", "delete", "update"]

def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()

# 전역 저장소: dict만 저장
_LOGS: List[Dict[str, Any]] = []

def append_log(device_id: int, action: Action, note: Optional[str] = None) -> None:
    # 필드셋: device_id, action, ts, note
    _LOGS.append(
        {
            "device_id": device_id,
            "action": action,
            "ts": now_ts(),
            "note": note,
        }
    )

def list_logs(
    action: Optional[Action] = None,
    device_id: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    res = _LOGS
    if action is not None:
        res = [l for l in res if l.get("action") == action]
    if device_id is not None:
        res = [l for l in res if l.get("device_id") == device_id]
    if limit is not None and limit >= 0:
        res = res[-limit:]  # 최신 순(append 순서)에서 뒤에서부터 제한
    return res
