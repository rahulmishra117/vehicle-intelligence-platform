import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.db.database import Database
from app.inspections.repository import InspectionRepository
from app.inspections.router import router as inspections_router
from app.inspections.router import vehicle_router
from app.intelligence.router import router as intelligence_router
from app.system.router import router as system_router


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(config.database_path)
        database.initialize()
        app.state.inspection_repository = InspectionRepository(database)
        yield

    logging.basicConfig(level=config.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app = FastAPI(
        title=config.app_name,
        version="1.0.0",
        description="Store vehicle inspections and query them in natural language.",
        lifespan=lifespan,
    )
    api_prefix = "/api/v1"
    app.include_router(system_router, prefix=api_prefix)
    app.include_router(inspections_router, prefix=api_prefix)
    app.include_router(vehicle_router, prefix=api_prefix)
    app.include_router(intelligence_router, prefix=api_prefix)
    return app


app = create_app()
