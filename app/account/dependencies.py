from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from app.db.config import SessionDep
from app.account.models import Users
from app.account.utils import DecodeToken


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/account/login")


async def GetCurrentUser(session: SessionDep, token: str = Depends(oauth2_scheme)) -> Users:
    payload = DecodeToken(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    stmt = select(Users).where(Users.id == int(payload.get("sub")))
    result = await session.scalars(stmt)
    user_obj = result.first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user_obj


async def IsAdmin(user: Users = Depends(GetCurrentUser)) -> Users:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an Admin.")
    
    return user