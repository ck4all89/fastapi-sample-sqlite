from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.mailbox.models import Mailbox
from app.mailbox.schemas import MailboxCreate, MailboxOut, MailboxUpdate



async def MailboxCreateService(session: AsyncSession, data: MailboxCreate) -> Mailbox:
    obj = Mailbox(to_email = data.to_email, from_email = data.from_email, subject = data.subject, contents = data.contents, is_active = True)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def ListMailboxService(session: AsyncSession, limit: int = 5, page: int = 1) -> dict:
    stmt = select(Mailbox)
    count_stmt = stmt.with_only_columns(func.count(Mailbox.id)).order_by(Mailbox.id)
    stmt = stmt.limit(limit).offset((page - 1) * limit)
    result = await session.execute(stmt)
   
    return {
        "total": await session.scalar(count_stmt),
        "page": page,
        "limit": limit,
        "items": result.scalars().all()
    }


async def SearchMailboxService(session: AsyncSession, to_email: str | None = None, from_email: str | None = None, subject: str | None = None, limit: int = 5, page: int = 1) -> dict:
    stmt = select(Mailbox)
    filters = []

    if to_email:
        filters.append(Mailbox.to_email.like(f"%{to_email}%"))

    if from_email:
        filters.append(Mailbox.from_email.like(f"%{from_email}%"))

    if subject:
        filters.append(Mailbox.subject.like(f"%{subject}%"))

    if filters:
        stmt = stmt.where(and_(*filters))

    count_stmt = stmt.with_only_columns(func.count(Mailbox.id)).order_by(Mailbox.id)
    stmt = stmt.limit(limit).offset((page - 1) * limit)
    result = await session.execute(stmt)
   
    return {
        "total": await session.scalar(count_stmt),
        "page": page,
        "limit": limit,
        "items": result.scalars().all()
    }


async def MailboxUpdateByIdService(session: AsyncSession, mailbox_id: int, data: MailboxUpdate) -> MailboxOut:
    mailbox = await session.get(Mailbox, mailbox_id)
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found.")

    if data.to_email is not None:
        mailbox.to_email = data.to_email
    if data.from_email is not None:
        mailbox.from_email = data.from_email
    if data.subject is not None:
        mailbox.subject = data.subject
    if data.contents is not None:
        mailbox.contents = data.contents
    if data.is_active is not None:
        mailbox.is_active = data.is_active

    await session.commit()
    await session.refresh(mailbox)
    return mailbox


async def DeleteMailboxService(session: AsyncSession, mailbox_id: int) -> bool:
    result = await session.execute(select(Mailbox).where(Mailbox.id == mailbox_id))
    obj = result.scalar()
    if not obj:
        return None
    await session.delete(obj)
    await session.commit()
    return True