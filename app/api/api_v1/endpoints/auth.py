from fastapi import APIRouter


router = APIRouter(tags=["auth"])

@router.post("/sign-in/")
async def login():
    pass
