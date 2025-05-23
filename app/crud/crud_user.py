from fastapi import HTTPException
from models import User
from schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy import select, or_, and_
from typing import List
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(user: UserCreate, db: AsyncSession) -> UserRead:
    existing_user = await db.execute(
        select(User).where(
            or_(User.email == user.email, User.username == user.username)
        )
    )
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=400, detail="User with this email or username already exists")

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        gender=user.gender,
        avatar_url=user.avatar_url,
        email=user.email,
        hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserRead.model_validate(new_user)


async def read_user(user_id: int, db: AsyncSession) -> UserRead:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


async def read_users(limit: int, offset: int, db: AsyncSession) -> List[UserRead]:
    result = await db.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]


async def update_user(user_id: int, updated_user: UserUpdate, db: AsyncSession) -> UserRead:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filters = []
    if updated_user.email:
        filters.append(User.email == updated_user.email)
    if updated_user.username:
        filters.append(User.username == updated_user.username)

    if filters:
        query = select(User).where(
            and_(
                or_(*filters),
                User.user_id != user_id
            )
        )
        existing_user = await db.execute(query)
        if existing_user.scalars().first():
            raise HTTPException(
                status_code=400, detail="User with this email or username already exists"
            )

    if updated_user.username:
        user.username = updated_user.username
    if updated_user.gender:
        user.gender = updated_user.gender
    if updated_user.avatar_url:
        if user.avatar_url and not user.avatar_url.endswith("default.png"):
            try:
                os.remove(user.avatar_url.lstrip("/"))
            except Exception:
                pass
        user.avatar_url = updated_user.avatar_url
    if updated_user.email:
        user.email = updated_user.email

    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


async def update_password(user_id: int, current_password: str, new_password: str, confirm_password: str, db: AsyncSession) -> None:
    if new_password != confirm_password:
        raise HTTPException(
            status_code=400, detail="New password and confirmation do not match")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(new_password)
    await db.commit()
    await db.refresh(user)


async def delete_user(user_id: int, db: AsyncSession) -> UserRead:
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = UserRead.model_validate(user)
    await db.delete(user)
    await db.commit()
    return deleted_user


async def read_non_admin_users(db: AsyncSession) -> List[UserRead]:
    result = await db.execute(select(User).where(User.role != "admin"))
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]
