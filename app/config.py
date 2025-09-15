import os
from pydantic import BaseModel

class Settings(BaseModel):
    mode: str = os.getenv("SM_MODE", "sim")  # "sim" | "hw"

settings = Settings()
