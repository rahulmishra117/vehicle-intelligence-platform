from pydantic import BaseModel, Field

from app.inspections.schemas import Inspection


class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500, examples=["Why was vehicle CAR-1002 rejected?"])
    limit: int = Field(default=20, ge=1, le=100)


class QueryInterpretation(BaseModel):
    intent: str
    filters: dict[str, str | int]


class QueryResponse(BaseModel):
    answer: str
    interpretation: QueryInterpretation
    results: list[Inspection]
    count: int

