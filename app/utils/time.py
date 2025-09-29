# Why: UTC epoch(float) 공통 타임스탬프 유틸
# What: now_ts() 반환
# How: time.time() 그대로 float 변환
import time as _time

def now_ts() -> float:
    return float(_time.time())
