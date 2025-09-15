from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Device
from ..config import settings

router = APIRouter(prefix="/api/devices", tags=["devices"])

# 인메모리 시뮬 상태
_SIM_DB: dict[int, Device] = {
    1: Device(id=1, name="Living Light", type="light", is_on=False),
    2: Device(id=2, name="Desk Plug", type="plug", is_on=True),
    3: Device(id=3, name="Temp Sensor", type="sensor", is_on=False),
}

@router.get("", response_model=List[Device])
async def list_devices():
    # 하드웨어 모드 전환 시, 여기서 실제 하드웨어 어댑터로 교체 예정
    return list(_SIM_DB.values())

@router.post("/{device_id}/toggle", response_model=Device)
async def toggle_device(device_id: int):
    dev = _SIM_DB.get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    if settings.mode != "sim":
        # 하드웨어 모드일 때는 실제 토글 로직/드라이버 호출로 대체
        pass
    dev.is_on = not dev.is_on
    _SIM_DB[device_id] = dev
    return dev
