from datetime import date
from decimal import Decimal

from app.models.recommendation import Recommendation


def test_get_daily_recommendations_empty(client):
    """无推荐时返回空列表"""
    response = client.get("/api/recommendations/daily")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["recommendations"] == []


def test_get_daily_recommendations_with_data(client, db_session):
    """有推荐时返回推荐列表"""
    rec = Recommendation(
        code="600519",
        recommend_date=date.today(),
        score=Decimal("85.50"),
        signals=["dual_ma:买入"],
        reason="技术面强势",
        suggested_action="buy",
        risk_level="medium",
    )
    db_session.add(rec)
    db_session.commit()

    response = client.get("/api/recommendations/daily")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["recommendations"][0]["code"] == "600519"
    assert data["recommendations"][0]["score"] == 85.5


def test_get_daily_recommendations_by_date(client, db_session):
    """按日期查询推荐"""
    rec = Recommendation(
        code="000001",
        recommend_date=date(2026, 5, 10),
        score=Decimal("72.00"),
        suggested_action="hold",
    )
    db_session.add(rec)
    db_session.commit()

    response = client.get("/api/recommendations/daily?date=2026-05-10")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["date"] == "2026-05-10"
