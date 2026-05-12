from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


class Indicator(Base):
    """技术指标缓存表"""

    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint(
            "code", "trade_date", "indicator_type",
            name="uq_indicators_code_date_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    indicator_type: Mapped[str] = mapped_column(String(20), nullable=False)
    indicator_value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<Indicator(code={self.code!r}, date={self.trade_date}, "
            f"type={self.indicator_type!r})>"
        )
