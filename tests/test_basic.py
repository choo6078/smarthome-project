# tests/test_basic.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

def _client():
    # lifespan 인자 제거
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.anyio
async def test_health_ok():
    async with _client() as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["mode"] in ("sim", "hw")

@pytest.mark.anyio
async def test_toggle_device():
    async with _client() as ac:
        before = (await ac.get("/api/devices")).json()
        target_id = before[0]["id"]
        prev = next(d for d in before if d["id"] == target_id)["is_on"]

        r = await ac.post(f"/api/devices/{target_id}/toggle")
        assert r.status_code == 200
        after = r.json()
        assert after["id"] == target_id
        assert after["is_on"] == (not prev)
