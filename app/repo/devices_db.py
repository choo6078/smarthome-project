# Why: 목록/상세를 DB에서 조회하고 기존 Pydantic Device로 응답
# What: orm→model 변환 + 필터/정렬/페이징(간단 버전)
# How: SQLAlchemy 쿼리 작성, 기존 규약(type, is_on, order, page, page_size) 준수 최소한

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, func
from ..models import Device
from ..models_orm import DeviceORM

def _to_model(o: DeviceORM) -> Device:
    return Device(id=o.id, name=o.name, type=o.type, is_on=o.is_on, updated_at=o.updated_at)

def get_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    row = db.get(DeviceORM, device_id)
    return _to_model(row) if row else None

def list_devices(
    db: Session,
    device_type: Optional[str] = None,
    is_on: Optional[bool] = None,
    order: str = "id",
    page: int = 1,
    page_size: int = 10,
) -> List[Device]:
    q = db.query(DeviceORM)
    if device_type:
        q = q.filter(DeviceORM.type == device_type)
    if is_on is not None:
        q = q.filter(DeviceORM.is_on == is_on)

    sort_desc = False
    key = order
    if order.startswith("-"):
        sort_desc = True
        key = order[1:]
    col = {
        "id": DeviceORM.id,
        "name": DeviceORM.name,
        "updated_at": DeviceORM.updated_at,
    }.get(key, DeviceORM.id)
    q = q.order_by(desc(col) if sort_desc else asc(col))

    if page < 1: page = 1
    if page_size < 1: page_size = 10
    q = q.offset((page - 1) * page_size).limit(page_size)

    return [_to_model(o) for o in q.all()]

def name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    norm = (name or "").strip().lower()
    q = db.query(DeviceORM.id).filter(func.lower(DeviceORM.name) == norm)
    if exclude_id is not None:
        q = q.filter(DeviceORM.id != exclude_id)
    return db.query(q.exists()).scalar()  # SA2에서도 동작
