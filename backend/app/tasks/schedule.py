from celery.schedules import crontab

from app.tasks.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "daily-pipeline": {
        "task": "tasks.daily_pipeline",
        "schedule": crontab(hour=15, minute=35, day_of_week="1-5"),
    },
}
