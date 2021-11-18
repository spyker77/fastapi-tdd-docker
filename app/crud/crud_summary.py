from typing import Dict, List, Optional
from uuid import UUID

from app.models import Summary
from app.schemas.summary import SummaryPayloadSchema


async def post(payload: SummaryPayloadSchema, user_id: UUID) -> Summary:
    summary = Summary(url=payload.url, summary="", user_id=user_id)
    await summary.save()
    return summary


async def get(id: UUID) -> Optional[Dict]:
    if summary := await Summary.filter(id=id).first():
        return dict(summary)
    return None


async def get_all() -> List[Dict]:
    return await Summary.all().values()


async def put(id: UUID, payload: SummaryPayloadSchema) -> Dict:
    new_data = payload.dict(exclude_unset=True, exclude_defaults=True, exclude_none=True)
    await Summary.filter(id=id).update(**new_data)
    updated_summary = await Summary.filter(id=id).first()
    return dict(updated_summary)  # type: ignore


async def delete(id: UUID) -> None:
    await Summary.filter(id=id).delete()
