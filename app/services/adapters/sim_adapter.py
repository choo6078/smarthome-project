from fastapi import HTTPException
from ...db import SessionLocal
from ...models import Device
from ...models_orm import DeviceORM
from ...services.adapters.base import DeviceAdapter
from ...services.logs import append_log
from ...utils.time import now_ts
from .base import DeviceAdapter
from ...state import _SIM_DB, seed_devices, refresh_cache_from_db

# Why: 기존 시뮬 토글 로직을 어댑터로 캡슐화해 DI로 주입하기 위함
# What: device_id로 디바이스 조회→토글→updated_at/로그→저장→Device 반환
# How: 인메모리 dict 사용, 못 찾으면 404 예외
class SimAdapter(DeviceAdapter):
    def toggle(self, device_id: int) -> Device:
        with SessionLocal() as s:
            row = s.get(DeviceORM, device_id)
            if row is None:
                from ...state import seed_devices
                seed_devices()
                row = s.get(DeviceORM, device_id)
                if row is None:
                    raise HTTPException(status_code=404, detail="Device not found")
            row.is_on = not row.is_on
            row.updated_at = now_ts()
            s.add(row)
            s.commit()
            s.refresh(row)
        append_log(device_id, "toggle")
        refresh_cache_from_db()
        return Device(id=row.id, name=row.name, type=row.type, is_on=row.is_on, updated_at=row.updated_at)