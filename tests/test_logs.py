import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

def _client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.anyio
async def test_toggle_creates_log_and_list():
    async with _client() as ac:
        # 1) 현재 디바이스 하나 집어오고 토글
        devices = (await ac.get("/api/devices")).json()
        assert devices, "seed devices should exist"
        target_id = devices[0]["id"]

        before_logs = (await ac.get("/api/logs")).json()
        r = await ac.post(f"/api/devices/{target_id}/toggle")
        assert r.status_code == 200

        after_logs = (await ac.get("/api/logs")).json()
        assert len(after_logs) >= len(before_logs) + 1

        # 최신 로그가 우리가 방금 만든 toggle인지 확인
        latest = after_logs[0]
        assert latest["device_id"] == target_id
        assert latest["action"] == "toggle"
        assert "note" in latest

@pytest.mark.anyio
async def test_logs_filter_by_device_and_action():
    async with _client() as ac:
        devices = (await ac.get("/api/devices")).json()
        target_id = devices[0]["id"]

        # 최소 한 번은 토글해서 로그 생성
        await ac.post(f"/api/devices/{target_id}/toggle")

        # 필터: device_id + action=toggle
        logs = (await ac.get(f"/api/logs?device_id={target_id}&action=toggle")).json()
        assert all(x["device_id"] == target_id and x["action"] == "toggle" for x in logs)
