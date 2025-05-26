from fastapi import HTTPException, Request, Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(identifier: str, password: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).filter(User.email == identifier))
    user = result.scalars().first()

    if user is None:
        result = await db.execute(select(User).filter(User.username == identifier))
        user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return user


async def get_current_user(request: Request, db: AsyncSession) -> Optional[User]:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


async def check_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
