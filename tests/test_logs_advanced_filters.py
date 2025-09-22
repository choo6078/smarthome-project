# ---------------------------------------------------------------------------
# 목적: /api/logs 기간 필터(since/until) + 정렬(order) 동작 확인
# 전략:
#  - 현재 시간 앞뒤로 액션을 발생시켜 정확한 윈도우에 들어오는지 검증
#  - asc/desc 정렬에서 첫 항목의 ts가 기대 방향인지 확인
# ---------------------------------------------------------------------------
import pytest
import time
from httpx import AsyncClient

@pytest.mark.anyio
async def test_logs_since_until_and_order(async_client: AsyncClient):
    # 1) 기준 시각을 찍고
    t0 = time.time()
    # 2) 토글 한 번 (t1 ~ t2 사이 발생)
    #    장치를 하나 가져와서 토글
    base = (await async_client.get("/api/devices")).json()
    target_id = base[0]["id"]

    # 살짝 기다려 ts 구분
    await async_client.get("/health")  # no-op
    r1 = await async_client.post(f"/api/devices/{target_id}/toggle")
    assert r1.status_code == 200
    t1 = time.time()

    # 또 한 번 토글해서 다른 로그 생성
    r2 = await async_client.post(f"/api/devices/{target_id}/toggle")
    assert r2.status_code == 200
    t2 = time.time()

    # 3) since~until 범위로 필터 (t0~t2 사이)
    logs_in_range = (await async_client.get(f"/api/logs?since={t0}&until={t2}&action=toggle")).json()
    assert isinstance(logs_in_range, list)
    assert len(logs_in_range) >= 2  # 방금 생성한 2건은 포함되어야 함

    # 4) asc 정렬일 때, 첫 로그가 더 과거여야 함
    asc = (await async_client.get(f"/api/logs?since={t0}&until={t2}&action=toggle&order=asc")).json()
    desc = (await async_client.get(f"/api/logs?since={t0}&until={t2}&action=toggle&order=desc")).json()
    assert asc[0]["ts"] <= asc[-1]["ts"]
    assert desc[0]["ts"] >= desc[-1]["ts"]

    # 5) limit 동작
    limited = (await async_client.get(f"/api/logs?since={t0}&until={t2}&action=toggle&order=desc&limit=1")).json()
    assert len(limited) == 1
