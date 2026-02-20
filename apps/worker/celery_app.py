"""Celery app for background tasks."""

import os

from celery import Celery

app = Celery(
    "nexusai",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=["worker.tasks.indexing", "worker.tasks.eval", "worker.tasks.cost_report"],
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "daily-cost-report": {
            "task": "worker.tasks.cost_report.generate_daily_report",
            "schedule": 86400,
        },
        "check-budget-alerts": {
            "task": "worker.tasks.cost_report.check_budget_alerts",
            "schedule": 300,
        },
    },
)
