from fastapi import APIRouter, HTTPException, Body, Query, Path
from typing import List, Optional, Literal, Annotated
from ..models import Device, DeviceCreate, DeviceUpdate
from ..config import settings
from ..services.logs import append_log
from app.models import Device

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
async def list_devices(
    type: Optional[Literal["light", "plug", "sensor"]] = None,
    is_on: Optional[bool] = None,
    order: Literal["id", "-id", "name", "-name", "type", "-type"] = "id",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    # 필터
    items = list(_SIM_DB.values())
    if type is not None:
        items = [d for d in items if d.type == type]
    if is_on is not None:
        items = [d for d in items if d.is_on == is_on]

    # 정렬
    key = order.lstrip("-")
    reverse = order.startswith("-")
    if key == "id":
        items.sort(key=lambda d: d.id, reverse=reverse)
    elif key == "name":
        items.sort(key=lambda d: d.name.lower(), reverse=reverse)
    elif key == "type":
        items.sort(key=lambda d: d.type, reverse=reverse)

    # 페이지네이션
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: Annotated[int, Path(ge=1)]):
    dev = _SIM_DB.get(device_id)  # _SIM_DB: dict[int, Device]
    if dev is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return dev

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
async def update_device(device_id: int, payload: DeviceUpdate):  # ★ Body 모델로 받기
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    updates = payload.model_dump(exclude_unset=True)  # ★ Body에서 온 필드만 반영
    if not updates:
        return dev  # 변경 없으면 그대로 반환(원하면 400으로 바꿔도 됨)

    updated = dev.model_copy(update=updates)
    _SIM_DB[device_id] = updated

    from ..services.logs import append_log
    append_log(
        device_id=device_id,
        action="update",
        note=f"{dev.model_dump()} -> {updated.model_dump()}",
    )
    return updated

@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: int):
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    _SIM_DB.pop(device_id)
    append_log(device_id=device_id, action="delete", note="deleted")
    return