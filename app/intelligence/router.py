from fastapi import APIRouter, Depends

from app.inspections.dependencies import get_inspection_repository
from app.inspections.repository import InspectionRepository
from app.intelligence.schemas import QueryRequest, QueryResponse
from app.intelligence.service import NaturalLanguageQueryService

router = APIRouter(prefix="/query", tags=["intelligence"])


@router.post("", response_model=QueryResponse)
def natural_language_query(
    payload: QueryRequest,
    repository: InspectionRepository = Depends(get_inspection_repository),
) -> dict:
    return NaturalLanguageQueryService(repository).execute(payload.query, payload.limit)

