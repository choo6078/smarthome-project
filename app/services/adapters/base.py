from abc import ABC, abstractmethod

# Why: 시뮬레이터 ↔ 하드웨어 전환 시 코드 중복/혼란 방지
# What: 모든 디바이스 제어 어댑터가 따라야 할 인터페이스 정의
# How: ABC 추상 클래스 사용, 구체 구현체에서 실제 동작/모사 구현
class DeviceAdapter(ABC):
    @abstractmethod
    def toggle(self, device_id: int) -> bool:
        """디바이스 상태 토글 후 결과 반환"""
        pass
