"""Automated model evaluation tasks."""

import structlog

from worker.celery_app import app

log = structlog.get_logger(__name__)


@app.task
def run_eval_suite(pipeline_id: str, eval_dataset_id: str):
    log.info("eval.start", pipeline_id=pipeline_id, eval_dataset_id=eval_dataset_id)


@app.task
def detect_model_drift(model_id: str):
    log.info("drift.detect", model_id=model_id)
