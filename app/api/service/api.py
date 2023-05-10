from fastapi import APIRouter

from .endpoints.log import router as log_route

router = APIRouter()
router.include_router(log_route, prefix="/log")
