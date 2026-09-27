from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.inspections.dependencies import get_inspection_repository
from app.inspections.repository import InspectionRepository


class HealthResponse(BaseModel):
    status: str
    database: str


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(repository: InspectionRepository = Depends(get_inspection_repository)) -> dict:
    with repository.database.connection() as connection:
        connection.execute("SELECT 1").fetchone()
    return {"status": "ok", "database": "connected"}

