from typing import Dict
from .models import Device
from .db import SessionLocal
from .models_orm import DeviceORM
from .services.logs import reset_logs

# Why: 인메모리 시뮬 DB와 재설정 지점을 한곳에서 관리(SSOT)
# What: _SIM_DB 저장소와 시드/리셋 유틸
# How: 테스트 픽스처에서 매 테스트마다 초기화해서 고립 보장

_SIM_DB: Dict[int, Device] = {}

# DB → 인메모리 캐시 전체 리프레시
def refresh_cache_from_db() -> None:
    _SIM_DB.clear()
    with SessionLocal() as s:
        for row in s.query(DeviceORM).all():
            _SIM_DB[row.id] = Device(
                id=row.id, name=row.name, type=row.type,
                is_on=row.is_on, updated_at=row.updated_at
            )

def seed_devices() -> None:
    # DB가 비어 있으면 시드 넣고, 그걸 캐시에 올림
    with SessionLocal() as s:
        if s.query(DeviceORM).count() == 0:
            rows = [
                DeviceORM(id=1, name="Living Light", type="light", is_on=False, updated_at=0.0),
                DeviceORM(id=2, name="Bedroom Fan", type="fan", is_on=True,  updated_at=0.0),
                DeviceORM(id=3, name="Desk Plug",    type="plug",  is_on=False, updated_at=0.0),
            ]
            s.add_all(rows)
            s.commit()
    refresh_cache_from_db()

def reset_state() -> None:
    seed_devices()
    reset_logs()