# Why: 라우터/서비스에서 DB 세션을 의존성 주입으로 사용할 준비
# What: 요청 범위 세션 생성/종료
# How: yield 사용
from .db import SessionLocal
from typing import Generator

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
