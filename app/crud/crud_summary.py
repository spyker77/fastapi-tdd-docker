from typing import Dict, List, Union

from app.models.summary import TextSummary
from app.schemas.summary import SummaryPayloadSchema, SummaryUpdatePayloadSchema


async def post(payload: SummaryPayloadSchema) -> int:
    summary = TextSummary(url=payload.url, summary="")
    await summary.save()
    return summary.id


async def get(id: int) -> Union[Dict, None]:
    summary = await TextSummary.filter(id=id).first().values()
    if summary:
        return summary[0]
    return None


async def get_all() -> List[Dict]:
    summaries = await TextSummary.all().values()
    return summaries


async def put(id: int, payload: SummaryUpdatePayloadSchema) -> Union[Dict, None]:
    summary = await TextSummary.filter(id=id).update(url=payload.url, summary=payload.summary)
    if summary:
        updated_summary = await TextSummary.filter(id=id).first().values()
        return updated_summary[0]
    return None


async def delete(id: int) -> int:
    summary = await TextSummary.filter(id=id).delete()
    return summary
