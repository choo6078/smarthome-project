from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import List, Optional, Literal, Annotated
from ..models import Device, DeviceCreate, DeviceUpdate
from ..config import settings
from ..services.logs import append_log
from app.models import Device, DeviceCreate, DeviceUpdate, now_ts
from pydantic import BaseModel
from app.services.logs import append_log
from app.deps import provide_device_adapter
from app.services.devices import toggle_device
from app.services.adapters.base import DeviceAdapter


router = APIRouter(prefix="/api/devices", tags=["devices"])

def _append_log(device_id: int, action: str):
    _LOGS.append({"device_id": device_id, "action": action, "ts": now_ts()})

_SIM_DB: dict[int, Device] = {
    1: Device(id=1, name="Living Light", type="light", is_on=False),
    2: Device(id=2, name="Desk Fan", type="fan", is_on=True),
    3: Device(id=3, name="Kitchen Outlet", type="outlet", is_on=False),  # ★ 추가
}

def _name_exists(name: str, exclude_id: int | None = None) -> bool:
    """대소문자 무시 중복 검사. 업데이트 시 자기 자신(exclude_id)은 제외."""
    target = name.strip().lower()
    for d in _SIM_DB.values():
        if exclude_id is not None and d.id == exclude_id:
            continue
        if d.name.strip().lower() == target:
            return True
    return False

def _next_id() -> int:
    return max(_SIM_DB.keys(), default=0) + 1

ORDERABLE = {"id", "name", "type", "updated_at"}

def _apply_filters(items: list[Device], type_: str | None, is_on: bool | None) -> list[Device]:
    res = items
    if type_ is not None:
        res = [d for d in res if d.type == type_]
    if is_on is not None:
        res = [d for d in res if d.is_on == is_on]
    return res

def _apply_order(items: list[Device], order: list[str]) -> list[Device]:
    # 다중 정렬 지원 (뒤에서부터 안정 정렬)
    res = items[:]
    for key in reversed(order):
        desc = key.startswith("-")
        field = key[1:] if desc else key
        if field not in ORDERABLE:
            raise HTTPException(status_code=400, detail=f"Invalid order field: {field}")
        res.sort(key=lambda d: getattr(d, field), reverse=desc)
    return res

def _paginate(items: list[Device], page: int, page_size: int) -> list[Device]:
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

@router.get("", response_model=list[Device])
async def list_devices(
    type_: Annotated[str | None, Query(alias="type", pattern="^(light|fan|outlet|sensor|plug)$")] = None,
    is_on: Annotated[bool | None, Query()] = None,
    order: Annotated[str | None, Query(description="콤마 구분. 예) name,-updated_at")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items = list(_SIM_DB.values())
    items = _apply_filters(items, type_, is_on)
    orders = [s.strip() for s in order.split(",")] if order else ["id"]
    items = _apply_order(items, orders)
    items = _paginate(items, page, page_size)
    return items

class DeviceListResponse(BaseModel):
    meta: dict
    items: list[Device]

@router.get("/advanced", response_model=DeviceListResponse)
async def list_devices_advanced(
    type_: Annotated[str | None, Query(alias="type", pattern="^(light|fan|outlet|sensor|plug)$")] = None,
    is_on: Annotated[bool | None, Query()] = None,
    order: Annotated[str | None, Query(description="콤마 구분. 예) name,-updated_at")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items = list(_SIM_DB.values())
    items = _apply_filters(items, type_, is_on)
    orders = [s.strip() for s in order.split(",")] if order else ["id"]
    items = _apply_order(items, orders)

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    sliced = items[start:end]
    meta = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if page_size else 1,
        "has_next": end < total,
        "has_prev": start > 0,
    }
    return {"meta": meta, "items": sliced}

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: Annotated[int, Path(ge=1)]):
    dev = _SIM_DB.get(device_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return dev

@router.post("", response_model=Device, status_code=201)
async def create_device(payload: DeviceCreate):
    # 1) 이름 중복(대소문자 무시) → 409
    if _name_exists(payload.name):
        raise HTTPException(status_code=409, detail=f"Device name already exists: {payload.name.strip()}")

    # 2) 생성
    new = Device(id=_next_id(), name=payload.name.strip(), type=payload.type, is_on=payload.is_on)
    _SIM_DB[new.id] = new
    append_log(new.id, "create", note=f"name={new.name}, type={new.type}, is_on={new.is_on}")
    return new

# Why: 라우터는 모드/저장소를 몰라도 되게 DI로 위임
# What: 어댑터가 토글 후 Device를 반환 → 그대로 응답
# How: provide_device_adapter가 SM_MODE에 맞는 구현체를 공급
@router.post("/{device_id}/toggle", response_model=Device)
async def toggle_device(
    device_id: Annotated[int, Path(ge=1)],
    adapter: DeviceAdapter = Depends(provide_device_adapter),
):
    return adapter.toggle(device_id)

@router.put("/{device_id}", response_model=Device)
async def update_device(device_id: Annotated[int, Path(ge=1)], payload: DeviceUpdate):
    dev = _SIM_DB.get(device_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="Device not found")

    updates = payload.model_dump(exclude_unset=True)
    # 1) 이름을 바꾸는 경우 → 중복 체크 (자기 자신 제외)
    if "name" in updates and updates["name"] is not None:
        new_name = updates["name"].strip()
        if _name_exists(new_name, exclude_id=device_id):
            raise HTTPException(status_code=409, detail=f"Device name already exists: {new_name}")
        updates["name"] = new_name

    # 2) 실제 적용
    before = dev.model_dump()
    updated = dev.model_copy(update=updates)
    updated.updated_at = now_ts()
    _SIM_DB[device_id] = updated

    append_log(device_id, "update", note=f"{before} -> {updated.model_dump()}")
    return updated

@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: Annotated[int, Path(ge=1)]):
    if device_id not in _SIM_DB:
        raise HTTPException(status_code=404, detail="Device not found")
    _SIM_DB.pop(device_id)
    append_log(device_id, "delete")
    return