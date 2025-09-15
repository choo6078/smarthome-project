from pydantic import BaseModel
from typing import Literal

class Device(BaseModel):
    id: int
    name: str
    type: Literal["light", "plug", "sensor"]
    is_on: bool = False
