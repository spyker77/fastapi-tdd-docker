from pydantic import AnyHttpUrl, BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.summary import TextSummary

SummarySchema = pydantic_model_creator(TextSummary)


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl


class SummaryResponseSchema(SummaryPayloadSchema):
    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    summary: str
