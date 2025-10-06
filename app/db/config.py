import os
from fastapi import Depends
from typing import AsyncGenerator, Annotated
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker



BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

db_path = os.path.join(BASE_DIR, "sqlite.db")

DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
