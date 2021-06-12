from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path

from app.background.tasks import generate_summary
from app.crud import crud_summary
from app.schemas.summary import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummarySchema,
    SummaryUpdatePayloadSchema,
)

router = APIRouter()


@router.post("/", response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema, background_tasks: BackgroundTasks):
    summary_id = await crud_summary.post(payload)
    background_tasks.add_task(generate_summary, summary_id, payload.url)
    return SummaryResponseSchema(id=summary_id, url=payload.url)


@router.get("/{id}/", response_model=SummarySchema)
async def read_summary(id: int = Path(..., gt=0)):
    summary = await crud_summary.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.get("/", response_model=List[SummarySchema])
async def read_all_summaries():
    return await crud_summary.get_all()


@router.put("/{id}/", response_model=SummarySchema)
async def update_summary(payload: SummaryUpdatePayloadSchema, id: int = Path(..., gt=0)):
    summary = await crud_summary.put(id, payload)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.delete("/{id}/", response_model=SummaryResponseSchema)
async def delete_summary(id: int = Path(..., gt=0)):
    summary = await crud_summary.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    await crud_summary.delete(id)
    return SummaryResponseSchema(id=summary["id"], url=summary["url"])
