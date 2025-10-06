from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from app.db.config import SessionDep
from app.account.models import Users
from app.account.dependencies import IsAdmin
from app.mailbox.schemas import PaginatedMailboxOut, MailboxCreate, MailboxOut, MailboxUpdate
from app.mailbox.services import MailboxCreateService, ListMailboxService, SearchMailboxService, MailboxUpdateByIdService, DeleteMailboxService


router = APIRouter()



@router.post("", response_model=MailboxOut)
async def MailboxCreate(session: SessionDep, data: MailboxCreate, admin_user: Users = Depends(IsAdmin)):
    return await MailboxCreateService(session, data)


@router.get("", response_model=PaginatedMailboxOut)
async def ListMailbox(session: SessionDep, limit: int = Query(default=5, ge=1, le=100), page: int = Query(default=1, ge=1)):
    return await ListMailboxService(session, limit, page)


@router.get("/search", response_model=PaginatedMailboxOut)
async def SearchMailbox(
    session: SessionDep,
    to_email: str | None = Query(None),
    from_email: str | None = Query(None),
    subject: str | None = Query(None),
    limit: int = Query(default=5, ge=1, le=100),
    page: int = Query(default=1, ge=1)
):
    return await SearchMailboxService(session=session, to_email=to_email, from_email=from_email, subject=subject, limit=limit, page=page)


@router.patch("/{mailbox_id}", response_model=MailboxOut)
async def MailboxUpdateById(session: SessionDep, mailbox_id: int, mailbox: MailboxUpdate, admin_user: Users = Depends(IsAdmin)):
    return await MailboxUpdateByIdService(session, mailbox_id, mailbox)


@router.delete("/{mailbox_id}", status_code=status.HTTP_204_NO_CONTENT)
async def DeleteMailbox(session: SessionDep, mailbox_id: int, admin_user: Users = Depends(IsAdmin)):
    success = await DeleteMailboxService(session, mailbox_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return JSONResponse(content={"msg": "Record has been deleted."})
