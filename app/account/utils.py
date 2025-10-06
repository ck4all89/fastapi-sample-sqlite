from decouple import config
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError, ExpiredSignatureError


JWT_SECRET_KEY = config("JWT_SECRET_KEY")
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_TIME_MIN = config("JWT_ACCESS_TOKEN_TIME_MIN", cast=int)
JWT_REFRESH_TOKEN_TIME_DAY = config("JWT_REFRESH_TOKEN_TIME_DAY", cast=int)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def HashPassword(password: str):
    return pwd_context.hash(password)


def VerifyPassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def CreateAccessToken(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def DecodeToken(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
    except JWTError:
        return None