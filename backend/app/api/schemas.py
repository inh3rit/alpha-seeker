from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# --- Response Schemas ---

class StockBase(BaseModel):
    code: str
    name: str | None = None


class RecommendationResponse(BaseModel):
    id: int
    code: str
    recommend_date: date
    score: float
    signals: list[str] | None = None
    reason: str | None = None
    suggested_action: str
    risk_level: str | None = None

    model_config = {"from_attributes": True}


class DailyRecommendationsResponse(BaseModel):
    date: date
    count: int
    recommendations: list[RecommendationResponse]


class PositionResponse(BaseModel):
    id: int
    user_id: str
    code: str
    buy_date: date
    buy_price: float
    quantity: int
    status: str

    model_config = {"from_attributes": True}


class PositionCreate(BaseModel):
    code: str = Field(..., max_length=10)
    buy_date: date
    buy_price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class PositionUpdate(BaseModel):
    buy_price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, gt=0)
    status: str | None = None


class RankingItem(BaseModel):
    code: str
    score: float
    dual_ma: float
    macd: float
    rsi: float


class RankingsResponse(BaseModel):
    type: str
    count: int
    items: list[RankingItem]


class ChartDataPoint(BaseModel):
    date: date
    open: float
    close: float
    high: float
    low: float
    volume: int


class ChartResponse(BaseModel):
    code: str
    data: list[ChartDataPoint]
