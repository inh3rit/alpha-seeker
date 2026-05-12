from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import ChartDataPoint, ChartResponse
from app.data.storage import DataStorage

router = APIRouter()


@router.get("/{code}/chart", response_model=ChartResponse)
def get_stock_chart(
    code: str,
    days: int = Query(60, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """获取股票 K 线数据"""
    end = date.today()
    start = end - timedelta(days=days)

    storage = DataStorage(db)
    quotes = storage.get_quotes(code, start, end)

    data = [
        ChartDataPoint(
            date=q.trade_date,
            open=float(q.open),
            close=float(q.close),
            high=float(q.high),
            low=float(q.low),
            volume=int(q.volume),
        )
        for q in quotes
    ]

    return ChartResponse(code=code, data=data)
