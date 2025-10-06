from uuid import uuid4
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.account.models import Users
from app.account.schemas import UserCreate, PasswordChangeRequest
from app.account.utils import HashPassword, VerifyPassword, CreateAccessToken


async def CreateUserService(session: AsyncSession, user: UserCreate):
    stmt = select(Users).where(Users.email == user.email)
    result = await session.scalars(stmt)
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    user_obj = Users(email=user.email, name=user.name, hashed_password=HashPassword(user.password))
    session.add(user_obj)
    await session.commit()
    await session.refresh(user_obj)
    return user_obj


async def AuthenticateUserService(session: AsyncSession, email: str, password: str):
    stmt = select(Users).where(Users.email == email)
    result = await session.scalars(stmt)
    user_obj = result.first()
    
    if not user_obj or not VerifyPassword(password, user_obj.hashed_password):
        return None
    
    return user_obj


async def CreateTokenService(session: AsyncSession, user: Users):
    access_token = CreateAccessToken(data={"sub": str(user.id)})
    refresh_token = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    user_obj = await session.execute(select(Users).where(Users.id == user.id))
    
    if not user_obj.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found.")
    
    await session.execute(update(Users).where(Users.id == user.id).values(token=refresh_token, expires_at=expires_at))
    await session.commit()

    return {"token_type": "bearer", "access_token": access_token, "refresh_token": refresh_token}


async def RefreshTokenService(session: AsyncSession, token: str):
    result = await session.scalars(select(Users).where(Users.token == token))
    user_obj = result.first()

    if user_obj and not user_obj.revoked:
        expires_at = user_obj.expires_at
        
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at > datetime.now(timezone.utc):
            return user_obj
    return None


async def ChangePasswordService(session: AsyncSession, user: Users, data: PasswordChangeRequest):
    if not VerifyPassword(data.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password is incorrect.")
    
    user.hashed_password = HashPassword(data.new_password)
    session.add(user)
    await session.commit()


async def RevokeRefreshTokenService(session: AsyncSession, token: str):
    result = await session.scalars(select(Users).where(Users.token == token))
    db_token = result.first()
    if db_token:
        db_token.revoked = True
        await session.commit()