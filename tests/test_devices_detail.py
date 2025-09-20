import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_get_device_detail_success(async_client: AsyncClient):
    response = await async_client.get("/api/devices/1")
    assert response.status_code == 200
    assert "id" in response.json()

@pytest.mark.anyio
async def test_get_device_detail_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/devices/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"
