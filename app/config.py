from functools import lru_cache
import os
from pydantic import BaseModel

# Why: 테스트 중 SM_MODE를 바꾸면 즉시 반영되어야 한다.
# What: 캐시 없이 환경변수에서 매번 읽어 Settings 생성.
# How: lru_cache 제거.

class Settings(BaseModel):
    sm_mode: str = "sim"  # sim | hw

def get_settings() -> Settings:
    return Settings(sm_mode=os.getenv("SM_MODE", "sim").lower())

settings = get_settings()