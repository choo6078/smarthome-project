from typing import Dict
from .models import Device
from .db import SessionLocal
from .models_orm import DeviceORM

# Why: 인메모리 시뮬 DB와 재설정 지점을 한곳에서 관리(SSOT)
# What: _SIM_DB 저장소와 시드/리셋 유틸
# How: 테스트 픽스처에서 매 테스트마다 초기화해서 고립 보장

_SIM_DB: Dict[int, Device] = {}

def seed_devices() -> None:
    _SIM_DB.clear()
    _SIM_DB[1] = Device(id=1, name="Living Light", type="light", is_on=False, updated_at=0.0)
    _SIM_DB[2] = Device(id=2, name="Bedroom Fan", type="fan", is_on=True, updated_at=0.0)
    _SIM_DB[3] = Device(id=3, name="Desk Plug", type="plug", is_on=False, updated_at=0.0)

    with SessionLocal() as s:
        cnt = s.query(DeviceORM).count()
        if cnt == 0:
            for dev in _SIM_DB.values():
                s.add(DeviceORM(
                    id=dev.id, name=dev.name, type=dev.type,
                    is_on=dev.is_on, updated_at=dev.updated_at
                ))
            s.commit()

from .services.logs import reset_logs
def reset_state() -> None:
    seed_devices()
    reset_logs()