import uuid
import pytest
from sqlalchemy import text
from app.db import engine, SessionLocal
from app.models_orm import DeviceORM, LogORM

@pytest.mark.anyio
async def test_db_tables_exist():
    with engine.connect() as conn:
        # sqlite 기준 테이블 존재 확인
        rows = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        names = {r[0] for r in rows}
        assert "devices" in names and "logs" in names

@pytest.mark.anyio
async def test_db_insert_select_device():
    # Why: 스켈레톤이 실제 CRUD 되는지 스모크 테스트
    unique = uuid.uuid4().hex[:8]  # ← 유니크 접미사
    with SessionLocal() as s:
        d = DeviceORM(name=f"DB-Lamp-{unique}", type="light", is_on=False, updated_at=0.0)
        s.add(d)
        s.commit()
        s.refresh(d)
        assert d.id > 0
        found = s.get(DeviceORM, d.id)
        assert found and found.name == d.name
