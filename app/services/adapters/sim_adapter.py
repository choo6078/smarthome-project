from fastapi import HTTPException
from app.models import Device
from app.services.adapters.base import DeviceAdapter
from app.services.logs import append_log
from app.utils.time import now_ts
from ...models import Device
from .base import DeviceAdapter
from ...services.logs import append_log
from ...utils.time import now_ts
from ...state import _SIM_DB, seed_devices

# Why: 기존 시뮬 토글 로직을 어댑터로 캡슐화해 DI로 주입하기 위함
# What: device_id로 디바이스 조회→토글→updated_at/로그→저장→Device 반환
# How: 인메모리 dict 사용, 못 찾으면 404 예외
class SimAdapter(DeviceAdapter):
    def toggle(self, device_id: int) -> Device:
        dev = _SIM_DB.get(device_id)
        if dev is None and not _SIM_DB:   # DB가 비어 있으면 1회 시드 후 재시도
            seed_devices()
            dev = _SIM_DB.get(device_id)

        if dev is None:
            raise HTTPException(status_code=404, detail="Device not found")

        dev.is_on = not dev.is_on
        dev.updated_at = now_ts()
        _SIM_DB[device_id] = dev
        append_log(device_id, "toggle")
        return dev