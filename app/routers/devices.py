from fastapi import APIRouter, HTTPException, Body
from typing import List
from ..models import Device
from ..config import settings
from ..services.logs import append_log

router = APIRouter(prefix="/api/devices", tags=["devices"])

# 인메모리 시뮬 상태
_SIM_DB: dict[int, Device] = {
    1: Device(id=1, name="Living Light", type="light", is_on=False),
    2: Device(id=2, name="Desk Plug", type="plug", is_on=True),
    3: Device(id=3, name="Temp Sensor", type="sensor", is_on=False),
}

@router.get("", response_model=List[Device])
async def list_devices():
    # 하드웨어 모드 전환 시, 여기서 실제 하드웨어 어댑터로 교체 예정
    return list(_SIM_DB.values())

@router.post("/{device_id}/toggle", response_model=Device)
async def toggle_device(device_id: int):
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    prev = dev.is_on
    # (하드웨어 모드면 나중에 실제 드라이버 호출 자리)
    dev.is_on = not dev.is_on
    _SIM_DB[device_id] = dev
    append_log(device_id=device_id, action="toggle", note=f"{prev} -> {dev.is_on}")  # ★로그
    return dev

@router.put("/{device_id}", response_model=Device)
async def update_device(
    device_id: int,
    name: str = Body(None),
    type: str = Body(None),
    is_on: bool = Body(None),
):
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    updates = {}
    if name is not None:
        updates["name"] = name
    if type is not None:
        updates["type"] = type
    if is_on is not None:
        updates["is_on"] = is_on

    updated = dev.model_copy(update=updates)  # copy() -> model_copy()
    _SIM_DB[device_id] = updated

    append_log(
        device_id=device_id,
        action="update",
        note=f"{dev.model_dump()} -> {updated.model_dump()}"  # dict() -> model_dump()
    )
    return updated