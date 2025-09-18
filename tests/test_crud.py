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
async def test_create_device_and_log():
    async with _client() as ac:
        payload = {"name": "New Plug", "type": "plug", "is_on": False}
        r = await ac.post("/api/devices", json=payload)
        assert r.status_code == 201
        created = r.json()
        assert created["name"] == "New Plug"
        assert created["type"] == "plug"

        # create 로그 확인
        logs = (await ac.get("/api/logs?action=create")).json()
        if isinstance(logs, dict):
            logs = [logs]
        assert any(l.get("device_id") == created["id"] and l.get("action") == "create" for l in logs)

@pytest.mark.anyio
async def test_delete_device_and_log():
    async with _client() as ac:
        # 먼저 하나 만들고 지우기
        payload = {"name": "Temp To Delete", "type": "light", "is_on": True}
        created = (await ac.post("/api/devices", json=payload)).json()
        did = created["id"]

        # 삭제
        r = await ac.delete(f"/api/devices/{did}")
        assert r.status_code == 204

        # 목록에서 사라졌는지
        items = (await ac.get("/api/devices")).json()
        assert all(d["id"] != did for d in items)

        # delete 로그 확인
        logs = (await ac.get("/api/logs?action=delete")).json()
        if isinstance(logs, dict):
            logs = [logs]
        assert any(l.get("device_id") == did and l.get("action") == "delete" for l in logs)
