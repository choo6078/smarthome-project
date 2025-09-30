# Why: 인메모리 모델과 1:1로 매핑되는 ORM 스켈레톤을 선 정의
# What: devices, logs 테이블 정의(제약은 최소). 후속 마이그레이션으로 보강 예정.
# How: SQLAlchemy 컬럼/인덱스 정의. 이름 유니크, 로그는 조회용 인덱스.
from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, engine

class DeviceORM(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(20))          # light|fan|outlet|sensor|plug
    is_on: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[float] = mapped_column(Float, default=0.0)

class LogORM(Base):
    __tablename__ = "logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(20), index=True)  # toggle|create|update|delete ...
    ts: Mapped[float] = mapped_column(Float, index=True)         # UTC epoch
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)

Index("ix_logs_device_action_ts", LogORM.device_id, LogORM.action, LogORM.ts)

def _ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)

_ensure_schema()