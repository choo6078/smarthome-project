import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_list_filter_sort_paging(async_client: AsyncClient):
    # type+is_on 필터 + 정렬 + 페이징 검증
    resp = await async_client.get("/api/devices/advanced?type=light&is_on=true&order=name,-updated_at&page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "meta" in data and "items" in data
    assert data["meta"]["page"] == 1 and data["meta"]["page_size"] == 2
    # 정렬 필드 유효성
    bad = await async_client.get("/api/devices?order=notexist")
    assert bad.status_code == 400
    assert "Invalid order field" in bad.json()["detail"]
