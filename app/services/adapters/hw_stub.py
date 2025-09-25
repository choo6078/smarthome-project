from .base import DeviceAdapter

# Why: 실제 GPIO는 아직 없지만 구조를 먼저 잡아야 테스트/전환이 쉽다
# What: 하드웨어 모드에서 동작할 스텁 구현 (로그 출력만)
# How: toggle 호출 시 단순히 print/logging 후 True 반환
class HardwareStubAdapter(DeviceAdapter):
    def toggle(self, device_id: int) -> bool:
        print(f"[HW-STUB] toggle called for device {device_id}")
        return True
