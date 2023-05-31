from typing import Dict, List, Optional

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Summary
from app.schemas.summary import SummaryPayloadSchema


async def post(user_id: int, payload: SummaryPayloadSchema, db: AsyncSession = Depends(get_db)) -> Summary:
    summary = Summary(url=payload.url, summary="", user_id=user_id)
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    return summary


async def get(summary_id: int, db: AsyncSession = Depends(get_db)) -> Optional[Dict]:
    result = await db.execute(select(Summary).filter_by(id=summary_id))
    summary = result.scalar()
    if summary:
        return summary
    return None


async def get_all(db: AsyncSession = Depends(get_db)) -> List[Dict]:
    result = await db.execute(select(Summary))
    summaries = result.scalars().all()
    return [summary for summary in summaries if summary]


async def put(summary_id: int, payload: SummaryPayloadSchema, db: AsyncSession = Depends(get_db)) -> Dict:
    new_data = payload.dict(exclude_unset=True, exclude_defaults=True, exclude_none=True)
    await db.execute(update(Summary).where(Summary.id == summary_id).values(**new_data))
    await db.commit()

    result = await db.execute(select(Summary).filter_by(id=summary_id))
    updated_summary = result.scalar()
    return updated_summary


async def remove(summary_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await db.execute(delete(Summary).where(Summary.id == summary_id))
    await db.commit()
