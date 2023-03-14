from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.key import router as key_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(key_router, prefix="/key")
