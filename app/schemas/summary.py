from typing import List, Type

from pydantic import AnyHttpUrl, BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.pydantic.base import PydanticModel

from app.models.summary import TextSummary

SummarySchema = pydantic_model_creator(TextSummary)

SummarySchemaList: Type[List[PydanticModel]] = List[SummarySchema]


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl


class SummaryResponseSchema(SummaryPayloadSchema):
    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    summary: str
