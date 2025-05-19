from fastapi import HTTPException
from models import User
from schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy import select
from typing import List


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


async def create_user(user: UserCreate, db: AsyncSession) -> UserRead:
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email,
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
    if updated_user.username:
        user.username = updated_user.username
    if updated_user.email:
        user.email = updated_user.email
    if updated_user.password:
        user.hashed_password = hash_password(updated_user.password)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


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
