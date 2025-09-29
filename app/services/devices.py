"""
디바이스 관련 비즈니스 로직 분리
- 라우터에서 직접 dict 다루지 않고 여기 함수들을 호출하게 됨
- 책임 분리: 라우터(입출력), 서비스(로직/데이터), 모델(검증)
"""

from ..models import Device
from ..services.logs import append_log
from datetime import datetime, timezone
from .adapters.base import DeviceAdapter

_SIM_DB: dict[int, Device] = {}   # 실제 DB 대신 dict 시뮬
_SEQ = 0

def _next_id() -> int:
    global _SEQ
    _SEQ += 1
    return _SEQ

def seed_devices():
    """테스트 실행 전마다 초기화"""
    global _SIM_DB, _SEQ
    _SIM_DB = {
        1: Device(id=1, name="Living Light", type="light", is_on=False, updated_at=datetime.now(timezone.utc)),
        2: Device(id=2, name="Desk Fan", type="fan", is_on=True, updated_at=datetime.now(timezone.utc)),
        3: Device(id=3, name="Kitchen Outlet", type="outlet", is_on=False, updated_at=datetime.now(timezone.utc)),
    }
    _SEQ = 3

def list_devices() -> list[Device]:
    return list(_SIM_DB.values())

def get_device(device_id: int) -> Device | None:
    return _SIM_DB.get(device_id)

def create_device(name: str, type: str, is_on: bool) -> Device:
    new = Device(id=_next_id(), name=name, type=type, is_on=is_on, updated_at=datetime.now(timezone.utc))
    _SIM_DB[new.id] = new
    append_log(new.id, "create", note=f"created {new.name}")
    return new

def update_device(device_id: int, updates: dict) -> Device | None:
    dev = _SIM_DB.get(device_id)
    if not dev:
        return None
    updated = dev.model_copy(update=updates)
    _SIM_DB[device_id] = updated
    append_log(device_id, "update", note=f"{dev.model_dump()} -> {updated.model_dump()}")
    return updated

def delete_device(device_id: int) -> bool:
    if device_id not in _SIM_DB:
        return False
    _SIM_DB.pop(device_id)
    append_log(device_id, "delete", note="device deleted")
    return True

# Why: 라우터에서 비즈니스 로직을 분리하고 테스트 용이성 확보.
# What: 어댑터로 토글 수행 후 결과 반환(추후 로그/검증 추가 예정).
# How: 주입된 DeviceAdapter 사용. I/O/부작용은 어댑터에 위임.

def toggle_device(adapter: DeviceAdapter, device_id: int) -> bool:
    return adapter.toggle(device_id)
