from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserPosition(Base):
    """用户持仓"""

    __tablename__ = "user_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)
    buy_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="holding", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserPosition(code={self.code!r}, qty={self.quantity}, status={self.status!r})>"
