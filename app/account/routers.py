from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.db.config import SessionDep
from app.account.models import Users
from app.account.dependencies import GetCurrentUser, IsAdmin
from app.account.schemas import UserCreate, UserOut, PasswordChangeRequest
from app.account.services import CreateUserService, AuthenticateUserService, CreateTokenService, RefreshTokenService, ChangePasswordService, RevokeRefreshTokenService


router = APIRouter()


@router.post("/register", response_model = UserOut)
async def CreateUser(session: SessionDep, user: UserCreate):
    return await CreateUserService(session, user)


@router.post("/login")
async def AuthenticateUser(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await AuthenticateUserService(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    tokens = await CreateTokenService(session, user)
    response = JSONResponse(content={"access_token": tokens["access_token"]})
    response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 24 * 7)
    return response


@router.post("/refresh-token")
async def RefreshToken(session: SessionDep, request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token.")
    
    user = await RefreshTokenService(session, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")
    
    return await CreateTokenService(session, user)


@router.get("/get-user", response_model = UserOut)
async def GetUser(user: Users = Depends(GetCurrentUser)):
    return user


@router.post("/change-password")
async def ChangePassword(session: SessionDep, data: PasswordChangeRequest, user: Users = Depends(GetCurrentUser)):
    await ChangePasswordService(session, user, data)
    return JSONResponse(content={"msg": "Password has been changed."})


@router.get("/admin")
async def admin(user: Users = Depends(IsAdmin)):
    return JSONResponse(content={"msg": f"Welcome Admin {user.name}"})


@router.post("/logout")
async def LogoutProcess(session: SessionDep, request: Request):
    token = request.cookies.get("refresh_token")
    if token:
        await RevokeRefreshTokenService(session, token)
    
    response = JSONResponse(content={"detail": "Logged out"})
    response.delete_cookie("refresh_token")
    return response