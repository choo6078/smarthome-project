# Why: ORM 사용을 위한 공통 엔진/세션/베이스 제공
# What: DB_URL 로 엔진 생성, 세션 팩토리, Declarative Base
# How: SQLAlchemy 2.0 스타일, 기본 sqlite 파일. 테스트는 메모리로 오버라이드 가능.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declarative_base
import os

DB_URL = os.getenv("DB_URL", "sqlite:///./app.db")

class Base(DeclarativeBase): pass

engine = create_engine(
    "sqlite:///smarthome.db",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)