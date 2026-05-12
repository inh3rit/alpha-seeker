from datetime import date, timedelta
from decimal import Decimal

from loguru import logger
from sqlalchemy.orm import Session

from app.data.storage import DataStorage
from app.models.recommendation import Recommendation
from app.strategies import register_builtin_strategies
from app.strategies.base import Signal, StrategyRegistry


register_builtin_strategies()


class RecommendationService:
    """推荐引擎：综合多策略评分，生成每日推荐清单"""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.storage = DataStorage(session)

    def generate_daily_recommendations(
        self,
        recommend_date: date | None = None,
        top_n: int = 10,
        days: int = 90,
        min_data_days: int = 60,
    ) -> list[Recommendation]:
        """
        生成每日推荐清单

        Args:
            recommend_date: 推荐日期（默认今天）
            top_n: 推荐数量
            days: 使用最近多少天数据
            min_data_days: 最少需要的数据天数
        """
        if recommend_date is None:
            recommend_date = date.today()

        end = recommend_date
        start = end - timedelta(days=days)

        codes = self.storage.list_stock_codes()
        logger.info(f"开始生成 {recommend_date} 推荐，共 {len(codes)} 只股票")

        scored: list[dict] = []
        for code in codes:
            data = self.storage.load_stock_data(code, start, end)
            if len(data.prices) < min_data_days:
                continue

            signals: list[str] = []
            scores: list[float] = []

            for strategy in StrategyRegistry.get_all():
                result = strategy.analyze(data)
                scores.append(result.score)
                if result.signal == Signal.BUY:
                    signals.append(f"{strategy.name}:买入")
                elif result.signal == Signal.SELL:
                    signals.append(f"{strategy.name}:卖出")

            avg_score = sum(scores) / len(scores) if scores else 0.0
            buy_signals = [s for s in signals if "买入" in s]

            scored.append({
                "code": code,
                "score": avg_score,
                "signals": signals,
                "buy_signals_count": len(buy_signals),
            })

        # 按评分降序排列
        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[:top_n]

        # 生成推荐记录
        recommendations: list[Recommendation] = []
        for item in top:
            action = "buy" if item["buy_signals_count"] > 0 else "hold"
            risk = "low" if item["score"] > 70 else "medium" if item["score"] > 50 else "high"
            reason_parts = item["signals"][:3] if item["signals"] else ["综合评分较高"]

            rec = Recommendation(
                code=item["code"],
                recommend_date=recommend_date,
                score=Decimal(str(round(item["score"], 2))),
                signals=item["signals"],
                reason="，".join(reason_parts),
                suggested_action=action,
                risk_level=risk,
            )
            self.session.add(rec)
            recommendations.append(rec)

        self.session.commit()
        logger.info(f"生成 {len(recommendations)} 条推荐")
        return recommendations

    def get_daily_recommendations(self, target_date: date) -> list[Recommendation]:
        """获取指定日期的推荐清单"""
        return (
            self.session.query(Recommendation)
            .filter(Recommendation.recommend_date == target_date)
            .order_by(Recommendation.score.desc())
            .all()
        )
