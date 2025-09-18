from fastapi import APIRouter, HTTPException, Body
from typing import List
from ..models import Device, DeviceCreate
from ..config import settings
from ..services.logs import append_log

router = APIRouter(prefix="/api/devices", tags=["devices"])

# 인메모리 시뮬 상태
_SIM_DB: dict[int, Device] = {
    1: Device(id=1, name="Living Light", type="light", is_on=False),
    2: Device(id=2, name="Desk Plug", type="plug", is_on=True),
    3: Device(id=3, name="Temp Sensor", type="sensor", is_on=False),
}

def _next_id() -> int:
    return (max(_SIM_DB.keys()) + 1) if _SIM_DB else 1

@router.get("", response_model=List[Device])
async def list_devices():
    # 하드웨어 모드 전환 시, 여기서 실제 하드웨어 어댑터로 교체 예정
    return list(_SIM_DB.values())

@router.post("", response_model=Device, status_code=201)
async def create_device(payload: DeviceCreate):
    # 하드웨어 모드에선 생성 금지
    if settings.mode != "sim":
        raise HTTPException(status_code=403, detail="Creation allowed only in simulator mode")
    new = Device(id=_next_id(), **payload.model_dump())
    _SIM_DB[new.id] = new
    append_log(device_id=new.id, action="create", note=f"created {new.model_dump()}")
    return new

@router.post("/{device_id}/toggle", response_model=Device)
async def toggle_device(device_id: int):
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    prev = dev.is_on
    updated = dev.model_copy(update={"is_on": (not dev.is_on)})
    _SIM_DB[device_id] = updated
    append_log(device_id=device_id, action="toggle", note=f"{prev} -> {updated.is_on}")
    return updated

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

@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: int):
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    # 하드웨어 모드에서도 정책에 따라 금지하고 싶으면 아래 주석 해제
    # if settings.mode != "sim":
    #     raise HTTPException(status_code=403, detail="Deletion allowed only in simulator mode")
    _SIM_DB.pop(device_id)
    append_log(device_id=device_id, action="delete", note="deleted")
    return  # 204 No Content