from pydantic import BaseModel
from typing import Literal, Optional

class Device(BaseModel):
    id: int
    name: str
    type: Literal["light", "plug", "sensor"]
    is_on: bool = False

class DeviceCreate(BaseModel):
    name: str
    type: Literal["light", "plug", "sensor"]
    is_on: bool = False

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["light", "plug", "sensor"]] = None
    is_on: Optional[bool] = None