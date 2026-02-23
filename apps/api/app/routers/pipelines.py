"""Pipeline CRUD + execution trigger."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_tenant, get_current_user
from app.models.pipeline import Pipeline, PipelineExecution

router = APIRouter()


class PipelineCreate(BaseModel):
    name: str
    description: str = ""
    steps: list[dict]
    nexus_orchestrated: bool = True


class ExecuteRequest(BaseModel):
    input: dict
    async_execution: bool = False


@router.get("/")
async def list_pipelines(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> dict:
    result = await db.execute(
        select(Pipeline)
        .where(Pipeline.status == "active", Pipeline.tenant_id == tenant["id"])
        .order_by(desc(Pipeline.created_at))
    )
    pipelines = result.scalars().all()
    return {
        "pipelines": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "total_runs": p.total_runs,
                "success_rate": p.success_rate,
                "status": p.status,
            }
            for p in pipelines
        ]
    }


@router.post("/", status_code=201)
async def create_pipeline(
    req: PipelineCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    pipeline = Pipeline(
        tenant_id=tenant["id"],
        created_by=user["id"],
        name=req.name,
        description=req.description,
        steps=req.steps,
        nexus_orchestrated=req.nexus_orchestrated,
    )
    db.add(pipeline)
    await db.commit()
    return {"id": pipeline.id, "name": pipeline.name}


@router.post("/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str,
    req: ExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> dict:
    result = await db.execute(
        select(Pipeline).where(Pipeline.id == pipeline_id, Pipeline.tenant_id == tenant["id"])
    )
    pipeline = result.scalar_one_or_none()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    execution = PipelineExecution(
        pipeline_id=pipeline_id,
        tenant_id=pipeline.tenant_id,
        total_steps=len(pipeline.steps),
        input_data=req.input,
    )
    db.add(execution)
    await db.commit()
    if req.async_execution:
        background_tasks.add_task(run_pipeline_async, execution.id, pipeline.id)
        return {"execution_id": execution.id, "status": "queued"}
    return {"execution_id": execution.id, "status": "running"}


async def run_pipeline_async(execution_id: str, pipeline_id: str) -> None:
    _ = (execution_id, pipeline_id)


@router.get("/{pipeline_id}/executions")
async def list_executions(
    pipeline_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[dict, Depends(get_current_tenant)],
) -> dict:
    result = await db.execute(
        select(PipelineExecution)
        .where(
            PipelineExecution.pipeline_id == pipeline_id,
            PipelineExecution.tenant_id == tenant["id"],
        )
        .limit(50)
    )
    execs = result.scalars().all()
    return {
        "executions": [
            {
                "id": e.id,
                "status": e.status,
                "cost_usd": e.cost_usd,
                "latency_ms": e.latency_ms,
                "started_at": e.started_at,
            }
            for e in execs
        ]
    }