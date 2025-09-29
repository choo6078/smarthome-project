from functools import lru_cache
from .base import DeviceAdapter
from .sim_adapter import SimAdapter
from .hw_stub import HardwareStubAdapter

# Why: 라우터/DI가 임포트될 때 어댑터 구현 모듈까지 즉시 로드하면 순환/경로 문제가 됨
# What: 모드에 따라 필요한 구현만 '지연 임포트'해서 인스턴스 생성
# How: import_module + getattr, lru_cache로 싱글턴 유지

@lru_cache
def get_adapter_by_mode(mode: str) -> DeviceAdapter:
    if mode == "hw":
        from .hw_stub import HardwareStubAdapter  # 지역 임포트
        return HardwareStubAdapter()
    # default: sim
    from importlib import import_module
    sim_mod = import_module("app.services.adapters.sim_adapter")
    SimAdapter = getattr(sim_mod, "SimAdapter")
    return SimAdapter()