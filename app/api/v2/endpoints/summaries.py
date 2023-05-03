from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.background.tasks import celery_generate_summary
from app.crud import crud_summary, crud_user
from app.database import get_db
from app.schemas.summary import SummaryPayloadSchema, SummarySchema, SummarySchemaList
from app.schemas.user import UserInDBSchema
from app.security.auth import get_current_active_user

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post(
    "/",
    response_model=SummarySchema,
    response_model_exclude={"summary"},
    status_code=status.HTTP_201_CREATED,
)
async def create_summary(
    payload: SummaryPayloadSchema,
    current_user: UserInDBSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    summary = await crud_summary.post(user_id=current_user.id, payload=payload, db=db)
    celery_generate_summary.delay(summary.id, payload.url)
    return summary


@router.get("/{id}", response_model=SummarySchema)
async def read_summary(id: UUID = Path(...), db: AsyncSession = Depends(get_db)):
    summary = await crud_summary.get(summary_id=id, db=db)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    return summary


@router.get("/", response_model=SummarySchemaList)
async def read_all_summaries(db: AsyncSession = Depends(get_db)):
    return await crud_summary.get_all(db=db)


@router.put("/{id}", response_model=SummarySchema)
async def update_summary(
    payload: SummaryPayloadSchema,
    id: UUID = Path(...),
    current_user: UserInDBSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    summary = await crud_summary.get(summary_id=id, db=db)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    if user := await crud_user.get(user_id=current_user.id, db=db):
        if (summary.user_id == current_user.id) or user.is_superuser:
            updated = await crud_summary.put(summary_id=id, payload=payload, db=db)
            celery_generate_summary.delay(id, payload.url)
            return updated
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient rights to update this summary"
            )


@router.delete("/{id}", response_model=SummarySchema)
async def delete_summary(
    id: UUID = Path(...),
    current_user: UserInDBSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    summary = await crud_summary.get(summary_id=id, db=db)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    if user := await crud_user.get(user_id=current_user.id, db=db):
        if (summary.user_id == current_user.id) or user.is_superuser:
            await crud_summary.remove(summary_id=id, db=db)
            return summary
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient rights to delete this summary"
            )
