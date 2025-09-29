from __future__ import annotations
from typing import Literal, List, Dict, Any, Optional
from datetime import datetime, timezone
from ..utils.time import now_ts

# 액션 타입은 Literal로 제한 (오타/불일치 예방)
Action = Literal["create", "toggle", "delete", "update"]

def now_ts() -> float:
    """UTC 기준 epoch 초. 프론트에서 범용적으로 쓰기 쉽고 비교도 간단."""
    return datetime.now(timezone.utc).timestamp()

_LOGS: List[Dict] = []

# Why: 생성/업데이트/토글 마다 중앙 로그 필요
# What: 단순 append + 조회를 위한 최소 구조
# How: 인메모리 리스트에 dict 추가. ts는 UTC epoch(float)

def append_log(device_id: int, action: str, note: Optional[str] = None) -> None:
    _LOGS.append({"device_id": device_id, "action": action, "ts": now_ts(), "note": note})

def reset_logs() -> None:
    _LOGS.clear()
    
def list_logs(
    action: Optional[Action] = None,
    device_id: Optional[int] = None,
    limit: Optional[int] = None,
    *,
    since: Optional[float] = None,   # >= 이 시각부터
    until: Optional[float] = None,   # <= 이 시각까지
    order: Literal["asc", "desc"] = "desc",  # 시간 정렬 방식
    ) -> List[Dict[str, Any]]:
    """
    - action/device_id로 1차 필터
    - since/until로 기간 필터 (epoch)
    - order로 정렬(asc: 오래된→최신, desc: 최신→오래된)
    - limit가 있으면 마지막에 슬라이스 (음수 방지)
    """
    res = _LOGS

    if action is not None:
        res = [l for l in res if l.get("action") == action]

    if device_id is not None:
        res = [l for l in res if l.get("device_id") == device_id]

    EPS = 1e-3  # 1ms
    if since is not None:
        thr = float(since) - EPS  # >= (since - ε)
        res = [l for l in res if float(l.get("ts", 0)) >= thr]
    if until is not None:
        thr = float(until) + EPS  # <= (until + ε)
        res = [l for l in res if float(l.get("ts", 0)) <= thr]

    # 정렬 (키 누락 시 0으로 간주하여 안정성 확보)
    reverse = (order == "desc")
    res = sorted(res, key=lambda l: float(l.get("ts", 0)), reverse=reverse)

    if limit is not None and limit >= 0:
        res = res[:limit]

    return res