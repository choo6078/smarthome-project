import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_name_trim_and_length(async_client: AsyncClient):
    # 좌우 공백이 있어도 trim 후 유효해야 함 (3자 이상)
    r = await async_client.post("/api/devices", json={"name":"  New Lamp  ", "type":"light", "is_on":False})
    assert r.status_code == 201
    assert r.json()["name"] == "New Lamp"

    # 2자 이하면 422
    r2 = await async_client.post("/api/devices", json={"name":"ab", "type":"light", "is_on":False})
    assert r2.status_code in (400, 422)

@pytest.mark.anyio
async def test_create_duplicate_name_conflict(async_client: AsyncClient):
    # 같은 이름(대소문자/공백 무시)은 409
    base = (await async_client.get("/api/devices")).json()
    assert base, "seed required"
    existing = base[0]["name"]

    r = await async_client.post("/api/devices", json={"name": existing.lower(), "type":"plug", "is_on":False})
    assert r.status_code == 409
    assert "already exists" in r.json()["detail"]

@pytest.mark.anyio
async def test_update_duplicate_name_conflict(async_client: AsyncClient):
    # 장치 두 개 준비
    items = (await async_client.get("/api/devices")).json()
    if len(items) < 2:
        await async_client.post("/api/devices", json={"name":"TmpOne","type":"fan","is_on":False})
        await async_client.post("/api/devices", json={"name":"TmpTwo","type":"light","is_on":True})
        items = (await async_client.get("/api/devices")).json()

    a, b = items[0], items[1]
    # b의 이름을 a와 동일하게 바꾸려 하면 409
    r = await async_client.put(f"/api/devices/{b['id']}", json={"name": a["name"]})
    assert r.status_code == 409
