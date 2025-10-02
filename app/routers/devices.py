from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import List, Optional, Literal, Annotated
from ..models import Device, DeviceCreate, DeviceUpdate, now_ts
from ..config import settings
from ..services.logs import append_log
from pydantic import BaseModel
from ..deps import provide_device_adapter
from ..services.devices import toggle_device
from ..services.adapters.base import DeviceAdapter
from ..deps_db import get_db
from sqlalchemy.orm import Session
from ..repo.devices_db import get_device_by_id as db_get_device, list_devices as db_list_devices, name_exists
from ..state import _SIM_DB, refresh_cache_from_db  # (인메모리 유지 시 필요)
from ..models_orm import DeviceORM
from ..utils.time import now_ts

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

# 목록 (DB) — 기존 파라미터 규약 유지(type, is_on, order, page, page_size)
@router.get("", response_model=List[Device])
async def list_devices(
    db: Session = Depends(get_db),
    type: Optional[str] = Query(None, description="light|fan|outlet|sensor|plug"),
    is_on: Optional[bool] = Query(None),
    order: str = Query("id"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    key = order.lstrip("-")
    allowed = {"id", "name", "updated_at"}
    if key not in allowed:
        # ✅ 테스트가 기대하는 문구로 고정
        raise HTTPException(status_code=400, detail="Invalid order field")
    return db_list_devices(db, device_type=type, is_on=is_on, order=order, page=page, page_size=page_size)

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

# 상세 (DB)
@router.get("/{device_id}", response_model=Device)
async def get_device_detail(device_id: Annotated[int, Path(ge=1)], db: Session = Depends(get_db)):
    dev = db_get_device(db, device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return dev

# 생성 (DB → 캐시)
@router.post("", response_model=Device, status_code=201)
async def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if name_exists(db, name):
        raise HTTPException(status_code=409, detail="name already exists")
    row = DeviceORM(name=name, type=payload.type, is_on=payload.is_on or False, updated_at=now_ts())
    db.add(row)
    db.commit()
    db.refresh(row)
    append_log(row.id, "create")
    # 캐시 동기화(부분 업데이트도 가능하지만 안전하게 전체 리프레시)
    refresh_cache_from_db()
    return Device(id=row.id, name=row.name, type=row.type, is_on=row.is_on, updated_at=row.updated_at)

# Why: 라우터는 모드/저장소를 몰라도 되게 DI로 위임
# What: 어댑터가 토글 후 Device를 반환 → 그대로 응답
# How: provide_device_adapter가 SM_MODE에 맞는 구현체를 공급

# 토글 (인메모리/어댑터 유지)
@router.post("/{device_id}/toggle", response_model=Device)
async def toggle_device(
    device_id: Annotated[int, Path(ge=1)],
    adapter: DeviceAdapter = Depends(provide_device_adapter),
):
    return adapter.toggle(device_id)

# 수정 (DB → 캐시)
@router.put("/{device_id}", response_model=Device)
async def update_device(
    device_id: Annotated[int, Path(ge=1)],
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
):
    row = db.get(DeviceORM, device_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Device not found")

    if payload.name is not None:
        name = payload.name.strip()
        if name_exists(db, name, exclude_id=device_id):
            raise HTTPException(status_code=409, detail="name already exists")
        row.name = name
    if payload.type is not None:
        row.type = payload.type
    if payload.is_on is not None:
        row.is_on = payload.is_on

    row.updated_at = now_ts()
    db.add(row)
    db.commit()
    db.refresh(row)
    append_log(device_id, "update")
    refresh_cache_from_db()
    return Device(id=row.id, name=row.name, type=row.type, is_on=row.is_on, updated_at=row.updated_at)


# 삭제 (DB → 캐시) — 204 그대로 유지
@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
):
    row = db.get(DeviceORM, device_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(row)
    db.commit()
    append_log(device_id, "delete")
    refresh_cache_from_db()
    # 204는 본문 없음