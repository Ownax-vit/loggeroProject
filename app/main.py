from fastapi import FastAPI
from fastapi.routing import APIRouter

from .api.api_v1.api import router as api_router
from .db.mongodb_utils import connect_to_mongo, close_connection_mongo
app = FastAPI(title="Loggero")

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_connection_mongo)

app.include_router(api_router)
