from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Response
from fastapi import status
from fastapi.exceptions import HTTPException

from ....core.config import JWT_REFRESH_TOKEN_NAME
from ....core.config import JWT_TOKEN_PREFIX
from ....core.jwt import create_access_token
from ....core.jwt import create_refresh_token
from ....core.jwt import get_current_user_refresh
from ....crud.shortcuts import check_free_username_and_email
from ....crud.user import create_user
from ....crud.user import get_user_by_email
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.user import User
from ....models.user import UserInCreate
from ....models.user import UserInLogin
from ....models.user import UserInResponse

router = APIRouter(tags=["auth"])


@router.post(
    "/sign-in",
    response_model=UserInResponse,
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    user: UserInLogin = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
):
    db_user = await get_user_by_email(db, user.email)
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"login": db_user.login})
    refresh_token = create_refresh_token(data={"login": db_user.login})
    response.set_cookie(
        key=JWT_REFRESH_TOKEN_NAME,
        value=f"{JWT_TOKEN_PREFIX} {refresh_token}",
        httponly=True,
    )

    return UserInResponse(**db_user.dict(), token=access_token)


@router.get(
    "/refresh",
    response_model=UserInResponse,
    tags=["auth"],
    status_code=status.HTTP_201_CREATED,
)
async def refresh(
    response: Response,
    user: User = Depends(get_current_user_refresh),
):
    """Refresh JWT Token"""
    access_token = create_access_token(data={"login": user.login})
    refresh_token = create_refresh_token(data={"login": user.login})

    response.set_cookie(
        key=JWT_REFRESH_TOKEN_NAME,
        value=f"{JWT_TOKEN_PREFIX} {refresh_token}",
        httponly=True,
    )
    user.token = access_token

    return UserInResponse(**user.dict())


@router.post(
    "/sign-up",
    response_model=UserInResponse,
    tags=["auth"],
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    user: UserInCreate = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
):
    await check_free_username_and_email(db, user.login, user.email)

    db_user = await create_user(db, user)
    token = create_access_token(data={"login": db_user.login})

    return UserInResponse(**db_user.dict(by_alias=True), token=token)
