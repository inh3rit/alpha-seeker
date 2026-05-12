from typing import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入：数据库 session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
