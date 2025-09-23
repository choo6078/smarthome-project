from pydantic import BaseModel, Field, field_validator
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
    name: str = Field(..., min_length=3, max_length=50, description="3~50자")
    type: DeviceType
    is_on: bool = False

    @field_validator("name")
    @classmethod
    def trim_and_check(cls, v: str) -> str:
        v2 = v.strip()
        if len(v2) < 3:
            raise ValueError("name must be at least 3 characters (after trimming)")
        return v2

class DeviceUpdate(BaseModel):
    # 부분 업데이트 허용: unset인 필드는 무시
    name: str | None = Field(None, min_length=3, max_length=50)
    type: DeviceType | None = None
    is_on: bool | None = None

    @field_validator("name")
    @classmethod
    def trim_and_check(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v2 = v.strip()
        if len(v2) < 3:
            raise ValueError("name must be at least 3 characters (after trimming)")
        return v2