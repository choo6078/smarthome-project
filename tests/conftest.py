import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.routers import devices
from app.services import logs
from app.db import reset_db
from app.state import seed_devices
from app.services.logs import reset_logs

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac



@pytest.fixture(autouse=True)
def _reset_db_and_state():
    # Why: 각 테스트 격리. 이전 테스트의 생성/수정이 다음 테스트에 영향 주지 않도록.
    reset_db()      # drop_all → create_all
    seed_devices()  # 비어 있으면 기본 3개 시드
    reset_logs()    # 로그 비움