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
async def test_update_device_fields_and_log():
    async with _client() as ac:
        devices = (await ac.get("/api/devices")).json()
        target_id = devices[0]["id"]

        payload = {"name": "Updated Device", "is_on": True}
        r = await ac.put(f"/api/devices/{target_id}", json=payload)
        assert r.status_code == 200
        updated = r.json()
        assert updated["name"] == "Updated Device"
        assert updated["is_on"] is True

        resp = await ac.get("/api/logs?action=update")
        assert resp.status_code == 200
        logs = resp.json()

        # 방어: 단일 객체가 와도 리스트로 취급
        if isinstance(logs, dict):
            logs = [logs]

        assert any(
            (l.get("device_id") == target_id) and (l.get("action") == "update")
            for l in logs
        )
