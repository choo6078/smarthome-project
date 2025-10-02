import pytest
import httpx
from httpx import ASGITransport
from app.main import create_app

@pytest.mark.anyio
async def test_db_backed_list_and_detail():
    app = create_app()
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r1 = await ac.get("/api/devices")
        assert r1.status_code == 200
        arr = r1.json()
        assert isinstance(arr, list) and len(arr) >= 1

        rid = arr[0]["id"]
        r2 = await ac.get(f"/api/devices/{rid}")
        assert r2.status_code == 200
        assert r2.json()["id"] == rid
