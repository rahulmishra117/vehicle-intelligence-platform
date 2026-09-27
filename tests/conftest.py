from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from scripts.seed import SEED_DATA


@pytest.fixture
def client(tmp_path: Path):
    app = create_app(Settings(database_path=tmp_path / "test.db"))
    with TestClient(app) as test_client:
        repository = app.state.inspection_repository
        from app.inspections.schemas import InspectionCreate
        for item in SEED_DATA:
            repository.create(InspectionCreate.model_validate(item))
        yield test_client
