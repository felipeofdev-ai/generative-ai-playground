"""Cost reporting and budget alerting tasks."""

import structlog

from worker.celery_app import app

log = structlog.get_logger(__name__)


@app.task
def generate_daily_report():
    log.info("cost_report.daily.start")
    log.info("cost_report.daily.complete")


@app.task
def check_budget_alerts():
    log.info("budget_alert.check.start")


@app.task
def send_alert(tenant_id: str, alert_type: str, details: dict):
    log.info("alert.send", tenant_id=tenant_id, type=alert_type, details=details)
