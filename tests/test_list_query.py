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
async def test_filter_by_type_and_is_on_and_sort_paging():
    async with _client() as ac:
        # 시드 확인
        base = (await ac.get("/api/devices")).json()
        assert len(base) >= 3

        # 필터: type=plug
        plugs = (await ac.get("/api/devices?type=plug")).json()
        assert all(d["type"] == "plug" for d in plugs)

        # 필터: is_on=false
        offs = (await ac.get("/api/devices?is_on=false")).json()
        assert all(d["is_on"] is False for d in offs)

        # 정렬: name 오름차순 → 소문자 기준 정렬 확인(첫 글자 비교)
        asc = (await ac.get("/api/devices?order=name")).json()
        names = [d["name"].lower() for d in asc]
        assert names == sorted(names)

        # 정렬: -name 내림차순
        desc = (await ac.get("/api/devices?order=-name")).json()
        names_desc = [d["name"].lower() for d in desc]
        assert names_desc == sorted(names_desc, reverse=True)

        # 페이징: page/page_size
        page1 = (await ac.get("/api/devices?page=1&page_size=2&order=id")).json()
        page2 = (await ac.get("/api/devices?page=2&page_size=2&order=id")).json()
        # page1 마지막 id < page2 첫 id (id 오름차순 가정)
        if page1 and page2:
            assert page1[-1]["id"] < page2[0]["id"]

@pytest.mark.anyio
async def test_get_device_detail():
    async with _client() as ac:
        items = (await ac.get("/api/devices")).json()
        target_id = items[0]["id"]
        detail = (await ac.get(f"/api/devices/{target_id}")).json()
        assert detail["id"] == target_id
        assert "name" in detail and "type" in detail and "is_on" in detail
