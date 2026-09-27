from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(StrEnum):
    minor = "minor"
    major = "major"
    critical = "critical"


class Decision(StrEnum):
    approved = "approved"
    rejected = "rejected"
    review = "review"


class IssueCreate(BaseModel):
    category: str = Field(min_length=2, max_length=50)
    component: str = Field(min_length=2, max_length=100)
    severity: Severity
    description: str = Field(min_length=3, max_length=1000)
    repair_cost: float = Field(default=0, ge=0)


class InspectionCreate(BaseModel):
    vehicle_id: str = Field(min_length=2, max_length=50, examples=["CAR-1001"])
    make: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1980, le=2100)
    odometer_km: int = Field(ge=0)
    inspector: str = Field(min_length=2, max_length=100)
    decision: Decision
    notes: str = Field(default="", max_length=2000)
    issues: list[IssueCreate] = Field(default_factory=list)

    @field_validator("vehicle_id")
    @classmethod
    def normalize_vehicle_id(cls, value: str) -> str:
        return value.strip().upper()


class Issue(IssueCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Inspection(BaseModel):
    id: int
    vehicle_id: str
    make: str
    model: str
    year: int
    odometer_km: int
    inspector: str
    decision: Decision
    notes: str
    inspected_at: datetime
    issues: list[Issue]

