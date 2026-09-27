from fastapi import Request

from app.inspections.repository import InspectionRepository


def get_inspection_repository(request: Request) -> InspectionRepository:
    return request.app.state.inspection_repository

