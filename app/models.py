from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime, timezone

def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()

DeviceType = Literal["light", "fan", "outlet", "sensor", "plug"]

class Device(BaseModel):
    id: int
    name: str
    # 저장되는 실제 type에도 plug 허용
    type: DeviceType
    is_on: bool = False
    updated_at: float = Field(default_factory=now_ts)


class DeviceCreate(BaseModel):
    name: str
    type: DeviceType
    is_on: bool = False

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["light", "plug", "sensor"]] = None
    is_on: Optional[bool] = None