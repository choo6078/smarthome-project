import importlib
import pytest
import httpx
from httpx import ASGITransport
from app.main import create_app

@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["sim", "hw"])
async def test_toggle_endpoint_by_mode(mode, monkeypatch):
    # 1) 모드 주입 & 설정 리로드
    monkeypatch.setenv("SM_MODE", mode)
    import app.config
    importlib.reload(app.config)

    # 2) 앱 생성
    app = create_app()

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # (A) 첫 토글
        r1 = await ac.post("/api/devices/1/toggle")
        assert r1.status_code == 200
        d1 = r1.json()
        assert isinstance(d1, dict) and d1.get("id") == 1

        # (B) 두 번째 토글 → 값이 반전되어야 함
        r2 = await ac.post("/api/devices/1/toggle")
        assert r2.status_code == 200
        d2 = r2.json()
        assert isinstance(d2, dict) and d2.get("id") == 1
        assert d2["is_on"] != d1["is_on"]

        # (C) /health 모드 일치 확인
        h = await ac.get("/health")
        assert h.status_code == 200
        assert h.json().get("mode") == mode