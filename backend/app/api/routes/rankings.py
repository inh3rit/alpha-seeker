from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import RankingItem, RankingsResponse
from app.data.storage import DataStorage
from app.strategies import register_builtin_strategies
from app.strategies.base import StrategyRegistry

register_builtin_strategies()

router = APIRouter()


@router.get("/{ranking_type}", response_model=RankingsResponse)
def get_rankings(
    ranking_type: str,
    top: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取排行榜（type: score）"""
    end = date.today()
    start = end - timedelta(days=90)

    storage = DataStorage(db)
    codes = storage.list_stock_codes()

    items: list[dict] = []
    for code in codes:
        data = storage.load_stock_data(code, start, end)
        if len(data.prices) < 60:
            continue

        scores: dict[str, float] = {}
        for strategy in StrategyRegistry.get_all():
            result = strategy.analyze(data)
            scores[strategy.name] = result.score

        avg = sum(scores.values()) / len(scores) if scores else 0.0
        items.append({
            "code": code,
            "score": round(avg, 1),
            "dual_ma": round(scores.get("dual_ma", 0), 1),
            "macd": round(scores.get("macd", 0), 1),
            "rsi": round(scores.get("rsi", 0), 1),
        })

    items.sort(key=lambda x: x["score"], reverse=True)

    return RankingsResponse(
        type=ranking_type,
        count=min(top, len(items)),
        items=[RankingItem(**item) for item in items[:top]],
    )
