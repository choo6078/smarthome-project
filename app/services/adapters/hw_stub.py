from .base import DeviceAdapter
from fastapi import HTTPException
from ...models import Device
from ...services.adapters.base import DeviceAdapter
from ...services.logs import append_log
from ...utils.time import now_ts
from ...state import _SIM_DB, seed_devices, refresh_cache_from_db
from ...db import SessionLocal
from ...models_orm import DeviceORM

# Why: UI/응답 일관성을 위해 hw 모드도 Device를 반환(실제 GPIO는 차후)
# What: 실제론 하드웨어 호출이겠지만 지금은 상태를 토글하고 로그 남김
# How: 시뮬 DB에 반영 + print로 호출 확인
class HardwareStubAdapter(DeviceAdapter):
    def toggle(self, device_id: int) -> Device:
        print(f"[HW-STUB] toggle called for device {device_id}", flush=True)
        with SessionLocal() as s:                     # ✅ 이제 OK
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