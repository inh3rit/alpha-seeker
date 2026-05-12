from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import DailyRecommendationsResponse, RecommendationResponse
from app.models.recommendation import Recommendation

router = APIRouter()


@router.get("/daily", response_model=DailyRecommendationsResponse)
def get_daily_recommendations(
    target_date: date | None = Query(None, alias="date"),
    db: Session = Depends(get_db),
):
    """获取每日推荐清单"""
    if target_date is None:
        target_date = date.today()

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.recommend_date == target_date)
        .order_by(Recommendation.score.desc())
        .all()
    )

    return DailyRecommendationsResponse(
        date=target_date,
        count=len(recs),
        recommendations=[RecommendationResponse.model_validate(r) for r in recs],
    )
