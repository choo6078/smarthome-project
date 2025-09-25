import pytest
from app.services.adapters.hw_stub import HardwareStubAdapter

@pytest.mark.anyio
async def test_hw_stub_toggle(capsys):
    adapter = HardwareStubAdapter()
    result = adapter.toggle(1)
    captured = capsys.readouterr()
    assert result is True
    assert "toggle called for device 1" in captured.out
