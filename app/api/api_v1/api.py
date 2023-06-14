from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.journal import router as journal_router
from .endpoints.key import router as key_router
from .endpoints.log import router as log_router

tags_metadata_api = [
    {
        "name": "auth",
        "description": "Operations with auth: login, registration, refresh token (JWT)",
    },
    {
        "name": "key",
        "description": "Operations with api-keys. Api-key is token for one app that sends logs.",
    },
    {
        "name": "journal",
        "description": "Working with journal (project) that contains multiples api-keys for monitoring",
    },
    {
        "name": "log",
        "description": "Logs from app.",
    },
]

router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(key_router, prefix="/api-key")
router.include_router(journal_router, prefix="")
router.include_router(log_router, prefix="")


@router.get("/ping_test")
async def root():
    return {"message": "Hello world"}
