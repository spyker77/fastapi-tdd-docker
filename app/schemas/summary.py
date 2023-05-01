from typing import List, TypeAlias
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel


class SummarySchema(BaseModel):
    id: UUID
    url: AnyHttpUrl
    summary: str
    user_id: UUID


SummarySchemaList: TypeAlias = List[SummarySchema]


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl
