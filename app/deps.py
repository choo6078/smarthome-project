from .config import get_settings
from .services.adapters import get_adapter_by_mode
from .services.adapters.base import DeviceAdapter

# Why: 라우터/서비스에서 설정 로직을 몰라도 되게 의존성으로 어댑터를 주입.
# What: 요청 시점에 Settings를 읽어 해당 어댑터를 반환.
# How: get_settings() → mode → get_adapter_by_mode(mode)

def provide_device_adapter() -> DeviceAdapter:
    settings = get_settings()
    return get_adapter_by_mode(settings.sm_mode)
