"""Knowledge Base + RAG endpoints."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.knowledge_base import Document, KnowledgeBase

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    kb_ids: list[str]
    top_k: int = 5
    rerank: bool = True


@router.get("/")
async def list_knowledge_bases(db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    result = await db.execute(select(KnowledgeBase))
    kbs = result.scalars().all()
    return {
        "knowledge_bases": [
            {
                "id": kb.id,
                "name": kb.name,
                "total_documents": kb.total_documents,
                "total_chunks": kb.total_chunks,
            }
            for kb in kbs
        ]
    }


@router.post("/", status_code=201)
async def create_kb(name: str, description: str = "", db: AsyncSession = Depends(get_db)) -> dict:
    kb = KnowledgeBase(tenant_id="", name=name, description=description)
    db.add(kb)
    await db.commit()
    return {"id": kb.id, "name": kb.name}


@router.post("/{kb_id}/upload")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    if background_tasks is None:
        background_tasks = BackgroundTasks()

    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    content = await file.read()

    doc = Document(
        kb_id=kb_id,
        tenant_id=kb.tenant_id,
        name=file.filename or "unknown",
        file_size_bytes=len(content),
        mime_type=file.content_type or "application/octet-stream",
        status="pending",
    )
    db.add(doc)
    await db.commit()

    background_tasks.add_task(index_document, doc.id, content, kb.embedding_model)

    return {"id": doc.id, "name": doc.name, "status": "indexing", "size_bytes": len(content)}


async def index_document(doc_id: str, content: bytes, embedding_model: str) -> None:
    _ = (doc_id, content, embedding_model)


@router.post("/search")
async def search(req: SearchRequest) -> dict:
    return {"results": [], "query": req.query, "total_searched": 0}
