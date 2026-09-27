from fastapi import APIRouter, Depends, HTTPException, status

from app.inspections.dependencies import get_inspection_repository
from app.inspections.repository import InspectionRepository
from app.inspections.schemas import Inspection, InspectionCreate

router = APIRouter(prefix="/inspections", tags=["inspections"])
vehicle_router = APIRouter(prefix="/vehicles", tags=["inspections"])


@router.post("", response_model=Inspection, status_code=status.HTTP_201_CREATED)
def create_inspection(
    payload: InspectionCreate,
    repository: InspectionRepository = Depends(get_inspection_repository),
) -> dict:
    return repository.create(payload)


@router.get("/{inspection_id}", response_model=Inspection)
def get_inspection(
    inspection_id: int,
    repository: InspectionRepository = Depends(get_inspection_repository),
) -> dict:
    inspection = repository.get(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@vehicle_router.get("/{vehicle_id}/latest-inspection", response_model=Inspection)
def latest_inspection(
    vehicle_id: str,
    repository: InspectionRepository = Depends(get_inspection_repository),
) -> dict:
    inspection = repository.latest_for_vehicle(vehicle_id.upper())
    if not inspection:
        raise HTTPException(status_code=404, detail="Vehicle inspection not found")
    return inspection

