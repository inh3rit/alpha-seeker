from datetime import date

from loguru import logger

from app.data.fetcher import AKShareFetcher
from app.data.storage import DataStorage
from app.database import SessionLocal
from app.services.notification import NotificationService
from app.services.recommendation import RecommendationService
from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.daily_pipeline")
def daily_pipeline() -> dict:
    """
    每日定时任务链：数据抓取 → 策略运行 → 推荐生成 → 通知推送
    在每个交易日 15:30 后执行
    """
    logger.info("开始执行每日任务链...")
    today = date.today()
    results = {}

    # Step 1: 抓取当日数据
    fetcher = AKShareFetcher()
    with SessionLocal() as session:
        storage = DataStorage(session)

        # 抓取股票列表（如果是首次运行）
        codes = storage.list_stock_codes()
        if not codes:
            logger.info("首次运行，抓取股票列表...")
            stocks = fetcher.fetch_stock_list()
            storage.upsert_stocks(stocks)
            codes = [s.code for s in stocks]
            results["stocks_fetched"] = len(codes)

        # 抓取日线数据（最近 5 天，覆盖可能的缺失）
        fetched_count = 0
        for code in codes[:100]:  # 限制数量避免超时
            try:
                from datetime import timedelta
                quotes = fetcher.fetch_daily_quotes(
                    code=code,
                    start_date=today - timedelta(days=5),
                    end_date=today,
                )
                if quotes:
                    storage.upsert_quotes(quotes)
                    fetched_count += 1
            except Exception as exc:
                logger.warning(f"抓取 {code} 失败: {exc}")
                continue

        results["quotes_fetched"] = fetched_count

    # Step 2: 生成推荐
    with SessionLocal() as session:
        rec_service = RecommendationService(session)
        recommendations = rec_service.generate_daily_recommendations(recommend_date=today)
        results["recommendations_count"] = len(recommendations)

        # Step 3: 推送通知
        notifier = NotificationService()
        sent = notifier.send_daily_report(recommendations, str(today))
        results["notification_sent"] = sent

    logger.info(f"每日任务链完成: {results}")
    return results
