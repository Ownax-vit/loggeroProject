from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.api_v1.api import router as api_router
from .db.mongodb_utils import close_connection_mongo
from .db.mongodb_utils import connect_to_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_connection_mongo()


app = FastAPI(title="Loggero", lifespan=lifespan)


app.include_router(api_router)
