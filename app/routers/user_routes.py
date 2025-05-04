from fastapi import APIRouter, Depends
from schemas import UserCreate, UserRead
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.crud_user import create_user


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserRead)
async def add_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await create_user(user, db)
