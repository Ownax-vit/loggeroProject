from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import router as api_router
from app.api.api_v1.api import tags_metadata_api
from app.api.service.api import router as api_router_service
from app.core.config import MONGODB_URL
from app.db.mongodb_utils import close_connection_mongo
from app.db.mongodb_utils import connect_to_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo(MONGODB_URL)
    yield
    await close_connection_mongo()


app = FastAPI(title="Loggero", lifespan=lifespan, openapi_tags=tags_metadata_api)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(api_router_service)
