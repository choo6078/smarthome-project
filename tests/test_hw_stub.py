import pytest
from app.services.adapters.hw_stub import HardwareStubAdapter
from app.state import seed_devices

@pytest.mark.anyio
async def test_hw_stub_toggle(capsys):
    seed_devices()
    adapter = HardwareStubAdapter()
    dev = adapter.toggle(1)

    captured = capsys.readouterr()
    assert "[HW-STUB] toggle called for device 1" in captured.out
    assert dev.id == 1
    assert hasattr(dev, "name") and hasattr(dev, "type")
    assert hasattr(dev, "is_on") and hasattr(dev, "updated_at")