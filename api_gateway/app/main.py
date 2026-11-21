import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings
from app.domain.services import CatalogService
from app.storage.storage_client import StorageHttpClient

settings = get_settings()
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(levelname)s %(name)s %(message)s",
)

storage_client = StorageHttpClient(
    base_url=settings.storage_base_url,
    timeout_s=settings.storage_timeout_s,
)
catalog_service = CatalogService(storage=storage_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    app.state.catalog_service.close()


app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.catalog_service = catalog_service
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
