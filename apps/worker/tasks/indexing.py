"""Document indexing tasks — runs when files are uploaded."""

import structlog

from worker.celery_app import app

log = structlog.get_logger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def index_document(self, document_id: str, s3_key: str, kb_id: str, embedding_model: str):
    try:
        log.info("indexing.start", document_id=document_id, kb_id=kb_id, s3_key=s3_key)
        log.info("indexing.complete", document_id=document_id, embedding_model=embedding_model)
    except Exception as exc:
        log.error("indexing.failed", document_id=document_id, error=str(exc))
        raise self.retry(exc=exc)


@app.task
def reindex_knowledge_base(kb_id: str):
    log.info("reindex.start", kb_id=kb_id)
