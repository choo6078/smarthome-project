import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.routers import devices
from app.services import logs

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
def reset_state():
    # 초기화
    devices._SIM_DB.clear()
    logs._LOGS.clear()

    # ✅ 최소 3개 시드 보장
    devices._SIM_DB[1] = devices.Device(id=1, name="Living Light", type="light", is_on=False)
    devices._SIM_DB[2] = devices.Device(id=2, name="Desk Fan", type="fan", is_on=True)
    devices._SIM_DB[3] = devices.Device(id=3, name="Kitchen Outlet", type="outlet", is_on=False)

    # _next_id가 max+1이면 불필요하지만, 카운터를 쓰는 구현이라면 보호적으로 맞춰줌
    if hasattr(devices, "_SEQ"):
        devices._SEQ = 3

    yield