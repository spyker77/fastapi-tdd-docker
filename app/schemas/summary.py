from typing import List, TypeAlias

from pydantic import AnyHttpUrl, BaseModel


class SummarySchema(BaseModel):
    id: int
    url: AnyHttpUrl
    summary: str
    user_id: int

    class Config:
        orm_mode = True


SummarySchemaList: TypeAlias = List[SummarySchema]


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl
