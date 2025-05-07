from fastapi import APIRouter, Depends, Query, HTTPException
from schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.crud_user import create_user, read_user, read_users, update_user, delete_user
from auth import get_current_user
from models import User
from typing import List

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserRead, status_code=201)
async def add_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(user, db)


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await read_user(user_id, db)


@user_router.get("/", response_model=List[UserRead])
async def get_users(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)):
    return await read_users(limit, offset, db)


@user_router.patch("/{user_id}", response_model=UserRead)
async def patch_user(
        user_id: int,
        new_user: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=404, detail="You can only update your own profile")
    return await update_user(user_id, new_user, db)


@user_router.delete("/{user_id}", response_model=UserRead, status_code=200)
async def remove_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=404, detail="You can only delete your own profile")
    return await delete_user(user_id, db)
