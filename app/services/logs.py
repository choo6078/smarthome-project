from __future__ import annotations
from typing import Literal, List, Dict, Any, Optional
from datetime import datetime, timezone

# 액션 타입은 Literal로 제한 (오타/불일치 예방)
Action = Literal["create", "toggle", "delete", "update"]

def now_ts() -> float:
    """UTC 기준 epoch 초. 프론트에서 범용적으로 쓰기 쉽고 비교도 간단."""
    return datetime.now(timezone.utc).timestamp()

# 메모리 내 로그 저장소 (지금은 dict 리스트 -> 나중에 DB로 치환 가능)
_LOGS: List[Dict[str, Any]] = []

def append_log(device_id: int, action: Action, note: Optional[str] = None) -> None:
    """로그 1건 추가. note는 선택 필드로 상세 변경점 등 기록."""
    _LOGS.append(
        {
            "device_id": device_id,
            "action": action,
            "ts": now_ts(),  # float(epoch seconds)
            "note": note,    # 항상 키를 유지(없으면 None) -> 스키마 안정성
        }
    )


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