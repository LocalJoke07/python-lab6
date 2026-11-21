import logging

from fastapi import FastAPI
import uvicorn

from app.api.routes import router
from app.config import get_settings
from app.domain.services import ItemService
from app.storage.repository import PostgresItemRepository


settings = get_settings()
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(levelname)s %(name)s %(message)s",
)

repository = PostgresItemRepository(settings.database_url)
item_service = ItemService(repository=repository)

app = FastAPI(
    title="Storage Service",
    version="2.0.0",
)
app.state.item_service = item_service
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
