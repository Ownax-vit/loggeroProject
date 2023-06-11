from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Path
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_404_NOT_FOUND

from ....core.jwt import get_current_user_authorizer
from ....crud.journal import create_journal_data
from ....crud.journal import delete_journal_data
from ....crud.journal import get_journal_data
from ....crud.journal import get_list_journals
from ....crud.journal import update_journal_data
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.journal import JournalCreate
from ....models.journal import JournalInResponse
from ....models.journal import JournalUpdate
from ....models.journal import ListJournalInResponse
from ....models.user import User

router = APIRouter(tags=["journal"])


@router.post("/journal", status_code=HTTP_201_CREATED, response_model=JournalInResponse)
async def create_journal(
    journal: JournalCreate = Body(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> JournalInResponse:
    journal = await create_journal_data(db, journal, user.login)
    return JournalInResponse(**journal.dict(by_alias=True))


@router.get(
    "/journal/{journal_id}", status_code=HTTP_200_OK, response_model=JournalInResponse
)
async def get_journal(
    journal_id: str = Path(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    journal = await get_journal_data(db, journal_id, user.login)
    if not journal:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Journal with current id for this user not found!",
        )

    return JournalInResponse(**journal.dict(by_alias=True))


@router.put("/journal", status_code=HTTP_200_OK, response_model=JournalInResponse)
async def update_journal(
    journal: JournalUpdate = Body(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> JournalInResponse:
    journal = await update_journal_data(db, journal, user.login)
    return JournalInResponse(**journal.dict())


@router.delete("/journal/{journal_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_journal(
    journal_id: str = Path(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    await delete_journal_data(db, journal_id, user.login)


@router.get("/journals", status_code=HTTP_200_OK, response_model=ListJournalInResponse)
async def get_journals(
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> ListJournalInResponse:
    journal_group = await get_list_journals(db, user.login)
    if not journal_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Journals not found!"
        )
    return ListJournalInResponse(journals=journal_group)
